# -*- coding: utf-8 -*-
"""
/***************************************************************************
 isochrone i18n
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


from PyQt4.QtCore import QCoreApplication


def tr(text):
    """
    :param text: String to be translated
    :type text: str, unicode

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str, unicode
    """
    # Ensure it's in unicode
    text = get_unicode(text)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)


def __if_not_basestring(text_object):
    converted_str = text_object
    if not isinstance(text_object, basestring):
        converted_str = str(text_object)
    return converted_str


def get_unicode(input_text, encoding='utf-8'):
    """Get the unicode representation of an object.

    :param input_text: The input text.
    :type input_text: unicode, str, float, int

    :param encoding: The encoding used to do the conversion, default to utf-8.
    :type encoding: str

    :returns: Unicode representation of the input.
    :rtype: unicode
    """
    input_text = __if_not_basestring(input_text)
    if isinstance(input_text, unicode):
        return input_text
    return unicode(input_text, encoding, errors='ignore')
