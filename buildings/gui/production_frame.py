# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFrame
from qgis.core import QgsVectorLayer
from qgis.utils import iface

from buildings.gui import production_changes
from buildings.utilities import database as db
from buildings.utilities import layers


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'production_edits.ui'))


class ProductionFrame(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, layer_registry, parent=None):
        """Constructor."""
        super(ProductionFrame, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.layer_registry = layer_registry
        self.db = db
        self.db.connect()
        self.building_layer = QgsVectorLayer()
        self.building_removed = QgsVectorLayer()
        self.territorial_auth = None
        self.add_outlines()
        # editing fields
        self.added_building_ids = []
        self.ids = []
        self.geoms = {}
        self.building_outline_id = None
        self.select_changed = False
        self.geom_changed = False
        self.edit_status = None
        self.change_instance = None
        # set up signals and slots
        self.rad_add.toggled.connect(self.canvas_add_outline)
        self.rad_edit.toggled.connect(self.canvas_edit_outlines)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_exit_edits.clicked.connect(self.exit_editing_clicked)

        self.cmb_capture_method.clear()
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.clear()
        self.cmb_capture_source.setDisabled(1)
        self.cmb_lifecycle_stage.setDisabled(1)
        self.cmb_lifecycle_stage.clear()
        self.cmb_ta.clear()
        self.cmb_ta.setDisabled(1)
        self.cmb_town.clear()
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.clear()
        self.cmb_suburb.setDisabled(1)
        self.btn_save.setDisabled(1)
        self.btn_reset.setDisabled(1)
        self.btn_exit_edits.setDisabled(1)

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

    @pyqtSlot()
    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        # set change instance to added class
        try:
            self.btn_save.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_reset.clicked.disconnect()
        except TypeError:
            pass
        self.change_instance = production_changes.AddProduction(self)
        # connect signals and slots
        self.btn_save.clicked.connect(
            partial(self.change_instance.save_clicked, True))
        self.btn_reset.clicked.connect(
            self.change_instance.reset_clicked)
        self.building_layer.featureAdded.connect(
            self.change_instance.creator_feature_added)
        self.building_layer.featureDeleted.connect(
            self.change_instance.creator_feature_deleted)
        # add territorial Authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})
        self.btn_exit_edits.setEnabled(1)

    @pyqtSlot()
    def canvas_edit_outlines(self):
        """
            When edit outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        # set change instance to edit class
        try:
            self.btn_save.clicked.disconnect()
        except Exception:
            pass
        try:
            self.btn_reset.clicked.disconnect()
        except Exception:
            pass
        if self.rad_edit.isChecked():
            self.change_instance = production_changes.EditProduction(self)
            # set up signals and slots
            self.btn_save.clicked.connect(
                partial(self.change_instance.save_clicked, True))
            self.btn_reset.clicked.connect(self.change_instance.reset_clicked)
            self.building_layer.selectionChanged.connect(
                self.change_instance.selection_changed)
            self.building_layer.geometryChanged.connect(
                self.change_instance.feature_changed)
            # add territorial authority layer
            self.territorial_auth = self.layer_registry.add_postgres_layer(
                'territorial_authorities', 'territorial_authority',
                'shape', 'buildings_reference', '', ''
            )
            layers.style_layer(self.territorial_auth,
                               {1: ['204,121,95', '0.3', 'dash', '5;2']})
            self.btn_exit_edits.setEnabled(1)

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
        self.rad_edit.setAutoExclusive(False)
        self.rad_edit.setChecked(False)
        self.rad_edit.setAutoExclusive(True)
        self.rad_add.setAutoExclusive(False)
        self.rad_add.setChecked(False)
        self.rad_add.setAutoExclusive(True)
        # reload layers
        iface.actionCancelEdits().trigger()
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
        dw.new_widget(MenuFrame(dw, self.layer_registry))

    @pyqtSlot()
    def exit_editing_clicked(self):
        # deselect both comboboxes
        self.rad_edit.setAutoExclusive(False)
        self.rad_edit.setChecked(False)
        self.rad_edit.setAutoExclusive(True)
        self.rad_add.setAutoExclusive(False)
        self.rad_add.setChecked(False)
        self.rad_add.setAutoExclusive(True)
        iface.actionCancelEdits().trigger()
        # reload layers
        self.layer_registry.remove_layer(self.territorial_auth)
        # disable comboboxes
        self.cmb_lifecycle_stage.setDisabled(1)
        self.cmb_lifecycle_stage.clear()
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_method.clear()
        self.cmb_capture_source.setDisabled(1)
        self.cmb_capture_source.clear()
        self.cmb_ta.setDisabled(1)
        self.cmb_ta.clear()
        self.cmb_town.setDisabled(1)
        self.cmb_town.clear()
        self.cmb_suburb.setDisabled(1)
        self.cmb_suburb.clear()
        self.btn_reset.setDisabled(1)
        self.btn_save.setDisabled(1)
        self.btn_exit_edits.setDisabled(1)
        self.ids = []
        self.selection_changed = False
        self.feature_changed = False
        if isinstance(self.change_instance, production_changes.EditProduction):
            try:
                self.building_layer.selectionChanged.disconnect(
                    self.change_instance.selection_changed)
            except TypeError:
                pass
            try:
                self.building_layer.geometryChanged.disconnect(
                    self.change_instance.feature_changed)
            except TypeError:
                pass
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()
