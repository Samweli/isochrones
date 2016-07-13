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
import processing

from iso.utilities.i18n import tr


from qgis.core import (
    QgsDataSourceURI,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMapLayerRegistry)

from qgis.utils import iface

from PyQt4.QtGui import (
    QDialog, QFileDialog, QProgressDialog)


def isochrone(
            input_network_file,
            input_catchment_file,
            progress_dialog=None):

        """Contains main logic on creating isochrone map
        :param input_network_file: Input network file
        :type input_network_file: str

        :param input_catchment_file: Input Catchment file.
        :type input_catchment_file: str

        :param progress_dialog: A progess dialog .
        :type progress_dialog: QProgressDialog

        :returns temp_output_directory: temporary path of the map
        :rtype temp_output_directory:str
        """
        if progress_dialog:
            progress_dialog.show()

        # Import files into database, have tables
        # connect to database
        # add the files get the tables name

        connection = psycopg2.connect(
            "dbname='roads' "
            "user='test' "
            "host='localhost' "
            "password='test'")

        curr = connection.cursor()

        # Create nodes from network

        if progress_dialog:
            progress_dialog.show()

            # Infinite progress bar when the server is fetching data.
            # The progress bar will be updated with the file size later.
            progress_dialog.setMinimum(0)
            progress_dialog.setMaximum(100)

            progress_dialog.setValue(0)

            label_text = tr("Creating network nodes table")
            progress_dialog.setLabelText(label_text)

        curr.execute(
            """CREATE OR REPLACE VIEW ext AS
                SELECT *, pgr_startpoint(geom), pgr_endpoint(geom)
                FROM dar""")
        connection.commit()

        curr.execute(
            """CREATE TABLE IF NOT EXISTS nodes AS
               SELECT row_number() OVER (ORDER BY foo.p)::integer AS id,
               foo.p AS the_geom
               FROM (
               SELECT DISTINCT ext.pgr_startpoint AS p FROM ext
               UNION
               SELECT DISTINCT ext.pgr_endpoint AS p FROM ext
               ) foo
               GROUP BY foo.p""")

        connection.commit()

        # Create routable network
        progress_dialog.setValue(10)
        label_text = tr("Creating a routable network table")
        progress_dialog.setLabelText(label_text)

        curr.execute(
            """CREATE TABLE IF NOT EXISTS network AS
               SELECT a.*, b.id as start_id, c.id as end_id FROM ext
               AS a
               JOIN nodes AS b ON a.pgr_startpoint = b.the_geom JOIN nodes AS c
               ON  a.pgr_endpoint = c.the_geom """)

        connection.commit()

        # Find nearest nodes from the catchments
        progress_dialog.setValue(30)
        label_text = tr("Preparing the catchment table")
        progress_dialog.setLabelText(label_text)

        # curr.execute(
        #    """ALTER TABLE facilities
        #        ADD COLUMN the_nearest_node integer;
        #
        #       CREATE TABLE temp AS
        #        SELECT a.gid, b.id, min(a.dist)
        #
        #        FROM
        #          (SELECT facilities.id as gid,
        #                  min(st_distance(facilities.geom, nodes.the_geom))
        #                   AS dist
        #           FROM facilities, nodes
        #           GROUP BY facilities.id) AS a,
        #          (SELECT facilities.id as gid, nodes.id,
        #                  st_distance(facilities.geom, nodes.the_geom) AS dist
        #           FROM facilities, nodes) AS b
        #        WHERE a.dist = b. dist
        #              AND a.gid = b.gid
        #        GROUP BY a.gid, b.id; """
        #      )
        # connection.commit()
        #
        # curr.execute(
        #     """UPDATE facilities
        #     SET the_nearest_node =
        #     (SELECT id
        #     FROM temp
        #     WHERE temp.gid = facilities.id);""")
        #
        # connection.commit()

        # Calculate drivetime for the nearest nodes

        progress_dialog.setValue(50)
        label_text = tr("Calculating drivetime for each catchment area")
        progress_dialog.setLabelText(label_text)

        curr.execute("""SELECT the_nearest_node from facilities""")
        rows = curr.fetchall()

        index = 0
        progress_percentage = 50

        for row in rows:
            # This step is 45% of all steps so calculating
            # percentage of each increment accordingly

            percentage = ((index + 1) / len(rows)) * 45
            percentage = round(percentage, 0)
            catchment_id = row[0]
            if index == 0:
                curr.execute(
                    """ CREATE TABLE
                        IF NOT EXISTS catchment AS
                    SELECT
                    id,
                    the_geom,
                    (SELECT sum(cost) FROM (
                       SELECT * FROM pgr_dijkstra('
                       SELECT id_0 AS id,
                          start_id::int4 AS source,
                          end_id::int4 AS target,
                          cost::float8 AS cost
                       FROM network',
                       '%s',
                       id,
                       false,
                       false)) AS foo ) AS cost
                    FROM nodes;""", (catchment_id,)
                 )
            else:
                curr.execute(
                    """ INSERT INTO catchment (
                    SELECT
                        id,
                        the_geom,
                        (SELECT sum(cost) FROM (
                           SELECT * FROM pgr_dijkstra('
                           SELECT id_0 AS id,
                              start_id::int4 AS source,
                              end_id::int4 AS target,
                              cost::float8 AS cost
                           FROM network',
                           '%s',
                           id,
                           false,
                           false)) AS foo ) AS cost
                    FROM nodes);""", (catchment_id,)

                )

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

        curr.execute(
            """ CREATE table catchment_final AS
               SELECT id, the_geom, min (cost) AS cost
               FROM catchment
               GROUP By id, the_geom
            """
               )

        connection.commit()

        # Export table as shapefile
        progress_percentage += 1
        progress_dialog.setValue(progress_percentage)
        label_text = tr("Exporting and preparing isochrone map")
        progress_dialog.setLabelText(label_text)

        uri = QgsDataSourceURI()
        # set host name, port, database name, username and password
        uri.setConnection("localhost", "5432", "roads", "test", "test")
        # set database schema, table name, geometry column and optionally
        # subset (WHERE clause)
        uri.setDataSource("public", "catchment_final", "the_geom")

        layer = QgsVectorLayer(uri.uri(), "isochrones", "postgres")

        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Run interpolation on the final file (currently use IDW)

        extent = layer.extent()
        xmin = extent[0]
        xmax = extent[1]
        ymin = extent[2]
        ymax = extent[3]

        raster_file = QgsRasterLayer('/tmp/isochrones/raster.asc')

        output_raster = processing.runalg(
            "grass:v.surf.idw",
            layer,
            12,
            2,
            "cost" ,
            False,
            "%f , %f, %f, %f "% (xmin, xmax, ymin, ymax),
            0.5,
            -1,
            0.001,
            raster_file)

        # Calculate contours

        # Style the tin , contour and network

        # Load tin, contour and network as one qgis doc

        progress_percentage += 4
        progress_dialog.setValue(progress_percentage)
        label_text = tr("Done loading isochrone map")

        progress_dialog.setLabelText(label_text)

        temp_output_directory = ''

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
