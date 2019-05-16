# -*- coding: utf-8 -*-

from functools import partial
import math
import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QAction, QColor, QFrame, QIcon, QMenu
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsProject, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar, QgsRubberBand
from qgis.utils import iface

from buildings.gui import production_changes
from buildings.gui.edit_dialog import EditDialog
from buildings.utilities import database as db
from buildings.utilities import layers
from buildings.utilities.layers import LayerRegistry
from buildings.utilities.point_tool import PointTool


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
        self.building_removed = QgsVectorLayer()
        self.territorial_auth = None
        self.add_outlines()
        # Set up edit dialog
        self.edit_dialog = EditDialog(self)
        # editing fields
        self.added_building_ids = []
        self.geom = None
        self.ids = []
        self.geoms = {}
        self.building_outline_id = None
        self.edit_status = None
        self.change_instance = None

        self.cb_production.setChecked(True)

        self.menu = QMenu()
        self.action_add_outline = QAction('Add Outline', self.menu)
        self.action_edit_attribute = QAction('Edit Attribute', self.menu)
        self.action_edit_geometry = QAction('Edit Geometry', self.menu)
        self.menu.addAction(self.action_add_outline)
        self.menu.addSeparator()
        self.menu.addAction(self.action_edit_attribute)
        self.menu.addAction(self.action_edit_geometry)
        self.menu.setFixedWidth(300)
        self.tbtn_edits.setMenu(self.menu)
        self.layout_capture_method.hide()
        self.layout_general_info.hide()
        self.layout_end_lifespan.hide()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.btn_circle.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'circle.png')))

        # set up signals and slots
        self.tbtn_edits.triggered.connect(self.tbtn_edits_triggered)
        self.tbtn_edits.clicked.connect(self.tbtn_edits_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_exit_edits.clicked.connect(self.edit_cancel_clicked)
        self.cb_production.clicked.connect(self.cb_production_clicked)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        # self.btn_edit_save.setDisabled(1)
        # self.btn_edit_reset.setDisabled(1)
        # self.btn_exit_edits.setDisabled(1)
        self.btn_circle.hide()

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

    @pyqtSlot(QAction)
    def tbtn_edits_triggered(self, action):
        """
            When edit tool button triggered
        """
        self.tbtn_edits.setDefaultAction(action)
        text = action.text()
        self.enter_edit_mode(text)

    @pyqtSlot()
    def tbtn_edits_clicked(self):
        """
            When edit tool button clicked
        """
        text = self.tbtn_edits.text()
        if text != 'Choose Edit Mode':
            self.enter_edit_mode(text)
        else:
            self.tbtn_edits.showMenu()

    def enter_edit_mode(self, text):

        # self.btn_edit_reset.setEnabled(True)
        # self.btn_exit_edits.setEnabled(True)
        self.tbtn_edits.setEnabled(False)
        self.tbtn_edits.setStyleSheet('QToolButton {color: green;}')
        if text == 'Add Outline':
            self.canvas_add_outline()
        elif text == 'Edit Attribute':
            self.canvas_edit_attribute()
        elif text == 'Edit Geometry':
            self.canvas_edit_geometry()

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.add_outline()
        self.change_instance = self.edit_dialog.get_change_instance()

        # self.geom = None
        self.polyline = None
        self.circle_tool = None
        # self.added_building_ids = []
        # iface.actionCancelEdits().trigger()
        # # reset toolbar
        # for action in iface.building_toolbar.actions():
        #     if action.objectName() not in ['mActionPan']:
        #         iface.building_toolbar.removeAction(action)
        # # set change instance to added class
        # try:
        #     self.btn_edit_save.clicked.disconnect()
        # except TypeError:
        #     pass
        # try:
        #     self.btn_edit_reset.clicked.disconnect()
        # except TypeError:
        #     pass
        # try:
        #     self.btn_exit_edits.clicked.disconnect()
        # except Exception:
        #     pass
        # self.layout_capture_method.show()
        # self.layout_general_info.show()
        # self.layout_end_lifespan.show()
        # self.change_instance = production_changes.AddProduction(self)
        # set up circle button
        self.btn_circle.clicked.connect(self.setup_circle)
        self.btn_circle.show()
        # # connect signals and slots
        # self.btn_edit_save.clicked.connect(partial(self.change_instance.save_clicked, True))
        # self.btn_edit_reset.clicked.connect(self.change_instance.reset_clicked)
        # self.btn_exit_edits.clicked.connect(self.edit_cancel_clicked)
        # self.building_layer.featureAdded.connect(self.change_instance.creator_feature_added)
        # self.building_layer.featureDeleted.connect(self.change_instance.creator_feature_deleted)
        # self.building_layer.geometryChanged.connect(self.change_instance.creator_geometry_changed)
        # # add territorial Authority layer
        # self.territorial_auth = self.layer_registry.add_postgres_layer(
        #     'territorial_authorities', 'territorial_authority',
        #     'shape', 'buildings_reference', '', ''
        # )
        # layers.style_layer(self.territorial_auth,
        #                    {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_attribute(self):
        """
            When edit outline radio button toggled
        """
        self.edit_dialog.show()
        self.edit_dialog.edit_attribute()
        self.change_instance = self.edit_dialog.get_change_instance()
        # iface.actionCancelEdits().trigger()
        # # reset toolbar
        # for action in iface.building_toolbar.actions():
        #     if action.objectName() not in ['mActionPan']:
        #         iface.building_toolbar.removeAction(action)
        # # set change instance to edit class
        # try:
        #     self.btn_edit_save.clicked.disconnect()
        # except Exception:
        #     pass
        # try:
        #     self.btn_edit_reset.clicked.disconnect()
        # except Exception:
        #     pass
        # try:
        #     self.btn_exit_edits.clicked.disconnect()
        # except Exception:
        #     pass
        # try:
        #     self.btn_end_lifespan.clicked.disconnect()
        # except Exception:
        #     pass
        # self.layout_capture_method.show()
        # self.layout_general_info.show()
        # self.layout_end_lifespan.show()
        # self.change_instance = production_changes.EditAttribute(self)
        # # set up signals and slots
        # self.btn_edit_save.clicked.connect(partial(self.change_instance.save_clicked, True))
        # self.btn_edit_reset.clicked.connect(self.change_instance.reset_clicked)
        # self.btn_exit_edits.clicked.connect(self.edit_cancel_clicked)
        # self.btn_end_lifespan.clicked.connect(partial(self.change_instance.end_lifespan, True))
        # self.building_layer.selectionChanged.connect(self.change_instance.selection_changed)
        # # add territorial authority layer
        # self.territorial_auth = self.layer_registry.add_postgres_layer(
        #     'territorial_authorities', 'territorial_authority',
        #     'shape', 'buildings_reference', '', ''
        # )
        # layers.style_layer(self.territorial_auth,
        #                    {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_geometry(self):
        self.edit_dialog.edit_geometry()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

        # iface.actionCancelEdits().trigger()
        # # reset toolbar
        # for action in iface.building_toolbar.actions():
        #     if action.objectName() not in ['mActionPan']:
        #         iface.building_toolbar.removeAction(action)
        # # set change instance to edit class
        # try:
        #     self.btn_edit_save.clicked.disconnect()
        # except Exception:
        #     pass
        # try:
        #     self.btn_edit_reset.clicked.disconnect()
        # except Exception:
        #     pass
        # try:
        #     self.btn_exit_edits.clicked.disconnect()
        # except Exception:
        #     pass
        # self.layout_capture_method.show()
        # self.layout_general_info.hide()
        # self.layout_end_lifespan.hide()
        # self.change_instance = production_changes.EditGeometry(self)
        # # set up signals and slots
        # self.btn_edit_save.clicked.connect(partial(self.change_instance.save_clicked, True))
        # self.btn_edit_reset.clicked.connect(self.change_instance.reset_clicked)
        # self.btn_exit_edits.clicked.connect(self.edit_cancel_clicked)
        # self.building_layer.geometryChanged.connect(self.change_instance.geometry_changed)
        # # add territorial authority layer
        # self.territorial_auth = self.layer_registry.add_postgres_layer(
        #     'territorial_authorities', 'territorial_authority',
        #     'shape', 'buildings_reference', '', ''
        # )
        # layers.style_layer(self.territorial_auth,
        #                    {1: ['204,121,95', '0.3', 'dash', '5;2']})

    @pyqtSlot()
    def setup_circle(self):
        # called when draw circle button is clicked
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
        # called when mapcanvas is clicked
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
            # add feature to building_outlines (triggering featureAdded)
            self.feature = QgsFeature(self.building_layer.pendingFields())
            self.feature.setGeometry(buffer)
            self.building_layer.addFeature(self.feature)
            self.building_layer.triggerRepaint()
            # reset points list
            self.points = []

    @pyqtSlot(QgsPoint)
    def update_line(self, point):
        # called when mouse moved on canvas
        if len(self.points) == 1:
            # if the center has been clicked have a line follow the mouse movement
            line = [self.points[0], point]
            self.polyline.setToGeometry(QgsGeometry.fromPolyline(line), None)

    @pyqtSlot()
    def exit_clicked(self):
        """
        Called when edit production exit button clicked.
        """
        self.edit_cancel_clicked()
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
        Clean up and remove the edit production frame.
        """
        # reload layers
        iface.actionCancelEdits().trigger()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.layer_registry.remove_layer(self.building_layer)
        self.layer_registry.remove_layer(self.building_historic)
        if self.territorial_auth is not None:
            self.layer_registry.remove_layer(self.territorial_auth)

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

        self.tbtn_edits.setEnabled(True)
        self.tbtn_edits.setStyleSheet('QToolButton {color: black;}')

        iface.actionCancelEdits().trigger()
        # reload layers
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.edit_dialog.remove_territorial_auth()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.btn_circle.hide()

        self.change_instance = None

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        layers = ['building_outlines', 'historic_outlines', 'territorial_authorities']
        for layer in layers:
            if layer in layerids:
                # self.btn_edit_save.setDisabled(1)
                # self.btn_edit_reset.setDisabled(1)
                # self.btn_exit_edits.setDisabled(1)
                self.tbtn_edits.setDisabled(1)
                self.cb_production.setDisabled(1)
                iface.messageBar().pushMessage("ERROR",
                                               "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                               level=QgsMessageBar.CRITICAL, duration=5)
                return
