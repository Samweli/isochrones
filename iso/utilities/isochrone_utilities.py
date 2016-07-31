# -*- coding: utf-8 -*-
"""
/***************************************************************************
 isochrone utilities
                                 A QGIS plugin
 This plugin create isochrones maps.
                             -------------------
        begin                : 2016-07-02
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Samweli Mwakisambwe
        email                : smwakisambwe@worldbank.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import psycopg2
import re
import processing

from iso.utilities.i18n import tr

from qgis.core import (
    QgsDataSourceURI,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMapLayerRegistry,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsRasterBandStats)

from qgis.utils import iface

from PyQt4.QtGui import (
    QDialog,
    QFileDialog,
    QProgressDialog,
    QColor
    )
from PyQt4.QtCore import (
    QFileInfo)

from iso.utilities.qgis_utilities import (
    display_warning_message_box)


def isochrone(
        database_name,
        host_name,
        port_number,
        user_name,
        password,
        network,
        network_geom,
        network_id_column,
        catchment,
        catchment_geom,
        catchment_id_column,
        style_checked,
        parent_dialog,
        progress_dialog=None):

        """Contains main logic on creating isochrone map
        :param database_name: Database name
        :type database_name: str

        :param host_name: Database host
        :type host_name: str

        :param port_number: Port number for the host
        :type port_number: str

        :param user_name: Username for connection with database
        :type user_name: str

        :param password: Password
        :type password: str

        :param network: Schema and Table containing the network.
        :type network: str

        :param network_geom: Geometry column in network.
        :type network_geom: str

        :param network_id_column: Id column in network.
        :type network_id_column: str

        :param catchment: Schema and Table containing catchment areas.
        :type catchment: str

        :param catchment_geom: Geometry column in catchment.
        :type catchment_geom: str

        :param catchment_id_column: Id column in catchment.
        :type catchment_id_column: str

        :param style_checked: Value for either to create a map style
        or not.
        :type  style_checked: boolean

        :param parent_dialog: A dialog that called this function.
        :type parent_dialog: QProgressDialog

        :param progress_dialog: A progess dialog .
        :type progress_dialog: QProgressDialog

        :returns temp_output_directory: temporary path of the map
        :rtype temp_output_directory:str
        """

        # Import files into database, have tables
        # connect to database
        # add the files get the tables name

        connection = psycopg2.connect(
            "dbname='" + str(database_name) + "' "
            "user='" + str(user_name) + "' "
            "host='" + str(host_name) + "' "
            "password='" + str(password) + "' ")

        curr = connection.cursor()

        # Create nodes from network

        if progress_dialog:
            progress_dialog.show()

            # Infinite progress bar when the server is fetching data.
            # The progress bar will be updated with the file size later.
            progress_dialog.setMinimum(0)
            progress_dialog.setMaximum(100)

            label_text = tr("Creating network nodes table")
            progress_dialog.setLabelText(label_text)
            progress_dialog.setValue(0)

        network_array = network.split('.')
        network_table = str(network_array[1])
        network_schema = network_array[0]
        catchment = catchment.split('.')
        catchment_table = catchment[1]
        catchment_schema = catchment[0]

        if not network_geom:
            network_geom = "geom"
        if not catchment_geom:
            catchment_geom = "geom"

        arguments = {}
        arguments["network_table"] = network_table
        arguments["network_geom"] = network_geom
        arguments["network_id"] = network_id_column
        arguments["catchment_table"] = catchment_table
        arguments["catchment_geom"] = catchment_geom
        arguments["catchment_id"] = catchment_id_column
        arguments["database_name"] = database_name
        arguments["port_number"] = port_number

        sql = """Create or replace view network_cache as
            select *, pgr_startpoint(%(network_geom)s),
            pgr_endpoint(%(network_geom)s) from %(network_table)s""" % arguments
        
        sql = clean_query(sql)

        try:
            curr.execute(sql)
        except Exception as exception:
            display_warning_message_box(
                parent_dialog, "Error", exception.message)
            pass
        connection.commit()

        sql = """CREATE TABLE IF NOT EXISTS nodes AS
               SELECT row_number() OVER (ORDER BY foo.p)::integer AS id,
               foo.p AS the_geom
               FROM (
               SELECT DISTINCT network_cache.pgr_startpoint AS p
                FROM network_cache
               UNION
               SELECT DISTINCT network_cache.pgr_endpoint AS p
               FROM network_cache
               ) foo
               GROUP BY foo.p"""

        curr.execute(sql)

        connection.commit()

        # Create routable network
        progress_dialog.setValue(10)
        label_text = tr("Creating a routable network table")
        progress_dialog.setLabelText(label_text)


        sql = """CREATE TABLE IF NOT EXISTS routable_network AS
               SELECT a.*, b.id as start_id, c.id as end_id FROM
               network_cache
               AS a
               JOIN nodes AS b ON a.pgr_startpoint = b.the_geom JOIN
               nodes AS c
               ON  a.pgr_endpoint = c.the_geom """

        curr.execute(sql)

        connection.commit()

        # Find nearest nodes from the catchments
        progress_dialog.setValue(30)
        label_text = tr("Preparing the catchment table")
        progress_dialog.setLabelText(label_text)

        # Drop column if exists, this will allow to update the table
        # with new data

        sql = """ALTER TABLE %(catchment_table)s
               DROP COLUMN IF EXISTS the_nearest_node;""" % arguments

        sql = clean_query(sql)

        curr.execute(sql)
        connection.commit()

        sql = """ALTER TABLE %(catchment_table)s
               ADD COLUMN the_nearest_node integer;

              CREATE TABLE IF NOT EXISTS temp AS
               SELECT a.gid, b.id, min(a.dist)

               FROM
                 (SELECT %(catchment_table)s.%(catchment_id)s as gid,
                         min(st_distance(
                         %(catchment_table)s.%(catchment_geom)s,
                         nodes.the_geom))
                          AS dist
                  FROM %(catchment_table)s, nodes
                  GROUP BY %(catchment_table)s.%(catchment_id)s) AS a,
                 (SELECT %(catchment_table)s.%(catchment_id)s as gid,
                 nodes.id, st_distance(
                 %(catchment_table)s.%(catchment_geom)s,
                 nodes.the_geom) AS dist
                  FROM %(catchment_table)s, nodes) AS b
               WHERE a.dist = b. dist
                     AND a.gid = b.gid
               GROUP BY a.gid, b.id; """ % arguments
        sql = clean_query(sql)

        curr.execute(sql)
        connection.commit()

        sql = """UPDATE %(catchment_table)s
            SET the_nearest_node =
            (SELECT id
            FROM temp
            WHERE temp.gid =
             %(catchment_table)s.%(catchment_id)s LIMIT 1);""" %arguments

        sql = clean_query(sql)

        curr.execute(sql)
        connection.commit()

        # Calculate drivetime for the nearest nodes

        progress_dialog.setValue(50)
        label_text = tr("Calculating drivetime for each catchment area")
        progress_dialog.setLabelText(label_text)

        sql = """SELECT the_nearest_node from
              %(catchment_table)s""" % arguments
        sql = clean_query(sql)

        curr.execute(sql)
        rows = curr.fetchall()

        index = 0
        progress_percentage = 50

        for row in rows:
            # This step is 45% of all steps so calculating
            # percentage of each increment accordingly

            percentage = ((index + 1) / len(rows)) * 45
            percentage = round(percentage, 0)
            catchment_id = row[0]
            arguments["catchment_current_id"] = catchment_id
            if index == 0:
                sql = """ CREATE TABLE
                        IF NOT EXISTS catchment_with_cost AS
                    SELECT
                    id,
                    the_geom,
                    (SELECT sum(cost) FROM (
                       SELECT * FROM pgr_dijkstra('
                       SELECT %(network_id)s AS id,
                          start_id::int4 AS source,
                          end_id::int4 AS target,
                          cost::float8 AS cost
                       FROM routable_network',
                       %(catchment_current_id)s,
                       id,
                       false,
                       false)) AS foo ) AS cost
                    FROM nodes;""" % arguments
                sql = clean_query(sql)
                curr.execute(sql)
            else:
                sql = """ INSERT INTO catchment_with_cost (
                    SELECT
                        id,
                        the_geom,
                        (SELECT sum(cost) FROM (
                           SELECT * FROM pgr_dijkstra('
                           SELECT  %(network_id)s AS id,
                              start_id::int4 AS source,
                              end_id::int4 AS target,
                              cost::float8 AS cost
                           FROM routable_network',
                           %(catchment_current_id)s,
                           id,
                           false,
                           false)) AS foo ) AS cost
                    FROM nodes);""" % arguments

                sql = clean_query(sql)

                curr.execute(sql)

            index += 1
            connection.commit()
            progress_percentage += percentage
            progress_dialog.setValue(progress_percentage)

            label_text = tr(
                str(index) +
                " catchment area(s) out of " +
                str(len(rows)) +
                " is(are) done")
            progress_dialog.setLabelText(label_text)

        label_text = tr("Preparing all the catchment areas table")
        progress_dialog.setLabelText(label_text)

        sql = """ CREATE TABLE IF NOT EXISTS catchment_final AS
               SELECT id, the_geom, min (cost) AS %s
               FROM catchment_with_cost
               GROUP By id, the_geom
            """ % "drivetime"

        sql = clean_query(sql)

        curr.execute(sql)

        connection.commit()

        sql = """ CREATE TABLE IF NOT EXISTS catchment_final_no_null AS
                SELECT *, (drivetime * 60) AS minutes FROM catchment_final WHERE %s
                IS NOT NULL
            """% "drivetime"

        sql = clean_query(sql)

        curr.execute(sql)

        connection.commit()

        uri = QgsDataSourceURI()
        # set host name, port, database name, username and password
        uri.setConnection(
            host_name,
            port_number,
            database_name,
            user_name,
            password)
        # set database schema, table name, geometry column and optionally
        # subset (WHERE clause)
        uri.setDataSource(
            network_schema,
            "catchment_final_no_null",
            "the_geom")

        # Export table as shapefile

        layer = QgsVectorLayer(uri.uri(), "isochrones", "postgres")

        QgsMapLayerRegistry.instance().addMapLayers([layer])

        iface.mapCanvas().refresh()

        layer_name = layer.dataProvider().dataSourceUri()

        (temp_output_directory, layer_name) = os.path.split(layer_name)

        if style_checked:

            progress_percentage += 1
            progress_dialog.setValue(progress_percentage)
            label_text = tr("Exporting and preparing isochrone map")
            progress_dialog.setLabelText(label_text)

            # TODO implement style creation logic

            # Run interpolation on the final file (currently use IDW)

            output_raster = processing.runalg(
                'gdalogr:gridinvdist',
                layer,
                'minutes',
                2, 0, 0, 0, 0, 0, 0, 0, 5,
                "[temporary file]")
            # retrieve the raster output and load it in Qgis:

            output_file = output_raster['OUTPUT']
            file_info = QFileInfo(output_file)
            base_name = file_info.baseName()

            raster_file = QgsRasterLayer(output_file, base_name)

            if raster_file.isValid():
                color_shader = QgsColorRampShader()
                color_shader.setColorRampType(QgsColorRampShader.INTERPOLATED)
                colors = {
                    'deep_green': '#1a9641',
                    'light_green': '#a6d96a',
                    'pale_yellow': '#ffffc0',
                    'light_red': '#fdae61',
                    'red': '#d7191c'
                }
                provider = raster_file.dataProvider()
                stats = provider.bandStatistics(
                    1,
                    QgsRasterBandStats.All,
                    raster_file.extent(),
                    0)

                values = {}

                if stats:
                    min = stats.minimumValue
                    max = stats.maximumValue
                    stat_range = max - min
                    add = stat_range / 4
                    values[0] = min
                    value = min
                    for index in range(1, 4):
                        value += add
                        values[index] = value
                    values[4] = max
                else:
                    display_warning_message_box(
                        parent_dialog,
                        parent_dialog.tr(
                            'Problem indexing the isochrones map'),
                        parent_dialog.tr('Error loading isochrone map'))

                color_list = [
                    QgsColorRampShader.ColorRampItem(
                        values[0],
                        QColor(colors['deep_green'])),
                    QgsColorRampShader.ColorRampItem(
                        values[1],
                        QColor(colors['light_green'])),
                    QgsColorRampShader.ColorRampItem(
                        values[2],
                        QColor(colors['pale_yellow'])),
                    QgsColorRampShader.ColorRampItem(
                        values[3],
                        QColor(colors['light_red'])),
                    QgsColorRampShader.ColorRampItem(
                        values[4],
                        QColor(colors['red']))
                ]

                color_shader.setColorRampItemList(color_list)
                raster_shader = QgsRasterShader()
                raster_shader.setRasterShaderFunction(color_shader)

                renderer = QgsSingleBandPseudoColorRenderer(
                    raster_file.dataProvider(),
                    1,
                    raster_shader)
                raster_file.setRenderer(renderer)
                QgsMapLayerRegistry.instance().addMapLayer(raster_file)

            else:
                display_warning_message_box(
                    parent_dialog,
                    parent_dialog.tr(
                        'Could not load interpolated file!'),
                    parent_dialog.tr('Error loading isochrone map'))

            # Generate contours

            output_vector = processing.runalg(
                'gdalogr:contour',
                raster_file,
                1,
                'minutes',
                None,
                '[temporary_file]')
            drivetime_layer = QgsVectorLayer(
                output_vector['OUTPUT_VECTOR'],
                'Drivetime',
                'ogr')
            # Load the network

            uri.setDataSource(network_schema, network_table, network_geom)
            network_layer = QgsVectorLayer(
                uri.uri(),
                "network",
                "postgres")

            uri.setDataSource(
                catchment_schema,
                catchment_table,
                catchment_geom)
            catchment_layer = QgsVectorLayer(
                uri.uri(),
                "catchment",
                "postgres")

            # Style the tin, contour and network

            drivetime_style = resources_path(
                'styles',
                'qgis',
                'drivetimes.qml')
            drivetime_layer.loadNamedStyle(drivetime_style)

            network_style = resources_path(
                'styles',
                'qgis',
                'network.qml')
            network_layer.loadNamedStyle(network_style)

            catchment_style = resources_path(
                'styles',
                'qgis',
                'catchment.qml')
            catchment_layer.loadNamedStyle(catchment_style)

            if drivetime_layer.isValid():
                QgsMapLayerRegistry.instance().addMapLayers(
                    [drivetime_layer])
            else:
                display_warning_message_box(
                    parent_dialog,
                    parent_dialog.tr(
                        "Could not load drivetimes file!"),
                    parent_dialog.tr('Error loading isochrone map'))

            if network_layer.isValid():
                QgsMapLayerRegistry.instance().addMapLayers(
                    [network_layer])
            else:
                display_warning_message_box(
                    parent_dialog,
                    parent_dialog.tr(
                        "Could not load network file!"),
                    parent_dialog.tr('Error loading isochrone map'))

            if catchment_layer.isValid():
                QgsMapLayerRegistry.instance().addMapLayers(
                    [catchment_layer])
            else:
                display_warning_message_box(
                    parent_dialog,
                    parent_dialog.tr(
                        "Could not load catchment file!"),
                    parent_dialog.tr('Error loading isochrone map'))

            # Load tin, contour and network as one qgis doc

            progress_percentage += 4
            progress_dialog.setValue(progress_percentage)
            label_text = tr("Done loading isochrone map")

            progress_dialog.setLabelText(label_text)

            temp_output_directory = ''

        progress_dialog.setValue(100)

        if progress_dialog:
            progress_dialog.done(QDialog.Accepted)

        return temp_output_directory


def resources_path(*args):
    """Get the path to our resources folder.

    .. versionadded:: 3.0

    Note that in version 3.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param args List of path elements e.g. ['img', 'logos', 'image.png']
    :type args: list

    :return: Absolute path to the resources folder.
    :rtype: str
    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(
        os.path.join(path, os.path.pardir, os.path.pardir, 'resources'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path

# def unique_filename(**kwargs):
#     """Create new filename guaranteed not to exist previously
#
#     """
#     if 'dir' not in kwargs:
#         path = temp_dir('iso')
#         kwargs['dir'] = path
#     else:
#         path = temp_dir(kwargs['dir'])
#         kwargs['dir'] = path
#     if not os.path.exists(kwargs['dir']):
#         # Ensure that the dir mask won't conflict with the mode
#         # Umask sets the new mask and returns the old
#         umask = os.umask(0000)
#         # Ensure that the dir is world writable by explicitly setting mode
#         os.makedirs(kwargs['dir'], 0777)
#         # Reinstate the old mask for tmp dir
#         os.umask(umask)
#     # Now we have the working dir set up go on and return the filename
#     handle, filename = mkstemp(**kwargs)
#
#     # Need to close it using the file handle first for windows!
#     os.close(handle)
#     try:
#         os.remove(filename)
#     except OSError:
#         pass
#     return filename

# def temp_dir(sub_dir='work'):
#     """Obtain the temporary working directory for the operating system.
#
#     :param sub_dir: Optional argument which will cause an additional
#         subdirectory to be created e.g. /tmp/isochrones/foo/
#     :type sub_dir: str
#
#     :return: Path to the temp dir that is created.
#     :rtype: str
#
#     :raises: Any errors from the underlying system calls.
#     """
#     user = getpass.getuser().replace(' ', '_')
#     current_date = date.today()
#     date_string = current_date.isoformat()
#     if 'ISOCHRONE_WORK_DIR' in os.environ:
#         new_directory = os.environ['ISOCHRONE_WORK_DIR']
#     else:
#         # Following 4 lines are a workaround for tempfile.tempdir()
#         # unreliabilty
#         handle, filename = mkstemp()
#         os.close(handle)
#         new_directory = os.path.dirname(filename)
#         os.remove(filename)
#
#     path = os.path.join(new_directory, 'isochrones', date_string, user, sub_dir)
#
#     if not os.path.exists(path):
#         # Ensure that the dir is world writable
#         # Umask sets the new mask and returns the old
#         old_mask = os.umask(0000)
#         os.makedirs(path, 0777)
#         # Reinstate the old mask for tmp
#         os.umask(old_mask)
#     return path


def clean_query(query):
    """Get the path to our resources folder.

    .. versionadded:: 3.0

    Note that in version 3.0 we removed the use of Qt Resource files in
    favour of directly accessing on-disk resources.

    :param query: sql query
    :type query: str

    :return: cleaned sql query
    :rtype: str"""

    query = query.replace('\n', ' ')
    query = re.sub(r'\s+', ' ', query)
    query = query.replace('( ', '(')
    query = query.replace(' )', ')')
    query = query.strip()

    return query
