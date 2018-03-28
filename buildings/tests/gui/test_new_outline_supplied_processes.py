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
from qgis.core import QgsRectangle, QgsPoint
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class SetUpBulkLoadGuiTest(unittest.TestCase):
    """Test Add New Bulk Outline GUI Processes"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get("roads"):
            pass
        else:
            cls.road_plugin = plugins.get("roads")
            if cls.road_plugin.is_active is False:
                cls.road_plugin.main_toolbar.actions()[0].trigger()
                cls.dockwidget = cls.road_plugin.dockwidget
            else:
                cls.dockwidget = cls.road_plugin.dockwidget
            if not plugins.get("buildings"):
                pass
            else:
                cls.building_plugin = plugins.get("buildings")
        if cls.dockwidget.stk_options.count() == 4:
            cls.dockwidget.stk_options.setCurrentIndex(3)
            cls.dockwidget.stk_options.addWidget(cls.dockwidget.frames['menu_frame'])
            cls.dockwidget.current_frame = 'menu_frame'
            cls.dockwidget.stk_options.setCurrentIndex(4)
        else:
            cls.dockwidget.stk_options.setCurrentIndex(4)
        cls.dockwidget.lst_options.setCurrentItem(cls.dockwidget.lst_options.item(2))

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get("roads")
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.cmb_add_outline.setCurrentIndex(1)
        self.new_bulk_frame = self.dockwidget.current_frame
        if self.new_bulk_frame.error_dialog is not None:
            self.no_supplied_data = True
            self.new_bulk_frame.error_dialog.close()
        else:
            self.no_supplied_data = False

    def tearDown(self):
        """Runs after each test."""
        self.new_bulk_frame.btn_cancel.click()

    def test_ui_on_geom_drawn(self):
        if self.no_supplied_data is False:
            # add geom to canvas
            canvas = iface.mapCanvas()
            zoom_rectangle = QgsRectangle(1747456, 5427988, 1748402, 5428705)
            canvas.setExtent(zoom_rectangle)
            canvas.refresh()
            widget = iface.mapCanvas().viewport()
            canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428152)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428102)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428102)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428152)), delay=300)
            QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPoint(1747520, 5428152)), delay=300)
            QTest.qWait(300)
            # tests
            self.assertTrue(self.new_bulk_frame.btn_save.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_suburb.isEnabled())

    def test_reset_button(self):
        if self.no_supplied_data is False:
            # add geom to canvas
            canvas = iface.mapCanvas()
            zoom_rectangle = QgsRectangle(1747456, 5427988, 1748402, 5428705)
            canvas.setExtent(zoom_rectangle)
            canvas.refresh()
            widget = iface.mapCanvas().viewport()
            canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428172)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428222)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428222)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428172)), delay=300)
            QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPoint(1747520, 5428172)), delay=300)
            QTest.qWait(300)
            # change indexes of comboboxes
            self.new_bulk_frame.cmb_capture_method.setCurrentIndex(1)
            self.new_bulk_frame.cmb_capture_source.setCurrentIndex(0)
            self.new_bulk_frame.cmb_ta.setCurrentIndex(1)
            self.new_bulk_frame.cmb_town.setCurrentIndex(0)
            self.new_bulk_frame.cmb_suburb.setCurrentIndex(1)
            # click reset button
            self.new_bulk_frame.btn_reset.click()
            # check geom removed from canvas
            self.assertEqual(len(self.new_bulk_frame.added_building_ids), 0)
            # check comboxbox indexes reset to 0
            self.assertEqual(self.new_bulk_frame.cmb_capture_method.currentIndex(), 0)
            self.assertEqual(self.new_bulk_frame.cmb_capture_source.currentIndex(), 0)
            self.assertEqual(self.new_bulk_frame.cmb_ta.currentIndex(), 0)
            self.assertEqual(self.new_bulk_frame.cmb_town.currentIndex(), 0)
            self.assertEqual(self.new_bulk_frame.cmb_suburb.currentIndex(), 0)
            # check comboboxes disabled
            self.assertFalse(self.new_bulk_frame.btn_save.isEnabled())
            self.assertFalse(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_suburb.isEnabled())

    def test_insert(self):
        if self.no_supplied_data is False:
            sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines"
            result = db._execute(sql)
            result = result.fetchall()[0][0]
            # add geom
            canvas = iface.mapCanvas()
            zoom_rectangle = QgsRectangle(1747456, 5427988, 1748402, 5428705)
            canvas.setExtent(zoom_rectangle)
            canvas.refresh()
            widget = iface.mapCanvas().viewport()
            canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428242)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747591, 5428302)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428302)), delay=300)
            QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPoint(1747520, 5428242)), delay=300)
            QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPoint(1747520, 5428242)), delay=300)
            QTest.qWait(300)
            # change indexes of comboboxes
            self.new_bulk_frame.cmb_capture_method.setCurrentIndex(1)
            self.new_bulk_frame.cmb_capture_source.setCurrentIndex(0)
            self.new_bulk_frame.cmb_ta.setCurrentIndex(1)
            self.new_bulk_frame.cmb_town.setCurrentIndex(0)
            self.new_bulk_frame.cmb_suburb.setCurrentIndex(1)
            self.new_bulk_frame.btn_save.click()
            sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines"
            result2 = db._execute(sql)
            result2 = result2.fetchall()[0][0]
            self.assertTrue(result2=result + 1)
            # remove row from table
            sql = "DELETE FROM buildings_bulk_load.buildings_bulk_load WHERE bulk_load_outline_id = (SELECT MAX(bulk_load_outline_id) FROM buildings_bulk_load.buildings_bulk_load)"
            db.execute(sql)
