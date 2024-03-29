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
from builtins import range
import psycopg2
import processing
import tempfile

from processing.core.Processing import Processing

from qgis.core import (
    QgsDataSourceUri,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProject,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsRasterBandStats,
    QgsVectorFileWriter)

from qgis.utils import *

from qgis.PyQt.QtWidgets import QDialog, QProgressDialog
from qgis.PyQt.QtGui import QColor

from qgis.PyQt.QtCore import Qt

from common.exceptions import \
    IsochroneMapStyleError

from .db_functions import *
from .utils import display_warning_message_box, resources_path


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
    will be generated
    :type  contour_interval: int

    :param parent_dialog: A dialog that called this function.
    :type parent_dialog: QProgressDialog

    :param progress_dialog: A progess dialog .
    :type progress_dialog: QProgressDialog

    :returns layer_name: temporary path of the isochrones map layer
    :rtype layer_name: str
    """

    # Import files into database, have tables
    # connect to database
    # add the files get the tables name

    connection = psycopg2.connect(
        "dbname='" + str(database_name) + "' "
        "user='" + str(user_name) + "' "
        "host='" + str(host_name) + "' "
        "port='" + str(port_number) + "' "
        "password='" + str(password) + "' ")

    curr = connection.cursor()

    # Setting up progress window
    progress_dialog = QProgressDialog('Progress', 'Cancel', 0, 100)
    progress_dialog.forceShow()
    progress_dialog.setWindowModality(Qt.WindowModal)

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

    try:

        create_network_view(
            connection,
            curr,
            arguments,
            parent_dialog,
            progress_dialog)

        create_nodes(connection, curr, arguments, parent_dialog)

        # Create routable network
        progress_percentage = 10

        progress_dialog.setValue(int(progress_percentage))
        label_text = tr("Creating a routable network table")
        progress_dialog.setLabelText(label_text)

        if progress_dialog.wasCanceled():
            return

        create_routable_network(connection, curr, arguments, parent_dialog)

        # Find the nearest nodes from the catchments
        progress_percentage = 30
        progress_dialog.setValue(progress_percentage)
        label_text = tr("Preparing the catchment table")
        progress_dialog.setLabelText(label_text)

        if progress_dialog.wasCanceled():
            return

        update_catchment(connection, curr, arguments, parent_dialog)

        # Calculate drivetimes for the nearest nodes

        progress_percentage = 50

        progress_dialog.setValue(progress_percentage)
        label_text = tr("Calculating drivetime for each catchment area")
        progress_dialog.setLabelText(label_text)

        if progress_dialog.wasCanceled():
            return

        progress_percentage = calculate_drivetimes(
            connection,
            curr,
            arguments,
            progress_dialog,
            parent_dialog,
            progress_percentage)

        if progress_dialog.wasCanceled():
            return

        prepare_drivetimes_table(connection, curr, arguments, parent_dialog)

        uri = QgsDataSourceUri()
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

        # Export table as a shapefile

        layer = QgsVectorLayer(uri.uri(), "isochrones", "ogr")
        temp_layer = QgsVectorLayer(uri.uri(), "isochrones", "postgres")

        QgsProject.instance().addMapLayers([temp_layer])

        if iface:
            iface.mapCanvas().refresh()

        layer_name = temp_layer.dataProvider().dataSourceUri()

        if style_checked:
            args = {}
            args['network_schema'] = network_schema
            args['network_table'] = network_table
            args['network_geom'] = network_geom
            args['catchment_schema'] = catchment_schema
            args['catchment_table'] = catchment_table
            args['catchment_geom'] = catchment_geom

            prepare_map_style(
                    uri,
                    progress_percentage,
                    contour_interval,
                    progress_dialog,
                    temp_layer,
                    parent_dialog,
                    args)

        if progress_dialog:
            progress_dialog.setValue(100)
            progress_dialog.done(QDialog.Accepted)

        return layer_name

    except (IsochroneDBError,
            IsochroneMapStyleError
            ) as exception:
        return None


def prepare_map_style(
        uri,
        progress_percentage,
        contour_interval,
        progress_dialog,
        temp_layer,
        parent_dialog,
        args):
    """Prepare map style if user requested for it

    :param uri: Identifier for the final layer table
    :type uri: QgsDataSourceUri

    :param progress_percentage: Progress percentage.
    :type progress_percentage: int

    :param contour_interval: Drivetime interval.
    :type contour_interval: int

    :param progress_dialog: Dialog for progress.
    :type progress_dialog: QDialog

    :param temp_layer: Temporary result layer.
    :type temp_layer: QgsVectorLayer

    :param parent_dialog: Isochrone parent dialog.
    :type parent_dialog: QDialog

    :param args: Database tables arguments
    :type args: {}

    """

    progress_percentage += 1
    if progress_dialog:
        progress_dialog.setValue(int(progress_percentage))
    label_text = tr("Exporting and preparing isochrone map")
    progress_dialog.setLabelText(label_text)

    if progress_dialog.wasCanceled():
        return

    # TODO implement style creation logic

    # Run interpolation on the final file (currently using IDW)
    raster_file = idw_interpolation(temp_layer, parent_dialog)

    # Generate drivetimes contour
    try:
        drivetime_layer = generate_drivetimes_contour(
            raster_file,
            contour_interval,
            parent_dialog)

        # Load all the required layers

        load_map_layers(uri, parent_dialog, drivetime_layer, args)

    except Exception as exception:
        message = 'Error generating drivetimes \n {}'. \
            format(str(exception))

        display_warning_message_box(
            parent_dialog,
            parent_dialog.tr(
                'Error'),
            parent_dialog.tr(
                message
            )
        )

        raise IsochroneMapStyleError

    progress_percentage += 4
    if progress_dialog:
        progress_dialog.setValue(int(progress_percentage))
        label_text = tr("Done, loading isochrone map")
        progress_dialog.setLabelText(label_text)

        if progress_dialog.wasCanceled():
            return


def idw_interpolation(layer, parent_dialog):
    """Run interpolation using inverse distance weight algorithm

    :param layer: Vector layer with drivetimes
    :type layer: QgsVectorLayer

    :param parent_dialog: A dialog for showing progress.
    :type parent_dialog: QProgressDialog

    :returns raster_layer: Interpolated raster layer with drivetimes
    :rtype raster_layer: QgsRasterLayer

    """
    raster_layer = None
    try:
        Processing.initialize()

        # Create temporary file

        temp_output_file = tempfile.NamedTemporaryFile()
        temp_output_file_path = temp_output_file.name + '.tif'

        saved_layer = save_layer(layer)

        params = {'INPUT': saved_layer.dataProvider().dataSourceUri(),
                  'Z_FIELD': 'minutes',
                  'POWER': 2,
                  'SMOOTHING': 0,
                  'RADIUS_1': 0,
                  'RADIUS_2': 0,
                  'ANGLE': 0,
                  'MAX_POINTS': 0,
                  'MIN_POINTS': 0,
                  'NODATA': 0,
                  'DATA_TYPE': 5,
                  'OUTPUT': temp_output_file_path
                  }

        output_raster = processing.run(
            'gdal:gridinversedistance', params
        )

        output_file = output_raster['OUTPUT']

        # retrieving the raster output , styling it and load it in Qgis

        raster_layer = QgsRasterLayer(output_file, 'styled map')

        raster_layer = style_raster_layer(raster_layer, parent_dialog)

        QgsProject.instance().addMapLayer(raster_layer)

        # TODO use stored static style instead of dynamic one??
        #  map_style = resources_path(
        #     'styles',
        #     'qgis',
        #     'map.qml')
        # raster_layer.loadNamedStyle(map_style)
        #
        # raster_layer.triggerRepaint()

    except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        if parent_dialog:
            message = 'Error loading isochrone map,'\
                      'please check if you have processing '\
                      'plugin installed \n'.\
                      format(str(exception))
            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    'Error'),
                parent_dialog.tr(message))
        else:
            display_warning_message_box(
                parent_dialog,
                'Error',
                'Error loading isochrone map,'
                'please check if you have processing '
                'plugin installed ')

        raise IsochroneMapStyleError

    return raster_layer


def style_raster_layer(raster_layer, parent_dialog):
    """Style interpolated raster layer

        :param raster_layer: Interpolated raster layer
        :type raster_layer: QgsRasterLayer

        :param parent_dialog: A dialog for showing progress.
        :type parent_dialog: QProgressDialog

        :returns raster_layer: Styled interpolated raster layer
        :rtype raster_layer: QgsRasterLayer

    """
    if raster_layer:
        if raster_layer.isValid():
            color_shader = QgsColorRampShader()
            color_shader.setColorRampType(QgsColorRampShader.Interpolated)
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
                        'Error'),
                    parent_dialog.tr('Error loading isochrone map'
                                     ' Problem indexing the isochrones map'))

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
            raster_layer.triggerRepaint()

        else:
            if parent_dialog:
                display_warning_message_box(
                    parent_dialog,
                    parent_dialog.tr(
                        'Problem'),
                    parent_dialog.tr('Problem styling the isochrone map'))
            else:
                display_warning_message_box(
                    parent_dialog,
                    'Problem',
                    'Problem styling the isochrone map')

    else:
        if parent_dialog:

            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    'Error'),
                parent_dialog.tr('Error loading isochrone map '
                                 'Could not load interpolated file!'))
        else:
            display_warning_message_box(
                parent_dialog,
                'Error',
                'Error loading isochrone map '
                'Could not load interpolated file!')

    return raster_layer


def generate_drivetimes_contour(raster_layer, interval, parent_dialog):
    """Creates drivetimes contour

    :param raster_layer: Interpolated raster layer with drivetimes
    :type raster_layer: QgsRasterLayer

    :param interval: drivetimes interval
    :type interval: int

    :param parent_dialog: A dialog that called this function.
    :type parent_dialog: QProgressDialog

    :returns layer: Vector layer with contour drivetimes
    :rtype layer: QgsVectorLayer

    """
    drivetime_layer = None

    try:
        Processing.initialize()

        temp_output_file = tempfile.NamedTemporaryFile()
        temp_output_file_path = temp_output_file.name + '.shp'

        params = {
                'INPUT': raster_layer,
                'INTERVAL': interval,
                'FIELD_NAME': 'minutes',
                'CREATE_3D': False,
                'IGNORE_NODATA': False,
                'NODATA': 0,
                'BAND': 1,
                'OUTPUT': temp_output_file_path
        }

        output_vector = processing.run(
            'gdal:contour', params
        )

        drivetime_layer = QgsVectorLayer(
                output_vector['OUTPUT'],
                'time(min)',
                'ogr')

    except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        if parent_dialog:
            message = 'Error loading isochrone map,' \
                      'please check if you have processing ' \
                      'plugin installed \n'. \
                      format(str(exception))
            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    'Error'),
                parent_dialog.tr(message))
        else:
            message = 'Error loading isochrone map,'\
                      'please check if you have processing '\
                        'plugin installed \n'.\
                        format(str(exception))

            display_warning_message_box(
                parent_dialog,
                'Error',
                message)

        raise IsochroneMapStyleError

    return drivetime_layer


def load_map_layers(uri, parent_dialog, drivetime_layer, args):
    """Style map layers and load them in Qgis

    :param uri: Connection to the database
    :type uri: QgsDataSourceUri

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

    if drivetime_layer and drivetime_layer.isValid():
        QgsProject.instance().addMapLayers(
            [drivetime_layer])
    else:
        if parent_dialog:
            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    "Error"),
                parent_dialog.tr('Error loading isochrone map '
                                 'Could not load drivetimes file!'))
        else:
            display_warning_message_box(
                parent_dialog,
                'Error',
                'Error loading isochrone map '
                'Could not load drivetimes file!')

    if network_layer and network_layer.isValid():
        QgsProject.instance().addMapLayers(
            [network_layer])
    else:
        if parent_dialog:
            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    "Error"),
                parent_dialog.tr('Error loading isochrone map '
                                 'Could not load network file!'))
        else:
            display_warning_message_box(
                parent_dialog,
                'Error',
                'Error loading isochrone map '
                'Could not load network file!')

    if catchment_layer and catchment_layer.isValid():
        QgsProject.instance().addMapLayers(
            [catchment_layer])
    else:
        if parent_dialog:
            display_warning_message_box(
                parent_dialog,
                parent_dialog.tr(
                    "Error"),
                parent_dialog.tr('Error loading isochrone map '
                                 'Could not load catchment file!'))
        else:
            display_warning_message_box(
                parent_dialog,
                'Error',
                'Error loading isochrone map '
                'Could not load catchment file!')


