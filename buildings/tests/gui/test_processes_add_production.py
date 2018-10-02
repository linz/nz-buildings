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

    Tests: Add New Outline to Production Processes

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import QgsRectangle, QgsPoint, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessProductionAddOutlinesTest(unittest.TestCase):
    """Test Add New Outline to Production Processes"""
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
            'Edit Outlines', Qt.MatchExactly)[0])
        self.production_frame = self.dockwidget.current_frame
        self.production_frame.rad_add.click()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_ui_on_geometry_drawn(self):
        """UI comboboxes enable when geometry is drawn"""
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=30)
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
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555290)),
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555290)),
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=30)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=30)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.btn_exit.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.production_frame.db.rollback_open_cursor()

    def test_reset_button(self):
        """Indexes are reset and comboxes disabled when reset is called"""
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=30)
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
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878262, 5555290)),
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555290)),
                         delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=30)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878223, 5555314)),
                         delay=30)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.btn_exit.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())

        # change indexes of comboboxes
        self.production_frame.cmb_capture_method.setCurrentIndex(1)
        self.production_frame.cmb_capture_source.setCurrentIndex(0)
        self.production_frame.cmb_ta.setCurrentIndex(1)
        self.production_frame.cmb_town.setCurrentIndex(0)
        self.production_frame.cmb_suburb.setCurrentIndex(1)
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(2)
        # click reset button
        self.production_frame.btn_reset.click()
        # check geom removed from canvas
        self.assertEqual(len(self.production_frame.added_building_ids), 0)
        # check comboxbox indexes reset to 0
        self.assertEqual(self.production_frame.cmb_capture_method.currentIndex(), -1)
        self.assertEqual(self.production_frame.cmb_capture_source.currentIndex(), -1)
        self.assertEqual(self.production_frame.cmb_ta.currentIndex(), -1)
        self.assertEqual(self.production_frame.cmb_town.currentIndex(), -1)
        self.assertEqual(self.production_frame.cmb_suburb.currentIndex(), -1)
        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentIndex(), -1)
        # check comboboxes disabled
        self.assertFalse(self.production_frame.btn_save.isEnabled())
        self.assertFalse(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.btn_exit.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_method.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.production_frame.cmb_ta.isEnabled())
        self.assertFalse(self.production_frame.cmb_town.isEnabled())
        self.assertFalse(self.production_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.production_frame.db.rollback_open_cursor()

    def test_new_outline_insert(self):
        """Data added to correct tables when save clicked"""
        sql = 'SELECT COUNT(building_outline_id) FROM buildings.building_outlines;'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
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
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.btn_exit.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        # change indexes of comboboxes
        self.production_frame.cmb_capture_method.setCurrentIndex(1)
        self.production_frame.cmb_capture_source.setCurrentIndex(0)
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(2)
        self.production_frame.cmb_ta.setCurrentIndex(0)
        self.production_frame.cmb_town.setCurrentIndex(0)
        self.production_frame.cmb_suburb.setCurrentIndex(0)
        self.production_frame.change_instance.save_clicked(False)
        sql = 'SELECT COUNT(building_outline_id) FROM buildings.building_outlines;'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.production_frame.db.rollback_open_cursor()
