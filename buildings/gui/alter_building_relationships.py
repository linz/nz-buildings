# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtGui import (QAbstractItemView, QColor, QFrame, QHeaderView,
                         QListWidgetItem, QTableWidgetItem)
from PyQt4.QtCore import Qt, pyqtSlot
from qgis.gui import QgsHighlight, QgsMessageBar
from qgis.utils import iface

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
        self.error_dialog = None
        self.highlight_features = []

        self.frame_setup()
        self.layers_setup()
        self.connect_signals()

    def frame_setup(self):

        self.message_bar_edit = QgsMessageBar()
        self.layout_msg_bar_edit.addWidget(self.message_bar_edit)
        self.message_bar_qa = QgsMessageBar()
        self.layout_msg_bar_qa.addWidget(self.message_bar_qa)

        self.maptool_clicked()
        self.reset_buttons()
        self.populate_cmb_relationship()

    def layers_setup(self):
        # set selected item color as transparent
        iface.mapCanvas().setSelectionColor(QColor('Transparent'))
        self.add_building_lyrs()
        self.repaint_view()
        self.clear_layer_filter()
        iface.setActiveLayer(self.lyr_bulk_load)

    def connect_signals(self):

        self.dockwidget.closed.connect(self.on_dockwidget_closed)

        self.btn_qa_okay.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_okay.text(), commit_status=True))
        self.btn_qa_pending.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_pending.text(), commit_status=True))
        self.btn_qa_refer2supplier.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_refer2supplier.text(), commit_status=True))
        self.btn_qa_not_checked.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_not_checked.text(), commit_status=True))
        self.btn_maptool.clicked.connect(self.maptool_clicked)
        self.btn_unlink.clicked.connect(self.unlink_clicked)
        self.btn_matched.clicked.connect(self.matched_clicked)
        self.btn_related.clicked.connect(self.related_clicked)
        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)
        self.cmb_relationship.currentIndexChanged.connect(self.cmb_relationship_current_index_changed)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

        self.cb_lyr_bulk_load.stateChanged.connect(self.cb_lyr_bulk_load_state_changed)
        self.cb_lyr_existing.stateChanged.connect(self.cb_lyr_existing_state_changed)

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
    def maptool_clicked(self):
        canvas = iface.mapCanvas()
        self.tool = MultiLayerSelection(canvas)
        canvas.setMapTool(self.tool)
        # set up signal and slot
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)

    @pyqtSlot()
    def multi_selection_changed(self):

        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
        self.tbl_relationship.clearSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.reset_buttons()

        selected_bulk = [feat.id() for feat in self.lyr_bulk_load.selectedFeatures()]
        selected_existing = [feat.id() for feat in self.lyr_existing.selectedFeatures()]

        has_multi_set = False
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
                if has_matched:
                    has_multi_set = True
                existing_to_lst = [id_matched[0]]
                bulk_to_list = [feat_id]
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                if has_related:
                    has_multi_set = True
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
                if has_matched:
                    has_multi_set = True
                existing_to_lst = [feat_id]
                bulk_to_list = [id_matched[0]]
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)
                    return
                if has_related:
                    has_multi_set = True
                existing_to_lst = ids_existing
                bulk_to_list = ids_bulk
                has_related = True
        self.insert_into_list(self.lst_existing, existing_to_lst)
        self.insert_into_list(self.lst_bulk, bulk_to_list)
        self.disable_listwidget(self.lst_existing)
        self.disable_listwidget(self.lst_bulk)
        self.lyr_existing.selectByIds(existing_to_lst)
        self.lyr_bulk_load.selectByIds(bulk_to_list)

        # error msg when more than one set of matched or related set are selected
        if has_multi_set:
            self.message_bar_edit.pushMessage('Multiple matched or related sets selected, can only unlink one at a time.')
        # switch botton
        if has_matched or has_related:
            self.btn_unlink.setEnabled(True)
        elif has_added and has_removed:
            self.switch_btn_match_and_related()
        # select rows in tbl_relationship
        self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        if has_removed:
            for id_existing in existing_to_lst:
                self.select_row_in_tbl_removed(id_existing)
        elif has_matched:
            self.select_row_in_tbl_matched(existing_to_lst[0], bulk_to_list[0])
        elif has_related:
            for id_existing in existing_to_lst:
                for id_bulk in bulk_to_list:
                    self.select_row_in_tbl_related(id_existing, id_bulk)
        self.tbl_relationship.setSelectionMode(QAbstractItemView.SingleSelection)

        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

    @pyqtSlot()
    def unfinished_error_msg(self):
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
        self.btn_maptool.setEnabled(False)
        self.btn_save.setEnabled(True)
        self.qa_button_set_enable(False)

        ids_existing = self.get_ids_from_lst(self.lst_existing)
        ids_bulk = self.get_ids_from_lst(self.lst_bulk)
        self.insert_into_lyr_removed_in_edit(ids_existing)
        self.insert_into_lyr_added_in_edit(ids_bulk)

        self.connect_to_error_msg()

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
            self.btn_maptool.setEnabled(False)
            self.btn_save.setEnabled(True)
            self.qa_button_set_enable(False)

            id_existing = int(self.lst_existing.item(0).text())
            id_bulk = int(self.lst_bulk.item(0).text())

            self.insert_into_lyr_matched_existing_in_edit(id_existing)
            self.insert_into_lyr_matched_bulk_load_in_edit(id_bulk)

            self.delete_original_relationship_in_existing(id_existing)
            self.delete_original_relationship_in_bulk_load(id_bulk)

            self.connect_to_error_msg()

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
        elif self.lst_existing.count() == 1 and self.lst_bulk.count() == 1:
            pass
        else:
            self.btn_related.setEnabled(False)
            self.btn_maptool.setEnabled(False)
            self.btn_save.setEnabled(True)
            self.qa_button_set_enable(False)

            for row in range(self.lst_existing.count()):
                id_existing = int(self.lst_existing.item(row).text())

                self.insert_into_lyr_related_existing_in_edit(id_existing)
                self.delete_original_relationship_in_existing(id_existing)

            for row in range(self.lst_bulk.count()):
                id_bulk = int(self.lst_bulk.item(row).text())

                self.insert_into_lyr_related_bulk_load_in_edit(id_bulk)
                self.delete_original_relationship_in_bulk_load(id_bulk)

            self.connect_to_error_msg()

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

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.reset_buttons()
        self.qa_button_set_enable(True)

        self.disconnect_to_error_msg()

        self.repaint_view()
        self.clear_layer_filter()
        iface.mapCanvas().refreshAllLayers()

        self.refresh_tbl_relationship()

    @pyqtSlot()
    def cancel_clicked(self):
        self.reset_buttons()
        self.qa_button_set_enable(True)
        self.lst_existing.clear()
        self.lst_bulk.clear()
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        try:
            self.disconnect_to_error_msg()
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
        self.cancel_clicked()

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
        if current_text == 'Related Outlines':
            self.init_tbl_relationship(['Group', 'Existing', 'Bulk Load', 'QA Status'])
            self.populate_tbl_related()
            self.is_empty_tbl_relationship('Related Outlines')
        elif current_text == 'Matched Outlines':
            self.init_tbl_relationship(['Existing Outlines', 'Bulk Load Outlines', 'QA Status'])
            self.populate_tbl_matched()
            self.is_empty_tbl_relationship('Matched Outlines')
        elif current_text == 'Removed Outlines':
            self.init_tbl_relationship(['Existing Outlines', 'QA Status'])
            self.populate_tbl_removed()
            self.is_empty_tbl_relationship('Removed Outlines')
        elif current_text == '':
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
        if current_text == 'Related Outlines':
            id_existing = int(self.tbl_relationship.item(row, 1).text())
            id_bulk = int(self.tbl_relationship.item(row, 2).text())
            ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
            self.insert_into_list(self.lst_existing, ids_existing)
            self.insert_into_list(self.lst_bulk, ids_bulk)
            self.lyr_existing.selectByIds(ids_existing)
            self.lyr_bulk_load.selectByIds(ids_bulk)
            self.btn_unlink.setEnabled(True)
        elif current_text == 'Matched Outlines':
            row = self.tbl_relationship.selectionModel().selectedRows()[0].row()
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            id_bulk = int(self.tbl_relationship.item(row, 1).text())
            self.insert_into_list(self.lst_existing, [id_existing])
            self.insert_into_list(self.lst_bulk, [id_bulk])
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([id_bulk])
            self.btn_unlink.setEnabled(True)
        elif current_text == 'Removed Outlines':
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            self.insert_into_list(self.lst_existing, [id_existing])
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([])

        self.zoom_to_feature()
        self.highlight_selection_changed()

        try:
            self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)
        except TypeError:
            pass

    @pyqtSlot()
    def btn_qa_status_clicked(self, qa_status, commit_status=True):

        selected_rows = [index.row() for index in self.tbl_relationship.selectionModel().selectedRows()]
        if not selected_rows:
            return
        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
        self.db.open_cursor()

        qa_status_id = self.get_qa_status_id(qa_status)
        current_text = self.cmb_relationship.currentText()

        ids_existing, ids_bulk = [], []
        if current_text == 'Related Outlines':
            # qa_column = 3
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 1).text())
                id_bulk = int(self.tbl_relationship.item(row, 2).text())
                self.update_qa_status_in_related(id_existing, id_bulk, qa_status_id)
                ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
        elif current_text == 'Matched Outlines':
            # qa_column = 2
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 0).text())
                id_bulk = int(self.tbl_relationship.item(row, 1).text())
                self.update_qa_status_in_matched(id_existing, id_bulk, qa_status_id)
                ids_existing.append(id_existing)
                ids_bulk.append(id_bulk)
        elif current_text == 'Removed Outlines':
            # qa_column = 1
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 0).text())
                self.update_qa_status_in_removed(id_existing, qa_status_id)
                ids_existing.append(id_existing)

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()
        self.reset_buttons()
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        self.lst_existing.clear()
        self.lst_bulk.clear()
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

        # Move to the next 'not checked'
        # for row in range(self.tbl_relationship.rowCount()):
        #     if self.tbl_relationship.item(row, qa_column).text() == "Not Checked":
        #         self.tbl_relationship.selectRow(row)
        #         break
        # self.tbl_relationship.setFocus(Qt.MouseFocusReason)

    def cb_lyr_bulk_load_state_changed(self):
        legend = iface.legendInterface()
        if self.cb_lyr_bulk_load.isChecked():
            legend.setLayerVisible(self.lyr_added_bulk_load_in_edit, True)
            legend.setLayerVisible(self.lyr_matched_bulk_load_in_edit, True)
            legend.setLayerVisible(self.lyr_related_bulk_load_in_edit, True)
            legend.setLayerVisible(self.lyr_added_bulk_load, True)
            legend.setLayerVisible(self.lyr_matched_bulk_load, True)
            legend.setLayerVisible(self.lyr_related_bulk_load, True)
        else:
            legend.setLayerVisible(self.lyr_added_bulk_load_in_edit, False)
            legend.setLayerVisible(self.lyr_matched_bulk_load_in_edit, False)
            legend.setLayerVisible(self.lyr_related_bulk_load_in_edit, False)
            legend.setLayerVisible(self.lyr_added_bulk_load, False)
            legend.setLayerVisible(self.lyr_matched_bulk_load, False)
            legend.setLayerVisible(self.lyr_related_bulk_load, False)

    def cb_lyr_existing_state_changed(self):
        legend = iface.legendInterface()
        if self.cb_lyr_existing.isChecked():
            legend.setLayerVisible(self.lyr_removed_existing_in_edit, True)
            legend.setLayerVisible(self.lyr_matched_existing_in_edit, True)
            legend.setLayerVisible(self.lyr_related_existing_in_edit, True)
            legend.setLayerVisible(self.lyr_removed_existing, True)
            legend.setLayerVisible(self.lyr_matched_existing, True)
            legend.setLayerVisible(self.lyr_related_existing, True)
        else:
            legend.setLayerVisible(self.lyr_removed_existing_in_edit, False)
            legend.setLayerVisible(self.lyr_matched_existing_in_edit, False)
            legend.setLayerVisible(self.lyr_related_existing_in_edit, False)
            legend.setLayerVisible(self.lyr_removed_existing, False)
            legend.setLayerVisible(self.lyr_matched_existing, False)
            legend.setLayerVisible(self.lyr_related_existing, False)

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
        return list(set(ids_existing)), list(set(ids_bulk))

    def find_related_bulk_load_outlines(self, id_existing):
        ids_existing, ids_bulk = [], []
        result = self.db._execute(select.related_by_existing_outlines, (id_existing, self.current_dataset))
        for (id_existing, id_bulk) in result.fetchall():
            ids_existing.append(id_existing)
            ids_bulk.append(id_bulk)
        return list(set(ids_existing)), list(set(ids_bulk))

    def insert_into_table(self, tbl, ids):
        rows = []
        for (id_existing, id_bulk) in ids:
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            if id_existing:
                tbl.setItem(row_tbl, 0, QTableWidgetItem('%s' % id_existing))
            if id_bulk:
                tbl.setItem(row_tbl, 1, QTableWidgetItem('%s' % id_bulk))
            rows.append(row_tbl)
        return rows

    def connect_to_error_msg(self):
        self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
        self.tool.multi_selection_changed.connect(self.unfinished_error_msg)
        self.tbl_relationship.itemSelectionChanged.disconnect(self.tbl_relationship_item_selection_changed)
        self.tbl_relationship.itemSelectionChanged.connect(self.unfinished_error_msg)

    def disconnect_to_error_msg(self):
        self.tool.multi_selection_changed.disconnect(self.unfinished_error_msg)
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)
        self.tbl_relationship.itemSelectionChanged.disconnect(self.unfinished_error_msg)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

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

    def reset_buttons(self):
        self.btn_unlink.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_maptool.setEnabled(True)

    def qa_button_set_enable(self, boolean):
        self.btn_qa_okay.setEnabled(boolean)
        self.btn_qa_pending.setEnabled(boolean)
        self.btn_qa_refer2supplier.setEnabled(boolean)
        self.btn_qa_not_checked.setEnabled(boolean)

    def insert_into_list(self, lst, ids):
        for fid in ids:
            lst.addItem(QListWidgetItem('%s' % fid))

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
        item_list = ['Removed Outlines', 'Matched Outlines', 'Related Outlines']
        self.cmb_relationship.addItems([""] + item_list)

    def init_tbl_relationship(self, header_items):
        """Initiates tbl_relationship """
        tbl = self.tbl_relationship
        tbl.setRowCount(0)
        tbl.setColumnCount(len(header_items))

        for i, header_item in enumerate(header_items):
            tbl.setHorizontalHeaderItem(i, QTableWidgetItem(header_item))

        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        tbl.setShowGrid(True)

    def populate_tbl_related(self):
        """Populates tbl_relationship when cmb_relationship switches to related"""
        tbl = self.tbl_relationship
        sql_related = """SELECT r.related_group_id, r.building_outline_id, r.bulk_load_outline_id, q.value
                         FROM buildings_bulk_load.related r
                         JOIN buildings_bulk_load.qa_status q USING (qa_status_id);"""
        result = self.db._execute(sql_related)
        for (id_group, id_existing, id_bulk, qa_status) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_group))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % qa_status))

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

    def is_empty_tbl_relationship(self, relationship):
        if self.tbl_relationship.rowCount() == 0:
            self.message_bar_qa.pushMessage('%s are not available in the current dataset.' % relationship)

    def get_qa_status_id(self, qa_status):
        """Returns qa_status_id according to the sender button"""
        if qa_status == 'Okay':
            qa_status_id = 2
        elif qa_status == 'Pending':
            qa_status_id = 3
        elif qa_status == 'Refer to Supplier':
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
            self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 1).text()) == id_existing and int(tbl.item(row, 2).text()) == id_bulk:
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
