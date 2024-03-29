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

from qgis.core import Qgis

# noinspection PyPackageRequirements
from qgis.PyQt import QtWidgets
# noinspection PyPackageRequirements
from qgis.PyQt.QtCore import QSettings, QFileInfo
# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUiType

from common.exceptions import (
    ImportDialogError,
    FileMissingError)

from iso.utils import display_warning_message_box
from iso.base import isochrone

FORM_CLASS, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), '../ui/isochrone_dialog_base.ui')
)


class QgisIsochronesDialog(QtWidgets.QDialog, FORM_CLASS):

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

        self.restore_state()

        self.canvas = iface.mapCanvas() if iface else None

    def accept(self):
        """Create an isochrone map and display it in QGIS."""

        try:
            self.save_state()
            self.require_input()

            database_name = self.database.text()
            host_name = self.host.text()
            port_number = self.port.text()
            user_name = self.user_name.text()
            password = self.password.text()
            network_table = self.network_table.text()
            network_geom = self.network_geom_column.text()
            network_id_column = self.network_id_column.text()
            catchment_geom = self.catchment_geom_column.text()
            catchment_table = self.catchment_table.text()
            catchment_id_column = self.catchment_id_column.text()
            contour_interval = self.contour_interval.text()

            if self.style.isChecked():
                style_checked = True
            else:
                style_checked = False

            isochrone(
                database_name,
                host_name,
                port_number,
                user_name,
                password,
                network_table,
                network_geom,
                network_id_column,
                catchment_table,
                catchment_geom,
                catchment_id_column,
                style_checked,
                contour_interval,
                self,
                None)

            self.done(QDialog.Accepted)

        except ImportDialogError as exception:
            error_dialog_title = self.tr("Error")

            display_warning_message_box(
                self, error_dialog_title, str(exception))
            pass
        except Exception as exception:  # pylint: disable=broad-except
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            error_dialog_title = self.tr("Error")
            display_warning_message_box(
                self, error_dialog_title, str(exception))
            pass
        finally:
            dialog_title = self.tr("Success")

    def require_input(self):
        """Ensure input files are entered in dialog exist.

        :raises: ImportDialogError - when one or all
        of the input files are empty
        """
        database_name = self.database.text()
        host_name = self.host.text()
        port_number = self.port.text()
        user_name = self.user_name.text()
        password = self.password.text()
        network_table = self.network_table.text()
        catchment_table = self.catchment_table.text()
        contour_interval = self.contour_interval.text()

        if database_name and host_name and port_number and \
                user_name and password and network_table and \
                catchment_table:
            return

        display_warning_message_box(
                    self,
                    self.tr('Error'),
                    self.tr('Input cannot be empty.'))

        raise ImportDialogError()

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        settings = QSettings()
        try:
            database_name = settings.value('database', type=str)
            host_name = settings.value('host', type=str)
            port_number = settings.value('port', type=str)
            user_name = settings.value('user_name', type=str)
            network_table = settings.value('network_table', type=str)
            network_geom_column = settings.value(
                'network_geom_column',
                type=str)
            network_id_column = settings.value('network_id_column', type=str)
            catchment_table = settings.value('catchment_table', type=str)
            catchment_geom_column = settings.value(
                'catchment_geom_column',
                type=str)
            catchment_id_column = settings.value(
                'catchment_id_column',
                type=str)
            contour_interval = settings.value(
                'contour_interval',
                type=str)

        except TypeError:
            database_name = ''
            host_name = ''
            port_number = ''
            user_name = ''
            network_table = ''
            network_geom_column = ''
            network_id_column = ''
            catchment_table = ''
            catchment_geom_column = ''
            catchment_id_column = ''
            contour_interval = ''

        self.database.setText(database_name)
        self.host.setText(host_name)
        self.port.setText(port_number)
        self.user_name.setText(user_name)
        self.network_table.setText(network_table)
        self.network_geom_column.setText(network_geom_column)
        self.network_id_column.setText(network_id_column)
        self.catchment_table.setText(catchment_table)
        self.catchment_geom_column.setText(catchment_geom_column)
        self.catchment_id_column.setText(catchment_id_column)
        self.contour_interval.setText(contour_interval)

    def save_state(self):
        """ Store current state of GUI to configuration file """
        settings = QSettings()

        settings.setValue('database', self.database.text())
        settings.setValue('host', self.host.text())
        settings.setValue('port', self.port.text())
        settings.setValue('user_name', self.user_name.text())
        settings.setValue('network_table', self.network_table.text())
        settings.setValue(
            'network_geom_column',
            self.network_geom_column.text())
        settings.setValue(
            'network_id_column',
            self.network_id_column.text())
        settings.setValue('catchment_table', self.catchment_table.text())
        settings.setValue(
            'catchment_geom_column',
            self.catchment_geom_column.text())
        settings.setValue(
            'catchment_id_column',
            self.catchment_id_column.text())
        settings.setValue(
            'contour_interval',
            self.contour_interval.text())

    def reject(self):
        """Redefinition of the reject() method
        """
        super(QgisIsochronesDialog, self).reject()

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

                if layer.endswith(".asc"):
                    self.iface.addRasterLayer(layer, layer_name)
                    continue
                elif layer.endswith(".shp"):
                    self.iface.addVectorLayer(layer, layer_name, 'ogr')
                    continue
                else:
                    continue
        canvas_srid = self.canvas.mapRenderer().destinationCrs().srsid()
        on_the_fly_projection = self.canvas.hasCrsTransformEnabled()
        if canvas_srid != 4326 and not on_the_fly_projection:
            if Qgis.QGIS_VERSION_INT >= 20400:
                self.canvas.setCrsTransformEnabled(True)
            else:
                display_warning_message_box(
                    self.iface,
                    self.tr('Enable \'on the fly\''),
                    self.tr(
                        'Your current projection is different than EPSG:4326.'
                        'You should enable \'on the fly\' to display '
                        'correctly the isochrone map')
                    )
