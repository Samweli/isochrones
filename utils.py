#
# Utility functions that are specific to the plugin logic.
import os

from qgis.core import Qgis, QgsMessageLog
import qgis  # pylint: disable=unused-import
from qgis.PyQt import QtCore, uic

from builtins import str
from qgis.PyQt.QtCore import QCoreApplication

from qgis.PyQt.QtWidgets import QMessageBox

import sys

QGIS_APP = None
CANVAS = None
PARENT = None
IFACE = None


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
    if not isinstance(text_object, str):
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
    if isinstance(input_text, str):
        return input_text
    return str(input_text, encoding, errors='ignore')

def get_ui_class(ui_file):
    """Get UI Python class from .ui file.

    :param ui_file: The file of the ui in isochrones.gui.ui
    :type ui_file: str
    """
    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]


def log(
        message: str,
        name: str = "qgis_isochrones",
        info: bool = True,
        notify: bool = True,
):
    """ Logs the message into QGIS logs using qgis_stac as the default
    log instance.
    If notify_user is True, user will be notified about the log.
    :param message: The log message
    :type message: str
    :param name: Name of te log instance, qgis_stac is the default
    :type message: str
    :param info: Whether the message is about info or a
    warning
    :type info: bool
    :param notify: Whether to notify user about the log
    :type notify: bool
     """
    level = Qgis.Info if info else Qgis.Warning
    QgsMessageLog.logMessage(
        message,
        name,
        level=level,
        notifyUser=notify,
    )

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


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFload_standard_layersACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas  # pylint: disable=no-name-in-module
        # noinspection PyPackageRequirements
        from qgis.PyQt import QtGui, QtCore  # pylint: disable=W0621
        # noinspection PyPackageRequirements
        from qgis.PyQt.QtCore import QCoreApplication, QSettings
        from qgis.gui import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode

        # AG: For testing purposes, we use our own configuration file instead
        # of using the QGIS apps conf of the host
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationName('QGIS')
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setOrganizationDomain('qgis.org')
        # noinspection PyCallByClass,PyArgumentList
        QCoreApplication.setApplicationName('IsochronesTesting')

        # noinspection PyPep8Naming
        QGIS_APP = QgsApplication(sys.argv, gui_flag)

        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()

        # Save some settings
        settings = QSettings()
        settings.setValue('locale/overrideFlag', True)
        settings.setValue('locale/userLocale', 'en_US')
        # We disabled message bars for now for extent selector as
        # we don't have a main window to show them in TS - version 3.2

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        # noinspection PyPep8Naming
        PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT
