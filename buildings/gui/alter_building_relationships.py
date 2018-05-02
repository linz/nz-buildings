# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal, Qt

import qgis

import processing

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

from PyQt4.QtGui import QListWidgetItem, QAbstractItemView, QTableWidgetItem, QHeaderView, QTableWidgetSelectionRange, QColor
from qgis.utils import iface
from qgis.core import QgsMapLayerRegistry, QgsProject
from qgis.gui import QgsMessageBar, QgsHighlight
# from functools import partial

import re

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "alter_building_relationship.ui"))

db.connect()


class AlterRelationships(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(AlterRelationships, self).__init__(parent)
        self.setupUi(self)
        # self.setWindowModality(Qt.WindowModal)

        self.layer_registry = layer_registry

        self.open_alter_relationship_dialog()

        # set up signals and slots

        self.btn_clear_slt.clicked.connect(self.clear_selection_clicked)
        self.btn_remove_slt.clicked.connect(self.remove_selected_clicked)
        self.btn_remove_all.clicked.connect(self.remove_all_clicked)

        self.btn_unlink_selected.clicked.connect(self.unlink_selected_clicked)
        self.btn_unlink_all.clicked.connect(self.unlink_all_clicked)

        self.btn_clear_slt2.clicked.connect(self.clear_selection2_clicked)
        self.btn_relink_slt.clicked.connect(self.relink_selected_clicked)
        self.btn_relink_all.clicked.connect(self.relink_all_clicked)

        self.btn_link.clicked.connect(self.link_clicked)

        self.btn_added.clicked.connect(self.added_clicked)
        self.btn_removed.clicked.connect(self.removed_clicked)
        self.btn_matched.clicked.connect(self.matched_clicked)
        self.btn_related.clicked.connect(self.related_clicked)

        self.btn_reunlink_slt.clicked.connect(self.reunlink_selected_clicked)
        self.btn_reunlink_all.clicked.connect(self.reunlink_all_clicked)

        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

        self.btn_unlink_selected.setEnabled(False)
        # self.btn_unlink_all.setEnabled(False)

        self.btn_link.setEnabled(False)

        # self.btn_save.setEnabled(False)

    def open_alter_relationship_dialog(self):
        """Select features on layers"""
        # self.show()

        # set selected item color as transparent
        iface.mapCanvas().setSelectionColor(QColor("Transparent"))

        self.init_table(self.tbl_original)
        self.init_table(self.tbl_result)

        self.init_list(self.lst_existing)
        self.init_list(self.lst_bulk)

        self.add_building_lyrs()

        iface.setActiveLayer(self.existing_lyr)
        iface.actionSelectRectangle().trigger()

        self.hl_list = []

        self.existing_lyr.removeSelection()
        self.existing_lyr.selectionChanged.connect(self.select_from_layer_existing)
        self.existing_lyr.selectionChanged.connect(self.highlight_features)

        self.bulk_load_lyr.removeSelection()
        self.bulk_load_lyr.selectionChanged.connect(self.select_from_layer_bulk)
        self.bulk_load_lyr.selectionChanged.connect(self.highlight_features)

        '''
        building_lyrs = [self.existing_lyr, self.bulk_load_lyr]
        for lyr in building_lyrs:
            lyr.removeSelection()
            lyr.selectionChanged.connect(self.select_from_layer_bulk)
            lyr.selectionChanged.connect(self.select_from_layer_existing)
            lyr.selectionChanged.connect(self.highlight_features)
        '''
        self.tbl_original.itemSelectionChanged.connect(self.select_from_tbl_original)
        # self.tbl_original.itemSelectionChanged.connect(self.select_from_tbl_original_existing)
        # self.tbl_original.itemSelectionChanged.connect(self.select_from_tbl_original_bulk)

        self.lst_existing.itemSelectionChanged.connect(self.select_from_lst_existing)
        self.lst_bulk.itemSelectionChanged.connect(self.select_from_lst_bulk)

        # self.tbl_result.itemSelectionChanged.connect(self.select_from_tbl_result_existing)
        # self.tbl_result.itemSelectionChanged.connect(self.select_from_tbl_result_bulk)

    def add_building_lyrs(self):
        self.remove_building_lyrs()

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles/')

        self.existing_lyr = self.layer_registry.add_postgres_layer(
            "existing_subset_extracts", "existing_subset_extracts", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.existing_lyr.loadNamedStyle(path + 'building_transparent.qml')

        self.bulk_load_lyr = self.layer_registry.add_postgres_layer(
            "bulk_load_outlines", "bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.bulk_load_lyr.loadNamedStyle(path + 'building_transparent.qml')

        self.lyr_related_bulk_load = self.layer_registry.add_postgres_layer(
            "related_bulk_load_outlines", "related_bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_related_bulk_load.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_related_existing = self.layer_registry.add_postgres_layer(
            "related_existing_outlines", "related_existing_outlines", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_related_existing.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_matched_bulk_load = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_outlines", "matched_bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_matched_bulk_load.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_matched_existing = self.layer_registry.add_postgres_layer(
            "matched_existing_outlines", "matched_existing_outlines", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_matched_existing.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_removed_existing = self.layer_registry.add_postgres_layer(
            "removed_outlines", "removed_outlines", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_removed_existing.loadNamedStyle(path + 'building_orange.qml')

        self.lyr_added_bulk_load = self.layer_registry.add_postgres_layer(
            "added_outlines", "added_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_added_bulk_load.loadNamedStyle(path + 'building_green.qml')

        self.lyr_related_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "related_bulk_load_in_edit", "bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_related_bulk_load_in_edit.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_related_existing_in_edit = self.layer_registry.add_postgres_layer(
            "related_existing_in_edit", "existing_subset_extracts", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_related_existing_in_edit.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_matched_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_in_edit", "bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_matched_bulk_load_in_edit.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_matched_existing_in_edit = self.layer_registry.add_postgres_layer(
            "matched_existing_in_edit", "existing_subset_extracts", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_matched_existing_in_edit.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_removed_existing_in_edit = self.layer_registry.add_postgres_layer(
            "removed_existing_in_edit", "existing_subset_extracts", "shape", "buildings_bulk_load", "building_outline_id", "")
        self.lyr_removed_existing_in_edit.loadNamedStyle(path + 'building_orange.qml')

        self.lyr_added_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "added_bulk_load_in_edit", "bulk_load_outlines", "shape", "buildings_bulk_load", "bulk_load_outline_id", "")
        self.lyr_added_bulk_load_in_edit.loadNamedStyle(path + 'building_green.qml')

        iface.mapCanvas().setExtent(self.bulk_load_lyr.extent())

        self.clear_layer_filter()

    def remove_building_lyrs(self):

        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        if group:
            for child in group.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                QgsMapLayerRegistry.instance().removeMapLayer(id)

    def clear_layer_filter(self):

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

        # tbl = self.tbl_original
        tbl.clearContents()
        tbl.setColumnCount(2)
        tbl.setRowCount(0)

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("existing_id"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("bulk_load_id"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.MultiSelection)

        tbl.setShowGrid(True)
        # tbl.setSortingEnabled(True)

    def init_list(self, lst):
        lst.clearSelection()
        lst.setSelectionMode(QAbstractItemView.MultiSelection)
        # lst.setSortingEnabled(True)

    def highlight_features(self):
        ''' function that does the work of highlighting selected features'''

        # remove all highlight objects
        for i in range(len(self.hl_list))[::-1]:
            self.hl_list.pop(i)

        for feat in self.existing_lyr.selectedFeatures():
            h = QgsHighlight(iface.mapCanvas(), feat.geometry(), self.existing_lyr)

            # set highlight symbol properties
            h.setColor(QColor(255, 0, 0, 255))
            h.setWidth(4)
            h.setFillColor(QColor(255, 255, 255, 0))
            self.hl_list.append(h)

        for feat in self.bulk_load_lyr.selectedFeatures():
            h = QgsHighlight(iface.mapCanvas(), feat.geometry(), self.bulk_load_lyr)

            # set highlight symbol properties
            h.setColor(QColor(255, 0, 0, 255))
            h.setWidth(4)
            h.setFillColor(QColor(255, 255, 255, 0))
            self.hl_list.append(h)

    def select_from_layer_existing(self):
        tbl = self.tbl_original

        tbl.itemSelectionChanged.disconnect(self.select_from_tbl_original)
        tbl.clearSelection()

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s"
        sql_matched = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE building_outline_id = %s"
        sql_removed = "SELECT * FROM buildings_bulk_load.removed WHERE building_outline_id = %s"

        for feat_id in self.existing_lyr.selectedFeaturesIds():

            result1 = db._execute(sql_related_existing, (feat_id,))
            feat_ids_related = result1.fetchall()
            if feat_ids_related:
                # remove the current items inside table
                for row_tbl in range(tbl.rowCount())[::-1]:
                    if not ((tbl.item(row_tbl, 1), ) in feat_ids_related or tbl.item(row_tbl, 0) == feat_id):
                        tbl.removeRow(row_tbl)
                for feat_id_related in feat_ids_related:
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id))
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id_related[0]))

                if len(feat_ids_related) == 1:
                    id_bulk = feat_ids_related[0][0]
                    result = db._execute(sql_related_bulk, (id_bulk,))
                    ids = result.fetchall()
                    for (id_existing, ) in ids:
                        if id_existing == feat_id:
                            continue
                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

                continue

            result2 = db._execute(sql_matched, (feat_id,))
            feat_id_matched = result2.fetchone()
            if feat_id_matched:
                # remove the current items inside table
                for row_tbl in range(tbl.rowCount())[::-1]:
                    tbl.removeRow(row_tbl)

                row_tbl = tbl.rowCount()
                tbl.setRowCount(row_tbl + 1)
                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id))
                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id_matched[0]))

                continue

            result3 = db._execute(sql_removed, (feat_id,))
            if result3.fetchone:
                # if the current items are not from added or removed table, remove them
                for row_tbl in range(tbl.rowCount())[::-1]:
                    item_existing = tbl.item(row_tbl, 0)
                    item_bulk = tbl.item(row_tbl, 1)
                    if item_existing and item_bulk:
                        tbl.removeRow(row_tbl)
                have_duplicate_row, the_row = self.check_duplicate_rows(feat_id, None)
                if not have_duplicate_row:
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id))

        tbl.itemSelectionChanged.connect(self.select_from_tbl_original)
        # self.enable_btn_unlink_all()
        tbl.selectAll()

    def select_from_layer_bulk(self):

        tbl = self.tbl_original

        tbl.itemSelectionChanged.disconnect(self.select_from_tbl_original)
        tbl.clearSelection()

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s"
        sql_matched = "SELECT building_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = %s"
        sql_added = "SELECT * FROM buildings_bulk_load.added WHERE bulk_load_outline_id = %s"

        for feat_id in self.bulk_load_lyr.selectedFeaturesIds():
            result1 = db._execute(sql_related_bulk, (feat_id,))
            feat_ids_related = result1.fetchall()
            if feat_ids_related:
                # remove the current items inside table
                for row_tbl in range(tbl.rowCount())[::-1]:
                    if not ((tbl.item(row_tbl, 0), ) in feat_ids_related or tbl.item(row_tbl, 1) == feat_id):
                        tbl.removeRow(row_tbl)
                for feat_id_related in feat_ids_related:
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id_related[0]))
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id))

                if len(feat_ids_related) == 1:
                    id_existing = feat_ids_related[0][0]
                    result = db._execute(sql_related_existing, (id_existing,))
                    ids = result.fetchall()
                    for (id_bulk, ) in ids:
                        if id_bulk == feat_id:
                            continue
                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                continue

            result2 = db._execute(sql_matched, (feat_id,))
            feat_id_matched = result2.fetchone()
            if feat_id_matched:
                # remove the current items inside table
                for row_tbl in range(tbl.rowCount())[::-1]:
                    tbl.removeRow(row_tbl)
                row_tbl = tbl.rowCount()
                tbl.setRowCount(row_tbl + 1)
                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id_matched[0]))
                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id))
                continue

            result3 = db._execute(sql_added, (feat_id,))
            if result3.fetchone:
                # if the current items are not from added or removed table, remove them
                for row_tbl in range(tbl.rowCount())[::-1]:
                    item_existing = tbl.item(row_tbl, 0)
                    item_bulk = tbl.item(row_tbl, 1)
                    if item_existing and item_bulk:
                        tbl.removeRow(row_tbl)
                have_duplicate_row, the_row = self.check_duplicate_rows(None, feat_id)
                if not have_duplicate_row:
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id))
        '''
        for row in range(tbl.rowCount()):
            tbl.showRow(row)
            for col in range(2):
                if tbl.item(row, col):
                    tbl.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        '''

        tbl.itemSelectionChanged.connect(self.select_from_tbl_original)
        # self.enable_btn_unlink_all()
        tbl.selectAll()

    def check_duplicate_rows(self, feat_id_existing, feat_id_bulk):

        tbl = self.tbl_original
        have_duplicate_row = False
        the_row = 0
        for row in range(tbl.rowCount()):
            item_existing = tbl.item(row, 0)
            item_bulk = tbl.item(row, 1)
            if item_existing:
                if item_bulk:
                    if int(item_existing.text()) == feat_id_existing and int(item_bulk.text()) == feat_id_bulk:
                        have_duplicate_row = True
                        the_row = row
                else:
                    if int(item_existing.text()) == feat_id_existing:
                        have_duplicate_row = True
                        the_row = row
            else:
                if item_bulk:
                    if int(item_bulk.text()) == feat_id_bulk:
                        have_duplicate_row = True
                        the_row = row

        return have_duplicate_row, the_row

    def select_from_tbl_original(self):
        self.lst_existing.clearSelection()
        self.tbl_result.clearSelection()
        self.lst_bulk.clearSelection()

        self.existing_lyr.selectionChanged.disconnect(self.select_from_layer_existing)
        self.bulk_load_lyr.selectionChanged.disconnect(self.select_from_layer_bulk)

        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

        feat_ids_existing = []
        feat_ids_bulk = []
        for index in self.tbl_original.selectionModel().selectedRows():
            item_existing = self.tbl_original.item(index.row(), 0)
            if item_existing:
                feat_ids_existing.append(int(item_existing.text()))

            item_bulk = self.tbl_original.item(index.row(), 1)
            if item_bulk:
                feat_ids_bulk.append(int(item_bulk.text()))

        self.existing_lyr.selectByIds(feat_ids_existing)
        self.bulk_load_lyr.selectByIds(feat_ids_bulk)

        self.existing_lyr.selectionChanged.connect(self.select_from_layer_existing)
        self.bulk_load_lyr.selectionChanged.connect(self.select_from_layer_bulk)

        self.enable_btn_unlink_selected()

    def clear_selection_clicked(self):

        self.tbl_original.clearSelection()
        self.btn_unlink_selected.setEnabled(False)

    def remove_selected_clicked(self):
        tbl = self.tbl_original

        rows = []
        for index in tbl.selectionModel().selectedRows()[::-1]:
            item_existing_0 = tbl.item(index.row(), 0)
            item_bulk_0 = tbl.item(index.row(), 1)
            if not item_existing_0 or not item_bulk_0:
                rows.append(index.row())
                continue

            for row in range(tbl.rowCount())[::-1]:
                item_existing = tbl.item(row, 0)
                item_bulk = tbl.item(row, 1)
                if not item_existing or not item_bulk:
                    continue
                if int(item_existing.text()) == int(item_existing_0.text())or int(item_bulk.text()) == int(item_bulk_0.text()):
                    rows.append(row)

        for row in sorted(set(rows), reverse=True):
            tbl.removeRow(row)

        tbl.clearSelection()
        self.enable_btn_unlink_selected()
        # self.enable_btn_unlink_all()

    def remove_all_clicked(self):
        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

        for row in range(self.tbl_original.rowCount())[::-1]:
            self.tbl_original.removeRow(row)
        self.btn_unlink_selected.setEnabled(False)
        # self.btn_unlink_all.setEnabled(False)

    def enable_btn_unlink_selected(self):
        self.btn_unlink_selected.setEnabled(False)
        for index in self.tbl_original.selectionModel().selectedRows():
            self.btn_unlink_selected.setEnabled(True)

    def enable_btn_unlink_all(self):
        self.btn_unlink_all.setEnabled(False)
        for row in range(self.tbl_original.rowCount()):
            self.btn_unlink_all.setEnabled(True)

    def unlink_selected_clicked(self):
        tbl = self.tbl_original
        for index in tbl.selectionModel().selectedRows()[::-1]:
            row = index.row()
            self.remove_from_tbl_to_lst(row)

    def unlink_all_clicked(self):

        tbl = self.tbl_original
        for row in range(tbl.rowCount())[::-1]:
            item_existing = tbl.item(row, 0)
            if item_existing:
                id_existing = int(item_existing.text())

                if not self.lyr_removed_existing_in_edit.subsetString():
                    self.lyr_removed_existing_in_edit.setSubsetString('"building_outline_id" = %s' % id_existing)
                else:
                    self.lyr_removed_existing_in_edit.setSubsetString(
                        self.lyr_removed_existing_in_edit.subsetString() + ' or "building_outline_id" = %s' % id_existing)

                self.remove_features_from_layer_existing(id_existing)

            item_bulk = tbl.item(row, 1)
            if item_bulk:
                id_bulk = int(item_bulk.text())

                if not self.lyr_added_bulk_load_in_edit.subsetString():
                    self.lyr_added_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" = %s' % id_bulk)
                else:
                    self.lyr_added_bulk_load_in_edit.setSubsetString(
                        self.lyr_added_bulk_load_in_edit.subsetString() + ' or "bulk_load_outline_id" = %s' % id_bulk)

                self.remove_features_from_layer_bulk(id_bulk)

            self.remove_from_tbl_to_lst(row)

        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

    def remove_from_tbl_to_lst(self, row):

        tbl = self.tbl_original
        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()
        item_existing = tbl.item(row, 0)
        if item_existing:
            id_existing = int(item_existing.text())
            have_duplicate_id, the_row = self.check_duplicate_listwidgetitems(self.lst_existing, id_existing)
            if not have_duplicate_id:
                self.lst_existing.addItem(QListWidgetItem('%s' % id_existing))
                # else:
                #     self.lst_existing.item(the_row).setSelected(True)
        item_bulk = tbl.item(row, 1)
        if item_bulk:
            id_bulk = int(item_bulk.text())
            have_duplicate_id, the_row = self.check_duplicate_listwidgetitems(self.lst_bulk, id_bulk)
            if not have_duplicate_id:
                self.lst_bulk.addItem(QListWidgetItem('%s' % id_bulk))
                # else:
                #     self.lst_bulk.item(the_row).setSelected(True)
        tbl.removeRow(row)

    def check_duplicate_listwidgetitems(self, lst, id_item):

        have_duplicate_id = False
        the_row = 0
        for row in range(lst.count()):
            item = lst.item(row)
            if int(item.text()) == id_item:
                have_duplicate_id = True
                the_row = row
                break
        return have_duplicate_id, the_row

    #######################################################################################

    def select_from_lst_existing(self):

        self.tbl_original.clearSelection()
        self.tbl_result.clearSelection()

        self.existing_lyr.selectionChanged.disconnect(self.select_from_layer_existing)
        self.existing_lyr.removeSelection()

        feat_ids_existing = []
        for index in self.lst_existing.selectionModel().selectedRows():
            item_existing = self.lst_existing.item(index.row())
            feat_ids_existing.append(int(item_existing.text()))

        self.existing_lyr.selectByIds(feat_ids_existing)

        self.existing_lyr.selectionChanged.connect(self.select_from_layer_existing)

        self.enable_btn_link()

    def select_from_lst_bulk(self):

        self.tbl_original.clearSelection()
        self.tbl_result.clearSelection()

        self.bulk_load_lyr.selectionChanged.disconnect(self.select_from_layer_bulk)
        self.bulk_load_lyr.removeSelection()

        feat_ids_bulk = []
        for index in self.lst_bulk.selectionModel().selectedRows():
            item_bulk = self.lst_bulk.item(index.row())
            feat_ids_bulk.append(int(item_bulk.text()))

        self.bulk_load_lyr.selectByIds(feat_ids_bulk)

        self.bulk_load_lyr.selectionChanged.connect(self.select_from_layer_bulk)

        self.enable_btn_link()

    def relink_selected_clicked(self):

        # lst_existing
        self.rows_lst_existing = []
        self.rows_lst_bulk = []
        for index in self.lst_existing.selectionModel().selectedRows():  # singleselection mode
            row_lst = index.row()
            self.remove_from_lst_existing_to_table(row_lst)
        rows_lst_existing1 = self.rows_lst_existing
        rows_lst_bulk1 = self.rows_lst_bulk

        for row in sorted(rows_lst_existing1, reverse=True):
            item = self.lst_existing.takeItem(row)
            self.lst_existing.removeItemWidget(item)

        self.lst_existing.clearSelection()

        # lst_bulk
        self.rows_lst_existing = []
        self.rows_lst_bulk = []
        for index in self.lst_bulk.selectionModel().selectedRows()[::-1]:
            row_lst = index.row()
            self.remove_from_lst_bulk_to_table(row_lst)
        rows_lst_existing2 = self.rows_lst_existing
        rows_lst_bulk2 = self.rows_lst_bulk

        for row in sorted(rows_lst_existing2, reverse=True):
            item = self.lst_existing.takeItem(row)
            self.lst_existing.removeItemWidget(item)

        for row in sorted(set(rows_lst_bulk1 + rows_lst_bulk2), reverse=True):
            item = self.lst_bulk.takeItem(row)
            self.lst_bulk.removeItemWidget(item)

        self.lst_bulk.clearSelection()
        self.btn_link.setEnabled(False)

    def relink_all_clicked(self):
        self.rows_lst_existing = []
        self.rows_lst_bulk = []

        for row in range(self.lst_existing.count())[::-1]:
            self.remove_from_lst_existing_to_table(row)
            item = self.lst_existing.takeItem(row)
            self.lst_existing.removeItemWidget(item)

        for row in range(self.lst_bulk.count())[::-1]:
            self.remove_from_lst_bulk_to_table(row)
            item = self.lst_bulk.takeItem(row)
            self.lst_bulk.removeItemWidget(item)

        self.btn_link.setEnabled(False)

        ##
        self.clear_layer_filter()

        self.btn_matched.setEnabled(True)
        self.btn_related.setEnabled(True)

    def remove_from_lst_existing_to_table(self, row_lst):
        tbl = self.tbl_original

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s"
        sql_matched_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE building_outline_id = %s"
        sql_removed = "SELECT * FROM buildings_bulk_load.removed WHERE building_outline_id = %s"

        if row_lst not in self.rows_lst_existing:

            self.rows_lst_existing.append(row_lst)

            id_existing = int(self.lst_existing.item(row_lst).text())

            result = db._execute(sql_related_existing, (id_existing,))
            ids_related = result.fetchall()
            if ids_related:
                count = 0
                for row in range(self.lst_bulk.count()):
                    id_bulk = int(self.lst_bulk.item(row).text())
                    if (id_bulk,) in ids_related:
                        count += 1
                        id_bulk_0 = id_bulk

                        self.rows_lst_bulk.append(row)

                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

                if count == 1:
                    result = db._execute(sql_related_bulk, (id_bulk_0,))
                    ids = result.fetchall()
                    for row in range(self.lst_existing.count()):
                        id_item_existing = int(self.lst_existing.item(row).text())
                        if (id_item_existing,) in ids:
                            if not row == row_lst:
                                self.rows_lst_existing.append(row)

                                row_tbl = tbl.rowCount()
                                tbl.setRowCount(row_tbl + 1)
                                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_item_existing))
                                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk_0))

            result = db._execute(sql_matched_existing, (id_existing,))
            id_matched = result.fetchone()
            if id_matched:
                for row in range(self.lst_bulk.count())[::-1]:
                    id_bulk = int(self.lst_bulk.item(row).text())
                    if id_bulk == id_matched[0]:
                        # self.rows_lst_existing.append(row_lst)
                        self.rows_lst_bulk.append(row)

                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

            result = db._execute(sql_removed, (id_existing,))
            if result.fetchone():
                # self.rows_lst_existing.append(row_lst)
                # self.rows_lst_bulk.append(None)

                row_tbl = tbl.rowCount()
                tbl.setRowCount(row_tbl + 1)
                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))

    def remove_from_lst_bulk_to_table(self, row_lst):
        tbl = self.tbl_original

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s"
        sql_matched_bulk = "SELECT building_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = %s"
        sql_added = "SELECT * FROM buildings_bulk_load.added WHERE bulk_load_outline_id = %s"

        if row_lst not in self.rows_lst_bulk:

            self.rows_lst_bulk.append(row_lst)

            id_bulk = int(self.lst_bulk.item(row_lst).text())

            result = db._execute(sql_related_bulk, (id_bulk,))
            ids_related = result.fetchall()
            if ids_related:
                count = 0
                for row in range(self.lst_existing.count()):
                    id_existing = int(self.lst_existing.item(row).text())
                    if (id_existing,) in ids_related:
                        count += 1
                        id_existing_0 = id_existing
                        self.rows_lst_existing.append(row)

                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

                if count == 1:
                    result = db._execute(sql_related_existing, (id_existing_0,))
                    ids = result.fetchall()
                    for row in range(self.lst_bulk.count()):
                        id_item_bulk = int(self.lst_bulk.item(row).text())
                        if (id_item_bulk,) in ids:
                            self.rows_lst_bulk.append(row)

                            row_tbl = tbl.rowCount()
                            tbl.setRowCount(row_tbl + 1)
                            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing_0))
                            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_item_bulk))

            result = db._execute(sql_matched_bulk, (id_bulk,))
            id_matched = result.fetchone()
            if id_matched:
                for row in range(self.lst_existing.count()):
                    id_existing = int(self.lst_existing.item(row).text())
                    if id_existing == id_matched[0]:
                        self.rows_lst_existing.append(row)

                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

            result = db._execute(sql_added, (id_bulk,))
            if result.fetchone():
                # self.rows_lst_existing.append(None)

                row_tbl = tbl.rowCount()
                tbl.setRowCount(row_tbl + 1)
                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

        # return self.rows_lst_existing, self.rows_lst_bulk

    def enable_btn_link(self):
        self.btn_link.setEnabled(False)
        for index in self.lst_existing.selectionModel().selectedRows():
            for index in self.lst_bulk.selectionModel().selectedRows():
                self.btn_link.setEnabled(True)

    def clear_selection2_clicked(self):
        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()
        self.btn_link.setEnabled(False)

