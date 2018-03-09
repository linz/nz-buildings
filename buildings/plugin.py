# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QListWidgetItem, QIcon
import qgis

from buildings.gui.menu_frame import MenuFrame
from buildings.gui.error_dialog import ErrorDialog

# Get the path for the parent directory of this file.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Buildings:
    """QGIS Plugin Implementation."""
    stop = False

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
        try:
            dw = qgis.utils.plugins['roads'].dockwidget
            exists = False
            if dw is not None:
                dw.insert_into_frames('menu_frame', MenuFrame)
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        exists = True
                if exists is False:
                    home_dir = os.path.split(os.path.dirname(__file__))
                    item = QListWidgetItem("Buildings")
                    image_path = os.path.join(home_dir[0], home_dir[1], "icons", "roads_plugin.png")
                    item.setIcon(QIcon(image_path))
                    dw.lst_options.addItem(item)
            else:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(" ")
                self.error_dialog.fill_report(" \n FAILED IMPORT \n \n Try opening the roads plugin GUI and then installing the buildings plugin.")
                self.error_dialog.show()
        except KeyError:
            print 'roads plugin not loaded'
            pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Should remove from roads plugin list options here
        try:
            dw = qgis.utils.plugins['roads'].dockwidget
            if dw is not None:
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        dw.lst_options.takeItem(row)
                dw.frames = {}
                if dw.stk_options.count() == 5:
                    dw.stk_options.setCurrentIndex(4)
                    dw.stk_options.removeWidget(dw.stk_options.currentWidget())
                    dw.stk_options.setCurrentIndex(1)

        except KeyError:
            print 'roads plugin not loaded'
            pass

    def on_click(self):
        dw = qgis.utils.plugins['roads'].dockwidget
        if dw.stk_options.count() == 5:  # 4th widget is not empty
            dw.stk_options.setCurrentIndex(4)  # set to fourth
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())  # delete fourth
        dw.stk_options.setCurrentIndex(3)
        dw.stk_options.addWidget(MenuFrame(dw))
        dw.stk_options.setCurrentIndex(4)
