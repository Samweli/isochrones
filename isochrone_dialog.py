# -*- coding: utf-8 -*-
"""
/***************************************************************************
 isochronesDialog
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

from PyQt4 import QtGui, uic

# noinspection PyPackageRequirements
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QRegExp, pyqtSlot
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog, QProgressDialog, QMessageBox, QFileDialog, QRegExpValidator)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'isochrone_dialog_base.ui'))


class isochronesDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(isochronesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_network_button_clicked(self):
        """Show a dialog to choose directory."""
        # noinspection PyCallByClass,PyTypeChecker
        self.input_network_file.setText(QFileDialog.getOpenFileName(
            self, self.tr('Select network file')))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_catchment_button_clicked(self):
        """Show a dialog to choose directory."""
        # noinspection PyCallByClass,PyTypeChecker
        self.input_catchment_file.setText(QFileDialog.getOpenFileName(
            self, self.tr('Select catchment file')))
