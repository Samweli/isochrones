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
from iso.utilities.db import *


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
        contour_interval,
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

        :param contour_interval: Interval between contour, if contour
        wiil be generated
        :type  contour_interval: int

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

        create_network_view(connection, curr, arguments, parent_dialog)

        create_nodes(connection, curr, arguments, parent_dialog)

        # Create routable network

        progress_dialog.setValue(10)
        label_text = tr("Creating a routable network table")
        progress_dialog.setLabelText(label_text)

        create_routable_network(connection, curr, arguments, parent_dialog)

        # Find nearest nodes from the catchments
        progress_dialog.setValue(30)
        label_text = tr("Preparing the catchment table")
        progress_dialog.setLabelText(label_text)

        update_catchment(connection, curr, arguments, parent_dialog)

        # Calculate drivetime for the nearest nodes

        progress_percentage = 50

        progress_dialog.setValue(progress_percentage)
        label_text = tr("Calculating drivetime for each catchment area")
        progress_dialog.setLabelText(label_text)

        calculate_drivetimes(
            connection,
            curr,
            arguments,
            parent_dialog,
            progress_percentage)

        prepare_drivetimes_table(connection, curr, arguments, parent_dialog)

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

            # Run interpolation on the final file (currently using IDW)

            raster_file = idw_interpolation(layer, parent_dialog)

            # Generate drivetimes contour

            drivetime_layer = generate_drivetimes_contour(
                raster_file,
                contour_interval)

            # Load all the required layers

            args = {}
            args['network_schema'] = network_schema
            args['network_table'] = network_table
            args['network_geom'] = network_geom
            args['catchment_schema'] = catchment_schema
            args['catchment_table'] = catchment_table
            args['catchment_geom'] = catchment_geom

            load_map_layers(uri, parent_dialog, drivetime_layer, args)

            progress_percentage += 4
            progress_dialog.setValue(progress_percentage)
            label_text = tr("Done loading isochrone map")

            progress_dialog.setLabelText(label_text)

        progress_dialog.setValue(100)

        if progress_dialog:
            progress_dialog.done(QDialog.Accepted)


def idw_interpolation(layer, parent_dialog):
    """Run interpolation using inverse distance weight algorithm

    :param layer: Vector layer with drivetimes
    :type layer: QgsVectorLayer

    :param parent_dialog: A dialog that called this function.
    :type parent_dialog: QProgressDialog

    :returns raster_layer: Interpolated raster layer with drivetimes
    :rtype raster_layer: QgsRasterLayer

    """
    output_raster = processing.runalg(
        'gdalogr:gridinvdist',
        layer,
        'minutes',
        2, 0, 0, 0, 0, 0, 0, 0, 5,
        "[temporary file]")

    # retrieving the raster output , styling it and load it in Qgis

    output_file = output_raster['OUTPUT']
    file_info = QFileInfo(output_file)
    base_name = file_info.baseName()

    raster_layer = QgsRasterLayer(output_file, base_name)

    if raster_layer.isValid():
        color_shader = QgsColorRampShader()
        color_shader.setColorRampType(QgsColorRampShader.INTERPOLATED)
        colors = {
            'deep_green': '#1a9641',
            'light_green': '#a6d96a',
            'pale_yellow': '#ffffc0',
            'light_red': '#fdae61',
            'red': '#d7191c'
        }
        provider = raster_layer.dataProvider()
        stats = provider.bandStatistics(
            1,
            QgsRasterBandStats.All,
            raster_layer.extent(),
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
            raster_layer.dataProvider(),
            1,
            raster_shader)
        raster_layer.setRenderer(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(raster_layer)

    else:
        display_warning_message_box(
            parent_dialog,
            parent_dialog.tr(
                'Could not load interpolated file!'),
            parent_dialog.tr('Error loading isochrone map'))

    return raster_layer


def generate_drivetimes_contour(raster_layer, interval):
    """Create drive times contour

    :param raster_layer: Interpolated raster layer with drivetimes
    :type raster_layer: QgsRasterLayer

    :returns layer: Vector layer with contour drivetimes
    :rtype layer: QgsVectorLayer

    """
    output_vector = processing.runalg(
                'gdalogr:contour',
                raster_layer,
                interval,
                'minutes',
                None,
                '[temporary_file]')
    drivetime_layer = QgsVectorLayer(
                output_vector['OUTPUT_VECTOR'],
                'time(min)',
                'ogr')
    return drivetime_layer


def load_map_layers(uri, parent_dialog, drivetime_layer, args):
    """Style map layers and load them in Qgis

    :param uri: Connection to the database
    :type uri: QgsDataSourceURI

    :param parent_dialog: A dialog that called this function.
    :type parent_dialog: QProgressDialog

    :param drivetime_layer: A layer containing drivetimes
    :type drivetime_layer: QgsVectorLayer

    :param args: List containing database parameters
    :type args: {}

    """

    uri.setDataSource(
        args['network_schema'],
        args['network_table'],
        args['network_geom'])
    network_layer = QgsVectorLayer(
        uri.uri(),
        "network",
        "postgres")

    uri.setDataSource(
        args['catchment_schema'],
        args['catchment_table'],
        args['catchment_geom'])
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


def resources_path(*args):
    """Get the path to our resources folder.

    :param args List of path elements e.g. ['img', 'examples', 'isochrone.png']
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
#     path = os.path.join(
#             new_directory,
#             'isochrones',
#              date_string,
#              user,
#              sub_dir)
#
#     if not os.path.exists(path):
#         # Ensure that the dir is world writable
#         # Umask sets the new mask and returns the old
#         old_mask = os.umask(0000)
#         os.makedirs(path, 0777)
#         # Reinstate the old mask for tmp
#         os.umask(old_mask)
#     return path
