# coding=utf-8
"""Tests for utilities."""

import unittest
import os

from test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from iso.utilities.isochrone_utilities import\
    isochrone, \
    idw_interpolation

from qgis.core import *


class UtilitiesTest(unittest.TestCase):
    """Tests for writing and reading isochrone map
    """

    def test_idw_interpolation(self):
        testdir = os.path.abspath(os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            '..',
            '..'))

        testdata = os.path.join(testdir, 'test','data')
        catchment_path = os.path.join(testdata, 'catchment')

        layer_path = os.path.join(catchment_path, 'isochrones.shp')
        vector_layer = QgsVectorLayer(layer_path, 'isochrones', 'ogr')

        raster_file = idw_interpolation(vector_layer, None)

        self.assertEquals(
            raster_file.dataProvider().dataSourceUri(),
            '[temporary file]')

    def test_isochrone_utilities(self):
        """ Tests for the main isochrone utility"""

        database_name = 'roads'
        host_name = 'localhost'
        port_number = '5432'
        user_name = 'test'
        password = 'test'
        network_table = 'public.network'
        network_id = 'id'
        network_geom = 'geom'
        catchment_table = 'public.catchment'
        catchment_id = 'id'
        catchment_geom = 'geom'
        style_checked = False
        contour_interval = 2
        parent_dialog = None
        progress_dialog = None

        output_base_file_path = isochrone(
                database_name,
                host_name,
                port_number,
                user_name,
                password,
                network_table,
                network_geom,
                network_id,
                catchment_table,
                catchment_geom,
                catchment_id,
                style_checked,
                contour_interval,
                parent_dialog,
                progress_dialog)

        self.assertEqual(output_base_file_path, "dbname='roads' host=localhost"
                                                " port=5432 user='test' "
                                                "password='test' key='tid' "
                                                "table=\"public\".\""
                                                "catchment_final_no_null\""
                                                " (the_geom) sql=")

if __name__ == '__main__':
    unittest.main()