def create_memory_layer(layer, layer_type, layer_name):
    """Create a copy of given layer in memory

       :param layer: Passed qgis layer
       :type layer: QgsMapLayer

       :param layer_type: Layer type
       :type layer: string

       :param layer_name: Layer name
       :type layer: string

       :return memory_layer: Copy of layer
       :rtype memory_layer: QgsMapLayer
       """
    memory_layer = None

    if isinstance(layer, QgsVectorLayer):
        features = [feature for feature in layer.getFeatures()]

        memory_layer = QgsVectorLayer(layer_type, layer_name, "memory")

        memory_layer_data = memory_layer.dataProvider()
        attr = layer.dataProvider().fields().toList()
        memory_layer_data.addAttributes(attr)
        memory_layer.updateFields()
        memory_layer_data.addFeatures(features)

    return memory_layer


def save_layer(layer):
    """Save given layer to file system

       :param layer: Passed qgis layer
       :type layer: QgsMapLayer

       :return saved_layer: Saved layer
       :rtype saved_layer: QgsMapLayer
       """

    # TODO use the temporary file method and check for layer type first
    # vector_path = get_temp_path("")

    temp_output_file = tempfile.NamedTemporaryFile()
    temp_output_file_path = temp_output_file.name + '.shp'

    error = QgsVectorFileWriter.writeAsVectorFormat(layer,
                                                    temp_output_file_path,
                                                    "utf-8", layer.crs(),
                                                    "ESRI Shapefile")

    saved_layer = QgsVectorLayer(temp_output_file_path, 'isochrones', 'ogr')

    return saved_layer


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
