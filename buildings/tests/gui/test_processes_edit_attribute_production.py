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

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import QgsCoordinateReferenceSystem, QgsPoint, QgsRectangle
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
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Edit Outlines', Qt.MatchExactly)[0])
        self.production_frame = self.dockwidget.current_frame
        self.production_frame.tbtn_edits.setDefaultAction(self.production_frame.action_edit_attribute)
        self.production_frame.tbtn_edits.click()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_ui_on_geom_selected(self):
        """UI and Canvas behave correctly when geometry is selected"""
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
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())

        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), 'Current')
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), 'Feature Extraction')
        self.assertEqual(self.production_frame.cmb_capture_source.currentText(),
                         u'NZ Aerial Imagery- external_source_id will link to the imagery_survey_id from https://data.linz.govt.nz/layer/95677-nz-imagery-surveys/- 1')
        self.assertEqual(self.production_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), 'Aro Valley')

    def test_reset_clicked(self):
        """Check comboboxes reset correctly when 'reset' called"""
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
        self.production_frame.btn_reset.click()
        self.assertFalse(self.production_frame.btn_save.isEnabled())
        self.assertFalse(self.production_frame.btn_reset.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_method.isEnabled())
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), '')
        self.assertFalse(self.production_frame.cmb_capture_source.isEnabled())
        self.assertEqual(self.production_frame.cmb_capture_source.currentText(), '')
        self.assertFalse(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), '')
        self.assertFalse(self.production_frame.cmb_ta.isEnabled())
        self.assertEqual(self.production_frame.cmb_ta.currentText(), '')
        self.assertFalse(self.production_frame.cmb_town.isEnabled())
        self.assertEqual(self.production_frame.cmb_town.currentText(), '')
        self.assertFalse(self.production_frame.cmb_suburb.isEnabled())
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), '')

    def test_save_clicked(self):
        """Check attributes are updated when save clicked"""
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
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(self.production_frame.cmb_lifecycle_stage.findText('Replaced'))
        self.production_frame.cmb_capture_method.setCurrentIndex(self.production_frame.cmb_capture_method.findText('Unknown'))
        self.production_frame.cmb_ta.setCurrentIndex(self.production_frame.cmb_ta.findText('Manawatu-Whanganui'))
        self.production_frame.cmb_town.setCurrentIndex(self.production_frame.cmb_town.findText('Palmerston North'))
        self.production_frame.cmb_suburb.setCurrentIndex(self.production_frame.cmb_suburb.findText('Hokowhitu'))

        self.production_frame.change_instance.save_clicked(False)

        sql = 'SELECT lifecycle_stage_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings.building_outlines WHERE building_outline_id = %s'
        result = db._execute(sql, (self.production_frame.building_outline_id,))
        result = result.fetchall()[0]
        # lifecycle_stage
        sql = 'SELECT value FROM buildings.lifecycle_stage WHERE lifecycle_stage_id = %s;'
        lifecycle_stage = db._execute(sql, (result[0],))
        lifecycle_stage = lifecycle_stage.fetchall()[0][0]
        self.assertEqual('Replaced', lifecycle_stage)
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

        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), '')
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), '')
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), '')
        self.assertEqual(self.production_frame.cmb_town.currentText(), '')
        self.assertEqual(self.production_frame.cmb_ta.currentText(), '')

        self.production_frame.ids = []
        self.production_frame.building_outline_id = None
        self.production_frame.db.rollback_open_cursor()

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
        zoom_rectangle = QgsRectangle(1878042, 5555668,
                                      1878327, 5555358)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878149, 5555640)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878203, 5555640)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878203, 5555384)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878149, 5555384)),
                         delay=50)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878203, 5555384)),
                         delay=50)
        QTest.qWait(100)
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(self.production_frame.cmb_lifecycle_stage.findText('Replaced'))
        self.production_frame.cmb_capture_method.setCurrentIndex(self.production_frame.cmb_capture_method.findText('Unknown'))
        self.production_frame.cmb_ta.setCurrentIndex(self.production_frame.cmb_ta.findText('Manawatu-Whanganui'))
        self.production_frame.cmb_town.setCurrentIndex(self.production_frame.cmb_town.findText('Palmerston North'))
        self.production_frame.cmb_suburb.setCurrentIndex(self.production_frame.cmb_suburb.findText('Hokowhitu'))

        self.production_frame.change_instance.save_clicked(False)

        for i in self.production_frame.ids:
            sql = 'SELECT lifecycle_stage_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings.building_outlines WHERE building_outline_id = %s;'
            result = db._execute(sql, (i,))
            result = result.fetchall()[0]
            # lifecycle_stage
            sql = 'SELECT value FROM buildings.lifecycle_stage WHERE lifecycle_stage_id = %s;'
            lifecycle_stage = db._execute(sql, (result[0],))
            lifecycle_stage = lifecycle_stage.fetchall()[0][0]
            self.assertEqual('Replaced', lifecycle_stage)
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
            self.assertEqual(len(self.production_frame.ids), 4)

        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), '')
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), '')
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), '')
        self.assertEqual(self.production_frame.cmb_town.currentText(), '')
        self.assertEqual(self.production_frame.cmb_ta.currentText(), '')

        self.production_frame.ids = []
        self.production_frame.building_outline_id = None
        self.production_frame.db.rollback_open_cursor()

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
        zoom_rectangle = QgsRectangle(1878042, 5555668,
                                      1878327, 5555358)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878149, 5555640)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878203, 5555640)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878203, 5555384)),
                         delay=50)
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878149, 5555384)),
                         delay=50)
        QTest.mouseClick(widget, Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878203, 5555384)),
                         delay=50)
        QTest.qWait(100)
        iface.actionSelect().trigger()
        QTest.mouseClick(widget, Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878202.1, 5555618.9)),
                         delay=50)
        self.production_frame.cmb_capture_method.setCurrentIndex(self.production_frame.cmb_capture_method.findText('Unknown'))

        self.production_frame.change_instance.save_clicked(False)

        sql = 'SELECT capture_method_id FROM buildings.building_outlines WHERE building_outline_id = 1031;'
        result = db._execute(sql)
        self.assertEqual(result.fetchall()[0][0], 1)
        sql = 'SELECT capture_method_id FROM buildings.building_outlines WHERE building_outline_id = 1030;'
        result = db._execute(sql)
        self.assertNotEqual(result.fetchall()[0][0], 1)
        self.production_frame.ids = []
        self.production_frame.building_outline_id = None
        self.production_frame.db.rollback_open_cursor()

    def test_select_geom_before_edit(self):
        """UI and Canvas behave correctly when one geometry is selected before editing is toggled"""
        self.production_frame.btn_exit_edits.click()
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
        self.production_frame.tbtn_edits.setDefaultAction(self.production_frame.action_edit_attribute)
        self.production_frame.tbtn_edits.click()
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())

        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), 'Current')
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), 'Feature Extraction')
        self.assertEqual(self.production_frame.cmb_capture_source.currentText(),
                         u'NZ Aerial Imagery- external_source_id will link to the imagery_survey_id from https://data.linz.govt.nz/layer/95677-nz-imagery-surveys/- 1')
        self.assertEqual(self.production_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), 'Aro Valley')

    def test_select_multiple_geom_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before editing is toggled"""
        self.production_frame.btn_exit_edits.click()
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
        self.production_frame.tbtn_edits.setDefaultAction(self.production_frame.action_edit_attribute)
        self.production_frame.tbtn_edits.click()
        self.assertTrue(self.production_frame.btn_save.isEnabled())
        self.assertTrue(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_method.isEnabled())
        self.assertTrue(self.production_frame.cmb_capture_source.isEnabled())
        self.assertTrue(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.production_frame.cmb_ta.isEnabled())
        self.assertTrue(self.production_frame.cmb_town.isEnabled())
        self.assertTrue(self.production_frame.cmb_suburb.isEnabled())

        self.assertEqual(self.production_frame.cmb_lifecycle_stage.currentText(), 'Current')
        self.assertEqual(self.production_frame.cmb_capture_method.currentText(), 'Feature Extraction')
        self.assertEqual(self.production_frame.cmb_capture_source.currentText(),
                         u'NZ Aerial Imagery- external_source_id will link to the imagery_survey_id from https://data.linz.govt.nz/layer/95677-nz-imagery-surveys/- 1')
        self.assertEqual(self.production_frame.cmb_ta.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_town.currentText(), 'Wellington')
        self.assertEqual(self.production_frame.cmb_suburb.currentText(), 'Kelburn')

    def test_cannot_select_nonidentical_multiple_geoms_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before editing is toggled"""
        self.production_frame.btn_exit_edits.click()
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
        self.production_frame.tbtn_edits.setDefaultAction(self.production_frame.action_edit_attribute)
        self.production_frame.tbtn_edits.click()
        self.production_frame.error_dialog.close()
        self.assertFalse(self.production_frame.btn_save.isEnabled())
        self.assertFalse(self.production_frame.btn_reset.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_method.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.production_frame.cmb_lifecycle_stage.isEnabled())
        self.assertFalse(self.production_frame.cmb_ta.isEnabled())
        self.assertFalse(self.production_frame.cmb_town.isEnabled())
        self.assertFalse(self.production_frame.cmb_suburb.isEnabled())
