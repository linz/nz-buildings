# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtGui import (QAbstractItemView, QColor, QFrame, QHeaderView,
                         QListWidgetItem, QTableWidgetItem)
from PyQt4.QtCore import Qt, pyqtSlot
from qgis.core import QgsFeatureRequest, QgsExpression, QgsExpressionContextUtils, QgsVectorLayer
from qgis.gui import QgsHighlight, QgsMessageBar
from qgis.utils import iface, isPluginLoaded, plugins

from buildings.utilities import database as db
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

        self.open_alter_relationship_frame()

        # set up signals and slots
        self.btn_clear_tbl_slt.clicked.connect(self.clear_selection_clicked)
        self.btn_remove_slt.clicked.connect(self.remove_selected_clicked)
        self.btn_remove_all.clicked.connect(self.remove_all_clicked)

        self.btn_unlink_all.clicked.connect(self.unlink_all_clicked)

        self.btn_clear_lst_slt.clicked.connect(self.clear_selection_clicked)
        self.btn_relink_all.clicked.connect(self.relink_all_clicked)

        self.btn_matched.clicked.connect(self.matched_clicked)
        self.btn_related.clicked.connect(self.related_clicked)

        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_cancel.clicked.connect(self.cancel_clicked)

        self.btn_qa_okay.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_okay.text(), commit_status=True))
        self.btn_qa_pending.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_pending.text(), commit_status=True))
        self.btn_qa_refer2supplier.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_refer2supplier.text(), commit_status=True))
        self.btn_qa_not_checked.clicked.connect(partial(self.btn_qa_status_clicked, self.btn_qa_not_checked.text(), commit_status=True))

        if isPluginLoaded('liqa'):
            self.error_inspector = plugins["liqa"].error_inspector
            self.error_inspector_btn_okay = self.error_inspector.btn_okay
            self.error_inspector_btn_fixed = self.error_inspector.btn_fixed
            self.error_inspector_btn_pending = self.error_inspector.btn_pending
            self.error_inspector_btn_inform_iic = self.error_inspector.btn_inform_iic
            self.error_inspector_btn_not_checked = self.error_inspector.btn_not_checked

            self.error_inspector_btn_okay.clicked.connect(partial(self.error_inspector_btn_clicked, self.error_inspector_btn_okay.text(), commit_status=True))
            self.error_inspector_btn_fixed.clicked.connect(partial(self.error_inspector_btn_clicked, self.error_inspector_btn_fixed.text(), commit_status=True))
            self.error_inspector_btn_pending.clicked.connect(partial(self.error_inspector_btn_clicked, self.error_inspector_btn_pending.text(), commit_status=True))
            self.error_inspector_btn_inform_iic.clicked.connect(partial(self.error_inspector_btn_clicked, self.error_inspector_btn_inform_iic.text(), commit_status=True))
            self.error_inspector_btn_not_checked.clicked.connect(partial(self.error_inspector_btn_clicked, self.error_inspector_btn_not_checked.text(), commit_status=True))

        self.dockwidget.closed.connect(self.on_dockwidget_closed)

    def open_alter_relationship_frame(self):
        """Called when opening of the frame"""

        # set selected item color as transparent
        iface.mapCanvas().setSelectionColor(QColor('Transparent'))

        self.init_table(self.tbl_original)
        self.init_list(self.lst_existing)
        self.init_list(self.lst_bulk)

        self.switch_buttons_table()

        self.btn_unlink_all.setEnabled(False)

        self.add_building_lyrs()
        self.clear_layer_filter()

        self.populate_cmb_relationship()

        iface.setActiveLayer(self.lyr_bulk_load)
        iface.actionSelectRectangle().trigger()

        self.highlight_features = []

        self.lyr_existing.selectionChanged.connect(self.lyr_selection_changed)
        self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)

        self.lyr_bulk_load.selectionChanged.connect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)

        self.tbl_original.itemSelectionChanged.connect(self.tbl_original_item_selection_changed)

        self.lst_existing.itemSelectionChanged.connect(self.lst_item_selection_changed)
        self.lst_bulk.itemSelectionChanged.connect(self.lst_item_selection_changed)

        self.cmb_relationship.currentIndexChanged.connect(self.cmb_relationship_current_index_changed)
        self.tbl_relationship.itemSelectionChanged.connect(self.tbl_relationship_item_selection_changed)

    @pyqtSlot()
    def on_dockwidget_closed(self):
        """Remove highlight when the dockwideget closes"""
        self.highlight_features = []

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

    def init_table(self, tbl):
        """ Initiates table """

        tbl.clearContents()
        tbl.setColumnCount(2)
        tbl.setRowCount(0)

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem('Existing Outlines'))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem('Bulk Load Outlines'))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.MultiSelection)

        tbl.setShowGrid(True)

    def init_list(self, lst):
        """ Initiates list """

        lst.clearSelection()
        lst.setSelectionMode(QAbstractItemView.MultiSelection)

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

    @pyqtSlot(int)
    def lyr_selection_changed(self, selected):
        """
        When user selects features in existing outline layers, the ids will be added to the table
        """
        current_layer = self.sender()
        if not isinstance(current_layer, QgsVectorLayer):
            return
        tbl = self.tbl_original
        if self.has_no_selection_in_layers():
            tbl.clearSelection()
            return
        if not selected:
            return
        tbl.itemSelectionChanged.disconnect(self.tbl_original_item_selection_changed)

        if current_layer.name() == 'bulk_load_outlines':
            self.select_from_bulk_load(selected)
        elif current_layer.name() == 'existing_subset_extracts':
            self.select_from_existing(selected)

        # set item not editable
        self.disable_tbl_editing(self.tbl_original)

        tbl.itemSelectionChanged.connect(self.tbl_original_item_selection_changed)
        self.btn_unlink_all.setEnabled(True)

    @pyqtSlot()
    def tbl_original_item_selection_changed(self):
        """
        When users select rows in table, select the corresponding features in layers.
        """
        if self.has_no_selection_in_table():
            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()
            return

        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()

        self.lyr_existing.selectionChanged.disconnect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.disconnect(self.lyr_selection_changed)

        self.select_features_in_layers()

        self.lyr_existing.selectionChanged.connect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.lyr_selection_changed)

    @pyqtSlot()
    def clear_selection_clicked(self):
        """"
        Clear Selection in the widgets
        Called when clear_selection botton is clicked
        """
        btn = self.sender()
        if btn == self.btn_clear_tbl_slt:
            self.tbl_original.clearSelection()
        elif btn == self.btn_clear_lst_slt:
            self.lst_existing.clearSelection()
            self.lst_bulk.clearSelection()

    @pyqtSlot()
    def remove_selected_clicked(self):
        """
        Remove selected row and related row
        Called when remove_selected botton is clicked
        """
        tbl = self.tbl_original
        pair_rows = self.find_pairs_rows_in_table()
        selected_rows = [index.row() for index in tbl.selectionModel().selectedRows()]
        tbl.clearSelection()
        selected_pair_rows = [row for row in selected_rows if row in pair_rows]
        if selected_pair_rows:
            rows = list(set(selected_rows + pair_rows))
        else:
            rows = selected_rows
        for row in reversed(sorted(rows)):
            tbl.removeRow(row)
        if tbl.rowCount() == 0:
            self.btn_unlink_all.setEnabled(False)

    @pyqtSlot()
    def remove_all_clicked(self):
        """
        Remove all rows in the table
        Called when remove_all botton is clicked
        """
        self.tbl_original.setRowCount(0)
        self.btn_unlink_all.setEnabled(False)

    @pyqtSlot()
    def unlink_all_clicked(self):
        """
        Unlink the buildings in the table
        Called when unlink_all botton is clicked
        """
        self.btn_unlink_all.setEnabled(False)

        ids_existing, ids_bulk = self.get_ids_from_tbl_original()

        self.insert_into_list(self.lst_existing, ids_existing)
        self.insert_into_list(self.lst_bulk, ids_bulk)

        self.insert_into_lyr_removed_in_edit(ids_existing)
        self.insert_into_lyr_added_in_edit(ids_bulk)

        self.tbl_original.setRowCount(0)

        self.lyr_existing.selectionChanged.disconnect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.disconnect(self.lyr_selection_changed)

        self.switch_buttons_list()

    @pyqtSlot()
    def lst_item_selection_changed(self):
        """
        When users select rows in lst_existing, select the corresponding features in layers.
        """

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

        ids_existing = self.get_selected_ids_from_lst(self.lst_existing)
        ids_bulk = self.get_selected_ids_from_lst(self.lst_bulk)

        self.lyr_existing.selectByIds(ids_existing)
        self.lyr_bulk_load.selectByIds(ids_bulk)

    @pyqtSlot()
    def relink_all_clicked(self):
        """
        Relink the buildings in the list
        Called when relink_all botton is clicked
        """
        self.lyr_existing.selectionChanged.connect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.lyr_selection_changed)

        self.switch_buttons_table()
        self.btn_unlink_all.setEnabled(True)

        id_list = self.relink_outlines()
        self.insert_into_table(self.tbl_original, id_list)

        self.clear_layer_filter()

        self.lst_existing.clear()
        self.lst_bulk.clear()

    @pyqtSlot()
    def matched_clicked(self):
        """
        Match the buildings in the list
        Called when matched botton is clicked
        """
        rows_lst_existing = [index.row() for index in self.lst_existing.selectionModel().selectedRows()]
        rows_lst_bulk = [index.row() for index in self.lst_bulk.selectionModel().selectedRows()]

        if len(rows_lst_bulk) == 1 and len(rows_lst_existing) == 1:

            item_existing = self.lst_existing.item(rows_lst_existing[0])
            id_existing = int(item_existing.text())
            item_bulk = self.lst_bulk.item(rows_lst_bulk[0])
            id_bulk = int(item_bulk.text())

            self.disable_listwidget_item(item_existing)
            self.disable_listwidget_item(item_bulk)

            self.insert_into_lyr_matched_existing_in_edit(id_existing)
            self.insert_into_lyr_matched_bulk_load_in_edit(id_bulk)

            self.delete_from_lyr_removed_in_edit(id_existing)
            self.delete_from_lyr_added_in_edit(id_bulk)

            self.delete_original_relationship_in_existing(id_existing)
            self.delete_original_relationship_in_bulk_load(id_bulk)

            self.btn_matched.setEnabled(False)
            self.lst_bulk.clearSelection()
            self.lst_existing.clearSelection()
        else:
            iface.messageBar().pushMessage('Error:', 'Do not match other than one building in each layer', level=QgsMessageBar.WARNING)
            return

    @pyqtSlot()
    def related_clicked(self):
        """
        Relate the buildings in the list
        Called when related botton is clicked
        """
        rows_lst_existing = [index.row() for index in self.lst_existing.selectionModel().selectedRows()]
        rows_lst_bulk = [index.row() for index in self.lst_bulk.selectionModel().selectedRows()]

        if len(rows_lst_bulk) < 1 or len(rows_lst_existing) < 1:
            iface.messageBar().pushMessage('Error:', 'Do not relate less than one building in each layer', level=QgsMessageBar.WARNING)
            return
        elif len(rows_lst_bulk) == 1 and len(rows_lst_existing) == 1:
            iface.messageBar().pushMessage('Error:', 'Do not relate only one building in each layer', level=QgsMessageBar.WARNING)
            return
        else:
            for index in self.lst_existing.selectionModel().selectedRows():
                item_existing = self.lst_existing.item(index.row())
                id_existing = int(item_existing.text())

                self.disable_listwidget_item(item_existing)

                self.insert_into_lyr_related_existing_in_edit(id_existing)
                self.delete_from_lyr_removed_in_edit(id_existing)
                self.delete_original_relationship_in_existing(id_existing)

            for index in self.lst_bulk.selectionModel().selectedRows():
                item_bulk = self.lst_bulk.item(index.row())
                id_bulk = int(item_bulk.text())

                self.disable_listwidget_item(item_bulk)

                self.insert_into_lyr_related_bulk_load_in_edit(id_bulk)
                self.delete_from_lyr_added_in_edit(id_bulk)
                self.delete_original_relationship_in_bulk_load(id_bulk)

            self.btn_related.setEnabled(False)
            self.lst_bulk.clearSelection()
            self.lst_existing.clearSelection()

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

        self.lyr_existing.selectionChanged.connect(self.lyr_selection_changed)
        self.lyr_bulk_load.selectionChanged.connect(self.lyr_selection_changed)

        self.switch_buttons_table()
        self.repaint_view()
        self.clear_layer_filter()

        self.btn_unlink_all.setEnabled(True)

        iface.mapCanvas().refreshAllLayers()

    @pyqtSlot()
    def cancel_clicked(self):
        """
        Relate the buildings in the list
        Called when cancel botton is clicked
        """
        self.tbl_original.clearSelection()
        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()

        try:
            self.lyr_existing.selectionChanged.disconnect(self.lyr_selection_changed)
            self.lyr_existing.selectionChanged.disconnect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.disconnect(self.lyr_selection_changed)
            self.lyr_bulk_load.selectionChanged.disconnect(self.highlight_selection_changed)
            self.tbl_original.itemSelectionChanged.disconnect(self.tbl_original_item_selection_changed)
            self.lst_existing.itemSelectionChanged.disconnect(self.lst_item_selection_changed)
            self.lst_bulk.itemSelectionChanged.disconnect(self.lst_item_selection_changed)
        except TypeError:
            pass

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
        try:
            self.lyr_existing.selectionChanged.disconnect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.disconnect(self.highlight_selection_changed)
        except TypeError:
            pass

        self.tbl_original.setRowCount(0)
        self.highlight_features = []
        # self.lyr_existing.removeSelection()
        # self.lyr_bulk_load.removeSelection()
        current_text = self.cmb_relationship.currentText()
        for index in self.tbl_relationship.selectionModel().selectedRows():
            if current_text == "Related Outlines":
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                id_bulk = int(self.tbl_relationship.item(index.row(), 1).text())
                self.lyr_existing.selectByIds([id_existing])
                self.lyr_bulk_load.selectByIds([id_bulk])
            elif current_text == "Matched Outlines":
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                id_bulk = int(self.tbl_relationship.item(index.row(), 1).text())
                self.lyr_existing.selectByIds([id_existing])
                self.lyr_bulk_load.selectByIds([id_bulk])
            elif current_text == "Removed Outlines":
                id_existing = int(self.tbl_relationship.item(index.row(), 0).text())
                self.lyr_existing.selectByIds([id_existing])
            elif current_text == "Added Outlines":
                id_bulk = int(self.tbl_relationship.item(index.row(), 0).text())
                self.lyr_bulk_load.selectByIds([id_bulk])
        self.zoom_to_feature()
        self.highlight_selection_changed()

        try:
            self.lyr_existing.selectionChanged.connect(self.highlight_selection_changed)
            self.lyr_bulk_load.selectionChanged.connect(self.highlight_selection_changed)
        except TypeError:
            pass

    @pyqtSlot()
    def btn_qa_status_clicked(self, qa_status, commit_status=True):

        qa_status_id = self.get_qa_status_id(qa_status)
        if not qa_status_id:
            return
        current_text = self.cmb_relationship.currentText()
        self.db.open_cursor()
        if current_text == "Related Outlines":
            id_existing, id_bulk = self.update_qa_status_in_related(qa_status_id)
        elif current_text == "Matched Outlines":
            id_existing, id_bulk = self.update_qa_status_in_matched(qa_status_id)
        elif current_text == "Removed Outlines":
            id_existing, id_bulk = self.update_qa_status_in_removed(qa_status_id)
        elif current_text == "Added Outlines":
            id_existing, id_bulk = self.update_qa_status_in_added(qa_status_id)

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()

        if isPluginLoaded('liqa'):
            self.update_status_in_qa_lyr(id_existing, id_bulk, qa_status)
            self.refresh_tbl_error_attr()

    @pyqtSlot()
    def error_inspector_btn_clicked(self, qa_status, commit_status=True):

        tbl_error_attr = self.error_inspector.tbl_error_attr
        qa_status_id = self.get_qa_status_id(qa_status)
        if not qa_status_id:
            return
        self.db.open_cursor()
        selected_rows = [index.row() for index in tbl_error_attr.selectionModel().selectedRows() if not tbl_error_attr.isRowHidden(index.row())]
        for i in selected_rows:
            fid = int(tbl_error_attr.item(i, 6).text())
            lyr_name = tbl_error_attr.item(i, 0).text()
            lyr = QgsMapLayerRegistry.instance().mapLayersByName(lyr_name)[0]
            id_outline = [feat.attributes()[3] for feat in lyr.getFeatures(QgsFeatureRequest().setFilterFid(fid))][0]

            source_lyr_name = QgsExpressionContextUtils.layerScope(lyr).variable('source_lyrs')
            if source_lyr_name == 'added_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Added Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 0)
                for row in rows:
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_added(qa_status_id)

            elif source_lyr_name == 'removed_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Removed Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 0)
                for row in rows:
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_removed(qa_status_id)

            elif source_lyr_name == 'matched_existing_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Matched Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 0)
                for row in rows:
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_matched(qa_status_id)
                    id_bulk = int(self.tbl_relationship.item(row, 1).text())
                    self.update_status_in_qa_lyr(None, id_bulk, qa_status)

            elif source_lyr_name == 'matched_bulk_load_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Matched Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 1)
                for row in rows:
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_matched(qa_status_id)
                    id_existing = int(self.tbl_relationship.item(row, 0).text())
                    self.update_status_in_qa_lyr(id_existing, None, qa_status)

            elif source_lyr_name == 'related_existing_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Related Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 0)
                print rows
                for row in rows:
                    print row
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_related(qa_status_id)
                    id_bulk = int(self.tbl_relationship.item(row, 1).text())
                    print id_bulk
                    self.update_status_in_qa_lyr(None, id_bulk, qa_status)

            elif source_lyr_name == 'related_bulk_load_outlines':
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText('Related Outlines'))
                rows = self.find_row_in_tbl_relationship_by_feat_id(id_outline, 1)
                print id_outline
                print rows
                for row in rows:
                    print row
                    self.tbl_relationship.selectRow(row)
                    self.update_qa_status_in_related(qa_status_id)
                    id_existing = int(self.tbl_relationship.item(row, 0).text())
                    print id_existing
                    self.update_status_in_qa_lyr(id_existing, None, qa_status)

            else:
                self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText(''))

        self.refresh_tbl_error_attr()

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()

    def switch_buttons_table(self):
        self.btn_remove_all.setEnabled(True)
        self.btn_remove_slt.setEnabled(True)
        self.btn_clear_tbl_slt.setEnabled(True)

        self.btn_relink_all.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)
        self.btn_clear_lst_slt.setEnabled(False)
        self.btn_save.setEnabled(False)

    def switch_buttons_list(self):
        self.btn_remove_all.setEnabled(False)
        self.btn_remove_slt.setEnabled(False)
        self.btn_clear_tbl_slt.setEnabled(False)

        self.btn_relink_all.setEnabled(True)
        self.btn_matched.setEnabled(True)
        self.btn_related.setEnabled(True)
        self.btn_clear_lst_slt.setEnabled(True)
        self.btn_save.setEnabled(True)

    def select_from_bulk_load(self, selected):
        tbl = self.tbl_original
        tbl.clearSelection()

        pair_rows = self.find_pairs_rows_in_table()

        related_set = []
        for feat_id in selected:
            row = self.find_existing_row(feat_id)
            if row is not None:
                if row in pair_rows:
                    for pair_row in pair_rows:
                        tbl.selectRow(pair_row)
                else:
                    tbl.selectRow(row)
                continue

            id_matched = self.find_matched_existing_outlines(feat_id)
            id_related = self.find_related_existing_outlines(feat_id)
            if id_matched:
                for pair_row in pair_rows:
                    tbl.removeRow(pair_row)
                insert_rows = self.insert_into_table(tbl, [(id_matched[0], feat_id)])
                self.select_rows_in_tbl_original(insert_rows)
            elif id_related:
                for pair_row in pair_rows:
                    tbl.removeRow(pair_row)
                for feat_id_related in id_related:
                    related_set.append((feat_id_related, feat_id))
                    result = self.db._execute(select.related_by_existing_outlines, (feat_id_related, self.current_dataset))
                    for (id_bulk_related, ) in result.fetchall():
                        related_set.append((feat_id_related, id_bulk_related))
            else:
                insert_rows = self.insert_into_table(tbl, [(None, feat_id)])
                self.select_rows_in_tbl_original(insert_rows)

        if related_set:
            related_set = list(set(related_set))
            insert_rows = self.insert_into_table(tbl, related_set)
            self.select_rows_in_tbl_original(insert_rows)

    def select_from_existing(self, selected):
        tbl = self.tbl_original
        tbl.clearSelection()

        pair_rows = self.find_pairs_rows_in_table()

        related_set = []
        for feat_id in selected:
            row = self.find_existing_row(feat_id)
            if row is not None:
                if row in pair_rows:
                    for pair_row in pair_rows:
                        tbl.selectRow(pair_row)
                else:
                    tbl.selectRow(row)
                continue

            id_matched = self.find_matched_bulk_load_outlines(feat_id)
            id_related = self.find_related_bulk_load_outlines(feat_id)
            if id_matched:
                for pair_row in pair_rows:
                    tbl.removeRow(pair_row)
                insert_rows = self.insert_into_table(tbl, [(feat_id, id_matched[0])])
                self.select_rows_in_tbl_original(insert_rows)
            elif id_related:
                for pair_row in pair_rows:
                    tbl.removeRow(pair_row)
                for (feat_id_related, ) in id_related:
                    related_set.append((feat_id, feat_id_related))
                    result = self.db._execute(select.related_by_bulk_load_outlines, (feat_id_related, self.current_dataset))
                    for (id_existing_related, ) in result.fetchall():
                        related_set.append((id_existing_related, feat_id_related))
            else:
                insert_rows = self.insert_into_table(tbl, [(feat_id, None)])
                self.select_rows_in_tbl_original(insert_rows)

        if related_set:
            related_set = list(set(related_set))
            insert_rows = self.insert_into_table(tbl, related_set)
            self.select_rows_in_tbl_original(insert_rows)

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
        result = self.db._execute(select.related_by_bulk_load_outlines, (id_bulk, self.current_dataset))
        return result.fetchall()

    def find_related_bulk_load_outlines(self, id_existing):
        result = self.db._execute(select.related_by_existing_outlines, (id_existing, self.current_dataset))
        return result.fetchall()

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

    def select_rows_in_tbl_original(self, rows):
        for row in rows:
            self.tbl_original.selectRow(row)

    def has_no_selection_in_table(self):
        if not self.tbl_original.selectionModel().selectedRows():
            return True
        return False

    def has_no_selection_in_layers(self):
        for lyr in [self.lyr_bulk_load, self.lyr_existing]:
            selected = [feat for feat in lyr.selectedFeatures()]
            if selected:
                return False
        return True

    def select_features_in_layers(self):

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        feat_ids_existing = []
        feat_ids_bulk = []
        for index in self.tbl_original.selectionModel().selectedRows():
            item_existing = self.tbl_original.item(index.row(), 0)
            item_bulk = self.tbl_original.item(index.row(), 1)
            if item_existing:
                feat_ids_existing.append(int(item_existing.text()))
            if item_bulk:
                feat_ids_bulk.append(int(item_bulk.text()))
        self.lyr_existing.selectByIds(feat_ids_existing)
        self.lyr_bulk_load.selectByIds(feat_ids_bulk)

    def find_pairs_rows_in_table(self):
        tbl = self.tbl_original
        rows = []
        for row in range(tbl.rowCount()):
            item_existing = tbl.item(row, 0)
            item_bulk = tbl.item(row, 1)
            if item_existing and item_bulk:
                rows.append(row)
        return list(reversed(rows))

    def find_existing_row(self, feat_id):
        """
        Check if table has the same id
        """
        tbl = self.tbl_original
        for row in range(tbl.rowCount()):
            item_existing = tbl.item(row, 0)
            item_bulk = tbl.item(row, 1)
            if item_bulk:
                if feat_id == int(item_bulk.text()):
                    return row
            if item_existing:
                if feat_id == int(item_existing.text()):
                    return row
        return None

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

    def get_ids_from_tbl_original(self):
        tbl = self.tbl_original
        ids_existing = []
        ids_bulk = []
        for row in range(tbl.rowCount()):
            item_existing = tbl.item(row, 0)
            item_bulk = tbl.item(row, 1)
            if item_existing:
                ids_existing.append(int(item_existing.text()))
            if item_bulk:
                ids_bulk.append(int(item_bulk.text()))
        ids_existing = list(set(ids_existing))
        ids_bulk = list(set(ids_bulk))

        return ids_existing, ids_bulk

    def insert_into_list(self, lst, ids):
        for id in ids:
            lst.addItem(QListWidgetItem('%s' % id))

    def get_selected_ids_from_lst(self, lst):
        feat_ids = []
        for index in lst.selectionModel().selectedRows():
            item = lst.item(index.row())
            feat_ids.append(int(item.text()))
        return feat_ids

    def get_ids_from_lst(self, lst):
        feat_ids = []
        for row in range(lst.count()):
            feat_ids.append(int(lst.item(row).text()))
        return feat_ids

    def relink_outlines(self):
        """
        Remove building ids from list to table
        """
        id_list = []

        ids_existing = self.get_ids_from_lst(self.lst_existing)
        ids_bulk = self.get_ids_from_lst(self.lst_bulk)

        if (len(ids_existing) == 1) and (len(ids_bulk) == 1):
            id_matched = self.find_matched_bulk_load_outlines(ids_existing[0])
            if id_matched:
                id_list.append((ids_existing[0], ids_bulk[0]))
            else:
                id_list.append((ids_existing[0], None))
                id_list.append((None, ids_bulk[0]))

        elif (len(ids_existing) == 0) or (len(ids_bulk) == 0):
            for id_existing in ids_existing:
                id_list.append((id_existing, None))
            for id_bulk in ids_bulk:
                id_list.append((None, id_bulk))

        else:
            for id_existing in ids_existing:
                id_removed = self.find_removed_outlines(id_existing)
                id_matched = self.find_matched_bulk_load_outlines(id_existing)
                ids_related = self.find_related_bulk_load_outlines(id_existing)
                if id_removed:
                    id_list.append((id_existing, None))
                elif id_matched:
                    id_list.append((id_existing, id_matched[0]))
                elif ids_related:
                    for (id_related, ) in ids_related:
                        id_list.append((id_existing, id_related))

            for id_bulk in ids_bulk:
                if self.find_added_outlines(id_bulk):
                    id_list.append((None, id_bulk))

        return id_list

    def disable_listwidget_item(self, item):
        item.setBackground(QColor('#E3ECEF'))
        item.setFlags(Qt.NoItemFlags)

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
        sql_insert_matched = 'SELECT buildings_bulk_load.matched_insert_buildling_outlines(%s, %s);'
        for feat1 in self.lyr_matched_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_matched_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_matched, (id_bulk, id_existing))

    def insert_new_related_outlines(self):
        # related
        sql_insert_related = 'SELECT buildings_bulk_load.related_insert_buildling_outlines(%s, %s);'
        for feat1 in self.lyr_related_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_related_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_related, (id_bulk, id_existing))

    def disable_tbl_editing(self, tbl):
        """Disable editing so item cannot be changed in the table"""
        for row in range(tbl.rowCount()):
            tbl.showRow(row)
            for col in range(tbl.columnCount()):
                if tbl.item(row, col):
                    tbl.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def refresh_tbl_relationship(self):
        """Refresh tbl_relationship by switching cmb_relationship"""
        text = self.cmb_relationship.currentText()
        self.cmb_relationship.setCurrentIndex(0)
        self.cmb_relationship.setCurrentIndex(self.cmb_relationship.findText(text))

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
            print [feat.id() for feat in lyr.selectedFeatures()]
            if selected_feat:
                if not extent:
                    extent = lyr.boundingBoxOfSelected()
                else:
                    extent.combineExtentWith(lyr.boundingBoxOfSelected())
        if extent:
            print extent.xMaximum(), extent.xMinimum(), extent.yMaximum(), extent.yMinimum()
            iface.mapCanvas().setExtent(extent)
            iface.mapCanvas().zoomScale(300.0)

    def update_qa_status_in_related(self, qa_status_id):
        """Updates qa_status_id in related table"""
        tbl = self.tbl_relationship
        for index in tbl.selectionModel().selectedRows():
            id_existing = tbl.item(index.row(), 0).text()
            id_bulk = tbl.item(index.row(), 1).text()
            sql_update_related = """UPDATE buildings_bulk_load.related
                                    SET qa_status_id = %s
                                    WHERE building_outline_id = %s AND bulk_load_outline_id = %s;"""
            self.db.execute_no_commit(sql_update_related, (qa_status_id, id_existing, id_bulk))

            # if singleselection in tbl_relationship
            return (id_existing, id_bulk)

    def update_qa_status_in_matched(self, qa_status_id):
        """Updates qa_status_id in matched table"""
        tbl = self.tbl_relationship
        for index in tbl.selectionModel().selectedRows():
            id_existing = tbl.item(index.row(), 0).text()
            id_bulk = tbl.item(index.row(), 1).text()
            sql_update_matched = """UPDATE buildings_bulk_load.matched
                                    SET qa_status_id = %s
                                    WHERE building_outline_id = %s AND bulk_load_outline_id = %s;"""
            self.db.execute_no_commit(sql_update_matched, (qa_status_id, id_existing, id_bulk))

            return (id_existing, id_bulk)

    def update_qa_status_in_removed(self, qa_status_id):
        """Updates qa_status_id in removed table"""
        tbl = self.tbl_relationship
        for index in tbl.selectionModel().selectedRows():
            id_existing = tbl.item(index.row(), 0).text()
            sql_update_removed = """UPDATE buildings_bulk_load.removed
                                    SET qa_status_id = %s
                                    WHERE building_outline_id = %s;"""
            self.db.execute_no_commit(sql_update_removed, (qa_status_id, id_existing))

            return (id_existing, None)

    def update_qa_status_in_added(self, qa_status_id):
        """Updates qa_status_id in added table"""
        tbl = self.tbl_relationship
        for index in tbl.selectionModel().selectedRows():
            id_bulk = tbl.item(index.row(), 0).text()
            sql_update_added = """UPDATE buildings_bulk_load.added
                                  SET qa_status_id = %s
                                  WHERE bulk_load_outline_id = %s;"""
            self.db.execute_no_commit(sql_update_added, (qa_status_id, id_bulk))

            return (None, id_bulk)

    def update_status_in_qa_lyr(self, id_existing, id_bulk, qa_status):

        qa_lyrs = self.error_inspector.find_qa_lyrs()
        current_text = self.cmb_relationship.currentText()
        for qa_lyr in qa_lyrs:
            input_name = QgsExpressionContextUtils.layerScope(qa_lyr).variable('source_lyrs')
            relationship = input_name.split('_')[0]
            if relationship in current_text.lower():
                if id_bulk and self.error_inspector.is_from_bulk_load(input_name):
                    qa_lyr.startEditing()
                    expr = QgsExpression("\"bulk_load_\"=%s" % id_bulk)
                    for feat in qa_lyr.getFeatures(QgsFeatureRequest(expr)):
                        qa_lyr.changeAttributeValue(feat.id(), 1, qa_status, True)
                    qa_lyr.commitChanges()
                elif id_existing and self.error_inspector.is_from_existing(input_name):
                    qa_lyr.startEditing()
                    expr = QgsExpression("\"building_o\"=%s" % id_existing)
                    for feat in qa_lyr.getFeatures(QgsFeatureRequest(expr)):
                        qa_lyr.changeAttributeValue(feat.id(), 1, qa_status, True)
                    qa_lyr.commitChanges()

    def find_row_in_tbl_relationship_by_feat_id(self, id_outline, column):
        rows = []
        for row in range(self.tbl_relationship.rowCount()):
            feat_id = int(self.tbl_relationship.item(row, column).text())
            if feat_id == id_outline:
                rows.append(row)
        return rows

    def refresh_tbl_error_attr(self):
        # refresh tbl_error_attrs
        if self.error_inspector.isVisible():
            self.error_inspector.tbl_error_attr.cellChanged.disconnect(self.error_inspector.update_comment)
            self.error_inspector.init_tbl_error_attr()
            self.error_inspector.tbl_error_attr.cellChanged.connect(self.error_inspector.update_comment)


from qgis.core import QgsRectangle, QgsMapLayerRegistry
from PyQt4.Qt import QCursor, QPixmap
from qgis.gui import QgsMapTool


class MultiLayerSelection(QgsMapTool):

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapTool.__init__(self, self.canvas)
        self.cursor = QCursor(QPixmap(['16 16 3 1',
                                       '# c None',
                                       'a c #000000',
                                       '. c #ffffff',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       'aaaaaaaaaaaaaaaaa',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########',
                                       '########a########']))

    def canvasPressEvent(self, e):

        layer_bulk = QgsMapLayerRegistry.instance().mapLayersByName('bulk_load_outlines')
        layer_existing = QgsMapLayerRegistry.instance().mapLayersByName('existing_subset_extracts')
        layers = [layer for layer in layer_bulk] + [layer for layer in layer_existing]
        p = self.toMapCoordinates(e.pos())
        w = self.canvas.mapUnitsPerPixel() * 3
        rect = QgsRectangle(p.x() - w, p.y() - w, p.x() + w, p.y() + w)
        for layer in layers:
            lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, rect)
            layer.select(lRect, False)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def setCursor(self, cursor):
        self.cursor = QCursor(cursor)
