# -*- coding: utf-8 -*-

from PyQt4.QtCore import QSettings
from qgis.core import QgsCoordinateReferenceSystem
from qgis.utils import iface

QGIS_SETTINGS = QSettings()

LOCALE = QGIS_SETTINGS.value('locale/userLocale')[0:2]

SRID = 2193


def get_attribute_dialog_setting():
    """
    Used to retrieve the user configuration of the attribute dialog so that
    this configuration can be reinstated when the roads plugin is closed.
    """

    return QGIS_SETTINGS.value(
        '/qgis/digitizing/disable_enter_attribute_values_dialog')


def set_attribute_dialog_setting(attribute_dialog_setting):
    """
    Set to True during use of the roads plugin to prevent attribute values
    dialog from appearing - unnecessary during the use of this plugin. Set
    back to whatever the user configuration was when the plugin is closed.
    """

    QGIS_SETTINGS.setValue(
        '/qgis/digitizing/disable_enter_attribute_values_dialog',
        attribute_dialog_setting
    )


def set_crs():
    """Ensures that CRS settings are correct for use of the roads plugin"""

    # Sets it away from prompting user
    QGIS_SETTINGS.setValue("/Projections/defaultBehaviour", "useProject")

    # Enable on the fly reprojections
    iface.mapCanvas().setCrsTransformEnabled(True)

    # Set project coordinate reference system to NZGD2000
    iface.mapCanvas().setDestinationCrs(
        QgsCoordinateReferenceSystem(
            SRID,
            QgsCoordinateReferenceSystem.PostgisCrsId
        )
    )
    iface.mapCanvas().setMapUnits(2)
