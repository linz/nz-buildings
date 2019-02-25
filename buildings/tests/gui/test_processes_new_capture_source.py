
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

    Tests: New Capture Source GUI Processes

 ***************************************************************************/
"""

import unittest

from qgis.utils import iface, plugins
from qgis.gui import QgsMapTool
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import QgsCoordinateReferenceSystem, QgsPoint

from buildings.utilities import database as db


class ProcessCaptureSourceTest(unittest.TestCase):
    """Test New Capture Source GUI Processes"""
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
            'Capture Sources', Qt.MatchExactly)[0])
        self.capture_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_frame.btn_exit.click()

    def test_filter_buttons_clicked(self):
        """
        Check the table filtered when btn_filter_add clicked
        and unfiltered when btn_filter_del clicked
        """
        count_original = self.capture_frame.tbl_capture_source_area.rowCount()
        self.capture_frame.le_filter.setText('1')
        self.capture_frame.btn_filter_add.click()
        count_filter_on = self.capture_frame.tbl_capture_source_area.rowCount()
        self.assertEqual(count_filter_on, 1)
        self.capture_frame.tbl_capture_source_area.selectRow(0)
        self.capture_frame.btn_filter_del.click()
        count_filter_off = self.capture_frame.tbl_capture_source_area.rowCount()
        self.assertEqual(count_filter_off, count_original)
        # Check if the old selection is reinstated
        selected_rows = [
            index.row() for index in self.capture_frame.tbl_capture_source_area.selectionModel().selectedRows()]
        self.assertEqual(len(selected_rows), 1)
        external_source_id = self.capture_frame.tbl_capture_source_area.item(selected_rows[0], 0).text()
        self.assertEqual(external_source_id, '1')

    def test_cmb_capture_source_group_changed(self):
        """
        Check the l_confirm info updated when cmb_capture_source_group changed
        """
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.tbl_capture_source_area.selectRow(0)
        self.assertIn('NZ Aerial Imagery', self.capture_frame.l_confirm.text())

        self.capture_frame.cmb_capture_source_group.addItem('Test group- Test')
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(1)
        self.assertIn('Test group', self.capture_frame.l_confirm.text())
        db.rollback_open_cursor()

    def test_add_valid_capture_source_with_external_id(self):
        """Valid capture source with valid external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.tbl_capture_source_area.selectRow(2)
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        self.assertNotEqual(self.capture_frame.l_confirm.text(), '')
        self.capture_frame.save_clicked(commit_status=False)
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        self.capture_frame.db.rollback_open_cursor()

    def test_table_selection_by_layer_selection(self):
        """Editing external source id using the capture source area layer"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        # test selecting an area
        # external id of 1
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878185, 5555335)), delay=-1)
        rows = [row.row() for row in self.capture_frame.tbl_capture_source_area.selectionModel().selectedRows()]
        self.assertEquals(rows[0], 0)
        # external id of 2
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878733, 5555375)), delay=-1)
        rows = [row.row() for row in self.capture_frame.tbl_capture_source_area.selectionModel().selectedRows()]
        self.assertEquals(rows[0], 1)
        # check clicking outside the shapefile/deselecting removes from frame
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878996, 5555445)), delay=-1)
        rows = [row.row() for row in self.capture_frame.tbl_capture_source_area.selectionModel().selectedRows()]
        self.assertEquals(len(rows), 0)

    def test_layer_selection_by_table_selection(self):
        """Editing external source id using the table"""
        # adding by table selection
        self.capture_frame.tbl_capture_source_area.selectRow(0)
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 1)
        self.assertEqual(self.ids[0], '1')
        # selected two ids in table
        self.capture_frame.tbl_capture_source_area.selectRow(1)
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 1)
        self.assertEqual(self.ids[0], '2')
        # deselecting everthing from table
        self.capture_frame.tbl_capture_source_area.clearSelection()
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 0)
