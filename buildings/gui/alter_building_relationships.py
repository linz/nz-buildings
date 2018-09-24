# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtGui import (QAbstractItemView, QColor, QFrame, QHeaderView,
                         QListWidgetItem, QTableWidgetItem)
from PyQt4.QtCore import Qt, pyqtSlot
from qgis.core import QgsFeatureRequest, QgsExpression, QgsExpressionContextUtils, QgsMapLayerRegistry
from qgis.gui import QgsHighlight
from qgis.utils import iface, isPluginLoaded, plugins

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db
from buildings.utilities.multi_layer_selection import MultiLayerSelection
from buildings.sql import select_statements as select


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'alter_building_relationship.ui'))


class AlterRelationships(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, layer_registry, current_dataset, parent=None):
        """Constructor."""
        super(AlterRelationships, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.dockwidget = dockwidget
        self.layer_registry = layer_registry
        self.current_dataset = current_dataset

        canvas = iface.mapCanvas()
        self.tool = MultiLayerSelection(canvas)
        canvas.setMapTool(self.tool)

        self.open_alter_relationship_frame()

        # set up signals and slots
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)

        self.btn_unlink.clicked.connect(self.unlink_clicked)

        self.btn_matched.clicked.connect(self.matched_clicked)
        self.btn_related.clicked.connect(self.related_clicked)

        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.btn_qa_okay.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_okay.text(), commit_status=True))
        self.btn_qa_pending.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_pending.text(), commit_status=True))
        self.btn_qa_refer2supplier.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_refer2supplier.text(), commit_status=True))
        self.btn_qa_not_checked.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_not_checked.text(), commit_status=True))

        if isPluginLoaded('liqa'):
            self.error_inspector = plugins["liqa"].error_inspector
            self.error_inspector.clicked_in_error_inspector.connect(partial(self.error_inspector_btn_clicked, commit_status=True))

        self.dockwidget.closed.connect(self.on_dockwidget_closed)

    def open_alter_relationship_frame(self):
        """Called when opening of the frame"""

        # set selected item color as transparent
        iface.mapCanvas().setSelectionColor(QColor('Transparent'))

        self.btn_unlink.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)

        self.btn_save.setEnabled(False)

        self.add_building_lyrs()
        self.clear_layer_filter()

        self.populate_cmb_relationship()

        iface.setActiveLayer(self.lyr_bulk_load)

        self.highlight_features = []

        self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)

        self.cmb_relationship.currentIndexChanged.connect(self.cmb_relationship_current_index_changed)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

    def add_building_lyrs(self):
        """ Add building layers """

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles/')

        self.lyr_existing = self.layer_registry.add_postgres_layer(
            'existing_subset_extracts', 'existing_subset_extracts', 'shape',
            'buildings_bulk_load', 'building_outline_id',
            'supplied_dataset_id = {0}'.format(self.current_dataset)
        )
        self.lyr_existing.loadNamedStyle(path + 'building_transparent.qml')

        self.lyr_bulk_load = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines', 'shape',
            'buildings_bulk_load', 'bulk_load_outline_id',
            'supplied_dataset_id = {0}'.format(self.current_dataset)
        )
        self.lyr_bulk_load.loadNamedStyle(path + 'building_transparent.qml')

        self.lyr_related_bulk_load = self.layer_registry.add_postgres_layer(
            'related_bulk_load_outlines', 'related_bulk_load_outlines',
            'shape', 'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_related_bulk_load.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_related_existing = self.layer_registry.add_postgres_layer(
            'related_existing_outlines', 'related_existing_outlines',
            'shape', 'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_related_existing.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_matched_bulk_load = self.layer_registry.add_postgres_layer(
            'matched_bulk_load_outlines', 'matched_bulk_load_outlines',
            'shape', 'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_matched_bulk_load.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_matched_existing = self.layer_registry.add_postgres_layer(
            'matched_existing_outlines', 'matched_existing_outlines', 'shape',
            'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_matched_existing.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_removed_existing = self.layer_registry.add_postgres_layer(
            'removed_outlines', 'removed_outlines', 'shape',
            'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_removed_existing.loadNamedStyle(path + 'building_red.qml')

        self.lyr_added_bulk_load = self.layer_registry.add_postgres_layer(
            'added_outlines', 'added_outlines', 'shape',
            'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_added_bulk_load.loadNamedStyle(path + 'building_green.qml')

        self.lyr_related_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            'related_bulk_load_in_edit', 'bulk_load_outlines', 'shape',
            'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_related_bulk_load_in_edit.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_related_existing_in_edit = self.layer_registry.add_postgres_layer(
            'related_existing_in_edit', 'existing_subset_extracts', 'shape',
            'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_related_existing_in_edit.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_matched_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            'matched_bulk_load_in_edit', 'bulk_load_outlines', 'shape',
            'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_matched_bulk_load_in_edit.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_matched_existing_in_edit = self.layer_registry.add_postgres_layer(
            'matched_existing_in_edit', 'existing_subset_extracts', 'shape',
            'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_matched_existing_in_edit.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_removed_existing_in_edit = self.layer_registry.add_postgres_layer(
            'removed_existing_in_edit', 'existing_subset_extracts', 'shape',
            'buildings_bulk_load', 'building_outline_id', ''
        )
        self.lyr_removed_existing_in_edit.loadNamedStyle(path + 'building_red.qml')

        self.lyr_added_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            'added_bulk_load_in_edit', 'bulk_load_outlines', 'shape',
            'buildings_bulk_load', 'bulk_load_outline_id', ''
        )
        self.lyr_added_bulk_load_in_edit.loadNamedStyle(path + 'building_green.qml')

    def repaint_view(self):
        """Repaint views to update changes in result"""
        self.lyr_added_bulk_load.triggerRepaint()
        self.lyr_removed_existing.triggerRepaint()
        self.lyr_matched_bulk_load.triggerRepaint()
        self.lyr_matched_existing.triggerRepaint()
        self.lyr_related_bulk_load.triggerRepaint()
        self.lyr_related_existing.triggerRepaint()

    def clear_layer_filter(self):
        """ Returns 'null' filter for layers """
        self.lyr_added_bulk_load_in_edit.setSubsetString('null')
        self.lyr_removed_existing_in_edit.setSubsetString('null')
        self.lyr_matched_existing_in_edit.setSubsetString('null')
        self.lyr_matched_bulk_load_in_edit.setSubsetString('null')
        self.lyr_related_existing_in_edit.setSubsetString('null')
        self.lyr_related_bulk_load_in_edit.setSubsetString('null')

        self.lyr_added_bulk_load.setSubsetString('')
        self.lyr_removed_existing.setSubsetString('')
        self.lyr_matched_existing.setSubsetString('')
        self.lyr_matched_bulk_load.setSubsetString('')
        self.lyr_related_existing.setSubsetString('')
        self.lyr_related_bulk_load.setSubsetString('')

    def init_tbl_matched_and_related(self):
        """Initiates tbl_relationship when cmb_relationship switches to matched or related"""
        tbl = self.tbl_relationship
        tbl.clearContents()
        tbl.setColumnCount(3)
        tbl.setRowCount(0)

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Existing Outlines"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("Bulk Load Outlines"))
        tbl.setHorizontalHeaderItem(2, QTableWidgetItem("QA Status"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        tbl.setShowGrid(True)

    def init_tbl_removed(self):
        """Initiates tbl_relationship when cmb_relationship switches to removed"""
        tbl = self.tbl_relationship
        tbl.clearContents()
        tbl.setColumnCount(2)
        tbl.setRowCount(0)

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Existing Outlines"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("QA Status"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        tbl.setShowGrid(True)

    def init_tbl_added(self):
        """Initiates tbl_relationship when cmb_relationship switches to added"""
        tbl = self.tbl_relationship
        tbl.clearContents()
        tbl.setColumnCount(2)
        tbl.setRowCount(0)

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Bulk Load Outlines"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("QA Status"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        tbl.setShowGrid(True)

    @pyqtSlot()
    def on_dockwidget_closed(self):
        """Remove highlight when the dockwideget closes"""
        self.highlight_features = []

    @pyqtSlot()
    def highlight_selection_changed(self):
        """ Highlights selected features"""

        # remove all highlight objects
        self.highlight_features = []

        for lyr in [self.lyr_existing, self.lyr_bulk_load]:
            for feat in lyr.selectedFeatures():
                h = QgsHighlight(iface.mapCanvas(), feat.geometry(), lyr)

                # set highlight symbol properties
                h.setColor(QColor(255, 255, 0, 255))
                h.setWidth(4)
                h.setFillColor(QColor(255, 255, 255, 0))
                self.highlight_features.append(h)

    @pyqtSlot()
    def multi_selection_changed(self):

        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
        self.tbl_relationship.clearSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.btn_unlink.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)

        selected_bulk = [feat.id() for feat in self.lyr_bulk_load.selectedFeatures()]
        selected_existing = [feat.id() for feat in self.lyr_existing.selectedFeatures()]

        has_added, has_removed, has_matched, has_related = False, False, False, False
        existing_to_lst, bulk_to_list = [], []
        for feat_id in selected_bulk:
            if feat_id in bulk_to_list:
                continue
            id_added = self.find_added_outlines(feat_id)
            id_matched = self.find_matched_existing_outlines(feat_id)
            ids_existing, ids_bulk = self.find_related_existing_outlines(feat_id)
            if id_added:
                if has_matched or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                bulk_to_list.append(feat_id)
                has_added = True
            elif id_matched:
                if has_added or has_removed or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                existing_to_lst, bulk_to_list = [], []
                existing_to_lst.append(id_matched[0])
                bulk_to_list.append(feat_id)
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                existing_to_lst = ids_existing
                bulk_to_list = ids_bulk
                has_related = True

        for feat_id in selected_existing:
            if feat_id in existing_to_lst:
                continue
            id_removed = self.find_removed_outlines(feat_id)
            id_matched = self.find_matched_bulk_load_outlines(feat_id)
            ids_existing, ids_bulk = self.find_related_bulk_load_outlines(feat_id)
            if id_removed:
                if has_matched or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                existing_to_lst.append(feat_id)
                has_removed = True
            elif id_matched:
                if has_added or has_removed or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                existing_to_lst, bulk_to_list = [], []
                existing_to_lst.append(feat_id)
                bulk_to_list.append(id_matched[0])
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                existing_to_lst = ids_existing
                bulk_to_list = ids_bulk
                has_related = True
        self.insert_into_list(self.lst_existing, existing_to_lst)
        self.insert_into_list(self.lst_bulk, bulk_to_list)
        self.lyr_existing.selectByIds(existing_to_lst)
        self.lyr_bulk_load.selectByIds(bulk_to_list)
        if has_matched or has_related:
            self.btn_unlink.setEnabled(True)
        elif has_added and has_removed:
            self.switch_btn_match_and_related()

        if has_removed:
            self.select_row_in_tbl_removed(existing_to_lst[-1])
        elif has_matched:
            self.select_row_in_tbl_matched(existing_to_lst[-1], bulk_to_list[-1])
        elif has_related:
            self.select_row_in_tbl_related(existing_to_lst[-1], bulk_to_list[-1])

        self.disable_listwidget(self.lst_existing)
        self.disable_listwidget(self.lst_bulk)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

    @pyqtSlot()
    def multi_selection_changed_error(self):
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n------------- UNFINISHED PROCESS -------------'
            '\n\nPlease click Save or Cancel to finish before continuing.'
        )
        self.error_dialog.show()

    @pyqtSlot()
    def unlink_clicked(self):
        """
        Unlink the buildings in the table
        Called when unlink_all botton is clicked
        """
        self.btn_unlink.setEnabled(False)
        self.btn_save.setEnabled(True)

        ids_existing = self.get_ids_from_lst(self.lst_existing)
        ids_bulk = self.get_ids_from_lst(self.lst_bulk)
        self.insert_into_lyr_removed_in_edit(ids_existing)
        self.insert_into_lyr_added_in_edit(ids_bulk)

        self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
        self.tool.multi_selection_changed.connect(self.multi_selection_changed_error)
        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed_error)

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

    @pyqtSlot()
    def matched_clicked(self):
        """
        Match the buildings in the list
        Called when matched botton is clicked
        """
        if self.lst_existing.count() == 1 and self.lst_bulk.count() == 1:
            self.btn_matched.setEnabled(False)
            self.btn_save.setEnabled(True)

            id_existing = int(self.lst_existing.item(0).text())
            id_bulk = int(self.lst_bulk.item(0).text())

            self.insert_into_lyr_matched_existing_in_edit(id_existing)
            self.insert_into_lyr_matched_bulk_load_in_edit(id_bulk)

            self.delete_original_relationship_in_existing(id_existing)
            self.delete_original_relationship_in_bulk_load(id_bulk)

            self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
            self.tool.multi_selection_changed.connect(self.multi_selection_changed_error)
            self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
            self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed_error)
            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()

    @pyqtSlot()
    def related_clicked(self):
        """
        Relate the buildings in the list
        Called when related botton is clicked
        """
        if self.lst_existing.count() == 0 or self.lst_bulk.count() == 0:
            pass
        elif self.lst_existing.count() == 1 and self.lst_existing.count() == 1:
            pass
        else:
            self.btn_related.setEnabled(False)
            self.btn_save.setEnabled(True)
            for row in range(self.lst_existing.count()):
                id_existing = int(self.lst_existing.item(row).text())

                self.insert_into_lyr_related_existing_in_edit(id_existing)
                self.delete_original_relationship_in_existing(id_existing)

            for row in range(self.lst_bulk.count()):
                id_bulk = int(self.lst_bulk.item(row).text())

                self.insert_into_lyr_related_bulk_load_in_edit(id_bulk)
                self.delete_original_relationship_in_bulk_load(id_bulk)

            self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
            self.tool.multi_selection_changed.connect(self.multi_selection_changed_error)
            self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
            self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed_error)
            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()

    @pyqtSlot()
    def save_clicked(self, commit_status=True):
        """
        Save result and change database
        Called when save botton is clicked
        """
        self.db.open_cursor()

        self.delete_original_relationships()

        self.insert_new_added_outlines()
        self.insert_new_removed_outlines()
        self.insert_new_matched_outlines()
        self.insert_new_related_outlines()

        if commit_status:
            self.db.commit_open_cursor()

        if isPluginLoaded('liqa'):
            ids_existing = self.get_ids_from_lst(self.lst_existing)
            ids_bulk = self.get_ids_from_lst(self.lst_bulk)
            self.update_status_in_qa_lyr(ids_existing, ids_bulk, 'Fixed')
            self.refresh_tbl_error_attr()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.btn_save.setEnabled(False)

        self.tool.multi_selection_changed.disconnect(self.multi_selection_changed_error)
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)
        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed_error)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

        self.repaint_view()
        self.clear_layer_filter()
        iface.mapCanvas().refreshAllLayers()

        self.refresh_tbl_relationship()

    @pyqtSlot()
    def cancel_clicked(self):
        self.btn_unlink.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.lst_existing.clear()
        self.lst_bulk.clear()
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        try:
            self.tool.multi_selection_changed.disconnect(self.multi_selection_changed_error)
            self.tool.multi_selection_changed.connect(self.multi_selection_changed)
            self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed_error)
            self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
        except TypeError:
            pass

        self.repaint_view()
        self.clear_layer_filter()
        iface.mapCanvas().refreshAllLayers()

    @pyqtSlot()
    def exit_clicked(self):
        """
        Relate the buildings in the list
        Called when cancel botton is clicked
        """
        try:
            self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
            self.tool.multi_selection_changed.disconnect(self.multi_selection_changed_error)
            self.lyr_existing.selectionChanged.disconnect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.disconnect(self.highlight_selection_changed)
            self.cmb_relationship.currentIndexChanged.disconnect(self.cmb_relationship_current_index_changed)
            self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
            self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed_error)
        except TypeError:
            pass
        self.lst_existing.clear()
        self.lst_bulk.clear()
        self.tbl_relationship.setCurrentIndex(0)
        self.highlight_features = []

        self.layer_registry.remove_layer(self.lyr_existing)
        self.layer_registry.remove_layer(self.lyr_bulk_load)
        self.layer_registry.remove_layer(self.lyr_added_bulk_load)
        self.layer_registry.remove_layer(self.lyr_removed_existing)
        self.layer_registry.remove_layer(self.lyr_matched_existing)
        self.layer_registry.remove_layer(self.lyr_matched_bulk_load)
        self.layer_registry.remove_layer(self.lyr_related_bulk_load)
        self.layer_registry.remove_layer(self.lyr_related_existing)
        self.layer_registry.remove_layer(self.lyr_added_bulk_load_in_edit)
        self.layer_registry.remove_layer(self.lyr_removed_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_matched_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_matched_bulk_load_in_edit)
        self.layer_registry.remove_layer(self.lyr_related_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_related_bulk_load_in_edit)

        from buildings.gui.bulk_load_frame import BulkLoadFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadFrame(dw, self.layer_registry))
        iface.actionPan().trigger()

    @pyqtSlot()
    def cmb_relationship_current_index_changed(self):
        current_text = self.cmb_relationship.currentText()
        if current_text == "Related Outlines":
            self.init_tbl_matched_and_related()
            self.populate_tbl_related()
        elif current_text == "Matched Outlines":
            self.init_tbl_matched_and_related()
            self.populate_tbl_matched()
        elif current_text == "Removed Outlines":
            self.init_tbl_removed()
            self.populate_tbl_removed()
        elif current_text == "Added Outlines":
            self.init_tbl_added()
            self.populate_tbl_added()
        elif current_text == "":
            self.tbl_relationship.setColumnCount(0)
            self.tbl_relationship.setRowCount(0)

        self.disable_tbl_editing(self.tbl_relationship)

    @pyqtSlot()
    def tbl_relationship_item_selection_changed(self):

        self.lst_existing.clear()
        self.lst_bulk.clear()
        if self.has_no_selection_in_table(self.tbl_relationship):
            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()
            return
        try:
            self.lyr_existing.selectionChanged.disconnect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.disconnect(self.highlight_selection_changed)
        except TypeError:
            pass

        row = self.tbl_relationship.selectionModel().selectedRows()[0].row()
        current_text = self.cmb_relationship.currentText()
        if current_text == "Related Outlines":
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            id_bulk = int(self.tbl_relationship.item(row, 1).text())
            ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
            self.insert_into_list(self.lst_existing, ids_existing)
            self.insert_into_list(self.lst_bulk, ids_bulk)
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([id_bulk])
            self.btn_unlink.setEnabled(True)
        elif current_text == "Matched Outlines":
            row = self.tbl_relationship.selectionModel().selectedRows()[0].row()
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            id_bulk = int(self.tbl_relationship.item(row, 1).text())
            self.insert_into_list(self.lst_existing, [id_existing])
            self.insert_into_list(self.lst_bulk, [id_bulk])
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([id_bulk])
            self.btn_unlink.setEnabled(True)
        elif current_text == "Removed Outlines":
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            self.insert_into_list(self.lst_existing, [id_existing])
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([])
        elif current_text == "Added Outlines":
            id_bulk = int(self.tbl_relationship.item(row, 0).text())
            self.insert_into_list(self.lst_bulk, [id_bulk])
            self.lyr_bulk_load.selectByIds([id_bulk])

        self.zoom_to_feature()
        self.highlight_selection_changed()

        try:
            self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)
        except TypeError:
            pass

    @pyqtSlot()
    def tbl_relationship_item_selection_changed_error(self):
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n------------- UNFINISHED PROCESS -------------'
            '\n\nPlease click Save or Cancel to finish before continuing.'
        )
        self.error_dialog.show()

    @pyqtSlot()
    def btn_qa_status_clicked(self, qa_status, commit_status=True):

        qa_status_id = self.get_qa_status_id(qa_status)
        if not qa_status_id:
            return
        current_text = self.cmb_relationship.currentText()
        self.db.open_cursor()
        if current_text == "Related Outlines":
            for index in self.tbl_relationship.selectionModel().selectedRows():
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                id_bulk = int(self.tbl_relationship.item(index.row(), 1).text())
                self.update_qa_status_in_related(id_existing, id_bulk, qa_status_id)
                ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
        elif current_text == "Matched Outlines":
            for index in self.tbl_relationship.selectionModel().selectedRows():
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                id_bulk = int(self.tbl_relationship.item(index.row(), 1).text())
                self.update_qa_status_in_matched(id_existing, id_bulk, qa_status_id)
                ids_existing.append(id_existing)
                ids_bulk.append(id_bulk)
        elif current_text == "Removed Outlines":
            for index in self.tbl_relationship.selectionModel().selectedRows():
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                self.update_qa_status_in_removed(id_existing, qa_status_id)
                ids_existing.append(id_existing)
        elif current_text == "Added Outlines":
            for index in self.tbl_relationship.selectionModel().selectedRows():
                id_bulk = int(self.tbl_relationship.item(index.row(), 0).text())
                self.update_qa_status_in_added(id_bulk, qa_status_id)
                ids_bulk.append(id_bulk)
        else:
            self.db.close_cursor()
            return

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()

        if isPluginLoaded('liqa'):
            self.update_status_in_qa_lyr(list(set(ids_existing)), list(set(ids_bulk)), qa_status)
            self.refresh_tbl_error_attr()

    @pyqtSlot(dict)
    def error_inspector_btn_clicked(self, status_changed_dict, commit_status=True):
        self.db.open_cursor()
        # If LIQA input layers have different relationships, this will just change one
        # Alternative way is to search for the same outline ids in the table which could take long
        for qa_lyr_name in status_changed_dict:
            lyr = QgsMapLayerRegistry.instance().mapLayersByName(qa_lyr_name)[0]
            for feat in status_changed_dict[qa_lyr_name]:
                id_outline = feat[0]
                qa_status = feat[1]
                qa_status_id = self.get_qa_status_id(qa_status)
                if qa_status_id is None:
                    return
                source_lyr_name = QgsExpressionContextUtils.layerScope(lyr).variable('source_lyrs')
                if source_lyr_name == 'added_outlines':
                    self.update_qa_status_in_added(id_outline, qa_status_id)

                elif source_lyr_name == 'removed_outlines':
                    self.update_qa_status_in_removed(id_outline, qa_status_id)

                elif source_lyr_name == 'matched_existing_outlines':
                    id_matched = self.find_matched_bulk_load_outlines(id_outline)
                    if id_matched:
                        self.update_qa_status_in_matched(id_outline, id_matched[0], qa_status_id)
                        self.update_status_in_qa_lyr([], [id_matched[0]], qa_status)

                elif source_lyr_name == 'matched_bulk_load_outlines':
                    id_matched = self.find_matched_bulk_load_outlines(id_outline)
                    if id_matched:
                        self.update_qa_status_in_matched(id_matched[0], id_outline, qa_status_id)
                        self.update_status_in_qa_lyr([id_matched[0]], [], qa_status)

                elif source_lyr_name == 'related_existing_outlines':
                    ids_existing, ids_bulk = self.find_related_bulk_load_outlines(id_outline)
                    if ids_existing and ids_bulk:
                        self.update_qa_status_in_related(ids_existing[0], ids_bulk[0], qa_status_id)
                        self.update_status_in_qa_lyr(ids_existing, ids_bulk, qa_status)

                elif source_lyr_name == 'related_bulk_load_outlines':
                    ids_existing, ids_bulk = self.find_related_existing_outlines(id_outline)
                    if ids_existing and ids_bulk:
                        self.update_qa_status_in_related(ids_existing[0], ids_bulk[0], qa_status_id)
                        self.update_status_in_qa_lyr(ids_existing, ids_bulk, qa_status)
                else:
                    self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText(''))

        self.refresh_tbl_error_attr()

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()

    def switch_btn_match_and_related(self):
        if self.lst_bulk.count() == 0 or self.lst_existing.count() == 0:
            pass
        elif self.lst_bulk.count() == 1 and self.lst_existing.count() == 1:
            self.btn_matched.setEnabled(True)
            self.btn_related.setEnabled(False)
        else:
            self.btn_related.setEnabled(True)
            self.btn_matched.setEnabled(False)

    def multi_relationship_selected_error_msg(self):
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n------------- MULTIPLE RELATIONSHIP SELECTED -------------'
            '\n\nThere are multiple relationships selected. Please unlink '
            'matched or related outlines before altering relationships.'
        )
        self.error_dialog.show()

    def find_added_outlines(self, id_bulk):
        result = self.db._execute(select.added_by_bulk_load_outlines, (id_bulk, self.current_dataset))
        return result.fetchone()

    def find_removed_outlines(self, id_existing):
        result = self.db._execute(select.removed_by_existing_outlines, (id_existing, self.current_dataset))
        return result.fetchone()

    def find_matched_existing_outlines(self, id_bulk):
        result = self.db._execute(select.matched_by_bulk_load_outlines, (id_bulk, self.current_dataset))
        return result.fetchone()

    def find_matched_bulk_load_outlines(self, id_existing):
        result = self.db._execute(select.matched_by_existing_outlines, (id_existing, self.current_dataset))
        return result.fetchone()

    def find_related_existing_outlines(self, id_bulk):
        ids_existing, ids_bulk = [], []
        result = self.db._execute(select.related_by_bulk_load_outlines, (id_bulk, self.current_dataset))
        for (id_existing, id_bulk) in result.fetchall():
            ids_existing.append(id_existing)
            ids_bulk.append(id_bulk)
        return ids_existing, ids_bulk

    def find_related_bulk_load_outlines(self, id_existing):
        ids_existing, ids_bulk = [], []
        result = self.db._execute(select.related_by_existing_outlines, (id_existing, self.current_dataset))
        for (id_existing, id_bulk) in result.fetchall():
            ids_existing.append(id_existing)
            ids_bulk.append(id_bulk)
        return ids_existing, ids_bulk

    def insert_into_table(self, tbl, ids):
        rows = []
        for (id_existing, id_bulk) in ids:
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            if id_existing:
                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            if id_bulk:
                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            rows.append(row_tbl)
        return rows

    def has_no_selection_in_table(self, tbl):
        if not tbl.selectionModel().selectedRows():
            return True
        return False

    def insert_into_lyr_removed_in_edit(self, ids_existing):
        for id_existing in ids_existing:
            filter = self.lyr_removed_existing_in_edit.subsetString()
            self.lyr_removed_existing_in_edit.setSubsetString(filter + ' or building_outline_id = %s' % id_existing)

    def insert_into_lyr_added_in_edit(self, ids_bulk):
        for id_bulk in ids_bulk:
            filter = self.lyr_added_bulk_load_in_edit.subsetString()
            self.lyr_added_bulk_load_in_edit.setSubsetString(filter + ' or bulk_load_outline_id = %s' % id_bulk)

    def delete_original_relationship_in_existing(self, id_existing):
        """
        Remove features in the view layer
        """
        if not self.lyr_removed_existing.subsetString():
            self.lyr_removed_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_removed_existing.setSubsetString(
                self.lyr_removed_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

        if not self.lyr_matched_existing.subsetString():
            self.lyr_matched_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_matched_existing.setSubsetString(
                self.lyr_matched_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

        if not self.lyr_related_existing.subsetString():
            self.lyr_related_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_related_existing.setSubsetString(
                self.lyr_related_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

    def delete_original_relationship_in_bulk_load(self, id_bulk):
        """
        Remove features in the view layer
        """
        if not self.lyr_added_bulk_load.subsetString():
            self.lyr_added_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_added_bulk_load.setSubsetString(
                self.lyr_added_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

        if not self.lyr_matched_bulk_load.subsetString():
            self.lyr_matched_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_matched_bulk_load.setSubsetString(
                self.lyr_matched_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

        if not self.lyr_related_bulk_load.subsetString():
            self.lyr_related_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_related_bulk_load.setSubsetString(
                self.lyr_related_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

    def insert_into_list(self, lst, ids):
        for id in list(set(ids)):
            lst.addItem(QListWidgetItem('%s' % id))

    def get_ids_from_lst(self, lst):
        feat_ids = []
        for row in range(lst.count()):
            feat_ids.append(int(lst.item(row).text()))
        return feat_ids

    def disable_listwidget(self, lst):
        for row in range(lst.count()):
            item = lst.item(row)
            item.setFlags(Qt.ItemIsEnabled)

    def delete_from_lyr_removed_in_edit(self, id_existing):
        filter = self.lyr_removed_existing_in_edit.subsetString()
        self.lyr_removed_existing_in_edit.setSubsetString('(' + filter + ') and "building_outline_id" != %s' % id_existing)

    def delete_from_lyr_added_in_edit(self, id_bulk):
        filter = self.lyr_added_bulk_load_in_edit.subsetString()
        self.lyr_added_bulk_load_in_edit.setSubsetString('(' + filter + ') and "bulk_load_outline_id" != %s' % id_bulk)

    def insert_into_lyr_matched_existing_in_edit(self, id_existing):
        self.lyr_matched_existing_in_edit.setSubsetString('"building_outline_id" = %s' % id_existing)

    def insert_into_lyr_matched_bulk_load_in_edit(self, id_bulk):
        self.lyr_matched_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" = %s' % id_bulk)

    def insert_into_lyr_related_existing_in_edit(self, id_existing):
        filter = self.lyr_related_existing_in_edit.subsetString()
        self.lyr_related_existing_in_edit.setSubsetString(filter + ' or "building_outline_id" = %s' % id_existing)

    def insert_into_lyr_related_bulk_load_in_edit(self, id_bulk):
        filter = self.lyr_related_bulk_load_in_edit.subsetString()
        self.lyr_related_bulk_load_in_edit.setSubsetString(filter + ' or "bulk_load_outline_id" = %s' % id_bulk)

    def delete_original_relationships(self):
        sql_delete_related_existing = 'SELECT buildings_bulk_load.related_delete_existing_outlines(%s);'
        sql_delete_matched_existing = 'SELECT buildings_bulk_load.matched_delete_existing_outlines(%s);'
        sql_delete_removed = 'SELECT buildings_bulk_load.removed_delete_existing_outlines(%s);'
        sql_delete_added = 'SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);'

        for row in range(self.lst_existing.count()):
            item = self.lst_existing.item(row)
            id_existing = int(item.text())
            self.db.execute_no_commit(sql_delete_removed, (id_existing, ))
            self.db.execute_no_commit(sql_delete_matched_existing, (id_existing, ))
            self.db.execute_no_commit(sql_delete_related_existing, (id_existing, ))

        for row in range(self.lst_bulk.count()):
            item = self.lst_bulk.item(row)
            id_bulk = int(item.text())

            self.db.execute_no_commit(sql_delete_added, (id_bulk, ))

    def insert_new_added_outlines(self):
        # added
        sql_insert_added = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'
        for feat in self.lyr_added_bulk_load_in_edit.getFeatures():
            id_bulk = feat['bulk_load_outline_id']
            self.db.execute_no_commit(sql_insert_added, (id_bulk,))

    def insert_new_removed_outlines(self):
        # removed
        sql_insert_removed = 'SELECT buildings_bulk_load.removed_insert_bulk_load_outlines(%s);'
        for feat in self.lyr_removed_existing_in_edit.getFeatures():
            id_existing = feat['building_outline_id']
            self.db.execute_no_commit(sql_insert_removed, (id_existing, ))

    def insert_new_matched_outlines(self):
        # matched
        sql_insert_matched = 'SELECT buildings_bulk_load.matched_insert_building_outlines(%s, %s);'
        for feat1 in self.lyr_matched_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_matched_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_matched, (id_bulk, id_existing))

    def insert_new_related_outlines(self):
        # related
        related_outlines = [feat for feat in self.lyr_related_bulk_load_in_edit.getFeatures()]
        if related_outlines:
            sql_insert_related_group = 'SELECT buildings_bulk_load.related_group_insert();'
            result = self.db.execute_no_commit(sql_insert_related_group)
            new_group_id = result.fetchone()[0]
        sql_insert_related = 'SELECT buildings_bulk_load.related_insert_building_outlines(%s, %s, %s);'
        for feat1 in self.lyr_related_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_related_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_related, (new_group_id, id_bulk, id_existing))

    def disable_tbl_editing(self, tbl):
        """Disable editing so item cannot be changed in the table"""
        for row in range(tbl.rowCount()):
            tbl.showRow(row)
            for col in range(tbl.columnCount()):
                if tbl.item(row, col):
                    tbl.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def refresh_tbl_relationship(self):
        """Refresh tbl_relationship by switching cmb_relationship"""
        index = self.cmb_relationship.currentIndex()
        self.cmb_relationship.setCurrentIndex(0)
        self.cmb_relationship.setCurrentIndex(index)

    def populate_cmb_relationship(self):
        """Populates cmb_relationship"""
        self.cmb_relationship.clear()
        item_list = ['Removed Outlines', 'Added Outlines', 'Matched Outlines', 'Related Outlines']
        self.cmb_relationship.addItems([""] + item_list)

    def change_current_item_in_cmb_relationship(self, source_lyr):
        if 'removed' in source_lyr:
            self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Removed Outlines'))
        elif 'matched' in source_lyr:
            self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Matched Outlines'))
        elif 'related' in source_lyr:
            self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Related Outlines'))
        elif 'added' in source_lyr:
            self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Added Outlines'))

    def populate_tbl_related(self):
        """Populates tbl_relationship when cmb_relationship switches to related"""
        tbl = self.tbl_relationship
        sql_related = """SELECT r.building_outline_id, r.bulk_load_outline_id, q.value
                         FROM buildings_bulk_load.related r
                         JOIN buildings_bulk_load.qa_status q USING (qa_status_id);"""
        result = self.db._execute(sql_related)
        for (id_existing, id_bulk, qa_status) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % qa_status))

    def populate_tbl_matched(self):
        """Populates tbl_relationship when cmb_relationship switches to matched"""
        tbl = self.tbl_relationship
        sql_matched = """SELECT m.building_outline_id, m.bulk_load_outline_id, q.value
                         FROM buildings_bulk_load.matched m
                         JOIN buildings_bulk_load.qa_status q USING (qa_status_id);"""
        result = self.db._execute(sql_matched)
        for (id_existing, id_bulk, qa_status) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % qa_status))

    def populate_tbl_removed(self):
        """Populates tbl_relationship when cmb_relationship switches to removed"""
        tbl = self.tbl_relationship
        sql_removed = """SELECT r.building_outline_id, q.value
                         FROM buildings_bulk_load.removed r
                         JOIN buildings_bulk_load.qa_status q USING (qa_status_id);"""
        result = self.db._execute(sql_removed)
        for (id_existing, qa_status) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % qa_status))

    def populate_tbl_added(self):
        """Populates tbl_relationship when cmb_relationship switches to added"""
        tbl = self.tbl_relationship
        sql_added = """SELECT a.bulk_load_outline_id, q.value
                       FROM buildings_bulk_load.added a
                       JOIN buildings_bulk_load.qa_status q USING (qa_status_id);"""
        result = self.db._execute(sql_added)
        for (id_bulk, qa_status) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % qa_status))

    def get_qa_status_id(self, qa_status):
        """Returns qa_status_id according to the sender button"""
        if qa_status == 'Okay' or qa_status == 'Fixed':
            qa_status_id = 2
        elif qa_status == 'Pending':
            qa_status_id = 3
        elif qa_status == 'Refer to Supplier' or qa_status == 'Inform IIC':  # 'Inform IIC' can be removed after refactoring error inspector'
            qa_status_id = 4
        elif qa_status == 'Not Checked':
            qa_status_id = 1
        else:
            qa_status_id = None
        return qa_status_id

    def zoom_to_feature(self):

        extent = None
        for lyr in [self.lyr_existing, self.lyr_bulk_load]:
            selected_feat = [feat for feat in lyr.selectedFeatures()]
            if selected_feat:
                if not extent:
                    extent = lyr.boundingBoxOfSelected()
                else:
                    extent.combineExtentWith(lyr.boundingBoxOfSelected())
        if extent:
            iface.mapCanvas().setExtent(extent)
            iface.mapCanvas().zoomScale(300.0)

    def update_qa_status_in_related(self, id_existing, id_bulk, qa_status_id):
        """Updates qa_status_id in related table"""
        sql_update_related = """UPDATE buildings_bulk_load.related
                                SET qa_status_id = %s
                                WHERE related_group_id in(
                                    SELECT related_group_id
                                    FROM buildings_bulk_load.related
                                    WHERE building_outline_id = %s AND bulk_load_outline_id = %s
                                )
                                """
        self.db.execute_no_commit(sql_update_related, (qa_status_id, id_existing, id_bulk))

    def update_qa_status_in_matched(self, id_existing, id_bulk, qa_status_id):
        """Updates qa_status_id in matched table"""
        sql_update_matched = """UPDATE buildings_bulk_load.matched
                                SET qa_status_id = %s
                                WHERE building_outline_id = %s AND bulk_load_outline_id = %s;"""
        self.db.execute_no_commit(sql_update_matched, (qa_status_id, id_existing, id_bulk))

    def update_qa_status_in_removed(self, id_existing, qa_status_id):
        """Updates qa_status_id in removed table"""
        sql_update_removed = """UPDATE buildings_bulk_load.removed
                                SET qa_status_id = %s
                                WHERE building_outline_id = %s;"""
        self.db.execute_no_commit(sql_update_removed, (qa_status_id, id_existing))

    def update_qa_status_in_added(self, id_bulk, qa_status_id):
        """Updates qa_status_id in added table"""
        sql_update_added = """UPDATE buildings_bulk_load.added
                              SET qa_status_id = %s
                              WHERE bulk_load_outline_id = %s;"""
        self.db.execute_no_commit(sql_update_added, (qa_status_id, id_bulk))

    def update_related_in_tbl_relationship(self, ids_existing, ids_bulk, qa_status_id, qa_status):
        for row in range(self.tbl_relationship.rowCount()):
            id_existing_tbl = int(self.tbl_relationship.item(row, 0).text())
            id_bulk_tbl = int(self.tbl_relationship.item(row, 1).text())
            qa_status_tbl = self.tbl_relationship.item(row, 2).text()
            if (id_existing_tbl in ids_existing) or (id_bulk_tbl in ids_bulk):
                if qa_status_tbl != qa_status:
                    sql_update_related = """UPDATE buildings_bulk_load.related
                                            SET qa_status_id = %s
                                            WHERE building_outline_id = %s AND bulk_load_outline_id = %s;"""
                    self.db.execute_no_commit(sql_update_related, (qa_status_id, id_existing_tbl, id_bulk_tbl))

    def update_status_in_qa_lyr(self, ids_existing, ids_bulk, qa_status):

        qa_lyrs = self.error_inspector.find_qa_lyrs()
        current_text = self.cmb_relationship.currentText()
        for qa_lyr in qa_lyrs:
            input_name = QgsExpressionContextUtils.layerScope(qa_lyr).variable('source_lyrs')
            relationship = input_name.split('_')[0]
            if relationship in current_text.lower():
                if ids_bulk and self.error_inspector.is_from_bulk_load(input_name):
                    qa_lyr.startEditing()
                    expr = QgsExpression(self.get_expression('bulk_load_', ids_bulk))
                    for feat in qa_lyr.getFeatures(QgsFeatureRequest(expr)):
                        qa_lyr.changeAttributeValue(feat.id(), 1, qa_status, True)
                    qa_lyr.commitChanges()
                elif ids_existing and self.error_inspector.is_from_existing(input_name):
                    qa_lyr.startEditing()
                    expr = QgsExpression(self.get_expression('building_o', ids_existing))
                    for feat in qa_lyr.getFeatures(QgsFeatureRequest(expr)):
                        qa_lyr.changeAttributeValue(feat.id(), 1, qa_status, True)
                    qa_lyr.commitChanges()

    def get_expression(self, field, ids):
        expr = ''
        for feat_id in ids:
            if not expr:
                expr = '"%s" = %s' % (field, feat_id)
            else:
                expr = expr + ' or "%s" = %s' % (field, feat_id)
        return expr

    def refresh_tbl_error_attr(self):
        # refresh tbl_error_attrs
        if self.error_inspector.isVisible():
            self.error_inspector.tbl_error_attr.cellChanged.disconnect(self.error_inspector.update_comment)
            self.error_inspector.init_tbl_error_attr()
            self.error_inspector.tbl_error_attr.cellChanged.connect(self.error_inspector.update_comment)

    def select_row_in_tbl_matched(self, id_existing, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText('Matched Outlines')
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_existing and int(tbl.item(row, 1).text()) == id_bulk:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_related(self, id_existing, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText('Related Outlines')
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_existing and int(tbl.item(row, 1).text()) == id_bulk:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_added(self, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText('Added Outlines')
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_bulk:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_removed(self, id_existing):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText('Removed Outlines')
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_existing:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))
