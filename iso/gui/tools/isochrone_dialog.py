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

from PyQt4 import uic

from qgis.core import QGis

# noinspection PyPackageRequirements
from PyQt4 import QtGui
# noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QFileInfo
# noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog, QFileDialog, QProgressDialog)
from iso.common.exceptions import (
    ImportDialogError,
    FileMissingError)

from iso.utilities.qgis_utilities import (
    display_warning_message_box)
from iso.utilities.resources import (
    get_ui_class)
from iso.utilities.isochrone_utilities import isochrone

FORM_CLASS = get_ui_class('isochrone_dialog_base.ui')


class isochronesDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, parent=None, iface=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.parent = parent
        self.iface = iface

        self.setupUi(self)

        # Setting up progress window

        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setAutoClose(False)
        title = self.tr('Isochrone')
        self.progress_dialog.setWindowTitle(title)

        self.canvas = iface.mapCanvas()

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

    def accept(self):
        """Create an isochrone map and display it in QGIS."""
        error_dialog_title = self.tr("Error")
        try:
            self.save_state()
            self.require_input_files()

            input_network_file = self.input_network_file.text()
            input_catchment_file = self.input_catchment_file.text()

            output_base_file_path = isochrone(
                input_network_file,
                input_catchment_file,
                self.progress_dialog)
            try:
                self.load_isochrone_map(output_base_file_path)

            except FileMissingError as exception:
                    display_warning_message_box(
                        self,
                        error_dialog_title,
                        exception.message)

            self.done(QDialog.Accepted)

        except ImportDialogError as exception:
            display_warning_message_box(
                self, error_dialog_title, exception.message)
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            display_warning_message_box(
                self, error_dialog_title, exception.message)

            self.progress_dialog.cancel()

        finally:
            dialog_title = self.tr("Success")

    def require_input_files(self):
        """Ensure input files are entered in dialog exist.

        :raises: ImportDialogError - when one or all
        of the input files are empty
        """
        network_path = self.input_network_file.text()
        catchment_path = self.input_catchment_file.text()

        if os.path.exists(network_path) and os.path.exists(catchment_path):
            return

        display_warning_message_box(
                    self,
                    self.tr('Error'),
                    self.tr('Input files can not be empty.'))

        raise ImportDialogError()

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        settings = QSettings()
        try:
            network_last_path = settings.value('network_file', type=str)
            catchment_last_path = settings.value('catchment_file', type=str)
        except TypeError:
            network_last_path = ''
            catchment_last_path = ''
        self.input_network_file.setText(network_last_path)
        self.input_catchment_file.setText(catchment_last_path)

    def save_state(self):
        """ Store current state of GUI to configuration file """
        settings = QSettings()
        settings.setValue('network_file', self.input_network_file.text())
        settings.setValue('catchment_file', self.input_catchment_file.text())

    def reject(self):
        """Redefinition of the reject() method
        """
        super(isochronesDialog, self).reject()

    def load_isochrone_map(self, base_path):
        """Load the isochrone map in the qgis

        :param base_path: Output path where layers are
        :type base_path:str
        """

        if not os.path.exists(base_path):
            message = self.tr("Error, failed to load the isochrone map")
            raise FileMissingError(message)
        else:
            for layer in os.listdir(base_path):
                layer_name = QFileInfo(layer).baseName

                if file.endswith(".asc"):
                    self.iface.addRasterLayer(file, layer_name)
                    continue
                elif file.endswith(".shp"):
                    self.iface.addVectorLayer(file, layer_name, 'ogr')
                    continue
                else:
                    continue
        canvas_srid = self.canvas.mapRenderer().destinationCrs().srsid()
        on_the_fly_projection = self.canvas.hasCrsTransformEnabled()
        if canvas_srid != 4326 and not on_the_fly_projection:
            if QGis.QGIS_VERSION_INT >= 20400:
                self.canvas.setCrsTransformEnabled(True)
            else:
                display_warning_message_box(
                    self.iface,
                    self.tr('Enable \'on the fly\''),
                    self.tr(
                        'Your current projection is different than EPSG:4326. '
                        'You should enable \'on the fly\' to display '
                        'correctly the isochrone map')
                    )



