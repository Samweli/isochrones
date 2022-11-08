# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import

__author__ = 'smwakisambwe@worldbank.org'
__date__ = '2016-07-02'
__copyright__ = 'Copyright 2016, Samweli Mwakisambwe'

import unittest

from isochrones.gui.qgis_isochrone_dialog import QgisIsochronesDialog
from isochrones.test.utilities import get_qgis_app
QGIS_APP = get_qgis_app()

from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog


class IsochronesDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = QgisIsochronesDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    # TODO find out why the test below hangs and doesn't exit
    # def test_dialog_ok(self):
    #     """Test we can click OK."""
    #
    #     button = self.dialog.button_box.button(QDialogButtonBox.Ok)
    #     button.click()
    #     result = self.dialog.result()
    #     self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)


if __name__ == "__main__":
    suite = unittest.makeSuite(IsochronesDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
