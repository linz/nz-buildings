import logging
import logging.handlers
from pathlib import Path

from qgis.core import Qgis, QgsApplication

from buildings.utilities.config import read_config_file
from buildings.utilities.warnings import buildings_warning

MAX_LOGFILE_SIZE = 1024*20  # Maximum file size before a logfile will be rotated, in bytes


class QgsHandler(logging.Handler):
    """Custom logging handler to print logs to QGIS GUI logging panel."""
    def emit(self, record: logging.LogRecord):
        if record.levelname == ("CRITICAL", "ERROR"):
            level = Qgis.Critical
        elif record.levelname == "WARNING":
            level = Qgis.Warning
        else:
            level = Qgis.Info
        QgsApplication.messageLog().logMessage(message=self.format(record), tag="Buildings", level=level)


def get_logfile_path() -> Path:
    """Gets the path of the logfile from the plugin config file."""
    try:
        raw_path = read_config_file()["logging"]["logfile"]
    except ValueError as error:
        buildings_warning("Config file error", str(error), "critical")
        raise error
    logfile = Path(raw_path)
    logfile = logfile.expanduser().resolve()
    return logfile


def configure_logger():
    """Configures logs to go to both the logfile defined in the config, and the QGIS GUI logging panel"""
    logger = logging.getLogger("buildings")
    logger.setLevel(logging.DEBUG)
    qgis_handler = QgsHandler()
    qgis_formatter = logging.Formatter(fmt="[{name}]  {message}", style="{")
    qgis_handler.setFormatter(qgis_formatter)
    logger.addHandler(qgis_handler)
    logfile = get_logfile_path()
    file_handler = logging.handlers.RotatingFileHandler(logfile, encoding="utf8", maxBytes=MAX_LOGFILE_SIZE)
    file_formatter = logging.Formatter(fmt="{asctime}  {levelname}  [{name}]  {message}", datefmt="%Y-%m-%dT%H:%M:%S", style="{")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
