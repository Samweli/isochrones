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
        email                : smwltwesa6@gmail.com
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

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4 import QtCore, uic


def get_ui_class(ui_file):
    """Get UI Python class from .ui file.

    :param ui_file: The file of the ui in safe.gui.ui
    :type ui_file: str
    """
    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'gui',
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]