##############################################################################

    def added_clicked(self):

        for index in self.lst_bulk.selectionModel().selectedRows():
            item_bulk = self.lst_bulk.item(index.row())
            item_bulk.setBackground(QColor('#E3ECEF'))
            id_bulk = int(item_bulk.text())

            if not self.lyr_added_bulk_load_in_edit.subsetString():
                self.lyr_added_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" = %s' % id_bulk)
            else:
                self.lyr_added_bulk_load_in_edit.setSubsetString(
                    self.lyr_added_bulk_load_in_edit.subsetString() + ' or "bulk_load_outline_id" = %s' % id_bulk)

            self.remove_features_from_layer_bulk(id_bulk)

            item_bulk.setFlags(Qt.NoItemFlags)

        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

    def removed_clicked(self):

        for index in self.lst_existing.selectionModel().selectedRows():
            item_existing = self.lst_existing.item(index.row())
            item_existing.setBackground(QColor('#E3ECEF'))
            id_existing = int(item_existing.text())

            if not self.lyr_removed_existing_in_edit.subsetString():
                self.lyr_removed_existing_in_edit.setSubsetString('"building_outline_id" = %s' % id_existing)
            else:
                self.lyr_removed_existing_in_edit.setSubsetString(
                    self.lyr_removed_existing_in_edit.subsetString() + ' or "building_outline_id" = %s' % id_existing)

            self.remove_features_from_layer_existing(id_existing)

            item_existing.setFlags(Qt.NoItemFlags)

        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

    def matched_clicked(self):

        rows_lst_existing = [index.row() for index in self.lst_existing.selectionModel().selectedRows()]
        rows_lst_bulk = [index.row() for index in self.lst_bulk.selectionModel().selectedRows()]

        if len(rows_lst_bulk) == 1 and len(rows_lst_existing) == 1:

            item_existing = self.lst_existing.item(rows_lst_existing[0])
            item_existing.setBackground(QColor('#E3ECEF'))
            id_existing = int(item_existing.text())

            self.lyr_matched_existing_in_edit.setSubsetString('"building_outline_id" = %s' % id_existing)
            item_existing.setFlags(Qt.NoItemFlags)

            item_bulk = self.lst_bulk.item(rows_lst_bulk[0])
            item_bulk.setBackground(QColor('#E3ECEF'))
            id_bulk = int(item_bulk.text())

            self.lyr_matched_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" = %s' % id_bulk)
            item_bulk.setFlags(Qt.NoItemFlags)

            ##
            ids_added = re.findall('\d+', self.lyr_added_bulk_load_in_edit.subsetString())
            for id_added in ids_added:
                if int(id_added) == id_bulk:
                    self.lyr_added_bulk_load_in_edit.setSubsetString(
                        '(' + self.lyr_added_bulk_load_in_edit.subsetString() + ') and "bulk_load_outline_id" != %s' % id_bulk)

            ids_removed = re.findall('\d+', self.lyr_removed_existing_in_edit.subsetString())
            for id_removed in ids_removed:
                if int(id_removed) == id_existing:
                    self.lyr_removed_existing_in_edit.setSubsetString(
                        '(' + self.lyr_removed_existing_in_edit.subsetString() + ') and "building_outline_id" != %s' % id_existing)

            self.remove_features_from_layer_existing(id_existing)
            self.remove_features_from_layer_bulk(id_bulk)

            self.btn_matched.setEnabled(False)

        else:
            iface.messageBar().pushMessage("Error:", "Do not match other than one building in each layer", level=QgsMessageBar.WARNING)

        self.lst_bulk.clearSelection()
        self.lst_existing.clearSelection()

    def related_clicked(self):

        rows_lst_existing = [index.row() for index in self.lst_existing.selectionModel().selectedRows()]
        rows_lst_bulk = [index.row() for index in self.lst_bulk.selectionModel().selectedRows()]

        if len(rows_lst_bulk) < 1 or len(rows_lst_existing) < 1:
            iface.messageBar().pushMessage("Error:", "Do not relate less than one building in each layer", level=QgsMessageBar.WARNING)
            self.btn_related.setEnabled(True)
        elif len(rows_lst_bulk) == 1 and len(rows_lst_existing) == 1:
            iface.messageBar().pushMessage("Error:", "Do not relate only one building in each layer", level=QgsMessageBar.WARNING)
            self.btn_related.setEnabled(True)
        else:
            # ids_existing = []
            # ids_bulk = []
            for index in self.lst_existing.selectionModel().selectedRows():
                item_existing = self.lst_existing.item(index.row())
                item_existing.setBackground(QColor('#E3ECEF'))
                id_existing = int(item_existing.text())
                # ids_existing.append(id_existing)

                self.lyr_related_existing_in_edit.setSubsetString(
                    self.lyr_related_existing_in_edit.subsetString() + ' or "building_outline_id" = %s' % id_existing)

                ids_removed = re.findall('\d+', self.lyr_removed_existing_in_edit.subsetString())
                for id_removed in ids_removed:
                    if int(id_removed) == id_existing:
                        self.lyr_removed_existing_in_edit.setSubsetString(
                            '(' + self.lyr_removed_existing_in_edit.subsetString() + ') and "building_outline_id" != %s' % id_existing)

                self.remove_features_from_layer_existing(id_existing)

                item_existing.setFlags(Qt.NoItemFlags)

            for index in self.lst_bulk.selectionModel().selectedRows():
                item_bulk = self.lst_bulk.item(index.row())
                item_bulk.setBackground(QColor('#E3ECEF'))
                id_bulk = int(item_bulk.text())
                # ids_bulk.append(id_bulk)

                self.lyr_related_bulk_load_in_edit.setSubsetString(
                    self.lyr_related_bulk_load_in_edit.subsetString() + ' or "bulk_load_outline_id" = %s' % id_bulk)

                ids_added = re.findall('\d+', self.lyr_added_bulk_load_in_edit.subsetString())
                for id_added in ids_added:
                    if int(id_added) == id_bulk:
                        self.lyr_added_bulk_load_in_edit.setSubsetString(
                            '(' + self.lyr_added_bulk_load_in_edit.subsetString() + ') and "bulk_load_outline_id" != %s' % id_bulk)

                self.remove_features_from_layer_bulk(id_bulk)

                item_bulk.setFlags(Qt.NoItemFlags)

            '''
            if len(ids_existing) > 1:
                self.lyr_related_existing_in_edit.setSubsetString('"building_outline_id" in {}'.format(tuple(ids_existing)))
            elif len(ids_existing) == 1:
                self.lyr_related_existing_in_edit.setSubsetString('"building_outline_id" = {}'.format(ids_existing[0]))

            if len(ids_bulk) > 1:
                self.lyr_related_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" in {}'.format(tuple(ids_bulk)))
            elif len(ids_bulk) == 1:
                self.lyr_related_bulk_load_in_edit.setSubsetString('"bulk_load_outline_id" = {}'.format(ids_bulk[0]))
            '''
            self.btn_related.setEnabled(False)

        self.lst_bulk.clearSelection()
        self.lst_existing.clearSelection()

    def remove_features_from_layer_bulk(self, id_bulk):
        #
        if not self.lyr_added_bulk_load.subsetString():
            self.lyr_added_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_added_bulk_load.setSubsetString(
                self.lyr_added_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

        #
        if not self.lyr_matched_bulk_load.subsetString():
            self.lyr_matched_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_matched_bulk_load.setSubsetString(
                self.lyr_matched_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

        #
        if not self.lyr_related_bulk_load.subsetString():
            self.lyr_related_bulk_load.setSubsetString('"bulk_load_outline_id" != %s' % id_bulk)
        else:
            self.lyr_related_bulk_load.setSubsetString(
                self.lyr_related_bulk_load.subsetString() + ' and "bulk_load_outline_id" != %s' % id_bulk)

    def remove_features_from_layer_existing(self, id_existing):
        #
        if not self.lyr_removed_existing.subsetString():
            self.lyr_removed_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_removed_existing.setSubsetString(
                self.lyr_removed_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

        #
        if not self.lyr_matched_existing.subsetString():
            self.lyr_matched_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_matched_existing.setSubsetString(
                self.lyr_matched_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

        #
        if not self.lyr_related_existing.subsetString():
            self.lyr_related_existing.setSubsetString('"building_outline_id" != %s' % id_existing)
        else:
            self.lyr_related_existing.setSubsetString(
                self.lyr_related_existing.subsetString() + ' and "building_outline_id" != %s' % id_existing)

    def link_clicked(self):

        tbl = self.tbl_result

        index = self.lst_existing.selectionModel().selectedRows()[0]  # singleselection mode
        item_existing = self.lst_existing.item(index.row())
        item_existing.setBackground(QColor('#E3ECEF'))
        id_existing = int(item_existing.text())

        index = self.lst_bulk.selectionModel().selectedRows()[0]
        item_bulk = self.lst_bulk.item(index.row())
        item_bulk.setBackground(QColor('#E3ECEF'))
        id_bulk = int(item_bulk.text())

        row_tbl = tbl.rowCount()
        tbl.setRowCount(row_tbl + 1)
        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
        tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))

        self.btn_relink_all.setEnabled(False)
        self.btn_relink_slt.setEnabled(False)

    def select_from_tbl_result_existing(self):
        self.tbl_original.clearSelection()
        self.lst_existing.clearSelection()

        self.existing_lyr.selectionChanged.disconnect(self.select_from_layer_existing)
        self.existing_lyr.removeSelection()

        feat_ids_existing = []
        for index in self.tbl_result.selectionModel().selectedRows():
            item_existing = self.tbl_result.item(index.row(), 0)
            if item_existing:
                feat_ids_existing.append(int(item_existing.text()))

        self.existing_lyr.selectByIds(feat_ids_existing)

        self.existing_lyr.selectionChanged.connect(self.select_from_layer_existing)

    def select_from_tbl_result_bulk(self):
        self.tbl_original.clearSelection()
        self.lst_bulk.clearSelection()

        self.bulk_load_lyr.selectionChanged.disconnect(self.select_from_layer_bulk)
        self.bulk_load_lyr.removeSelection()

        feat_ids_bulk = []
        for index in self.tbl_result.selectionModel().selectedRows():
            item_bulk = self.tbl_result.item(index.row(), 1)
            if item_bulk:
                feat_ids_bulk.append(int(item_bulk.text()))

        self.bulk_load_lyr.selectByIds(feat_ids_bulk)

        self.bulk_load_lyr.selectionChanged.connect(self.select_from_layer_bulk)

    def reunlink_selected_clicked(self):
        tbl = self.tbl_result

        for index in tbl.selectionModel().selectedRows()[::-1]:

            id_existing = int(tbl.item(index.row(), 0).text())
            id_bulk = int(tbl.item(index.row(), 1).text())

            # remove the highlight from items on lst_existing
            keep_highlight_existing = False
            keep_highlight_bulk = False
            for row in range(tbl.rowCount()):
                if row == index.row():
                    continue
                if int(tbl.item(row, 0).text()) == id_existing:
                    keep_highlight_existing = True
                if int(tbl.item(row, 1).text()) == id_bulk:
                    keep_highlight_bulk = True

            if not keep_highlight_existing:
                for row in range(self.lst_existing.count()):
                    item = self.lst_existing.item(row)
                    if int(item.text()) == id_existing:
                        item.setBackground(QColor(Qt.white))

            if not keep_highlight_bulk:
                for row in range(self.lst_bulk.count()):
                    item = self.lst_bulk.item(row)
                    if int(item.text()) == id_bulk:
                        item.setBackground(QColor(Qt.white))

            tbl.removeRow(index.row())

        self.enable_btn_relink()

        ##

    def reunlink_all_clicked(self):
        tbl = self.tbl_result

        for row in range(tbl.rowCount())[::-1]:
            tbl.removeRow(row)

        for row in range(self.lst_existing.count()):
            item = self.lst_existing.item(row)
            item.setBackground(QColor(Qt.white))

        for row in range(self.lst_bulk.count()):
            item = self.lst_bulk.item(row)
            item.setBackground(QColor(Qt.white))

        self.btn_relink_all.setEnabled(True)
        self.btn_relink_slt.setEnabled(True)

    def enable_btn_relink(self):
        have_highlight_existing = False
        have_highlight_bulk = False

        for row in range(self.lst_existing.count()):
            item = self.lst_existing.item(row)
            if item.background().color() == QColor('#E3ECEF'):
                have_highlight_existing = True
        for row in range(self.lst_bulk.count()):
            item = self.lst_bulk.item(row)
            if item.background().color() == QColor('#E3ECEF'):
                have_highlight_bulk = True

        if not (have_highlight_existing or have_highlight_bulk):
            self.btn_relink_all.setEnabled(True)
            self.btn_relink_slt.setEnabled(True)

    def save_clicked(self):

        sql_related_existing = '''DELETE FROM buildings_bulk_load.related
                                  WHERE building_outline_id = %s;
                                  '''
        sql_related_bulk = '''DELETE FROM buildings_bulk_load.related
                              WHERE bulk_load_outline_id = %s;
                              '''
        sql_matched_existing = '''DELETE FROM buildings_bulk_load.matched
                                  WHERE building_outline_id = %s;
                                  '''
        sql_matched_bulk = '''DELETE FROM buildings_bulk_load.matched
                              WHERE bulk_load_outline_id = %s;
                              '''
        sql_removed = '''DELETE FROM buildings_bulk_load.removed
                         WHERE building_outline_id = %s;
                         '''
        sql_added = '''DELETE FROM buildings_bulk_load.added
                       WHERE bulk_load_outline_id = %s;
                       '''

        sql_new_added = '''INSERT INTO buildings_bulk_load.added
                            VALUES (%s, 1);
                            '''

        sql_new_removed = '''INSERT INTO buildings_bulk_load.removed
                            VALUES (%s, 1);
                            '''

        sql_new_matched = '''INSERT INTO buildings_bulk_load.matched(bulk_load_outline_id
                                                                   , building_outline_id
                                                                   , qa_status_id
                                                                   , area_bulk_load
                                                                   , area_existing
                                                                   , percent_area_difference
                                                                   , area_overlap
                                                                   , percent_bulk_load_overlap
                                                                   , percent_existing_overlap
                                                                   , hausdorff_distance)
                             SELECT supplied.bulk_load_outline_id,
                                    current.building_outline_id,
                                    1,
                                    ST_Area(supplied.shape),
                                    ST_Area(current.shape),
                                    @(ST_Area(current.shape) - ST_Area(supplied.shape)) / ST_Area(current.shape) * 100,
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)),
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) * 100 ,
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) * 100,
                                    ST_HausdorffDistance(supplied.shape, current.shape)
                             FROM buildings_bulk_load.bulk_load_outlines supplied,
                                  buildings_bulk_load.existing_subset_extracts current
                             WHERE supplied.bulk_load_outline_id = %s and current.building_outline_id = %s;

                            '''

        sql_refresh = '''CREATE OR REPLACE VIEW buildings_bulk_load.added_outlines AS
                            SELECT a.bulk_load_outline_id, b.shape
                            FROM buildings_bulk_load.added a
                            JOIN buildings_bulk_load.bulk_load_outlines b USING (bulk_load_outline_id);

                        CREATE OR REPLACE VIEW buildings_bulk_load.removed_outlines AS
                            SELECT r.building_outline_id, e.shape
                            FROM buildings_bulk_load.removed r
                            JOIN buildings_bulk_load.existing_subset_extracts e USING (building_outline_id);

                        CREATE OR REPLACE VIEW buildings_bulk_load.matched_bulk_load_outlines AS
                            SELECT m.bulk_load_outline_id, b.shape
                            FROM buildings_bulk_load.matched m
                            JOIN buildings_bulk_load.bulk_load_outlines b USING (bulk_load_outline_id);

                        CREATE OR REPLACE VIEW buildings_bulk_load.related_bulk_load_outlines AS
                            SELECT DISTINCT r.bulk_load_outline_id, b.shape
                            FROM buildings_bulk_load.related r
                            JOIN buildings_bulk_load.bulk_load_outlines b USING (bulk_load_outline_id);

                        CREATE OR REPLACE VIEW buildings_bulk_load.matched_existing_outlines AS
                            SELECT m.building_outline_id, e.shape
                            FROM buildings_bulk_load.matched m
                            JOIN buildings_bulk_load.existing_subset_extracts e USING (building_outline_id);

                        CREATE OR REPLACE VIEW buildings_bulk_load.related_existing_outlines AS
                            SELECT DISTINCT r.building_outline_id, e.shape
                            FROM buildings_bulk_load.related r
                            JOIN buildings_bulk_load.existing_subset_extracts e USING (building_outline_id);
                        '''

        for row in range(self.lst_existing.count())[::-1]:
            item = self.lst_existing.item(row)
            id_existing = int(item.text())

            db._execute(sql_removed, (id_existing, ))
            db._execute(sql_matched_existing, (id_existing, ))
            db._execute(sql_related_existing, (id_existing, ))

            if not item.background().color() == QColor('#E3ECEF'):
                db._execute(sql_new_removed, (id_existing, ))

        for row in range(self.lst_bulk.count())[::-1]:
            item = self.lst_bulk.item(row)
            id_bulk = int(item.text())

            db._execute(sql_added, (id_bulk, ))
            db._execute(sql_matched_bulk, (id_bulk, ))
            db._execute(sql_related_bulk, (id_bulk, ))

            if not item.background().color() == QColor('#E3ECEF'):
                db._execute(sql_new_added, (id_bulk, ))

        # added
        for feat in self.lyr_added_bulk_load_in_edit.getFeatures():
            id_bulk = feat['bulk_load_outline_id']
            db._execute(sql_new_added, (id_bulk,))

        # removed
        for feat in self.lyr_removed_existing_in_edit.getFeatures():
            id_existing = feat['building_outline_id']
            db._execute(sql_new_removed, (id_existing, ))

        # matched
        for feat1 in self.lyr_matched_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_matched_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                db._execute(sql_new_matched, (id_bulk, id_existing))

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.clear_layer_filter()

        self.btn_matched.setEnabled(True)
        self.btn_related.setEnabled(True)

        # refresh relationship view
        db._execute(sql_refresh)

        iface.mapCanvas().refreshAllLayers()

    def cancel_clicked(self):
        """
        Called when cancel button is clicked
        """
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

        self.existing_lyr.removeSelection()
        self.bulk_load_lyr.removeSelection()

        try:
            self.existing_lyr.selectionChanged.disconnect(self.select_from_layer_existing)
            self.existing_lyr.selectionChanged.disconnect(self.highlight_features)
            self.bulk_load_lyr.selectionChanged.disconnect(self.select_from_layer_bulk)
            self.bulk_load_lyr.selectionChanged.disconnect(self.highlight_features)
            self.tbl_original.itemSelectionChanged.disconnect(self.select_from_tbl_original)
            self.lst_existing.itemSelectionChanged.disconnect(self.select_from_lst_existing)
            self.lst_bulk.itemSelectionChanged.disconnect(self.select_from_lst_bulk)
            # self.tbl_result.itemSelectionChanged.disconnect(self.select_from_tbl_result_existing)
            # self.tbl_result.itemSelectionChanged.disconnect(self.select_from_tbl_result_bulk)
        except TypeError:
            pass
        self.clear_layer_filter()

        self.remove_building_lyrs()

    #####################
    def save_clicked2(self):
        """
        Called when save button is clicked
        """
        tbl = self.tbl_result

        sql_related_existing = '''DELETE FROM buildings_bulk_load.related
                                  WHERE building_outline_id = %s;
                                  '''
        sql_related_bulk = '''DELETE FROM buildings_bulk_load.related
                              WHERE bulk_load_outline_id = %s;
                              '''
        sql_matched_existing = '''DELETE FROM buildings_bulk_load.matched
                                  WHERE building_outline_id = %s;
                                  '''
        sql_matched_bulk = '''DELETE FROM buildings_bulk_load.matched
                              WHERE bulk_load_outline_id = %s;
                              '''
        sql_removed = '''DELETE FROM buildings_bulk_load.removed
                         WHERE building_outline_id = %s;
                         '''
        sql_added = '''DELETE FROM buildings_bulk_load.added
                       WHERE bulk_load_outline_id = %s;
                       '''
        sql_new_removed = '''INSERT INTO buildings_bulk_load.removed
                            VALUES (%s, 1);
                            '''
        sql_new_added = '''INSERT INTO buildings_bulk_load.added
                            VALUES (%s, 1);
                            '''
        sql_new_matched = '''INSERT INTO buildings_bulk_load.matched(bulk_load_outline_id
                                                                   , building_outline_id
                                                                   , qa_status_id
                                                                   , area_bulk_load
                                                                   , area_existing
                                                                   , percent_area_difference
                                                                   , area_overlap
                                                                   , percent_bulk_load_overlap
                                                                   , percent_existing_overlap
                                                                   , hausdorff_distance)
                             SELECT supplied.bulk_load_outline_id,
                                    current.building_outline_id,
                                    1,
                                    ST_Area(supplied.shape),
                                    ST_Area(current.shape),
                                    @(ST_Area(current.shape) - ST_Area(supplied.shape)) / ST_Area(current.shape) * 100,
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)),
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) * 100 ,
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) * 100,
                                    ST_HausdorffDistance(supplied.shape, current.shape)
                             FROM buildings_bulk_load.bulk_load_outlines supplied,
                                  buildings_bulk_load.existing_subset_extracts current
                             WHERE supplied.bulk_load_outline_id = %s and current.building_outline_id = %s;

                            '''
        ##
        sql_new_related = '''INSERT INTO buildings_bulk_load.related(bulk_load_outline_id
                                                                   , building_outline_id
                                                                   , qa_status_id
                                                                   , area_bulk_load
                                                                   , area_existing
                                                                   , area_overlap
                                                                   , percent_bulk_load_overlap
                                                                   , percent_existing_overlap
                                                                   , total_area_bulk_load_overlap
                                                                   , total_area_existing_overlap
                                                                   , total_percent_bulk_load_overlap
                                                                   , total_percent_existing_overlap)
                             SELECT supplied.bulk_load_outline_id,
                                    current.building_outline_id,
                                    1,
                                    ST_Area(supplied.shape),
                                    ST_Area(current.shape),
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)),
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) * 100,
                                    ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) * 100,

                            '''

        sql_new_related = '''INSERT INTO buildings_bulk_load.related(bulk_load_outline_id, building_outline_id)
                             VALUES (%s, %s)
                            '''

        for row in range(self.lst_existing.count())[::-1]:
            item = self.lst_existing.item(row)
            id_existing = int(item.text())

            db._execute(sql_related_existing, (id_existing, ))
            db._execute(sql_matched_existing, (id_existing, ))
            db._execute(sql_removed, (id_existing, ))

            if not item.background().color() == QColor('#E3ECEF'):
                db._execute(sql_new_removed, (id_existing, ))

        for row in range(self.lst_bulk.count())[::-1]:
            item = self.lst_bulk.item(row)
            id_bulk = int(item.text())

            db._execute(sql_related_bulk, (id_bulk, ))
            db._execute(sql_matched_bulk, (id_bulk, ))
            db._execute(sql_added, (id_bulk, ))

            if not item.background().color() == QColor('#E3ECEF'):
                db._execute(sql_new_added, (id_bulk, ))

        ids_existing = []
        ids_bulk = []
        for row in range(tbl.rowCount())[::-1]:
            ids_existing.append(int(tbl.item(row, 0).text()))
            ids_bulk.append(int(tbl.item(row, 1).text()))

        for row in range(tbl.rowCount())[::-1]:
            id_existing = int(tbl.item(row, 0).text())
            id_bulk = int(tbl.item(row, 1).text())

            if ids_existing.count(id_existing) > 1 or ids_bulk.count(id_bulk) > 1:
                db._execute(sql_new_related, (id_bulk, id_existing))
            else:
                db._execute(sql_new_matched, (id_bulk, id_existing))

            tbl.removeRow(row)
        self.lst_existing.clear()
        self.lst_bulk.clear()

    '''
    def select_from_tbl_original_existing(self):
        self.lst_existing.clearSelection()
        self.tbl_result.clearSelection()

        self.existing_lyr.selectionChanged.disconnect(self.select_from_layer_existing)
        self.existing_lyr.removeSelection()

        feat_ids_existing = []
        for index in self.tbl_original.selectionModel().selectedRows():
            item_existing = self.tbl_original.item(index.row(), 0)
            if item_existing:
                feat_ids_existing.append(int(item_existing.text()))

        self.existing_lyr.selectByIds(feat_ids_existing)

        self.existing_lyr.selectionChanged.connect(self.select_from_layer_existing)

        self.enable_btn_unlink_selected()

    def select_from_tbl_original_bulk(self):

        self.lst_bulk.clearSelection()
        self.tbl_result.clearSelection()

        self.bulk_load_lyr.selectionChanged.disconnect(self.select_from_layer_bulk)
        self.bulk_load_lyr.removeSelection()

        feat_ids_bulk = []
        for index in self.tbl_original.selectionModel().selectedRows():
            item_bulk = self.tbl_original.item(index.row(), 1)
            if item_bulk:
                feat_ids_bulk.append(int(item_bulk.text()))

        self.bulk_load_lyr.selectByIds(feat_ids_bulk)

        self.bulk_load_lyr.selectionChanged.connect(self.select_from_layer_bulk)

        self.enable_btn_unlink_selected()
    '''
