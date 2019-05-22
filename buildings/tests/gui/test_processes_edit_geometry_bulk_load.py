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

    Tests: Edit Bulk Loaded Outlines GUI Processes

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import (QgsCoordinateReferenceSystem, QgsPoint, QgsRectangle)
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkLoadEditOutlinesTest(unittest.TestCase):
    """Test Edit Bulk Outline GUI Processes"""
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
        self.edit_dialog = self.bulk_load_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == 'Edit Geometry':
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_ui_on_geom_changed(self):
        """UI and canvas behave correctly when geometry is changed"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747651, 5428152)),
                         delay=50)
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
                         pos=canvas_point(QgsPoint(1878204.8, 5555290.8)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878205.6, 5555283.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878215.6, 5555283.2)),
                           delay=30)
        QTest.qWait(10)
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), 'Trace Orthophotography')

    def test_reset_clicked(self):
        """Check Geometries reset correctly when 'reset' called"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747651, 5428152)),
                         delay=50)
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
                         pos=canvas_point(QgsPoint(1878204.8, 5555290.8)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878205.6, 5555283.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878215.6, 5555283.2)),
                           delay=30)
        QTest.qWait(10)
        self.edit_dialog.btn_edit_reset.click()
        layer = iface.activeLayer()
        idx = layer.fieldNameIndex('bulk_load_outline_id')
        for feature in layer.getFeatures():
            current_id = feature.attributes()[idx]
            current_shape = feature.geometry()
            wkt = current_shape.exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
            result = db._execute(sql, data=(wkt, ))
            current_shape = result.fetchall()[0][0]
            sql = 'SELECT shape from buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
            result = db._execute(sql, (current_id,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, current_shape)

    def test_save_clicked(self):
        """Check geometry is updated when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747651, 5428152)),
                         delay=50)
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
                         pos=canvas_point(QgsPoint(1878204.8, 5555290.8)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878205.6, 5555283.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878215.6, 5555283.2)),
                           delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        for key in self.bulk_load_frame.edit_dialog.geoms:
            sql = 'SELECT shape FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s'
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.edit_dialog.geoms[key])
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.edit_dialog.geoms = {}
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_edit_multiple_geometries(self):
        """Checks the geometries of multiple features can be edited at the same time"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747651, 5428152)),
                         delay=50)
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
                         pos=canvas_point(QgsPoint(1878204.8, 5555290.8)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878205.6, 5555283.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878215.6, 5555283.2)),
                           delay=30)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878210.2, 5555275.2)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878210.2, 5555275.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878222.6, 5555275.2)),
                           delay=30)
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        for key in self.bulk_load_frame.edit_dialog.geoms:
            sql = 'SELECT shape FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.edit_dialog.geoms[key])
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.edit_dialog.geoms = {}
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_capture_method_on_geometry_changed(self):
        """Check capture method is 'Trace Orthophotography' after the geometry changes occur. #100"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1747651, 5428152)),
                         delay=50)
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
                         pos=canvas_point(QgsPoint(1878204.8, 5555290.8)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878205.6, 5555283.2)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878215.6, 5555283.2)),
                           delay=30)
        QTest.qWait(10)

        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), 'Trace Orthophotography')
