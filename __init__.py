# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Isochrones
                                 A QGIS plugin
 This plugin creates ischorone map from the given data
                             -------------------
        begin                : 2016-06-05
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Isochrones class from file Isochrones.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .isochrone import Isochrones
    return Isochrones(iface)
