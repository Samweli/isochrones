#
# Utility functions that are specific to the plugin logic.

from qgis.core import Qgis, QgsMessageLog


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