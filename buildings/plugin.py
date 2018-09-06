# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import QCoreApplication, Qt
from PyQt4.QtGui import (QAction, QDockWidget, QIcon, QListWidgetItem,
                         QMenu, QToolBar)
from qgis.core import QgsCoordinateReferenceSystem
from qgis.utils import iface, plugins

from buildings.gui.dockwidget import BuildingsDockwidget
from buildings.gui.menu_frame import MenuFrame
from buildings.settings.project import (get_attribute_dialog_setting,
                                        set_attribute_dialog_setting)
from utilities.layers import LayerRegistry

# Get the path for the parent directory of this file.
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Buildings:
    """QGIS Plugin Implementation."""
    stop = False

    def __init__(self, iface):
        """Constructor."""

        # Store original enter attribute values dialog setting
        self.attribute_dialog_setting = get_attribute_dialog_setting()

        self.iface = iface
        self.plugin_dir = __location__
        self.image_dir = os.path.join(__location__, '..', 'images')
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
        self.dockwidget = None

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
        """Initiate buildings plugin"""
        home_dir = os.path.dirname(__file__)
        icon_path = os.path.join(home_dir, 'icons', 'buildings_plugin.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Building Maintenance'),
            callback=self.run,
            parent=iface.mainWindow()
        )
        try:
            dw = plugins['buildings'].dockwidget
            exists = False
            if dw is not None:
                self.dockwidget = plugins['buildings'].dockwidget
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        exists = True
                if exists is False:
                    self.run()
        except KeyError:
            pass
        set_attribute_dialog_setting(True)

    def unload(self):
        """Removes the buildings plugin."""

        # Close dockwidget and delete widget completely
        if self.is_active:
            self.dockwidget.close()
            self.dockwidget.setParent(None)
            del self.dockwidget

        try:
            dw = self.dockwidget
            if dw is not None:
                for row in range(0, (dw.lst_options.count()), 1):
                    if dw.lst_options.item(row).text() == 'Buildings':
                        dw.lst_options.takeItem(row)
                if self.layer_registry is not None:
                    self.layer_registry.clear_layer_selection()
                    self.layer_registry.remove_all_layers()
                dw.frames = {}
                if dw.stk_options.count() == 2:
                    dw.stk_options.setCurrentIndex(1)
                    dw.stk_options.removeWidget(dw.stk_options.currentWidget())
                    dw.stk_options.setCurrentIndex(0)

                    # Remove main toolbar
                    for action in self.actions:
                        iface.removePluginMenu(self.tr(u'&Building Maintenance'), action)
                        iface.removeToolBarIcon(action)
                    del self.main_toolbar

                    for toolbar in iface.mainWindow().findChildren(QToolBar, 'Building Tools'):
                        iface.mainWindow().removeToolBar(toolbar)
                        # Setting parent to None, deletes the widget completely
                        toolbar.setParent(None)

                        # Remove action triggering toolbar from ToolBar menu
                        toolbar_menu = iface.mainWindow().findChildren(QMenu, 'mToolbarMenu')[0]
                        for act in toolbar_menu.actions():
                            if act.text() == u'Building Tools':
                                toolbar_menu.removeAction(act)

        except KeyError:
            pass

        # Remove Dockwidget from Panel menu
        panel = iface.mainWindow().findChildren(QMenu, 'mPanelMenu')[0]
        for act in panel.actions():
            if act.text() == u'Buildings':
                panel.removeAction(act)

        # Delete the mainWindow reference to the buildings dockwidget
        for dock in iface.mainWindow().findChildren(QDockWidget, u'BuildingsDockWidgetBase'):
            dock.setParent(None)

    def run(self):
        """Run method that loads and starts the plugin"""
        if not iface.building_toolbar:
            # Set up toolbar
            iface.building_toolbar = QToolBar(u'Building Tools')
            iface.addToolBar(iface.building_toolbar, Qt.RightToolBarArea)

        # Create the dockwidget and dialog and keep reference
        if not self.dockwidget:
            self.dockwidget = BuildingsDockwidget()

            # Connect with close
            self.dockwidget.closed.connect(self.on_dockwidget_closed)

            # Show the dockwidget as a tab
            layerdock = iface.mainWindow().findChild(QDockWidget, 'Layers')
            iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            iface.mainWindow().tabifyDockWidget(layerdock, self.dockwidget)

        self.dockwidget.show()
        self.dockwidget.raise_()

        self.setup_main_toolbar()
        dw = self.dockwidget
        self.layer_registry = LayerRegistry()
        # no base layers
        self.menu_frame = MenuFrame(self.dockwidget, self.layer_registry)
        dw.insert_into_frames('menu_frame', self.menu_frame)
        if dw.lst_options.item(0) is None:
            home_dir = os.path.split(os.path.dirname(__file__))
            icon_path = os.path.join(home_dir[0], home_dir[1], 'icons', 'buildings_plugin.png')
            item = QListWidgetItem('Buildings')
            item.setIcon(QIcon(icon_path))
            dw.lst_options.addItem(item)
            dw.lst_options.setCurrentItem(item)
        canvas = iface.mapCanvas()
        selectedcrs = 'EPSG:2193'
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        self.on_click()

    def on_click(self):
        dw = self.dockwidget
        if dw.stk_options.count() == 2:  # 4th widget is not empty
            dw.stk_options.setCurrentIndex(1)  # set to fourth
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.stk_options.setCurrentIndex(0)
        dw.stk_options.addWidget(MenuFrame(self.dockwidget, self.layer_registry))
        dw.stk_options.setCurrentIndex(1)

    def setup_main_toolbar(self):
        """ Set up the custom tool bar in its most basic state """
        try:
            iface.building_toolbar.clear()
            iface.building_toolbar.setObjectName(u'Building Tools')
            iface.building_toolbar.hide()

            # Choose necessary basic tools
            for nav in iface.mapNavToolToolBar().actions():
                if nav.objectName() in ['mActionPan']:
                    iface.building_toolbar.addAction(nav)
        except AttributeError:
            # iface.building_toolbar hadn't been created yet
            pass
        iface.actionPan().trigger()

    def on_dockwidget_closed(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        from buildings.settings.project import set_attribute_dialog_setting

        # Clear selection on all layers
        self.layer_registry.clear_layer_selection()

        set_attribute_dialog_setting(self.attribute_dialog_setting)
        self.layer_registry.remove_all_layers()

        # Set up toolbar
        self.setup_main_toolbar()
        self.is_active = False
