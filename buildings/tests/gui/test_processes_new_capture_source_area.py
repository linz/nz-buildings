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

    Tests: New Capture Source Area GUI Processes

 ***************************************************************************/
"""

import os
import unittest

from qgis.utils import iface, plugins
from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsPointXY, QgsRectangle

from buildings.utilities import database as db


class ProcessCaptureSourceTest(unittest.TestCase):
    """Test New Capture Source Area GUI Processes"""

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
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Capture Sources", Qt.MatchExactly)[0])
        self.capture_frame = self.dockwidget.current_frame
        self.capture_frame.btn_new_geometry.click()
        self.capture_area_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_area_frame.btn_exit.click()

    def test_add_new_geometry(self):
        """Check new capture source area added by hand draw."""
        sql = "SELECT area_polygon_id FROM buildings_reference.capture_source_area;"
        result = db._execute(sql)
        result = result.fetchall()

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1877987, 5555614, 1880088, 5554738)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877898.8, 5555614.9)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877896.5, 5555450.5)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877782.1, 5555450.8)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877782.1, 5555450.8)), delay=-1)
        QTest.qWait(1)

        self.assertTrue(self.capture_area_frame.le_external_id.isEnabled())
        self.assertTrue(self.capture_area_frame.le_area_title.isEnabled())

        self.capture_area_frame.le_external_id.setText("Test external id")
        self.capture_area_frame.le_area_title.setText("Test area title")

        self.capture_area_frame.save_clicked(False)

        result2 = db._execute(sql)
        result2 = result2.fetchall()

        self.assertEqual(len(result) + 1, len(result2))

        self.capture_area_frame.db.rollback_open_cursor()

    def test_select_singlepolygon_from_layer(self):
        """Check new capture source area added by selecting polygon from other layer"""
        sql = "SELECT area_polygon_id FROM buildings_reference.capture_source_area;"
        result = db._execute(sql)
        result = result.fetchall()

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testdata/test_external_area_polygon.shp")
        layer = iface.addVectorLayer(path, "", "ogr")
        layer2 = iface.addVectorLayer(path, "", "ogr")
        iface.setActiveLayer(layer2)

        self.capture_area_frame.rb_select_from_layer.setChecked(True)
        self.capture_area_frame.mcb_selection_layer.hidePopup()
        self.capture_area_frame.mcb_selection_layer.setLayer(layer2)

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1877987, 5555614, 1880088, 5554738)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877590.8, 5555370.0)), delay=-1)
        QTest.qWait(1)

        self.assertTrue(self.capture_area_frame.le_external_id.isEnabled())
        self.assertTrue(self.capture_area_frame.le_area_title.isEnabled())

        self.capture_area_frame.le_external_id.setText("Test external id")
        self.capture_area_frame.le_area_title.setText("Test area title")

        self.capture_area_frame.save_clicked(False)

        result2 = db._execute(sql)
        result2 = result2.fetchall()

        self.assertEqual(len(result) + 1, len(result2))

        self.capture_area_frame.db.rollback_open_cursor()

        self.capture_area_frame.rb_select_from_layer.setChecked(False)
        # remove temporary layers from canvas
        QgsProject.instance().removeMapLayer(layer.id())
        QgsProject.instance().removeMapLayer(layer2.id())

    def test_select_multipolygon_from_layer(self):
        """Check new capture source area added by selecting multipolygon from other layer"""
        sql = "SELECT area_polygon_id FROM buildings_reference.capture_source_area;"
        result = db._execute(sql)
        result = result.fetchall()

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testdata/test_external_area_multipolygon.shp")
        layer = iface.addVectorLayer(path, "", "ogr")
        layer2 = iface.addVectorLayer(path, "", "ogr")
        iface.setActiveLayer(layer2)

        self.capture_area_frame.rb_select_from_layer.setChecked(True)
        self.capture_area_frame.mcb_selection_layer.hidePopup()
        self.capture_area_frame.mcb_selection_layer.setLayer(layer2)

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1877987, 5555614, 1880088, 5554738)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877590.8, 5555370.0)), delay=-1)
        QTest.qWait(1)

        self.assertTrue(self.capture_area_frame.le_external_id.isEnabled())
        self.assertTrue(self.capture_area_frame.le_area_title.isEnabled())

        self.capture_area_frame.le_external_id.setText("Test external id")
        self.capture_area_frame.le_area_title.setText("Test area title")

        self.capture_area_frame.save_clicked(False)

        result2 = db._execute(sql)
        result2 = result2.fetchall()

        self.assertEqual(len(result) + 1, len(result2))

        self.capture_area_frame.db.rollback_open_cursor()

        self.capture_area_frame.rb_select_from_layer.setChecked(False)
        # remove temporary layers from canvas
        QgsProject.instance().removeMapLayer(layer.id())
        QgsProject.instance().removeMapLayer(layer2.id())

    def test_select_wrong_projection(self):
        """Check error messages by selecting from wrong projection"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testdata/test_external_area_polygon_wrong_proj.shp")
        layer = iface.addVectorLayer(path, "", "ogr")
        layer2 = iface.addVectorLayer(path, "", "ogr")
        iface.setActiveLayer(layer2)

        self.capture_area_frame.rb_select_from_layer.setChecked(True)
        self.capture_area_frame.mcb_selection_layer.hidePopup()
        self.capture_area_frame.mcb_selection_layer.setLayer(layer2)
        print(self.capture_area_frame.l_wrong_projection.text())

        self.assertNotEqual(self.capture_area_frame.l_wrong_projection.text(), "")
        self.assertIn("INCORRECT CRS", self.capture_area_frame.error_dialog.tb_error_report.toPlainText())
        self.capture_area_frame.error_dialog.close()

        self.capture_area_frame.rb_select_from_layer.setChecked(False)
        # remove temporary layers from canvas
        QgsProject.instance().removeMapLayer(layer.id())
        QgsProject.instance().removeMapLayer(layer2.id())

    def test_reset_clicked(self):
        """Check if gui is reset when reset clicked."""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1877987, 5555614, 1880088, 5554738)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877795.6, 5555615.2)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877898.8, 5555614.9)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877896.5, 5555450.5)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1877782.1, 5555450.8)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1877782.1, 5555450.8)), delay=-1)
        QTest.qWait(1)

        self.assertTrue(self.capture_area_frame.le_external_id.isEnabled())
        self.assertTrue(self.capture_area_frame.le_area_title.isEnabled())

        self.capture_area_frame.btn_reset.click()

        self.assertFalse(self.capture_area_frame.le_external_id.isEnabled())
        self.assertFalse(self.capture_area_frame.le_area_title.isEnabled())
        self.assertFalse(self.capture_area_frame.rb_select_from_layer.isChecked())
        self.assertEqual(self.capture_area_frame.geom, None)
