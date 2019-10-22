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

    Tests: Edit Production Outlines Processes

 ***************************************************************************/
"""

import unittest

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest
from qgis.core import QgsCoordinateReferenceSystem, QgsPointXY, QgsRectangle
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessProductionEditOutlinesTest(unittest.TestCase):
    """Test Edit Production Outline Processes"""

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
        sub_menu.setCurrentItem(sub_menu.findItems("Edit Outlines", Qt.MatchExactly)[0])
        self.production_frame = self.dockwidget.current_frame
        self.edit_dialog = self.production_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Geometry":
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_ui_on_geom_changed(self):
        """UI and canvas behave correctly when geometry is changed"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555291.6)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555298.1)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878211.4, 5555304.6)), delay=30)
        QTest.qWait(10)
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())

    def test_reset_clicked(self):
        """Check Geometries reset correctly when 'reset' called"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555291.6)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555298.1)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878211.4, 5555304.6)), delay=30)
        QTest.qWait(10)
        self.edit_dialog.btn_edit_reset.click()
        layer = iface.activeLayer()
        idx = layer.fields().indexFromName("building_outline_id")
        for feature in layer.getFeatures():
            current_id = feature.attributes()[idx]
            current_shape = feature.geometry()
            wkt = current_shape.asWkt()
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);"
            result = db._execute(sql, (wkt,))
            current_shape = result.fetchall()[0][0]
            sql = "SELECT shape from buildings.building_outlines WHERE building_outline_id = %s;"
            result = db._execute(sql, (current_id,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, current_shape)

    def test_save_clicked(self):
        """Check geometry is updated when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878151.0, 5555311.9)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878151.0, 5555311.9)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878132.1, 5555303.9)), delay=30)
        QTest.qWait(10)

        self.edit_dialog.change_instance.edit_save_clicked(False)

        for key in self.edit_dialog.geoms:
            sql = "SELECT shape FROM buildings.building_outlines WHERE building_outline_id = %s"
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.edit_dialog.geoms[key])
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.edit_dialog.geoms = {}
        self.edit_dialog.db.rollback_open_cursor()

    def test_edit_multiple_geometries(self):
        """Checks the geometries of multiple features can be edited at the same time"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878149, 5555311)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878149, 5555311)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878132.1, 5555303.9)), delay=30)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878210.2, 5555275.2)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878210.2, 5555275.2)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878222.6, 5555275.2)), delay=30)

        self.edit_dialog.change_instance.edit_save_clicked(False)

        for key in self.edit_dialog.geoms:
            sql = "SELECT shape FROM buildings.building_outlines WHERE building_outline_id = %s;"
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.edit_dialog.geoms[key])
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.edit_dialog.geoms = {}
        self.edit_dialog.db.rollback_open_cursor()

    def test_capture_method_on_geometry_changed(self):
        """Check capture method is 'Trace Orthophotography' after the geometry changes occur. #100"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555291.6)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878202.1, 5555298.1)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878211.4, 5555304.6)), delay=30)
        QTest.qWait(10)

        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "Trace Orthophotography")

    def test_modified_date_update_on_save(self):
        """Check modified_date is updated when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747651, 5428152)), delay=50)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878151.0, 5555311.9)), delay=30)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878151.0, 5555311.9)), delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878132.1, 5555303.9)), delay=30)
        QTest.qWait(10)

        self.edit_dialog.change_instance.edit_save_clicked(False)
        sql = "SELECT now()::timestamp;"
        result = db._execute(sql)
        time = result.fetchall()[0]

        for key in self.edit_dialog.geoms:
            sql = "SELECT last_modified FROM buildings.building_outlines WHERE building_outline_id = %s"
            result = db._execute(sql, (key,))
            bo_modified_date = result.fetchall()[0]
            self.assertEqual(bo_modified_date, time)

        self.edit_dialog.geoms = {}
        self.edit_dialog.db.rollback_open_cursor()
