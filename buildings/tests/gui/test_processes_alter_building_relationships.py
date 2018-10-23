# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2018 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

    Tests: Alter Building Relationships GUI processing

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QListWidgetItem, QMessageBox
from PyQt4.QtTest import QTest
from qgis.core import QgsCoordinateReferenceSystem, QgsPoint, QgsRectangle
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessAlterRelationshipsTest(unittest.TestCase):
    """Test Alter Building Relationships GUI processing"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        db.connect()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Bulk Load', Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.btn_alter_rel.click()
        self.alter_relationships_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.alter_relationships_frame.db.rollback_open_cursor()

    def test_multi_selection_changed(self):
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas = iface.mapCanvas()
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878028.94, 5555123.14,
                                      1878449.89, 5555644.95)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mousePress(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878033.23, 5555351.12)),
                         delay=-1)
        QTest.mouseRelease(widget,
                           Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878045.70, 5555324.07)),
                           delay=-1)
        QTest.qWait(1)
        count_lst_existing = self.alter_relationships_frame.lst_existing.count()
        count_lst_bulk = self.alter_relationships_frame.lst_bulk.count()
        self.assertEqual(count_lst_existing, 1)
        self.assertEqual(count_lst_bulk, 1)
        id_existing = int(self.alter_relationships_frame.lst_existing.item(0).text())
        id_bulk = int(self.alter_relationships_frame.lst_bulk.item(0).text())
        self.assertEqual(id_existing, 1006)
        self.assertEqual(id_bulk, 2010)

        selected = self.alter_relationships_frame.tbl_relationship.selectionModel().selectedRows()
        self.assertEqual(len(selected), 1)
        id_tbl = int(self.alter_relationships_frame.tbl_relationship.item(selected[0].row(), 0).text())
        self.assertEqual(id_tbl, 1006)

        self.alter_relationships_frame.btn_exit.click()

    def test_maptool_clicked(self):
        iface.actionSelectRectangle().trigger()
        self.alter_relationships_frame.btn_maptool.click()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas = iface.mapCanvas()
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878028.94, 5555123.14,
                                      1878449.89, 5555644.95)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mousePress(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878033.23, 5555351.12)),
                         delay=-1)
        QTest.mouseRelease(widget,
                           Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878045.70, 5555324.07)),
                           delay=-1)
        QTest.qWait(1)
        self.assertEqual(self.alter_relationships_frame.lst_existing.count(), 1)
        self.assertEqual(self.alter_relationships_frame.lst_bulk.count(), 1)
        self.alter_relationships_frame.btn_exit.click()

    def test_unlink_and_save_clicked(self):

        sql_matched = 'SELECT count(*)::integer FROM buildings_bulk_load.matched'
        sql_added = 'SELECT count(*)::integer FROM buildings_bulk_load.added'
        sql_removed = 'SELECT count(*)::integer FROM buildings_bulk_load.removed'
        result = db._execute(sql_matched)
        matched_original = result.fetchone()[0]
        result = db._execute(sql_added)
        added_original = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_original = result.fetchone()[0]

        self.alter_relationships_frame.lst_existing.addItem(QListWidgetItem('1001'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2031'))
        self.alter_relationships_frame.btn_unlink.setEnabled(True)
        self.alter_relationships_frame.btn_unlink.click()
        self.assertTrue(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_maptool.isEnabled())

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql_matched)
        matched_test = result.fetchone()[0]
        result = db._execute(sql_added)
        added_test = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_test = result.fetchone()[0]
        self.assertEqual(matched_test, matched_original - 1)
        self.assertEqual(added_test, added_original + 1)
        self.assertEqual(removed_test, removed_original + 1)

        self.alter_relationships_frame.db.rollback_open_cursor()
        self.alter_relationships_frame.btn_exit.click()

    def test_match_and_save_clicked(self):

        sql_matched = 'SELECT count(*)::integer FROM buildings_bulk_load.matched'
        sql_added = 'SELECT count(*)::integer FROM buildings_bulk_load.added'
        sql_removed = 'SELECT count(*)::integer FROM buildings_bulk_load.removed'
        result = db._execute(sql_matched)
        matched_original = result.fetchone()[0]
        result = db._execute(sql_added)
        added_original = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_original = result.fetchone()[0]

        self.alter_relationships_frame.lst_existing.addItem(QListWidgetItem('1006'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2010'))
        self.alter_relationships_frame.btn_matched.setEnabled(True)
        self.alter_relationships_frame.btn_matched.click()
        self.assertTrue(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_maptool.isEnabled())

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql_matched)
        matched_test = result.fetchone()[0]
        result = db._execute(sql_added)
        added_test = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_test = result.fetchone()[0]
        self.assertEqual(matched_test, matched_original + 1)
        self.assertEqual(added_test, added_original - 1)
        self.assertEqual(removed_test, removed_original - 1)

        self.alter_relationships_frame.db.rollback_open_cursor()
        self.alter_relationships_frame.btn_exit.click()

    def test_related_and_save_clicked(self):
        sql_related = 'SELECT count(*)::integer FROM buildings_bulk_load.related'
        sql_added = 'SELECT count(*)::integer FROM buildings_bulk_load.added'
        sql_removed = 'SELECT count(*)::integer FROM buildings_bulk_load.removed'
        result = db._execute(sql_related)
        related_original = result.fetchone()[0]
        result = db._execute(sql_added)
        added_original = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_original = result.fetchone()[0]

        self.alter_relationships_frame.lst_existing.addItem(QListWidgetItem('1006'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2010'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2003'))
        self.alter_relationships_frame.btn_related.setEnabled(True)
        self.alter_relationships_frame.btn_related.click()
        self.assertTrue(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_maptool.isEnabled())

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql_related)
        related_test = result.fetchone()[0]
        result = db._execute(sql_added)
        added_test = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_test = result.fetchone()[0]
        self.assertEqual(related_test, related_original + 2)
        self.assertEqual(added_test, added_original - 2)
        self.assertEqual(removed_test, removed_original - 1)

        self.alter_relationships_frame.db.rollback_open_cursor()
        self.alter_relationships_frame.btn_exit.click()

    def test_cancel_clicked(self):
        self.alter_relationships_frame.lst_existing.addItem(QListWidgetItem('1001'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2031'))
        self.alter_relationships_frame.btn_unlink.setEnabled(True)
        self.alter_relationships_frame.btn_unlink.click()
        self.alter_relationships_frame.btn_cancel.click()
        self.assertTrue(self.alter_relationships_frame.btn_maptool.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_unlink.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_matched.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_related.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertEqual(self.alter_relationships_frame.lst_existing.count(), 0)
        self.assertEqual(self.alter_relationships_frame.lst_bulk.count(), 0)

        self.alter_relationships_frame.btn_exit.click()

    def test_exit_clicked(self):
        self.alter_relationships_frame.btn_exit.click()
        self.assertNotEqual(self.alter_relationships_frame, self.dockwidget.current_frame)

    def test_cmb_relationship_current_index_changed(self):
        self.alter_relationships_frame.cmb_relationship.setCurrentIndex(1)
        self.assertEqual(self.alter_relationships_frame.tbl_relationship.columnCount(), 2)
        self.assertEqual(int(self.alter_relationships_frame.tbl_relationship.item(0, 0).text()), 1004)

        self.assertTrue(self.alter_relationships_frame.btn_qa_not_checked.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_refer2supplier.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_pending.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_okay.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_not_removed.isEnabled())

        self.alter_relationships_frame.cmb_relationship.setCurrentIndex(2)
        self.assertEqual(self.alter_relationships_frame.tbl_relationship.columnCount(), 3)
        self.assertEqual(int(self.alter_relationships_frame.tbl_relationship.item(0, 0).text()), 1001)

        self.assertTrue(self.alter_relationships_frame.btn_qa_not_checked.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_refer2supplier.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_pending.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_okay.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_not_removed.isEnabled())

        self.alter_relationships_frame.cmb_relationship.setCurrentIndex(3)
        self.assertEqual(self.alter_relationships_frame.tbl_relationship.columnCount(), 4)
        self.assertEqual(int(self.alter_relationships_frame.tbl_relationship.item(0, 0).text()), 1)

        self.assertTrue(self.alter_relationships_frame.btn_qa_not_checked.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_refer2supplier.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_pending.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_okay.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_not_removed.isEnabled())

        self.alter_relationships_frame.btn_exit.click()

    def test_tbl_relationship_item_selection_changed(self):
        self.alter_relationships_frame.cmb_relationship.setCurrentIndex(1)
        self.alter_relationships_frame.tbl_relationship.selectRow(0)
        selected_id_tbl = int(self.alter_relationships_frame.tbl_relationship.item(0, 0).text())
        selected_id_lyr = [feat.id() for feat in self.alter_relationships_frame.lyr_existing.selectedFeatures()]
        self.assertEqual(selected_id_lyr, [selected_id_tbl])
        id_lst = int(self.alter_relationships_frame.lst_existing.item(0).text())
        self.assertEqual(id_lst, selected_id_tbl)

        self.alter_relationships_frame.btn_exit.click()

    def test_btn_qa_status_clicked(self):
        self.alter_relationships_frame.cmb_relationship.setCurrentIndex(1)
        self.alter_relationships_frame.tbl_relationship.selectRow(0)
        selected_id_tbl = int(self.alter_relationships_frame.tbl_relationship.item(0, 0).text())
        self.alter_relationships_frame.btn_qa_status_clicked(qa_status='Okay', commit_status=False)
        sql = 'SELECT qa_status_id FROM buildings_bulk_load.removed WHERE building_outline_id = %s' % selected_id_tbl
        result = db._execute(sql)
        qa_status_id = result.fetchone()[0]
        self.assertEqual(qa_status_id, 2)
        selected_row = [index.row() for index in self.alter_relationships_frame.tbl_relationship.selectionModel().selectedRows()]
        self.assertEqual(selected_row, [1])

        self.alter_relationships_frame.db.rollback_open_cursor()
        self.alter_relationships_frame.btn_exit.click()

    def test_cb_lyr_bulk_load_state_changed(self):
        self.alter_relationships_frame.cb_lyr_bulk_load.setChecked(False)
        legend = iface.legendInterface()
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_added_bulk_load_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_matched_bulk_load_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_related_bulk_load_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_added_bulk_load))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_matched_bulk_load))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_related_bulk_load))

        self.alter_relationships_frame.btn_exit.click()

    def test_cb_lyr_existing_state_changed(self):
        self.alter_relationships_frame.cb_lyr_existing.setChecked(False)
        legend = iface.legendInterface()
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_removed_existing_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_matched_existing_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_related_existing_in_edit))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_removed_existing))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_matched_existing))
        self.assertFalse(legend.isLayerVisible(self.alter_relationships_frame.lyr_related_existing))

        self.alter_relationships_frame.btn_exit.click()

    def test_cb_autosave_stage_changed(self):

        btn_yes = self.alter_relationships_frame.msgbox.button(QMessageBox.Yes)
        QTimer.singleShot(1000, btn_yes.click)
        self.alter_relationships_frame.cb_autosave.setChecked(True)

        self.assertFalse(self.alter_relationships_frame.btn_save.isVisible())

        sql_matched = 'SELECT count(*)::integer FROM buildings_bulk_load.matched'
        sql_added = 'SELECT count(*)::integer FROM buildings_bulk_load.added'
        sql_removed = 'SELECT count(*)::integer FROM buildings_bulk_load.removed'
        result = db._execute(sql_matched)
        matched_original = result.fetchone()[0]
        result = db._execute(sql_added)
        added_original = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_original = result.fetchone()[0]

        self.alter_relationships_frame.lst_existing.addItem(QListWidgetItem('1001'))
        self.alter_relationships_frame.lst_bulk.addItem(QListWidgetItem('2031'))
        self.alter_relationships_frame.unlink_clicked(commit_status=False)

        result = db._execute(sql_matched)
        matched_test = result.fetchone()[0]
        result = db._execute(sql_added)
        added_test = result.fetchone()[0]
        result = db._execute(sql_removed)
        removed_test = result.fetchone()[0]
        self.assertEqual(matched_test, matched_original - 1)
        self.assertEqual(added_test, added_original + 1)
        self.assertEqual(removed_test, removed_original + 1)

        self.alter_relationships_frame.db.rollback_open_cursor()

        self.alter_relationships_frame.cb_autosave.setChecked(False)
        self.assertTrue(self.alter_relationships_frame.btn_save.isVisible())

        self.alter_relationships_frame.btn_exit.click()
