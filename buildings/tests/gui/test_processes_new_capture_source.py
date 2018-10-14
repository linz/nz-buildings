
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

from qgis.utils import iface
from qgis.utils import plugins
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

    def test_external_radio_button(self):
        """External source line edit enabled when external source radiobutton selected"""
        self.capture_frame.rad_external_source.click()
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.capture_frame.rad_external_source.click()
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())

    def test_add_valid_capture_source_no_external_id(self):
        """Valid capture source added when ok clicked"""
        # add valid capture source no external id
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]

        # Add a capture source group for testing
        self.capture_frame.db.open_cursor()
        sql = "INSERT INTO buildings_common.capture_source_group (value, description) VALUES ('Test Source', 'Test Source');"
        self.capture_frame.db.execute_no_commit(sql)
        # populate the combobox including the test data
        self.capture_frame.cmb_capture_source_group.clear()
        self.capture_frame.populate_combobox()

        self.capture_frame.cmb_capture_source_group.setCurrentIndex(self.capture_frame.cmb_capture_source_group.findText('Test Source- Test Source'))
        self.capture_frame.ok_clicked(commit_status=False)
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        self.capture_frame.db.rollback_open_cursor()

    def test_add_blank_external_id_line_edit(self):
        """Error dialog when external radio button checked and no external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.ok_clicked(commit_status=False)
        if self.capture_frame.error_dialog is not None:
            self.capture_frame.error_dialog.close()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        if result != result2:
            if self.capture_frame.error_dialog is not None:
                self.capture_frame.error_dialog.close()
        self.capture_frame.db.rollback_open_cursor()

    def test_add_valid_capture_source_with_external_id(self):
        """Valid capture source with valid external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.le_external_source_id.setText('Test Ext Source')
        self.capture_frame.ok_clicked(commit_status=False)
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
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878185, 5555335)), delay=-1)
        self.assertTrue(self.capture_frame.rad_external_source.isChecked())
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '1')
        # test selecting an area and toggling on and off takes the value away and brings it back
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878733, 5555375)), delay=-1)
        self.assertTrue(self.capture_frame.rad_external_source.isChecked())
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '2')
        self.capture_frame.rad_external_source.toggle()
        self.assertFalse(self.capture_frame.rad_external_source.isChecked())
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '')
        self.capture_frame.rad_external_source.toggle()
        self.assertTrue(self.capture_frame.rad_external_source.isChecked())
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '')
        # check clicking outside the shapefile/deselecting removes from frame
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1878996, 5555445)), delay=-1)
        self.assertTrue(self.capture_frame.rad_external_source.isChecked())
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.assertEquals(self.capture_frame.le_external_source_id.text(), '')
