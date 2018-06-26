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

    Tests: Add New Bulk Outline Processes

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import QgsRectangle, QgsPoint, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkAddOutlinesTest(unittest.TestCase):
    """Test Add New Bulk Outline GUI Processes"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get('roads'):
            pass
        else:
            cls.road_plugin = plugins.get('roads')
            if cls.road_plugin.is_active is False:
                cls.road_plugin.main_toolbar.actions()[0].trigger()
                cls.dockwidget = cls.road_plugin.dockwidget
            else:
                cls.dockwidget = cls.road_plugin.dockwidget
            if not plugins.get('buildings'):
                pass
            else:
                db.connect()
                cls.building_plugin = plugins.get('buildings')
                cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.startup_frame = self.building_plugin.startup_frame
        self.startup_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.rad_add.click()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_ui_on_geometry_drawn(self):
        """UI comboboxes enable when geometry is drawn"""
        # add geom to canvas
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
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0,
                                      1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.bulk_load_frame.btn_edit_ok.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_reset_button(self):
        """Indexes are reset and comboxes disabled when reset is called"""
        # add geom to canvas
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
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0,
                                      1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.bulk_load_frame.btn_edit_ok.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())

        # change indexes of comboboxes
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(1)
        self.bulk_load_frame.cmb_capture_source.setCurrentIndex(0)
        self.bulk_load_frame.cmb_ta.setCurrentIndex(1)
        self.bulk_load_frame.cmb_town.setCurrentIndex(0)
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(1)
        # click reset button
        self.bulk_load_frame.btn_edit_reset.click()
        # check geom removed from canvas
        self.assertEqual(len(self.bulk_load_frame.added_building_ids), 0)
        # check comboxbox indexes reset to 0
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentIndex(), -1)
        self.assertEqual(self.bulk_load_frame.cmb_capture_source.currentIndex(), -1)
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentIndex(), -1)
        self.assertEqual(self.bulk_load_frame.cmb_town.currentIndex(), -1)
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentIndex(), -1)
        # check comboboxes disabled
        self.assertFalse(self.bulk_load_frame.btn_edit_ok.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_new_outline_insert(self):
        """Data added to correct tables when save clicked"""
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;'
        added_result = db._execute(sql)
        added_result = added_result.fetchall()[0][0]
        # add geom
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
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0,
                                      1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555290)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.bulk_load_frame.btn_edit_ok.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        # change indexes of comboboxes
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(1)
        self.bulk_load_frame.cmb_capture_source.setCurrentIndex(0)
        self.bulk_load_frame.cmb_ta.setCurrentIndex(0)
        self.bulk_load_frame.cmb_town.setCurrentIndex(0)
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(0)
        self.bulk_load_frame.change_instance.edit_ok_clicked(False)
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;'
        added_result2 = db._execute(sql)
        added_result2 = added_result2.fetchall()[0][0]
        self.assertEqual(added_result2, added_result + 1)
        self.bulk_load_frame.db.rollback_open_cursor()
