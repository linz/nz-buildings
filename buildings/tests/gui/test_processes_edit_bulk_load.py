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
from qgis.core import QgsRectangle, QgsPoint, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkLoadEditOutlinesTest(unittest.TestCase):
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
        self.menu_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.rad_edit.click()

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
        self.assertTrue(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())

    def test_ui_on_geom_selected(self):
        """UI and Canvas behave correctly when geometry is selected"""
        iface.actionSelect().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878035.0, 5555256.0)),
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
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.qWait(10)
        self.assertTrue(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_status.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())

        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), 'Supplied')
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), 'Feature Extraction')
        self.assertEqual(self.bulk_load_frame.cmb_capture_source.currentText(), u'NZ Aerial Imagery- Replace with link to LDS table...- None')
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), 'Aro Valley')

    def test_ui_on_geom_changed_and_selected(self):
        """UI and Canvas behave correctly when both selections and geometry changes occur"""
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
        iface.actionSelect().trigger()
        QTest.qWait(10)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.qWait(10)

        self.assertTrue(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_status.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_status.currentText(), 'Supplied')
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), 'Feature Extraction')
        self.assertEqual(self.bulk_load_frame.cmb_capture_source.currentText(), u'NZ Aerial Imagery- Replace with link to LDS table...- None')
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), 'Aro Valley')

    def test_geometries_on_reset(self):
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
        self.bulk_load_frame.btn_edit_reset.click()
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

    def test_comboboxes_on_reset(self):
        """Check comboboxes reset correctly when 'reset' called"""
        iface.actionSelect().trigger()
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
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.btn_edit_reset.click()
        self.assertFalse(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), '')
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_capture_source.currentText(), '')
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), '')
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), '')
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), '')
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), '')

    def test_attributes_save_clicked(self):
        """Check attributes are updated when save clicked"""
        iface.actionSelect().trigger()
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
                         pos=canvas_point(QgsPoint(1878137.41, 5555313.84)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.cmb_capture_method.setCurrentIndex(self.bulk_load_frame.cmb_capture_method_2.findText('Unknown'))
        self.bulk_load_frame.cmb_ta.setCurrentIndex(self.bulk_load_frame.cmb_ta.findText('Manawatu-Whanganui'))
        self.bulk_load_frame.cmb_town.setCurrentIndex(self.bulk_load_frame.cmb_town.findText('Palmerston North'))
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(self.bulk_load_frame.cmb_suburb.findText('Hokowhitu'))
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = 'SELECT bulk_load_status_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s'
        result = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;'
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), status)
        # capture method
        sql = 'SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;'
        capture_method = db._execute(sql, (result[1],))
        capture_method = capture_method.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), capture_method)
        # suburb
        sql = 'SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;'
        suburb = db._execute(sql, (result[2],))
        suburb = suburb.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), suburb)
        # town
        sql = 'SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;'
        town_city = db._execute(sql, (result[3],))
        town_city = town_city.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), town_city)
        # territorial Authority
        sql = 'SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;'
        territorial_authority = db._execute(sql, (result[4],))
        territorial_authority = territorial_authority.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), territorial_authority)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_geometries_save_clicked(self):
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
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878132.1, 5555303.9)),
                           delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        for key in self.bulk_load_frame.geoms:
            sql = 'SELECT shape FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s'
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.bulk_load_frame.geoms[key])
        self.assertFalse(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_edit_mutiple_attributes(self):
        """Checks Multiple outlines with the same attributes can be edited together"""
        iface.actionSelectPolygon().trigger()
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
        zoom_rectangle = QgsRectangle(1878053.0, 5555587.0,
                                      1878315.0, 5555655.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878053, 5555631)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878053, 5555612)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878315, 5555612)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878315, 5555631)),
                         delay=50)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878315, 5555631)),
                         delay=50)
        QTest.qWait(100)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(self.bulk_load_frame.cmb_capture_method_2.findText('Unknown'))
        self.bulk_load_frame.cmb_ta.setCurrentIndex(self.bulk_load_frame.cmb_ta.findText('Manawatu-Whanganui'))
        self.bulk_load_frame.cmb_town.setCurrentIndex(self.bulk_load_frame.cmb_town.findText('Palmerston North'))
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(self.bulk_load_frame.cmb_suburb.findText('Hokowhitu'))
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        for i in self.bulk_load_frame.ids:
            sql = 'SELECT bulk_load_status_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
            result = db._execute(sql, (i,))
            result = result.fetchall()[0]
            # status
            sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;'
            status = db._execute(sql, (result[0],))
            status = status.fetchall()[0][0]
            self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), status)
            # capture method
            sql = 'SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;'
            capture_method = db._execute(sql, (result[1],))
            capture_method = capture_method.fetchall()[0][0]
            self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), capture_method)
            # suburb
            sql = 'SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;'
            suburb = db._execute(sql, (result[2],))
            suburb = suburb.fetchall()[0][0]
            self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), suburb)
            # town
            sql = 'SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;'
            town_city = db._execute(sql, (result[3],))
            town_city = town_city.fetchall()[0][0]
            self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), town_city)
            # territorial Authority
            sql = 'SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;'
            territorial_authority = db._execute(sql, (result[4],))
            territorial_authority = territorial_authority.fetchall()[0][0]
            self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), territorial_authority)
            self.assertEqual(len(self.bulk_load_frame.ids), 6)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()
        iface.actionSelect().trigger()

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
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.mousePress(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.mouseRelease(widget, Qt.LeftButton,
                           pos=canvas_point(QgsPoint(1878132.1, 5555303.9)),
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
        for key in self.bulk_load_frame.geoms:
            sql = 'SELECT shape FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
            result = db._execute(sql, (key,))
            result = result.fetchall()[0][0]
            self.assertEqual(result, self.bulk_load_frame.geoms[key])
        self.assertFalse(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()
