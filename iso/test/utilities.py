# coding=utf-8
"""Common functionality used by regression tests."""

import sys
import logging

from qgis.utils import iface


LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """
    global QGIS_APP, PARENT, IFACE, CANVAS  # pylint: disable=W0603

    if iface:
        from qgis.core import QgsApplication
        QGIS_APP = QgsApplication
        CANVAS = iface.mapCanvas()
        PARENT = iface.mainWindow()
        IFACE = iface
        return QGIS_APP, CANVAS, IFACE, PARENT

    try:
        from qgis.PyQt import QtGui, QtCore, QtWidgets
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas

    except ImportError:
        return None, None, None, None

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        # noinspection PyPep8Naming
        QgsApplication.setPrefixPath('/usr', True)

        QGIS_APP = QgsApplication([], gui_flag)

        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()

        LOGGER.debug(s)

    if PARENT is None:
        # noinspection PyPep8Naming
        PARENT = QtWidgets.QWidget

    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas()
        CANVAS.resize(QtCore.QSize(400, 400))
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        # IFACE = QgisInterface(CANVAS)
        IFACE = None

    return QGIS_APP, CANVAS, IFACE, PARENT
