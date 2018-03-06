# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import QCoreApplication

# Get the path for the parent directory of this file.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Buildings:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.plugin_dir = __location__
        self.image_dir = os.path.join(__location__, "..", "images")

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        """
        return QCoreApplication.translate("Buildings", message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Should add to roads plugin list options here
        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Should remove from roads plugin list options here
        pass
