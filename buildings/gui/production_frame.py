# -*- coding: utf-8 -*-

import math
import os.path

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot, Qt, QSize
from qgis.PyQt.QtWidgets import QAction, QFrame
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsProject, QgsVectorLayer
from qgis.gui import QgsRubberBand
from qgis.utils import Qgis, iface

from buildings.gui import production_changes
from buildings.gui.edit_dialog import EditDialog
from buildings.utilities import circle_tool
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry
from buildings.utilities.point_tool import PointTool

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "production_edits.ui"))


class ProductionFrame(QFrame, FORM_CLASS):
    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(ProductionFrame, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.db = db
        self.db.connect()
        self.add_outlines()
        self.change_instance = None
        # Set up edit dialog
        self.edit_dialog = EditDialog(self)

        self.cb_production.setChecked(True)
        self.cb_historic.setChecked(True)

        # set up signals and slots
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.cb_production.clicked.connect(self.cb_production_clicked)
        self.cb_historic.clicked.connect(self.cb_historic_clicked)
        QgsProject.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.setup_toolbar()

    def setup_toolbar(self):

        if "Add Outline" not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "plus.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.add_action = QAction(icon, "Add Outline", iface.building_toolbar)
            iface.registerMainWindowAction(self.add_action, "Ctrl+1")
            self.add_action.triggered.connect(self.canvas_add_outline)
            iface.building_toolbar.addAction(self.add_action)

        if "Edit Geometry" not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "edit_geometry.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_geom_action = QAction(icon, "Edit Geometry", iface.building_toolbar)
            iface.registerMainWindowAction(self.edit_geom_action, "Ctrl+2")
            self.edit_geom_action.triggered.connect(self.canvas_edit_geometry)
            iface.building_toolbar.addAction(self.edit_geom_action)

        if "Edit Attributes" not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "edit_attributes.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_attrs_action = QAction(icon, "Edit Attributes", iface.building_toolbar)
            iface.registerMainWindowAction(self.edit_attrs_action, "Ctrl+3")
            self.edit_attrs_action.triggered.connect(self.canvas_edit_attribute)
            iface.building_toolbar.addAction(self.edit_attrs_action)

        iface.building_toolbar.show()

    def add_outlines(self):
        """
            Add building outlines to canvas
        """
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles/")
        self.building_historic = self.layer_registry.add_postgres_layer(
            "historic_outlines", "building_outlines", "shape", "buildings", "", "end_lifespan is not NULL"
        )
        self.building_historic.loadNamedStyle(path + "historic_production_outlines.qml")
        self.building_layer = None
        self.building_layer = self.layer_registry.add_postgres_layer(
            "building_outlines", "building_outlines", "shape", "buildings", "", "end_lifespan is NULL"
        )
        self.building_layer.loadNamedStyle(path + "production_outlines.qml")
        iface.setActiveLayer(self.building_layer)

    @pyqtSlot(bool)
    def cb_production_clicked(self, checked):
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.building_layer.id())
        layer_tree_model = iface.layerTreeView().layerTreeModel()
        categories = layer_tree_model.layerLegendNodes(layer_tree_layer)
        current_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == "Building Outlines"]
        if checked:
            current_category[0].setData(Qt.Checked, Qt.CheckStateRole)
        else:
            current_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)

    @pyqtSlot(bool)
    def cb_historic_clicked(self, checked):
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.building_historic.id())
        layer_tree_model = iface.layerTreeView().layerTreeModel()
        categories = layer_tree_model.layerLegendNodes(layer_tree_layer)
        current_category = [ln for ln in categories if ln.data(Qt.DisplayRole) == "Historic Outlines"]
        if checked:
            current_category[0].setData(Qt.Checked, Qt.CheckStateRole)
        else:
            current_category[0].setData(Qt.Unchecked, Qt.CheckStateRole)

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.add_outline()
        self.change_instance = self.edit_dialog.get_change_instance()

        self.circle_tool = None
        self.polyline = None
        # setup circle button
        image_dir = os.path.join(__location__, "..", "icons")
        icon_path = os.path.join(image_dir, "circle.png")
        icon = QIcon()
        icon.addFile(icon_path, QSize(8, 8))
        self.circle_action = QAction(icon, "Draw Circle", iface.building_toolbar)
        iface.registerMainWindowAction(self.circle_action, "Ctrl+0")
        self.circle_action.triggered.connect(self.circle_tool_clicked)
        self.circle_action.setCheckable(True)
        iface.building_toolbar.addAction(self.circle_action)

    def circle_tool_clicked(self):
        if self.circle_action.isChecked():
            circle_tool.setup_circle(self)
        else:
            iface.actionAddFeature().trigger()

    def canvas_edit_attribute(self):
        """
            When edit outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.edit_attribute()
        self.change_instance = self.edit_dialog.get_change_instance()

    def canvas_edit_geometry(self):
        """
            When edit geometry radio button toggled
        """
        self.edit_dialog.edit_geometry()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

    @pyqtSlot()
    def exit_clicked(self):
        """
        Called when edit production exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
        Clean up and remove the edit production frame.
        """
        if self.change_instance is not None:
            self.edit_dialog.close()
        QgsProject.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        iface.actionCancelEdits().trigger()
        self.layer_registry.remove_layer(self.building_layer)
        self.layer_registry.remove_layer(self.building_historic)

        from buildings.gui.menu_frame import MenuFrame

        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

    @pyqtSlot()
    def edit_cancel_clicked(self):
        if len(QgsProject.instance().mapLayersByName("building_outlines")) > 0:
            if isinstance(self.change_instance, production_changes.EditAttribute):
                try:
                    self.building_layer.selectionChanged.disconnect(self.change_instance.selection_changed)
                except TypeError:
                    pass
            elif isinstance(self.change_instance, production_changes.EditGeometry):
                try:
                    self.building_layer.geometryChanged.disconnect(self.change_instance.geometry_changed)
                except TypeError:
                    pass
            elif isinstance(self.change_instance, production_changes.AddProduction):
                try:
                    self.building_layer.featureAdded.disconnect()
                except TypeError:
                    pass
                try:
                    self.building_layer.featureDeleted.disconnect()
                except TypeError:
                    pass
                try:
                    self.building_layer.geometryChanged.disconnect()
                except TypeError:
                    pass
                if self.polyline:
                    self.polyline.reset()
                if isinstance(self.circle_tool, PointTool):
                    self.circle_tool.canvas_clicked.disconnect()
                    self.circle_tool.mouse_moved.disconnect()
                    self.circle_tool.deactivate()
                iface.actionPan().trigger()

        iface.actionCancelEdits().trigger()

        self.setup_toolbar()
        self.change_instance = None

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        for layer in ["building_outlines", "historic_outlines"]:
            if layer in layerids:
                self.cb_production.setDisabled(1)
                iface.messageBar().pushMessage(
                    "ERROR",
                    "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                    level=Qgis.Critical,
                    duration=5,
                )
                return

    def reload_production_layer(self):
        """To ensure QGIS has most up to date ID for the newly split feature see #349"""
        self.cb_production_clicked(False)
        self.cb_production_clicked(True)
        self.cb_historic_clicked(False)
        self.cb_historic_clicked(True)
