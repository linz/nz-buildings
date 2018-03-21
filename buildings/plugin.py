# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QListWidgetItem, QIcon

import qgis

from buildings.gui.menu_frame import MenuFrame
from buildings.gui.error_dialog import ErrorDialog

from utilities.layers import LayerRegistry

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
        self.menu_frame = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        """
        return QCoreApplication.translate("Buildings", message)

    def initGui(self):
        """Inserts buildings plugin into the roads plugin"""
        # Should add to roads plugin list options here
        try:
            dw = qgis.utils.plugins['roads'].dockwidget
            exists = False
            if dw is not None:
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        exists = True
                if exists is False:
                    home_dir = os.path.split(os.path.dirname(__file__))
                    icon_path = os.path.join(home_dir[0], home_dir[1], "icons", "roads_plugin.png")
                    dw = qgis.utils.plugins['roads'].dockwidget
                    item = QListWidgetItem("Buildings")
                    item.setIcon(QIcon(icon_path))
                    dw.lst_options.addItem(item)
                    self.run()

            else:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(" ")
                self.error_dialog.fill_report(" \n -------------------------------FAILED IMPORT------------------------------ \n \n Try opening the roads plugin GUI and then installing the buildings plugin.")
                self.error_dialog.show()
        except KeyError:
            pass

    def unload(self):
        """Removes the plugin from Roads."""
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
            pass

    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.menu_frame:
            dw = qgis.utils.plugins['roads'].dockwidget
            self.layer_registry = LayerRegistry()
            # no base layers 
            # self.layer_registry.set_up_base_layers()
            self.menu_frame = MenuFrame(self.layer_registry)
            dw.insert_into_frames('menu_frame', self.menu_frame)

    def on_click(self):
        dw = qgis.utils.plugins['roads'].dockwidget
        if dw.stk_options.count() == 5:  # 4th widget is not empty
            dw.stk_options.setCurrentIndex(4)  # set to fourth
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())  # delete fourth
        dw.stk_options.setCurrentIndex(3)
        dw.stk_options.addWidget(MenuFrame(self.layer_registry))
        dw.stk_options.setCurrentIndex(4)
