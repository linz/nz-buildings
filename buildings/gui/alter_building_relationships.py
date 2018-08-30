# -*- coding: utf-8 -*-

import os.path

from qgis.utils import iface, plugins
from qgis.gui import QgsMessageBar, QgsHighlight

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QListWidgetItem, QAbstractItemView, QTableWidgetItem, QHeaderView, QColor
from PyQt4.QtCore import Qt, pyqtSlot

from buildings.utilities import database as db

from functools import partial
import re

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "alter_building_relationship.ui"))


class AlterRelationships(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, current_dataset, parent=None):
        """Constructor."""
        super(AlterRelationships, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.layer_registry = layer_registry

        self.current_dataset = current_dataset

        self.open_alter_relationship_frame()

        # set up signals and slots
        self.btn_clear_slt.clicked.connect(
            partial(self.clear_selection_clicked, [self.tbl_original]))
        self.btn_remove_slt.clicked.connect(self.remove_selected_clicked)
        self.btn_remove_all.clicked.connect(self.remove_all_clicked)

        self.btn_unlink_all.clicked.connect(self.unlink_all_clicked)

        self.btn_clear_slt2.clicked.connect(
            partial(self.clear_selection_clicked,
                    [self.lst_existing, self.lst_bulk]))
        self.btn_relink_all.clicked.connect(self.relink_all_clicked)

        self.btn_matched.clicked.connect(self.matched_clicked)
        self.btn_related.clicked.connect(self.related_clicked)

        self.btn_save.clicked.connect(
            partial(self.save_clicked, commit_status=True))
        self.btn_cancel.clicked.connect(self.cancel_clicked)

        self.dockwidget = plugins['buildings'].dockwidget
        self.dockwidget.closed.connect(self.on_dockwidget_closed)

    def open_alter_relationship_frame(self):
        """Called when opening of the frame"""

        # set selected item color as transparent
        iface.mapCanvas().setSelectionColor(QColor("Transparent"))

        self.init_table(self.tbl_original)
        self.init_list(self.lst_existing)
        self.init_list(self.lst_bulk)

        self.add_building_lyrs()
        self.clear_layer_filter()

        iface.setActiveLayer(self.lyr_bulk_load)
        iface.actionSelectRectangle().trigger()

        self.lst_highlight = []

        self.lyr_existing.removeSelection()
        self.lyr_existing.selectionChanged.connect(self.select_from_layer)

        self.lyr_bulk_load.removeSelection()
        self.lyr_bulk_load.selectionChanged.connect(self.select_from_layer)

        self.tbl_original.itemSelectionChanged.connect(self.select_from_tbl_original)

        self.lst_existing.itemSelectionChanged.connect(self.select_from_lst)
        self.lst_bulk.itemSelectionChanged.connect(self.select_from_lst)

    def on_dockwidget_closed(self):
        """Remove highlight when the dockwideget closes"""
        self.lst_highlight = []

    def add_building_lyrs(self):
        """ Add building layers """

        self.layer_registry.remove_all_layers()

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles/')

        self.lyr_existing = self.layer_registry.add_postgres_layer(
            "existing_subset_extracts", "existing_subset_extracts", "shape",
            "buildings_bulk_load", "building_outline_id",
            "supplied_dataset_id = {0}".format(self.current_dataset)
        )
        self.lyr_existing.loadNamedStyle(path + 'building_transparent.qml')

        self.lyr_bulk_load = self.layer_registry.add_postgres_layer(
            "bulk_load_outlines", "bulk_load_outlines", "shape",
            "buildings_bulk_load", "bulk_load_outline_id",
            "supplied_dataset_id = {0}".format(self.current_dataset)
        )
        self.lyr_bulk_load.loadNamedStyle(path + 'building_transparent.qml')

        self.lyr_related_bulk_load = self.layer_registry.add_postgres_layer(
            "related_bulk_load_outlines", "related_bulk_load_outlines",
            "shape", "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_related_bulk_load.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_related_existing = self.layer_registry.add_postgres_layer(
            "related_existing_outlines", "related_existing_outlines",
            "shape", "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_related_existing.loadNamedStyle(path + 'building_purple.qml')

        self.lyr_matched_bulk_load = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_outlines", "matched_bulk_load_outlines",
            "shape", "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_matched_bulk_load.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_matched_existing = self.layer_registry.add_postgres_layer(
            "matched_existing_outlines", "matched_existing_outlines", "shape",
            "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_matched_existing.loadNamedStyle(path + 'building_blue.qml')

        self.lyr_removed_existing = self.layer_registry.add_postgres_layer(
            "removed_outlines", "removed_outlines", "shape",
            "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_removed_existing.loadNamedStyle(path + 'building_red.qml')

        self.lyr_added_bulk_load = self.layer_registry.add_postgres_layer(
            "added_outlines", "added_outlines", "shape",
            "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_added_bulk_load.loadNamedStyle(path + 'building_green.qml')

        self.lyr_related_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "related_bulk_load_in_edit", "bulk_load_outlines", "shape",
            "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_related_bulk_load_in_edit.loadNamedStyle(
            path + 'building_purple.qml')

        self.lyr_related_existing_in_edit = self.layer_registry.add_postgres_layer(
            "related_existing_in_edit", "existing_subset_extracts", "shape",
            "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_related_existing_in_edit.loadNamedStyle(
            path + 'building_purple.qml')

        self.lyr_matched_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_in_edit", "bulk_load_outlines", "shape",
            "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_matched_bulk_load_in_edit.loadNamedStyle(
            path + 'building_blue.qml')

        self.lyr_matched_existing_in_edit = self.layer_registry.add_postgres_layer(
            "matched_existing_in_edit", "existing_subset_extracts", "shape",
            "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_matched_existing_in_edit.loadNamedStyle(
            path + 'building_blue.qml')

        self.lyr_removed_existing_in_edit = self.layer_registry.add_postgres_layer(
            "removed_existing_in_edit", "existing_subset_extracts", "shape",
            "buildings_bulk_load", "building_outline_id", ""
        )
        self.lyr_removed_existing_in_edit.loadNamedStyle(
            path + 'building_red.qml')

        self.lyr_added_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "added_bulk_load_in_edit", "bulk_load_outlines", "shape",
            "buildings_bulk_load", "bulk_load_outline_id", ""
        )
        self.lyr_added_bulk_load_in_edit.loadNamedStyle(
            path + 'building_green.qml')

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

        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Existing Outlines"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("Bulk Load Outlines"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.MultiSelection)

        tbl.setShowGrid(True)
        # tbl.setSortingEnabled(True)

    def init_list(self, lst):
        """ Initiates list """

        lst.clearSelection()
        lst.setSelectionMode(QAbstractItemView.MultiSelection)
        # lst.setSortingEnabled(True)

    def highlight_features(self):
        """ Highlights selected features"""

        # remove all highlight objects
        self.lst_highlight = []

        for feat in self.lyr_existing.selectedFeatures():
            h = QgsHighlight(iface.mapCanvas(), feat.geometry(), self.lyr_existing)

            # set highlight symbol properties
            h.setColor(QColor(255, 255, 0, 255))
            h.setWidth(4)
            h.setFillColor(QColor(255, 255, 255, 0))
            self.lst_highlight.append(h)

        for feat in self.lyr_bulk_load.selectedFeatures():
            h = QgsHighlight(iface.mapCanvas(), feat.geometry(), self.lyr_bulk_load)

            # set highlight symbol properties
            h.setColor(QColor(255, 255, 0, 255))
            h.setWidth(4)
            h.setFillColor(QColor(255, 255, 255, 0))
            self.lst_highlight.append(h)

    @pyqtSlot(int)
    def select_from_layer(self, selected):
        """
        When user selects features in existing outline layers, the ids will be added to the table
        """
        current_layer = self.sender()

        tbl = self.tbl_original

        tbl.itemSelectionChanged.disconnect(self.select_from_tbl_original)
        tbl.clearSelection()

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s;"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s;"

        sql_matched_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE building_outline_id = %s;"
        sql_removed = "SELECT building_outline_id FROM buildings_bulk_load.removed WHERE building_outline_id = %s;"

        sql_matched_bulk = "SELECT building_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = %s;"
        sql_added = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = %s;"

        if current_layer.name() == 'existing_subset_extracts':
            for feat_id in selected:
                result1 = self.db._execute(sql_related_existing, (feat_id,))
                feat_ids_related = result1.fetchall()
                if feat_ids_related:
                    # remove the current items inside table
                    for row_tbl in range(tbl.rowCount())[::-1]:  # reverse list so item could be removed from the bottom
                        tbl.removeRow(row_tbl)

                    ids_bulk = []
                    ids_existing = [feat_id]
                    for (feat_id_related,) in feat_ids_related:
                        ids_bulk.append(feat_id_related)
                        result = self.db._execute(
                            sql_related_bulk, (feat_id_related,))
                        ids = result.fetchall()
                        for (id_existing, ) in ids:
                            ids_existing.append(id_existing)

                    for id_existing in list(set(ids_existing)):
                        for id_bulk in list(set(ids_bulk)):
                            row_tbl = tbl.rowCount()
                            tbl.setRowCount(row_tbl + 1)
                            tbl.setItem(
                                row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                            tbl.setItem(
                                row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                    continue

                result2 = self.db._execute(sql_matched_existing, (feat_id,))
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

                result3 = self.db._execute(sql_removed, (feat_id,))
                if result3.fetchone:
                    # remove the currrent items if they are not from added or removed table
                    for row_tbl in range(tbl.rowCount())[::-1]:
                        item_existing = tbl.item(row_tbl, 0)
                        item_bulk = tbl.item(row_tbl, 1)
                        if item_existing and item_bulk:
                            tbl.removeRow(row_tbl)
                    # add the removed building ids into table where not duplicate
                    have_duplicate_row = self.check_duplicate_rows(feat_id, None)
                    if not have_duplicate_row:
                        row_tbl = tbl.rowCount()
                        tbl.setRowCount(row_tbl + 1)
                        tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id))

        elif current_layer.name() == 'bulk_load_outlines':
            for feat_id in selected:
                result1 = self.db._execute(sql_related_bulk, (feat_id,))
                feat_ids_related = result1.fetchall()
                if feat_ids_related:
                    # remove the current items inside table
                    for row_tbl in range(tbl.rowCount())[::-1]:
                        tbl.removeRow(row_tbl)

                    ids_bulk = [feat_id]
                    ids_existing = []
                    for (feat_id_related,) in feat_ids_related:
                        ids_existing.append(feat_id_related)
                        result = self.db._execute(
                            sql_related_existing, (feat_id_related,))
                        ids = result.fetchall()
                        for (id_bulk, ) in ids:
                            ids_bulk.append(id_bulk)

                    for id_existing in list(set(ids_existing)):
                        for id_bulk in list(set(ids_bulk)):
                            row_tbl = tbl.rowCount()
                            tbl.setRowCount(row_tbl + 1)
                            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                    continue

                result2 = self.db._execute(sql_matched_bulk, (feat_id,))
                feat_id_matched = result2.fetchone()
                if feat_id_matched:
                    # remove the current items inside table
                    for row_tbl in range(tbl.rowCount())[::-1]:
                        tbl.removeRow(row_tbl)
                    # add the matched building ids into table
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % feat_id_matched[0]))
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id))
                    continue

                result3 = self.db._execute(sql_added, (feat_id,))
                if result3.fetchone:
                    # if the current items are not from added or removed table, remove them
                    for row_tbl in range(tbl.rowCount())[::-1]:
                        item_existing = tbl.item(row_tbl, 0)
                        item_bulk = tbl.item(row_tbl, 1)
                        if item_existing and item_bulk:
                            tbl.removeRow(row_tbl)
                # add the added building ids into table where not duplicate
                have_duplicate_row = self.check_duplicate_rows(None, feat_id)
                if not have_duplicate_row:
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % feat_id))

        # set item not editable
        for row in range(tbl.rowCount()):
            tbl.showRow(row)
            for col in range(2):
                if tbl.item(row, col):
                    tbl.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        tbl.itemSelectionChanged.connect(self.select_from_tbl_original)
        tbl.selectAll()

    def check_duplicate_rows(self, feat_id_existing, feat_id_bulk):
        """
        Check if table has the same row
        """
        tbl = self.tbl_original
        have_duplicate_row = False
        for row in range(tbl.rowCount()):
            item_existing = tbl.item(row, 0)
            item_bulk = tbl.item(row, 1)
            if item_existing:
                if item_bulk:
                    if int(item_existing.text()) == feat_id_existing and int(item_bulk.text()) == feat_id_bulk:
                        have_duplicate_row = True
                else:
                    if int(item_existing.text()) == feat_id_existing:
                        have_duplicate_row = True
            else:
                if item_bulk:
                    if int(item_bulk.text()) == feat_id_bulk:
                        have_duplicate_row = True
        return have_duplicate_row

    @pyqtSlot()
    def select_from_tbl_original(self):
        """
        When users select rows in table, select the corresponding features in layers.
        """
        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()

        self.lyr_existing.selectionChanged.disconnect(self.select_from_layer)
        self.lyr_bulk_load.selectionChanged.disconnect(self.select_from_layer)

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

        feat_ids_existing = []
        feat_ids_bulk = []
        for index in self.tbl_original.selectionModel().selectedRows():
            item_existing = self.tbl_original.item(index.row(), 0)
            if item_existing:
                feat_ids_existing.append(int(item_existing.text()))
            item_bulk = self.tbl_original.item(index.row(), 1)
            if item_bulk:
                feat_ids_bulk.append(int(item_bulk.text()))

        self.lyr_existing.selectByIds(feat_ids_existing)
        self.lyr_bulk_load.selectByIds(feat_ids_bulk)

        self.highlight_features()

        self.lyr_existing.selectionChanged.connect(self.select_from_layer)
        self.lyr_bulk_load.selectionChanged.connect(self.select_from_layer)

    def clear_selection_clicked(self, widgets):
        """"
        Clear Selection in the widgets
        Called when clear_selection botton is clicked
        """
        for widget in widgets:
            widget.clearSelection()

    def remove_selected_clicked(self):
        """
        Remove selected row and related row
        Called when remove_selected botton is clicked
        """
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

    def remove_all_clicked(self):
        """
        Remove all rows in the table
        Called when remove_all botton is clicked
        """
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

        for row in range(self.tbl_original.rowCount())[::-1]:
            self.tbl_original.removeRow(row)

    def unlink_all_clicked(self):
        """
        Unlink the buildings in the table
        Called when unlink_all botton is clicked
        """
        tbl = self.tbl_original
        for row in range(tbl.rowCount())[::-1]:
            item_existing = tbl.item(row, 0)
            if item_existing:
                id_existing = int(item_existing.text())

                self.lyr_removed_existing_in_edit.setSubsetString(
                    self.lyr_removed_existing_in_edit.subsetString() + ' or "building_outline_id" = %s' % id_existing)

                self.remove_features_from_layer_existing(id_existing)

            item_bulk = tbl.item(row, 1)
            if item_bulk:
                id_bulk = int(item_bulk.text())

                self.lyr_added_bulk_load_in_edit.setSubsetString(
                    self.lyr_added_bulk_load_in_edit.subsetString() + ' or "bulk_load_outline_id" = %s' % id_bulk)

                self.remove_features_from_layer_bulk(id_bulk)

            self.remove_from_tbl_to_lst(row)

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

    def remove_from_tbl_to_lst(self, row):
        """
        Remove building ids from table to list
        """
        tbl = self.tbl_original

        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()

        item_existing = tbl.item(row, 0)
        if item_existing:
            id_existing = int(item_existing.text())
            have_duplicate_id = self.check_duplicate_listwidgetitems(self.lst_existing, id_existing)
            if not have_duplicate_id:
                self.lst_existing.addItem(QListWidgetItem('%s' % id_existing))

        item_bulk = tbl.item(row, 1)
        if item_bulk:
            id_bulk = int(item_bulk.text())
            have_duplicate_id = self.check_duplicate_listwidgetitems(self.lst_bulk, id_bulk)
            if not have_duplicate_id:
                self.lst_bulk.addItem(QListWidgetItem('%s' % id_bulk))

        tbl.removeRow(row)

    def check_duplicate_listwidgetitems(self, lst, id_item):
        """
        Check if list has the same row
        """
        have_duplicate_id = False
        for row in range(lst.count()):
            item = lst.item(row)
            if int(item.text()) == id_item:
                have_duplicate_id = True
                break
        return have_duplicate_id

    @pyqtSlot()
    def select_from_lst(self):
        """
        When users select rows in lst_existing, select the corresponding features in layers.
        """
        self.tbl_original.clearSelection()

        self.lyr_existing.selectionChanged.disconnect(self.select_from_layer)
        self.lyr_bulk_load.selectionChanged.disconnect(self.select_from_layer)

        current_list = self.sender()

        feat_ids = []
        for index in current_list.selectionModel().selectedRows():
            item = current_list.item(index.row())
            feat_ids.append(int(item.text()))

        if current_list == self.lst_existing:
            self.lyr_existing.selectByIds(feat_ids)
        elif current_list == self.lst_bulk:
            self.lyr_bulk_load.selectByIds(feat_ids)

        self.highlight_features()

        self.lyr_existing.selectionChanged.connect(self.select_from_layer)
        self.lyr_bulk_load.selectionChanged.connect(self.select_from_layer)

    def relink_all_clicked(self):
        """
        Relink the buildings in the list
        Called when relink_all botton is clicked
        """
        self.remove_from_lst_to_tbl()

        self.clear_layer_filter()

        self.btn_matched.setEnabled(True)
        self.btn_related.setEnabled(True)

    def remove_from_lst_to_tbl(self):
        """
        Remove building ids from list to table
        """
        tbl = self.tbl_original

        sql_related_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.related WHERE building_outline_id = %s"
        sql_related_bulk = "SELECT building_outline_id FROM buildings_bulk_load.related WHERE bulk_load_outline_id = %s"
        sql_matched_existing = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE building_outline_id = %s"
        sql_removed = "SELECT * FROM buildings_bulk_load.removed WHERE building_outline_id = %s"
        sql_added = "SELECT * FROM buildings_bulk_load.added WHERE bulk_load_outline_id = %s"

        rows_lst_existing = []
        rows_lst_bulk = []

        for row_lst in range(self.lst_existing.count())[::-1]:
            if row_lst not in rows_lst_existing:

                rows_lst_existing.append(row_lst)

                id_existing = int(self.lst_existing.item(row_lst).text())

                result = self.db._execute(sql_related_existing, (id_existing,))
                ids_related = result.fetchall()
                if ids_related:
                    id_bulk_count = 0
                    for row in range(self.lst_bulk.count())[::-1]:
                        id_bulk = int(self.lst_bulk.item(row).text())
                        if (id_bulk,) in ids_related:
                            id_bulk_count += 1
                            id_bulk_0 = id_bulk

                            rows_lst_bulk.append(row)

                            row_tbl = tbl.rowCount()
                            tbl.setRowCount(row_tbl + 1)
                            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                            item = self.lst_bulk.takeItem(row)
                            self.lst_bulk.removeItemWidget(item)
                    item = self.lst_existing.takeItem(row_lst)
                    self.lst_existing.removeItemWidget(item)

                    if id_bulk_count == 1:
                        result = self.db._execute(sql_related_bulk, (id_bulk_0,))
                        ids = result.fetchall()
                        for row in range(self.lst_existing.count())[::-1]:
                            id_item_existing = int(self.lst_existing.item(row).text())
                            if (id_item_existing,) in ids:
                                if row == row_lst:
                                    continue
                                rows_lst_existing.append(row)

                                row_tbl = tbl.rowCount()
                                tbl.setRowCount(row_tbl + 1)
                                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_item_existing))
                                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk_0))
                                item = self.lst_existing.takeItem(row)
                                self.lst_existing.removeItemWidget(item)
                    continue

                result = self.db._execute(sql_matched_existing, (id_existing,))
                id_matched = result.fetchone()
                if id_matched:
                    for row in range(self.lst_bulk.count())[::-1]:
                        id_bulk = int(self.lst_bulk.item(row).text())
                        if id_bulk == id_matched[0]:
                            rows_lst_bulk.append(row)

                            row_tbl = tbl.rowCount()
                            tbl.setRowCount(row_tbl + 1)
                            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                            item = self.lst_bulk.takeItem(row)
                            self.lst_bulk.removeItemWidget(item)

                            break

                    item = self.lst_existing.takeItem(row_lst)
                    self.lst_existing.removeItemWidget(item)
                    continue

                result = self.db._execute(sql_removed, (id_existing,))
                if result.fetchone():
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
                    item = self.lst_existing.takeItem(row_lst)
                    self.lst_existing.removeItemWidget(item)

        for row_lst in range(self.lst_bulk.count())[::-1]:
            if row_lst not in rows_lst_bulk:

                rows_lst_bulk.append(row_lst)

                id_bulk = int(self.lst_bulk.item(row_lst).text())

                result = self.db._execute(sql_added, (id_bulk,))
                if result.fetchone():
                    row_tbl = tbl.rowCount()
                    tbl.setRowCount(row_tbl + 1)
                    tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
                    item = self.lst_bulk.takeItem(row_lst)
                    self.lst_bulk.removeItemWidget(item)

    def matched_clicked(self):
        """
        Match the buildings in the list
        Called when matched botton is clicked
        """
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
        """
        Relate the buildings in the list
        Called when related botton is clicked
        """
        rows_lst_existing = [index.row() for index in self.lst_existing.selectionModel().selectedRows()]
        rows_lst_bulk = [index.row() for index in self.lst_bulk.selectionModel().selectedRows()]

        if len(rows_lst_bulk) < 1 or len(rows_lst_existing) < 1:
            iface.messageBar().pushMessage("Error:", "Do not relate less than one building in each layer", level=QgsMessageBar.WARNING)
            self.btn_related.setEnabled(True)
        elif len(rows_lst_bulk) == 1 and len(rows_lst_existing) == 1:
            iface.messageBar().pushMessage("Error:", "Do not relate only one building in each layer", level=QgsMessageBar.WARNING)
            self.btn_related.setEnabled(True)
        else:
            for index in self.lst_existing.selectionModel().selectedRows():
                item_existing = self.lst_existing.item(index.row())
                item_existing.setBackground(QColor('#E3ECEF'))
                id_existing = int(item_existing.text())

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

                self.lyr_related_bulk_load_in_edit.setSubsetString(
                    self.lyr_related_bulk_load_in_edit.subsetString() + ' or "bulk_load_outline_id" = %s' % id_bulk)

                ids_added = re.findall('\d+', self.lyr_added_bulk_load_in_edit.subsetString())
                for id_added in ids_added:
                    if int(id_added) == id_bulk:
                        self.lyr_added_bulk_load_in_edit.setSubsetString(
                            '(' + self.lyr_added_bulk_load_in_edit.subsetString() + ') and "bulk_load_outline_id" != %s' % id_bulk)

                self.remove_features_from_layer_bulk(id_bulk)

                item_bulk.setFlags(Qt.NoItemFlags)

            self.btn_related.setEnabled(False)

        self.lst_bulk.clearSelection()
        self.lst_existing.clearSelection()

    def remove_features_from_layer_bulk(self, id_bulk):
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

    def remove_features_from_layer_existing(self, id_existing):
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

    def save_clicked(self, commit_status=True):
        """
        Save result and change database
        Called when save botton is clicked
        """

        sql_delete_related_existing = 'SELECT buildings_bulk_load.related_delete_existing_outlines(%s);'

        sql_delete_matched_existing = 'SELECT buildings_bulk_load.matched_delete_existing_outlines(%s);'

        sql_delete_removed = 'SELECT buildings_bulk_load.removed_delete_existing_outlines(%s);'

        sql_delete_added = 'SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);'

        sql_insert_added = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'

        sql_insert_removed = 'SELECT buildings_bulk_load.removed_insert_bulk_load_outlines(%s);'

        sql_insert_matched = 'SELECT buildings_bulk_load.matched_insert_buildling_outlines(%s, %s);'

        sql_insert_related = 'SELECT buildings_bulk_load.related_insert_buildling_outlines(%s, %s);'

        self.db.open_cursor()

        for row in range(self.lst_existing.count())[::-1]:
            item = self.lst_existing.item(row)
            id_existing = int(item.text())

            self.db.execute_no_commit(sql_delete_removed, (id_existing, ))
            self.db.execute_no_commit(sql_delete_matched_existing, (id_existing, ))
            self.db.execute_no_commit(sql_delete_related_existing, (id_existing, ))

        for row in range(self.lst_bulk.count())[::-1]:
            item = self.lst_bulk.item(row)
            id_bulk = int(item.text())

            self.db.execute_no_commit(sql_delete_added, (id_bulk, ))

        # added
        for feat in self.lyr_added_bulk_load_in_edit.getFeatures():
            id_bulk = feat['bulk_load_outline_id']
            self.db.execute_no_commit(sql_insert_added, (id_bulk,))

        # removed
        for feat in self.lyr_removed_existing_in_edit.getFeatures():
            id_existing = feat['building_outline_id']
            self.db.execute_no_commit(sql_insert_removed, (id_existing, ))

        # matched
        for feat1 in self.lyr_matched_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_matched_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_matched, (id_bulk, id_existing))

        # related
        for feat1 in self.lyr_related_bulk_load_in_edit.getFeatures():
            id_bulk = feat1['bulk_load_outline_id']
            for feat2 in self.lyr_related_existing_in_edit.getFeatures():
                id_existing = feat2['building_outline_id']
                self.db.execute_no_commit(sql_insert_related, (id_bulk, id_existing))

        if commit_status:
            self.db.commit_open_cursor()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.repaint_view()
        self.clear_layer_filter()

        self.btn_matched.setEnabled(True)
        self.btn_related.setEnabled(True)

        iface.mapCanvas().refreshAllLayers()

    def cancel_clicked(self):
        """
        Relate the buildings in the list
        Called when cancel botton is clicked
        """
        self.tbl_original.clearSelection()
        self.lst_existing.clearSelection()
        self.lst_bulk.clearSelection()

        try:
            self.lyr_existing.selectionChanged.disconnect(self.select_from_layer)
            self.lyr_bulk_load.selectionChanged.disconnect(self.select_from_layer)
            self.tbl_original.itemSelectionChanged.disconnect(self.select_from_tbl_original)
            self.lst_existing.itemSelectionChanged.disconnect(self.select_from_lst)
            self.lst_bulk.itemSelectionChanged.disconnect(self.select_from_lst)
        except TypeError:
            pass
        self.clear_layer_filter()

        self.layer_registry.remove_all_layers()

        from buildings.gui.bulk_load_frame import BulkLoadFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadFrame(self.layer_registry))
        iface.actionPan().trigger()


from qgis.core import QgsRectangle, QgsMapLayerRegistry
from PyQt4.Qt import QCursor, QPixmap
from qgis.gui import QgsMapTool


class MultiLayerSelection(QgsMapTool):

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapTool.__init__(self, self.canvas)
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "# c None",
                                       "a c #000000",
                                       ". c #ffffff",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "aaaaaaaaaaaaaaaaa",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########",
                                       "########a########"]))

    def canvasPressEvent(self, e):

        layer_bulk = QgsMapLayerRegistry.instance().mapLayersByName("bulk_load_outlines")
        layer_existing = QgsMapLayerRegistry.instance().mapLayersByName("existing_subset_extracts")
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
