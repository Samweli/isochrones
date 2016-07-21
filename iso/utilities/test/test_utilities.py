# coding=utf-8
"""Tests for utilities."""

import unittest

from iso.utilities.isochrone_utilities import isochrone
from iso.utilities.qgis_utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class UtilitiesTest(unittest.TestCase):
    """Tests for writing and reading isochrone map
    """
    def test_isochrone_utilities(self):
        """ Tests for the main isochrone utility"""
        QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

        database_name = 'roads'
        host_name = 'localhost'
        port_number = '5432'
        user_name = 'test'
        password = 'test'
        network_table = 'public.dar'
        network_geom = 'geom'
        catchment_table = 'public.facilities'
        catchment_geom = ''
        style_checked = False
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
                catchment_table,
                catchment_geom,
                style_checked,
                parent_dialog,
                progress_dialog)

        self.assertNotEqual(output_base_file_path, '')








