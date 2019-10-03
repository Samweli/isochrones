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


class IsochroneError(RuntimeError):
    """Base class for all user defined exceptions"""
    suggestion = 'An unspecified error occurred.'


class IsochroneDBError(RuntimeError):
    """Base class for all user defined exceptions"""
    suggestion = 'Check that the input tables and their attributes are right.'


class ReadLayerError(IsochroneError):
    """When a layer can't be read"""
    suggestion = (
        'Check that the file exists and you have permissions to read it')


class WriteLayerError(IsochroneError):
    """When a layer can't be written"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class BoundingBoxError(IsochroneError):
    """For errors relating to bboxes"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class VerificationError(IsochroneError):
    """Exception thrown by verify()
    """
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class PolygonInputError(IsochroneError):
    """For invalid inputs to numeric polygon functions"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class PointsInputError(IsochroneError):
    """For invalid inputs to numeric point functions"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class BoundsError(IsochroneError):
    """For points falling outside interpolation grid"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class GetDataError(IsochroneError):
    """When layer data cannot be obtained"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class PostProcessorError(IsochroneError):
    """Raised when requested import cannot be performed if QGIS is too old."""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class WindowsError(IsochroneError):
    """For windows specific errors."""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class GridXmlFileNotFoundError(IsochroneError):
    """An exception for when an grid.xml could not be found"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class GridXmlParseError(IsochroneError):
    """An exception for when something went wrong parsing the grid.xml """
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class ContourCreationError(IsochroneError):
    """An exception for when creating contours from shakemaps goes wrong"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class InvalidLayerError(IsochroneError):
    """Raised when a gis layer is invalid"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class ShapefileCreationError(IsochroneError):
    """Raised if an error occurs creating the cities file"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class ZeroImpactException(IsochroneError):
    """Raised if an impact function return zero impact"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class WrongDataTypeException(IsochroneError):
    """Raised if expected and received data types are different"""
    suggestion = 'Please ask the developers of Isochrones to add a suggestion.'


class InvalidClipGeometryError(IsochroneError):
    """Custom exception for when clip geometry is invalid."""
    pass


class FileNotFoundError(IsochroneError):
    """Custom exception for when a file could not be found."""
    pass


class TestNotImplementedError(IsochroneError):
    """Custom exception for when a test exists only as a stub."""
    pass


class NoFunctionsFoundError(IsochroneError):
    """Custom exception for when a no impact calculation
    functions can be found."""
    pass


class KeywordDbError(IsochroneError):
    """Custom exception for when an error is encountered with keyword cache db.
    """
    pass


class HashNotFoundError(IsochroneError):
    """Custom exception for when a no keyword hash can be found."""
    pass


class StyleInfoNotFoundError(IsochroneError):
    """Custom exception for when a no styleInfo can be found."""
    pass


class InvalidParameterError(IsochroneError):
    """Custom exception for when an invalid parameter is passed to a function.
    """
    pass


class TranslationLoadError(IsochroneError):
    """Custom exception handler for whe translation file fails
    to load."""
    pass


class LegendLayerError(IsochroneError):
    """An exception raised when trying to create a legend from
    a QgsMapLayer that does not have suitable characteristics to
    allow a legend to be created from it."""
    pass


class NoFeaturesInExtentError(IsochroneError):
    """An exception that gets thrown when no features are within
    the extent being clipped."""
    pass


class InvalidProjectionError(IsochroneError):
    """An exception raised if a layer needs to be reprojected."""
    pass


class InsufficientOverlapError(IsochroneError):
    """An exception raised if an error occurs during extent calculation
    because the bounding boxes do not overlap."""
    pass


class StyleError(IsochroneError):
    """An exception relating to reading / generating GIS styles"""
    pass


class MemoryLayerCreationError(IsochroneError):
    """Raised if an error occurs creating the cities file"""
    pass


class MethodUnavailableError(IsochroneError):
    """Raised if the requested import cannot be performed dur to qgis being
    to old"""
    pass


class CallGDALError(IsochroneError):
    """Raised if failed to call gdal command. Indicate by error message that is
    not empty"""
    pass


class ImportDialogError(IsochroneError):
    """Raised if import process failed."""
    pass


class FileMissingError(IsochroneError):
    """Raised if a file cannot be found."""
    pass


class CanceledImportDialogError(IsochroneError):
    """Raised if import process canceled"""
    pass


class HelpFileMissingError(IsochroneError):
    """Raised if a help file cannot be found."""
    pass


class InvalidGeometryError(IsochroneError):
    """Custom exception for when a feature geometry is invalid or none."""
    pass


class UnsupportedProviderError(IsochroneError):
    """For unsupported provider (e.g. openlayers plugin) encountered."""
    pass


class ReportCreationError(IsochroneError):
    """Raised when error occurs during report generation."""
    pass


class EmptyDirectoryError(IsochroneError):
    """Raised when output directory is empty string path."""
    pass


class NoValidLayerError(IsochroneError):
    """Raised when there no valid layer in Isochrone."""
    pass


class InsufficientMemoryWarning(IsochroneError):
    """Raised when there is a possible insufficient memory."""
    pass


class InvalidExtentError(IsochroneError):
    """Raised if an extent is not valid."""
    pass


class NoAttributeInLayerError(IsochroneError):
    """Raised if the attribute not exists in the vector layer"""
    pass
