# -*- coding: utf-8 -*-
"""
/***************************************************************************
 exception classes
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

from PyQt4.QtGui import QMessageBox, QPushButton


def display_information_message_box(
        parent=None, title=None, message=None):
    """
    Display an information message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.information(parent, title, message)


def display_warning_message_box(parent=None, title=None, message=None):
    """
    Display a warning message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.warning(parent, title, message)


def display_critical_message_box(parent=None, title=None, message=None):
    """
    Display a critical message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.critical(parent, title, message)

