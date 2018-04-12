# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QListWidgetItem, QIcon, QAction, QMenu

import qgis
from qgis.core import QgsProject, QgsCoordinateReferenceSystem
from qgis.utils import iface

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
        self.layer_registry = None

        # declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Building Maintenance')
        self.main_toolbar = iface.addToolBar(u'Building Maintenance')
        self.main_toolbar.setObjectName(u'Building Maintenance')

        # set up the customizable toolbar
        iface.building_toolbar = None
        self.is_active = False
        self.dockwidget = None  # qgis.utils.plugins['roads'].dockwidget

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        """
        return QCoreApplication.translate('BuildingMaintenance', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=True,
            whats_this=None,
            parent=None):
        """ Add a toolbar icon to the toolbar. 

        @param icon_path: Path to the icon for this action. Can be a resource
        path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
                @param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        @type icon_path: str
        @param text: Text that should be shown in menu items for this action.
        @type text: str
        @param callback: Function to be called when the action is triggered.
        @type callback: function
        @param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        @type enabled_flag: bool
        @param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        @type add_to_menu: bool
        @param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        @type add_to_toolbar: bool
        @param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        @type status_tip: str
        @param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        @param parent: Parent widget for the new action. Defaults None.
        @type parent: QWidget
        @return action: The action that was created.
            Note that the action is also added to self.actions list.
        @rtype action: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.main_toolbar.addAction(action)

        if add_to_menu:
            iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Inserts buildings plugin into the roads plugin"""
        home_dir = os.path.split(os.path.dirname(__file__))
        icon_path = os.path.join(home_dir[0], home_dir[1], "icons", "roads_plugin.png")
        self.add_action(icon_path,
                        text=self.tr(u'Building Maintenance'),
                        callback=self.run,
                        parent=iface.mainWindow())
        try:
            dw = qgis.utils.plugins['roads'].dockwidget
            exists = False
            if dw is not None:
                self.dockwidget = qgis.utils.plugins['roads'].dockwidget
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        exists = True
                if exists is False:
                    dw = qgis.utils.plugins['roads'].dockwidget
                    self.run()
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
                if self.layer_registry is not None:
                    self.layer_registry.clear_layer_selection()
                    self.layer_registry.remove_all_layers()
                dw.frames = {}
                if dw.stk_options.count() == 5:
                    dw.stk_options.setCurrentIndex(4)
                    dw.stk_options.removeWidget(dw.stk_options.currentWidget())
                    dw.stk_options.setCurrentIndex(1)

                # Delete road toolbar
                if iface.building_toolbar:
                    iface.mainWindow().removeToolBar(iface.building_toolbar)
                    iface.building_toolbar = None
                    del iface.building_toolbar

        except KeyError:
            pass

    def run(self):
        """Run method that loads and starts the plugin"""
        if not self.menu_frame:
            if not qgis.utils.plugins['roads'].dockwidget:
                qgis.utils.plugins['roads'].main_toolbar.actions()[0].trigger()
            dw = qgis.utils.plugins['roads'].dockwidget
            self.layer_registry = LayerRegistry()
            # no base layers
            self.menu_frame = MenuFrame(self.layer_registry)
            home_dir = os.path.split(os.path.dirname(__file__))
            icon_path = os.path.join(home_dir[0], home_dir[1], "icons", "roads_plugin.png")
            item = QListWidgetItem("Buildings")
            item.setIcon(QIcon(icon_path))
            dw.lst_options.addItem(item)
            dw.lst_options.setCurrentItem(item)
            canvas = iface.mapCanvas()
            selectedcrs = "EPSG:2193"
            target_crs = QgsCoordinateReferenceSystem()
            target_crs.createFromUserInput(selectedcrs)
            canvas.setDestinationCrs(target_crs)
            dw.lst_options.currentItemChanged.connect(self.item_changed)
            dw.insert_into_frames('menu_frame', self.menu_frame)
            self.on_click()

            panel = iface.mainWindow().findChildren(QMenu, "mPanelMenu")[0]
            for act in panel.actions():
                if act.text() == u"Road Maintenance":
                    print 'yup'
                    act.setText(u"Building Maintenance")
                # panel.removeAction(act)
        else:
            dw = qgis.utils.plugins['roads'].dockwidget
            if not qgis.utils.plugins['roads'].is_active:
                qgis.utils.plugins['roads'].main_toolbar.actions()[0].trigger()

                canvas = iface.mapCanvas()
                selectedcrs = "EPSG:2193"
                target_crs = QgsCoordinateReferenceSystem()
                target_crs.createFromUserInput(selectedcrs)
                canvas.setDestinationCrs(target_crs)
                dw.lst_options.currentItemChanged.connect(self.item_changed)
                dw.lst_options.setCurrentRow(2)
                self.on_click()

                panel = iface.mainWindow().findChildren(QMenu, "mPanelMenu")[0]
                for act in panel.actions():
                    if act.text() == u"Road Maintenance":
                        print 'yup'
                        act.setText(u"Building Maintenance")

            else:
                canvas = iface.mapCanvas()
                selectedcrs = "EPSG:2193"
                target_crs = QgsCoordinateReferenceSystem()
                target_crs.createFromUserInput(selectedcrs)
                canvas.setDestinationCrs(target_crs)
                dw.lst_options.currentItemChanged.connect(self.item_changed)
                dw.lst_options.setCurrentRow(2)
                self.on_click()

                panel = iface.mainWindow().findChildren(QMenu, "mPanelMenu")[0]
                for act in panel.actions():
                    if act.text() == u"Road Maintenance":
                        print 'yup'
                        act.setText(u"Building Maintenance")

    def on_click(self):
        dw = qgis.utils.plugins['roads'].dockwidget
        if dw.stk_options.count() == 5:  # 4th widget is not empty
            dw.stk_options.setCurrentIndex(4)  # set to fourth
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.stk_options.setCurrentIndex(3)
        dw.stk_options.addWidget(MenuFrame(self.layer_registry))
        dw.stk_options.setCurrentIndex(4)

    def setup_main_toolbar(self):
        """ Set up the custom tool bar in its most basic state """
        try:
            iface.building_toolbar.clear()
            iface.building_toolbar.setObjectName(u'Road Tools')
            iface.building_toolbar.hide()

            # Choose necessary basic tools
            for nav in iface.mapNavToolToolBar().actions():
                if nav.objectName() in ["mActionPan"]:
                    iface.building_toolbar.addAction(nav)
        except AttributeError:
            # iface.building_toolbar hadn't been created yet
            pass
        iface.actionPan().trigger()

    def item_changed(self, item):
        if item.text() != "Buildings":
            if QgsProject is not None:
                root = QgsProject.instance().layerTreeRoot()
                group = root.findGroup("Building Tool Layers")
                layers = group.findLayers()
                for layer in layers:
                    if layer.layer().name() == "building_outlines":
                        iface.setActiveLayer(layer.layer())
                        iface.actionCancelEdits().trigger()
                    if layer.layer().name() == "bulk_load_outlines":
                        iface.setActiveLayer(layer.layer())
                        iface.actionCancelEdits().trigger()
        else:
            if QgsProject is not None:
                root = QgsProject.instance().layerTreeRoot()
                group = root.findGroup("Building Tool Layers")
                layers = group.findLayers()
                for layer in layers:
                    if layer.layer().name() == "building_outlines":
                        iface.setActiveLayer(layer.layer())
                        layer.layer().startEditing()
                        iface.actionAddFeature().trigger()
                    if layer.layer().name() == "bulk_load_outlines":
                        iface.setActiveLayer(layer.layer())
                        layer.layer().startEditing()
                        iface.actionAddFeature().trigger()