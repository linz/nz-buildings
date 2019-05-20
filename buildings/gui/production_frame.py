# -*- coding: utf-8 -*-

import math
import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, Qt, QSize
from PyQt4.QtGui import QAction, QColor, QFrame, QIcon
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsProject, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar, QgsRubberBand
from qgis.utils import iface

from buildings.gui import production_changes
from buildings.gui.edit_dialog import EditDialog
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry
from buildings.utilities.point_tool import PointTool

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'production_edits.ui'))


class ProductionFrame(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(ProductionFrame, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.db = db
        self.db.connect()
        self.building_layer = QgsVectorLayer()
        self.add_outlines()
        # Set up edit dialog
        self.edit_dialog = EditDialog(self)
        self.change_instance = None

        self.cb_production.setChecked(True)

        # set up signals and slots
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.cb_production.clicked.connect(self.cb_production_clicked)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.setup_toolbar()

    def setup_toolbar(self):

        if 'Add Outline' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
            icon_path = os.path.join(image_dir, "plus.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.add_action = QAction(icon, "Add Outline", iface.building_toolbar)
            iface.registerMainWindowAction(self.add_action, "Ctrl+1")
            self.add_action.triggered.connect(self.canvas_add_outline)
            iface.building_toolbar.addAction(self.add_action)

        if 'Edit Geometry' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
            icon_path = os.path.join(image_dir, "edit_geometry.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_geom_action = QAction(icon, "Edit Geometry", iface.building_toolbar)
            iface.registerMainWindowAction(self.edit_geom_action, "Ctrl+2")
            self.edit_geom_action.triggered.connect(self.canvas_edit_geometry)
            iface.building_toolbar.addAction(self.edit_geom_action)

        if 'Edit Attributes' not in (action.text() for action in iface.building_toolbar.actions()):
            image_dir = os.path.join(__location__, '..', 'icons')
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
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.layer_registry.remove_layer(self.building_layer)
        self.building_historic = self.layer_registry.add_postgres_layer(
            'historic_outlines', 'building_outlines',
            'shape', 'buildings', '',
            'end_lifespan is not NULL')
        self.building_historic.loadNamedStyle(path + 'building_historic.qml')
        self.building_layer = None
        self.building_layer = self.layer_registry.add_postgres_layer(
            'building_outlines', 'building_outlines',
            'shape', 'buildings', '',
            'end_lifespan is NULL')
        self.building_layer.loadNamedStyle(path + 'building_blue.qml')
        iface.setActiveLayer(self.building_layer)

    @pyqtSlot(bool)
    def cb_production_clicked(self, checked):
        group = QgsProject.instance().layerTreeRoot().findGroup('Building Tool Layers')
        if checked:
            group.setVisible(Qt.Checked)
        else:
            group.setVisible(Qt.Unchecked)

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.add_outline()
        self.change_instance = self.edit_dialog.get_change_instance()

        image_dir = os.path.join(__location__, '..', 'icons')
        icon_path = os.path.join(image_dir, "circle.png")
        icon = QIcon()
        icon.addFile(icon_path, QSize(8, 8))
        self.circle_action = QAction(icon, "Draw Circle", iface.building_toolbar)
        iface.registerMainWindowAction(self.circle_action, "Ctrl+0")
        self.circle_action.triggered.connect(self.setup_circle)
        self.circle_action.setCheckable(True)
        iface.building_toolbar.addAction(self.circle_action)

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
    def setup_circle(self):
        """
            called when draw circle button is clicked
        """
        self.points = []
        # set map tool to new point tool
        self.circle_tool = PointTool(iface.mapCanvas())
        iface.mapCanvas().setMapTool(self.circle_tool)
        # create polyline to track drawing on canvas
        self.polyline = QgsRubberBand(iface.mapCanvas(), False)
        self.polyline.setLineStyle(Qt.PenStyle(Qt.DotLine))
        self.polyline.setColor(QColor(255, 0, 0))
        self.polyline.setWidth(1)
        # signals for new map tool
        self.circle_tool.canvas_clicked.connect(self.draw_circle)
        self.circle_tool.mouse_moved.connect(self.update_line)

    @pyqtSlot(QgsPoint)
    def draw_circle(self, point):
        """
            called when mapcanvas is clicked
        """
        self.points.append(point)
        self.polyline.addPoint(point, True)
        self.polyline.setToGeometry(QgsGeometry.fromPolyline(self.points), None)
        # if two points have been clicked (center and edge)
        if len(self.points) == 2:
            # calculate radius of circle
            radius = math.sqrt((self.points[1][0] - self.points[0][0])**2 + (self.points[1][1] - self.points[0][1])**2)
            # number of vertices of circle
            nodes = (round(math.pi / math.acos((radius - 0.001) / radius))) / 10
            # create point on center location
            point = QgsGeometry.fromPoint(QgsPoint(self.points[0]))
            # create buffer of specified distance around point
            buffer = point.buffer(radius, nodes)
            # add feature to bulk_load_outlines (triggering featureAdded)
            self.feature = QgsFeature(self.building_layer.pendingFields())
            self.feature.setGeometry(buffer)
            self.building_layer.addFeature(self.feature)
            self.building_layer.triggerRepaint()
            # reset points list
            self.points = []

    @pyqtSlot(QgsPoint)
    def update_line(self, point):
        """
            called when mouse moved on canvas
        """
        if len(self.points) == 1:
            # if the center has been clicked have a line follow the mouse movement
            line = [self.points[0], point]
            self.polyline.setToGeometry(QgsGeometry.fromPolyline(line), None)

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
        iface.actionCancelEdits().trigger()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.layer_registry.remove_layer(self.building_layer)
        self.layer_registry.remove_layer(self.building_historic)
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

        from buildings.gui.menu_frame import MenuFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot()
    def edit_cancel_clicked(self):
        if len(QgsMapLayerRegistry.instance().mapLayersByName('building_outlines')) > 0:
            if isinstance(self.change_instance, production_changes.EditAttribute):
                try:
                    self.building_layer.selectionChanged.disconnect(self.change_instance.selection_changed)
                except TypeError:
                    pass
            elif isinstance(self.change_instance, production_changes.EditGeometry):
                try:
                    self.building_layer.geometryChanged.disconnect()
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
        # reload layers
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.edit_dialog.remove_territorial_auth()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.setup_toolbar()
        self.change_instance = None

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        for layer in ['building_outlines', 'historic_outlines', 'territorial_authorities']:
            if layer in layerids:
                self.cb_production.setDisabled(1)
                iface.messageBar().pushMessage("ERROR",
                                               "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                               level=QgsMessageBar.CRITICAL, duration=5)
                return
