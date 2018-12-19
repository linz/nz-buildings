# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFrame, QToolButton, QTableWidgetItem, QHeaderView, QAbstractItemView
from qgis.core import QgsFeatureRequest, QgsGeometry, QgsMapLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_reference_select_statements as reference_select,
                           general_select_statements as general_select)
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'new_capture_source_area.ui'))


class NewCaptureSourceArea(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(NewCaptureSourceArea, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.error_dialog = None
        self.current_layer = None

        self.added_building_ids = []
        self.geom = None

        self.add_capture_source_area_layer()
        self.init_table()
        self.setup_toolbar()

        self.le_area_title.setDisabled(True)
        self.le_external_id.setDisabled(True)
        self.mcb_selection_layer.setDisabled(True)
        self.mcb_selection_layer.setExceptedLayerList([self.capture_source_area])
        self.rb_select_from_layer.setChecked(False)

        self.capture_source_area.featureAdded.connect(self.creator_feature_added)
        self.capture_source_area.featureDeleted.connect(self.creator_feature_deleted)
        self.capture_source_area.geometryChanged.connect(self.creator_geometry_changed)

        self.rb_select_from_layer.toggled.connect(self.rb_select_from_layer_clicked)

        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)

        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()

    @pyqtSlot(bool)
    def rb_select_from_layer_clicked(self, checked):
        if checked:
            self.mcb_selection_layer.setEnabled(True)
            iface.actionSelect().trigger()
            if self.mcb_selection_layer.count() > 0:
                self.current_layer = self.mcb_selection_layer.currentLayer()
                iface.setActiveLayer(self.current_layer)
                self.current_layer.selectionChanged.connect(self.current_layer_selection_changed)
            self.mcb_selection_layer.layerChanged.connect(self.mcb_selection_layer_changed)
        else:
            self.mcb_selection_layer.layerChanged.disconnect(self.mcb_selection_layer_changed)
            if self.mcb_selection_layer.count() > 0:
                self.current_layer.removeSelection()
                self.current_layer.selectionChanged.disconnect(self.current_layer_selection_changed)

            self.mcb_selection_layer.setDisabled(True)
            iface.actionAddFeature().trigger()
            self.current_layer = None
            iface.setActiveLayer(self.current_layer)

    @pyqtSlot(QgsMapLayer)
    def mcb_selection_layer_changed(self, current_layer):
        if current_layer is None:
            return
        if self.current_layer is not None:
            self.current_layer.removeSelection()
            try:
                self.current_layer.selectionChanged.disconnect(self.current_layer_selection_changed)
            except TypeError:
                pass
        self.current_layer = current_layer
        iface.setActiveLayer(current_layer)
        self.current_layer.selectionChanged.connect(self.current_layer_selection_changed)

    @pyqtSlot()
    def current_layer_selection_changed(self):
        selection = self.current_layer.selectedFeatures()
        if (len(selection) > 1) or (len(selection) == 0):
            self.le_external_id.setDisabled(True)
            self.le_area_title.setDisabled(True)
            iface.messageBar().pushMessage(
                "INFO",
                "More than one feature selected, please re-select.",
                level=QgsMessageBar.INFO, duration=3)
        elif len(selection) == 1:
            new_geometry = selection[0].geometry()
            # error pops up if geometry type is not polygon or multipolygon
            if new_geometry.type() not in [2, 4]:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- WRONG GEOMETRY TYPE ------'
                    '-------------- \n\nInserted capture source area '
                    'should be either polygon or multipolygon.'
                )
                self.error_dialog.show()
                return
            self.le_external_id.setEnabled(True)
            self.le_area_title.setEnabled(True)
            # convert to correct format
            if new_geometry.type() == 2:
                new_geometry = QgsGeometry.fromMultiPolygon([new_geometry.asPolygon()])
            wkt = new_geometry.exportToWkt()
            sql = general_select.convert_geometry
            result = self.db._execute(sql, (wkt,))
            self.geom = result.fetchall()[0][0]

    def add_capture_source_area_layer(self):
        """
            Called on opening of frame to add capture source area layer
        """
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        # add layer
        self.capture_source_area = self.layer_registry.add_postgres_layer(
            'capture_source_area', 'capture_source_area',
            'shape', 'buildings_reference', '', '')
        # set style
        self.capture_source_area.loadNamedStyle(path + 'capture_source.qml')
        # make capture source area the active layer
        iface.setActiveLayer(self.capture_source_area)

    def init_table(self):
        """
            Set up capture source area table
        """
        tbl = self.tbl_capture_source_area
        tbl.setRowCount(0)
        tbl.setColumnCount(2)
        tbl.setHorizontalHeaderItem(0, QTableWidgetItem('Id'))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem('Area Title'))
        tbl.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setShowGrid(True)
        sql_csa = reference_select.capture_source_area_id_and_name
        result = self.db._execute(sql_csa)
        for (polygon_id, area_title) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % polygon_id))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % area_title))
        tbl.sortItems(0)

    def setup_toolbar(self):
        """
            Called on opening of from to set up the buildings toolbar for selection only
        """
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == 'Select Feature(s)':
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # editing actions
        iface.building_toolbar.addSeparator()
        for dig in iface.digitizeToolBar().actions():
            if dig.objectName() in [
                'mActionAddFeature', 'mActionNodeTool',
                'mActionMoveFeature'
            ]:
                iface.building_toolbar.addAction(dig)
        # advanced Actions
        iface.building_toolbar.addSeparator()
        for adv in iface.advancedDigitizeToolBar().actions():
            if adv.objectName() in [
                'mActionUndo', 'mActionRedo',
                'mActionReshapeFeatures', 'mActionOffsetCurve'
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

    @pyqtSlot(int)
    def creator_feature_added(self, qgsfId):
        """
           Called when feature is added
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId not in self.added_building_ids:
            self.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.capture_source_area.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        if new_geometry.type() == 2:
            new_geometry = QgsGeometry.fromMultiPolygon([new_geometry.asPolygon()])
        wkt = new_geometry.exportToWkt()
        sql = general_select.convert_geometry
        result = self.db._execute(sql, (wkt,))
        self.geom = result.fetchall()[0][0]
        self.le_area_title.setEnabled(True)
        self.le_external_id.setEnabled(True)

    @pyqtSlot(int)
    def creator_feature_deleted(self, qgsfId):
        """
            Called when a Feature is Deleted
            @param qgsfId:      Id of deleted feature
            @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.added_building_ids:
            self.added_building_ids.remove(qgsfId)
            if self.added_building_ids == []:
                self.le_area_title.setDisabled(True)
                self.le_external_id.setDisabled(True)
                self.geom = None

    @pyqtSlot(int, QgsGeometry)
    def creator_geometry_changed(self, qgsfId, geom):
        """
           Called when feature is changed
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
           @param geom:        geometry of added feature
           @type  geom:        qgis.core.QgsGeometry
        """
        if qgsfId in self.added_building_ids:
            if geom.type() == 2:
                geom = QgsGeometry.fromMultiPolygon([geom.asPolygon()])
            wkt = geom.exportToWkt()
            if not wkt:
                self.disable_UI_functions()
                self.geom = None
                return
            sql = general_select.convert_geometry
            result = self.db._execute(sql, (wkt,))
            self.geom = result.fetchall()[0][0]
        else:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n -------------------- WRONG GEOMETRY EDITED ------'
                '-------------- \n\nOnly current added outline can '
                'be edited. Please go to [Edit Geometry] to edit '
                'existing outlines.'
            )
            self.error_dialog.show()

    @pyqtSlot()
    def save_clicked(self, commit_status):

        if self.le_area_title.text() == '' or self.le_external_id.text() == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n -------------------- Empty Area Title ------'
                '-------------- \n\nPlease add the title and '
                'external id for the newly created capture '
                'source area.'
            )
            self.error_dialog.show()
            return

        self.db.open_cursor()

        area_title = self.le_area_title.text()
        external_id = self.le_external_id.text()
        geom = self.geom
        sql = 'SELECT buildings_reference.capture_source_area_insert(%s, %s, %s)'
        self.db.execute_no_commit(sql, (external_id, area_title, geom))

        self.init_table()
        self.le_area_title.clear()
        self.le_external_id.clear()
        self.le_area_title.setDisabled(True)
        self.le_external_id.setDisabled(True)

        if commit_status:
            self.db.commit_open_cursor()
            self.geom = None
            self.added_building_ids = []

    @pyqtSlot()
    def reset_clicked(self):
        self.geom = None
        self.added_building_ids = []
        self.le_area_title.clear()
        self.le_area_title.setDisabled(True)
        self.le_external_id.setDisabled(True)
        self.rb_select_from_layer.setChecked(False)

        self.capture_source_area.geometryChanged.disconnect(self.creator_geometry_changed)
        iface.actionCancelEdits().trigger()
        self.capture_source_area.geometryChanged.connect(self.creator_geometry_changed)
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()

    @pyqtSlot()
    def exit_clicked(self):
        self.close_frame()

    def close_frame(self):
        self.rb_select_from_layer.setChecked(False)
        self.mcb_selection_layer.setDisabled(True)
        self.geom = None
        self.added_building_ids = []
        self.current_layer = None
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.layer_registry.remove_layer(self.capture_source_area)
        from buildings.gui.new_capture_source import NewCaptureSource
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSource(dw))

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        if 'capture_source_area' in layerids:
            self.le_area_title.setDisabled(1)
            self.le_external_id.setDisabled(1)
            self.btn_save.setDisabled(1)
            self.btn_reset.setDisabled(1)
            self.tbl_capture_source_area.setDisabled(1)
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            return
