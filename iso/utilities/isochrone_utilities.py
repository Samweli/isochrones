# -*- coding: utf-8 -*-
"""
/***************************************************************************
 isochrone utilities
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


def isochrone(
            self,
            input_network_file,
            input_catchment_file,
            progress_dialog=None):

        """Contains main logic on creating isochrone map
        :param input_network_file: Input network file
        :type input_network_file: str

        :param input_catchment_file: Input Catchment file.
        :type input_catchment_file: str

        :param progress_dialog: A progess dialog .
        :type progress_dialog: QProgressDialog

        :returns temp_output_directory: temporary path of the map
        :rtype temp_output_directory:str
        """
        if progress_dialog:
            progress_dialog.show()

        # Import files into database, have tables

        # Create nodes from network

        # Create routable network

        # Find nearest nodes from the catchments

        # Calculate drivetime for the nearest nodes

        # Export table as shapefile

        # Run interpolation on the final file (currently use IDW)

        # Calculate contours

        # Style the tin , contour and network

        # Load tin, contour and network as one qgis doc

        temp_output_directory = ''

        if progress_dialog:
            progress_dialog.done(QDialog.Accepted)

        return temp_output_directory