
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

    def test_add_valid_capture_source_with_external_id(self):
        """Valid capture source with valid external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.le_external_source_id.setText('3')
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        self.capture_frame.save_clicked(commit_status=False)
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        self.capture_frame.db.rollback_open_cursor()

    def test_adding_capture_source_by_capture_source_area_layer(self):
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
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '1')
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        # external id of 2
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878733, 5555375)), delay=-1)
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '2')
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        # check clicking outside the shapefile/deselecting removes from frame
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878996, 5555445)), delay=-1)
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '')
        self.assertFalse(self.capture_frame.btn_save.isEnabled())

    def test_adding_capture_source_by_line_edit(self):
        """Editing external source id using the line edit"""
        # adding by line edit one selection
        self.capture_frame.le_external_source_id.setText('1')
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 1)
        self.assertEqual(self.ids[0], '1')
        # adding by line edit two selections
        self.capture_frame.le_external_source_id.setText('1,2')
        self.assertFalse(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 2)
        self.assertEqual(self.ids[0], '1')
        self.assertEqual(self.ids[1], '2')
        # clearing line edit
        self.capture_frame.le_external_source_id.setText('')
        self.assertFalse(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 0)

    def test_adding_capture_source_by_table_selection(self):
        """Editing external source id using the table"""
        # adding by table selection
        self.capture_frame.tbl_capture_source_area.selectRow(0)
        self.assertTrue(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 1)
        self.assertEqual(self.ids[0], '1')
        # selected two ids in table
        self.capture_frame.tbl_capture_source_area.selectRow(1)
        self.assertFalse(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 2)
        self.assertEqual(self.ids[0], '1')
        self.assertEqual(self.ids[1], '2')
        # deselecting everthing from table
        self.capture_frame.tbl_capture_source_area.clearSelection()
        self.assertFalse(self.capture_frame.btn_save.isEnabled())
        self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_frame.capture_source_area.selectedFeatures()]
        self.assertEqual(len(self.ids), 0)
