# -*- coding: utf-8 -*-
"""
/***************************************************************************
 isochrones
                                 A QGIS plugin
 This plugin create isochrones maps.
                             -------------------
        begin                : 2016-07-02
        copyright            : (C) 2016 by Samweli Mwakisambwe
        email                : smwakisambwe@worldbank.org
        git sha              : $Format:%H$
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import
import os
import sys

sys.path.append(os.path.dirname(__file__))

sys.path.extend([os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir))])


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load isochrones class from file isochrones.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .main import QgisIsochrones
    return QgisIsochrones(iface)
