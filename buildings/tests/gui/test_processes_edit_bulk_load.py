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
from qgis.core import QgsRectangle, QgsPoint, QgsCoordinateReferenceSystem, QgsExpression, QgsFeatureRequest
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkLoadEditOutlinesTest(unittest.TestCase):
    """Test Edit Bulk Outline GUI Processes"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get('buildings'):
            pass
        else:
            db.connect()
            cls.building_plugin = plugins.get('buildings')
            cls.dockwidget = cls.building_plugin.dockwidget
            cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger() 
        self.dockwidget = self.building_plugin.dockwidget
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
        self.assertFalse(self.bulk_load_frame.le_deletion_reason.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), '')
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
        self.assertFalse(self.bulk_load_frame.le_deletion_reason.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), '')
        self.assertTrue(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_suburb.isEnabled())

        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), 'Supplied')
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), 'Feature Extraction')
        self.assertEqual(self.bulk_load_frame.cmb_capture_source.currentText(), u'NZ Aerial Imagery- Replace with link to LDS table...- None')
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), 'Aro Valley')

    def test_select_geom_before_edit(self):
        """UI and Canvas behave correctly when geometry is selected before editing is toggled"""
        self.bulk_load_frame.btn_edit_cancel.click()
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
        iface.actionSelect().trigger()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878132.1, 5555323.9)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.rad_edit.click()
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

    def test_select_multiple_geom_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before editing is toggled"""
        self.bulk_load_frame.btn_edit_cancel.click()
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
        self.bulk_load_frame.rad_edit.click()
        iface.actionSelect().trigger()
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
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), 'Kelburn')

    def test_cannot_select_nonidentical_multiple_geoms_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before editing is toggled"""
        self.bulk_load_frame.btn_edit_cancel.click()
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
        zoom_rectangle = QgsRectangle(1878155.0, 5555119.0,
                                      1878219.0, 5555190.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878155, 5555190)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878155, 5555119)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878219, 5555612)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878219, 5555190)),
                         delay=50)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878219, 5555190)),
                         delay=50)
        QTest.qWait(100)
        self.bulk_load_frame.rad_edit.click()
        iface.actionSelect().trigger()
        self.bulk_load_frame.error_dialog.close()
        self.assertFalse(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())

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
        self.assertFalse(self.bulk_load_frame.le_deletion_reason.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), '')
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
        self.assertFalse(self.bulk_load_frame.le_deletion_reason.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), '')
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
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Added During QA'))
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(self.bulk_load_frame.cmb_capture_method_2.findText('Unknown'))
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
        self.assertEqual('Added During QA', status)
        # capture method
        sql = 'SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;'
        capture_method = db._execute(sql, (result[1],))
        capture_method = capture_method.fetchall()[0][0]
        self.assertEqual('Unknown', capture_method)
        # suburb
        sql = 'SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;'
        suburb = db._execute(sql, (result[2],))
        suburb = suburb.fetchall()[0][0]
        self.assertEqual('Hokowhitu', suburb)
        # town
        sql = 'SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;'
        town_city = db._execute(sql, (result[3],))
        town_city = town_city.fetchall()[0][0]
        self.assertEqual('Palmerston North', town_city)
        # territorial Authority
        sql = 'SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;'
        territorial_authority = db._execute(sql, (result[4],))
        territorial_authority = territorial_authority.fetchall()[0][0]
        self.assertEqual('Manawatu-Whanganui', territorial_authority)

        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), '')

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
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Added During QA'))
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
            self.assertEqual('Added During QA', status)
            # capture method
            sql = 'SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;'
            capture_method = db._execute(sql, (result[1],))
            capture_method = capture_method.fetchall()[0][0]
            self.assertEqual('Unknown', capture_method)
            # suburb
            sql = 'SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;'
            suburb = db._execute(sql, (result[2],))
            suburb = suburb.fetchall()[0][0]
            self.assertEqual('Hokowhitu', suburb)
            # town
            sql = 'SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;'
            town_city = db._execute(sql, (result[3],))
            town_city = town_city.fetchall()[0][0]
            self.assertEqual('Palmerston North', town_city)
            # territorial Authority
            sql = 'SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;'
            territorial_authority = db._execute(sql, (result[4],))
            territorial_authority = territorial_authority.fetchall()[0][0]
            self.assertEqual('Manawatu-Whanganui', territorial_authority)
            self.assertEqual(len(self.bulk_load_frame.ids), 6)

        self.assertEqual(self.bulk_load_frame.cmb_status.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_capture_method_2.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_suburb.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_town.currentText(), '')
        self.assertEqual(self.bulk_load_frame.cmb_ta.currentText(), '')

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

    def test_deleted_geom(self):
        """Check geom 'deleted' when save clicked
        This test protects against a regression of #59"""
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
                         pos=canvas_point(QgsPoint(1878037.5, 5555349.2)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.assertTrue(self.bulk_load_frame.le_deletion_reason.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), '')
        self.bulk_load_frame.le_deletion_reason.setText('Reason for deletion')

        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
        result = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;'
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual('Deleted During QA', status)
        # deletion description
        sql = 'SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;'
        reason = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        reason = reason.fetchall()[0][0]
        self.assertEqual('Reason for deletion', reason)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2010;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [])
        selection = len(self.bulk_load_frame.bulk_load_layer.selectedFeatures())
        self.assertEqual(selection, 0)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_multiple_deleted_geom(self):
        """Check multiple geoms 'deleted' when save clicked
        This test protects against a regression of #59"""
        expr = QgsExpression("bulk_load_outline_id=2010 or bulk_load_outline_id =2003")
        it = self.bulk_load_frame.bulk_load_layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.bulk_load_frame.bulk_load_layer.setSelectedFeatures(ids)
        self.bulk_load_frame.rad_edit.click()
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.le_deletion_reason.setText('Reason for deletion')
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2010 OR bulk_load_outline_id = 2003;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result[0][0], 3)
        self.assertEqual(result[1][0], 3)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2010 OR bulk_load_outline_id = 2003;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [])
        selection = len(self.bulk_load_frame.bulk_load_layer.selectedFeatures())
        self.assertEqual(selection, 0)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails(self):
        """Check 'deleting' geom fails when save clicked"""
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
                         pos=canvas_point(QgsPoint(1878090.9, 5555322.0)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.le_deletion_reason.setText('Reason for deletion')
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self.bulk_load_frame.error_dialog.close()
        sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
        result = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;'
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual('Supplied', status)
        # deletion description
        sql = 'SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;'
        reason = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        reason = reason.fetchall()
        self.assertEqual([], reason)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = 2031;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [(2031,)])
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails_reason(self):
        """Check 'delete' fail when enter none in 'reason for deletion' """
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
                         pos=canvas_point(QgsPoint(1878228.6, 5555334.9)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.le_deletion_reason.setText('Reason for deletion')
        self.bulk_load_frame.change_instance.edit_save_clicked(False)

        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878037.5, 5555349.2)),
                         delay=30)
        QTest.qWait(10)
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.assertTrue(self.bulk_load_frame.le_deletion_reason.isEnabled())
        # check autocompleting of the previous reason
        self.assertEqual(self.bulk_load_frame.le_deletion_reason.text(), 'Reason for deletion')
        self.bulk_load_frame.le_deletion_reason.setText('')

        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self.bulk_load_frame.error_dialog.close()

        sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
        result = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;'
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual('Supplied', status)
        # deletion description
        sql = 'SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;'
        reason = db._execute(sql, (self.bulk_load_frame.bulk_load_outline_id,))
        reason = reason.fetchall()
        self.assertEqual([], reason)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual([(2010,)], result)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails_multiple_selection(self):
        """Check nothing is changed when correct and incorrect outlines are deleted
        This test protects against a regression of #59"""
        expr = QgsExpression("bulk_load_outline_id=2003 or bulk_load_outline_id =2004")
        it = self.bulk_load_frame.bulk_load_layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.bulk_load_frame.bulk_load_layer.setSelectedFeatures(ids)
        self.bulk_load_frame.rad_edit.click()
        self.bulk_load_frame.cmb_status.setCurrentIndex(self.bulk_load_frame.cmb_status.findText('Deleted During QA'))
        self.bulk_load_frame.le_deletion_reason.setText('Reason for deletion')
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self.bulk_load_frame.error_dialog.close()
        sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2003 OR bulk_load_outline_id = 2004;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[1][0], 1)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2003;'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(result, 2003)
        # matched
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = 2004;'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(result, 2004)
        # selection
        selection = len(self.bulk_load_frame.bulk_load_layer.selectedFeatures())
        self.assertEqual(selection, 2)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_selection_change(self):
        """Check change only occurs on currently selected outlines.
        This test protects against a regression of #55."""
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
        iface.actionSelect().trigger()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878202.1, 5555618.9)),
                         delay=50)
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(self.bulk_load_frame.cmb_capture_method_2.findText('Unknown'))
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = 'SELECT capture_method_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2027;'
        result = db._execute(sql)
        self.assertEqual(result.fetchall()[0][0], 1)
        sql = 'SELECT capture_method_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2025;'
        result = db._execute(sql)
        self.assertNotEqual(result.fetchall()[0][0], 1)
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        self.bulk_load_frame.db.rollback_open_cursor()
