# coding=utf-8
"""Tests for utilities."""

import unittest
import os

from iso.test.utilities import get_qgis_app

from qgis.core import *

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from iso.utilities.isochrone_utilities import\
    isochrone, \
    idw_interpolation, \
    generate_drivetimes_contour, \
    load_map_layers


class UtilitiesTest(unittest.TestCase):
    """Tests for writing and reading isochrone map
    """

    def test_idw_interpolation(self):
        """ Test layer interpolation. """

        testdir = os.path.abspath(os.path.join(
            os.path.realpath(os.path.dirname(__file__))))

        testdata = os.path.join(testdir, 'data')
        catchment_path = os.path.join(testdata, 'catchment')

        layer_path = os.path.join(catchment_path, 'isochrones.shp')
        vector_layer = QgsVectorLayer(layer_path, 'isochrones', 'ogr')

        file = idw_interpolation(vector_layer, False, None)

        # Assert if file is a raster layer
        self.assertEqual(
            file.type(), QgsMapLayer.RasterLayer)

        self.assertEqual(
            file.isValid(), True)

        self.assertEqual(
            file.bandCount(), 1)

    def test_generate_drivetimes_contour(self):
        """ Test drivetimes generation. """

        testdir = os.path.abspath(os.path.join(
            os.path.realpath(os.path.dirname(__file__))))

        testdata = os.path.join(testdir, 'data')
        catchment_path = os.path.join(testdata, 'catchment')

        layer_path = os.path.join(catchment_path, 'raster_iso.tif')
        raster_layer = QgsRasterLayer(layer_path, 'raster_iso')
        contour_interval = 1
        parent_dialog = None

        vector_layer = generate_drivetimes_contour(
            raster_layer,
            contour_interval,
            parent_dialog)

        # Assert if file is a vector layer
        self.assertEqual(
            vector_layer.type(),
            QgsMapLayer.VectorLayer)
        self.assertEqual(
            vector_layer.isValid(),
            True)
        self.assertNotEqual(
            vector_layer,
            None)

    # def test_load_map_layers(self):
    #     """ Test loading map layers. """
    #
    #     database_name = 'isochrones_test'
    #     host_name = 'localhost'
    #     port_number = '5432'
    #     user_name = 'postgres'
    #     password = ''
    #     network_table = 'public.network'
    #     network_id = 'id'
    #     network_geom = 'geom'
    #     catchment_table = 'public.catchment'
    #     catchment_id = 'id'
    #     catchment_geom = 'geom'
    #     style_checked = False
    #     contour_interval = 2
    #     parent_dialog = None
    #     progress_dialog = None
    #
    #     network_array = network_table.split('.')
    #     network_table = str(network_array[1])
    #     network_schema = network_array[0]
    #     catchment = catchment_table.split('.')
    #     catchment_table = catchment[1]
    #     catchment_schema = catchment[0]
    #
    #     args = {}
    #     args['network_schema'] = network_schema
    #     args['network_table'] = network_table
    #     args['network_geom'] = network_geom
    #     args['catchment_schema'] = catchment_schema
    #     args['catchment_table'] = catchment_table
    #     args['catchment_geom'] = catchment_geom
    #
    #     uri = QgsDataSourceURI()
    #     # set host name, port, database name, username and password
    #     uri.setConnection(
    #         host_name,
    #         port_number,
    #         database_name,
    #         user_name,
    #         password)
    #     # set database schema, table name, geometry column and optionally
    #     # subset (WHERE clause)
    #     uri.setDataSource(
    #         network_schema,
    #         "catchment_final_no_null",
    #         "the_geom")
    #
    #     testdir = os.path.abspath(os.path.join(
    #         os.path.realpath(os.path.dirname(__file__))))
    #
    #     testdata = os.path.join(testdir, 'data')
    #
    #     catchment_path = os.path.join(testdata, 'catchment')
    #
    #     layer_path = os.path.join(
    #       catchment_path,
    #       'drivetime_layer.shp')
    #
    #     drivetime_layer = QgsVectorLayer(
    #       layer_path,
    #       'drivetime_layer',
    #       'ogr')
    #
    #     load_map_layers(uri, parent_dialog , drivetime_layer, args)
    #
    #     self.assertEquals(QgsMapLayerRegistry.instance().count(), 5)

    # def test_isochrone_utilities(self):
    #     """ Tests for the main isochrone utilities"""
    #
    #     database_name = 'isochrones_test'
    #     host_name = 'localhost'
    #     port_number = '5432'
    #     user_name = 'postgres'
    #     password = ''
    #     network_table = 'public.network'
    #     network_id = 'id'
    #     network_geom = 'geom'
    #     catchment_table = 'public.catchment'
    #     catchment_id = 'id'
    #     catchment_geom = 'geom'
    #     style_checked = False
    #     contour_interval = 2
    #     parent_dialog = None
    #     progress_dialog = None
    #
    #     output_base_file_path = isochrone(
    #             database_name,
    #             host_name,
    #             port_number,
    #             user_name,
    #             password,
    #             network_table,
    #             network_geom,
    #             network_id,
    #             catchment_table,
    #             catchment_geom,
    #             catchment_id,
    #             style_checked,
    #             contour_interval,
    #             parent_dialog,
    #             progress_dialog)
    #
    #     self.assertEqual(output_base_file_path, "dbname='isochrones_test'"
    #                                             " host=localhost"
    #                                             " port=5432 user='postgres' "
    #                                             "password='' key='tid' "
    #                                             "table=\"public\".\""
    #                                             "catchment_final_no_null\""
    #                                             " (the_geom) sql=")


if __name__ == '__main__':
    unittest.main()
