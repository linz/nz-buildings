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


class ProcessBulkNewOutlinesTest(unittest.TestCase):
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
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.cmb_add_outline.setCurrentIndex(0)
        self.menu_frame.cmb_add_outline.setCurrentIndex(1)
        self.new_bulk_frame = self.dockwidget.current_frame
        if self.new_bulk_frame.error_dialog is not None:
            self.no_supplied_data = True
            self.new_bulk_frame.error_dialog.close()
        else:
            self.no_supplied_data = False
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1747497.2, 5428082.0,
                                      1747710.3, 5428318.7)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()

    def tearDown(self):
        """Runs after each test."""
        self.new_bulk_frame.btn_exit.click()

    def test_ui_on_geometry_drawn(self):
        """UI comboboxes enable when geometry is drawn"""
        self.new_bulk_frame.database.open_cursor()
        if self.no_supplied_data is True:
            # insert capture source
            sql = 'SELECT buildings_common.fn_capture_source_insert(1, NULL);'
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.capture_source = result.fetchall()[0][0]
            # insert supplied data
            sql = "SELECT buildings_bulk_load.fn_supplied_datasets_insert('Test Data Insert', 1)"
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.dataset = result.fetchall()[0][0]
            # add geoms to bl
            sql = "SELECT buildings_bulk_load.fn_bulk_load_outlines_insert(%s, NULL, 2, 1, %s, NULL, NULL, NULL, '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441')"
            self.new_bulk_frame.database.execute_no_commit(sql, (self.dataset, self.capture_source))
            # reload setup
            self.new_bulk_frame.btn_reset.setEnabled(1)
            self.new_bulk_frame.reload_setup()
            self.new_bulk_frame.populate_lookup_comboboxes()
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1747497.2, 5428082.0,
                                      1747710.3, 5428318.7)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        QTest.qWait(300)
        # tests
        self.assertTrue(self.new_bulk_frame.btn_save.isEnabled())
        self.assertTrue(self.new_bulk_frame.btn_reset.isEnabled())
        self.assertTrue(self.new_bulk_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.new_bulk_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.new_bulk_frame.cmb_ta.isEnabled())
        self.assertTrue(self.new_bulk_frame.cmb_town.isEnabled())
        self.assertTrue(self.new_bulk_frame.cmb_suburb.isEnabled())
        self.new_bulk_frame.database.rollback_open_cursor()

    def test_reset_button(self):
        """Indexes are reset and comboxes disabled when reset is called"""
        self.new_bulk_frame.database.open_cursor()
        if self.no_supplied_data is True:
            # insert capture source
            sql = 'SELECT buildings_common.fn_capture_source_insert(1, NULL);'
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.capture_source = result.fetchall()[0][0]
            # insert supplied data
            sql = "SELECT buildings_bulk_load.fn_supplied_datasets_insert('Test Data Insert', 1)"
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.dataset = result.fetchall()[0][0]
            # add geoms to bl
            sql = "SELECT buildings_bulk_load.fn_bulk_load_outlines_insert(%s, NULL, 2, 1, %s, NULL, NULL, NULL, '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441')"
            self.new_bulk_frame.database.execute_no_commit(sql, (self.dataset, self.capture_source))
            # reload setup
            self.new_bulk_frame.btn_reset.setEnabled(1)
            self.new_bulk_frame.reload_setup()
            self.new_bulk_frame.populate_lookup_comboboxes()
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1747497.2, 5428082.0,
                                      1747710.3, 5428318.7)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
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
        self.new_bulk_frame.database.rollback_open_cursor()

    def test_new_outline_insert(self):
        """Data added to correct tables when save clicked"""
        self.new_bulk_frame.database.open_cursor()
        if self.no_supplied_data is True:
            # insert capture source
            sql = 'SELECT buildings_common.fn_capture_source_insert(1, NULL);'
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.capture_source = result.fetchall()[0][0]
            # insert supplied data
            sql = "SELECT buildings_bulk_load.fn_supplied_datasets_insert('Test Data Insert', 1)"
            result = self.new_bulk_frame.database.execute_no_commit(sql)
            self.dataset = result.fetchall()[0][0]
            # add geoms to bl
            sql = "SELECT buildings_bulk_load.fn_bulk_load_outlines_insert(%s, NULL, 2, 1, %s, NULL, NULL, NULL, '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441')"
            self.new_bulk_frame.database.execute_no_commit(sql, (self.dataset, self.capture_source))
            # reload setup
            self.new_bulk_frame.btn_reset.setEnabled(1)
            self.new_bulk_frame.reload_setup()
            self.new_bulk_frame.populate_lookup_comboboxes()
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        # add geom
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1747497.2, 5428082.0, 1747710.3, 5428318.7)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747591, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428102)),
                         delay=300)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747520, 5428152)),
                         delay=300)
        QTest.qWait(300)
        # change indexes of comboboxes
        self.new_bulk_frame.cmb_capture_method.setCurrentIndex(1)
        self.new_bulk_frame.cmb_capture_source.setCurrentIndex(0)
        self.new_bulk_frame.cmb_ta.setCurrentIndex(0)
        self.new_bulk_frame.cmb_town.setCurrentIndex(0)
        self.new_bulk_frame.cmb_suburb.setCurrentIndex(0)
        self.new_bulk_frame.save_clicked(commit_status=False)
        sql = 'SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.new_bulk_frame.database.rollback_open_cursor()


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessBulkNewOutlinesTest)
unittest.TextTestRunner(verbosity=2).run(suite)
