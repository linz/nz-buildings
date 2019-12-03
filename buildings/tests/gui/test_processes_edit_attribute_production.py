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

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QMessageBox
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
            if action.text() == "Edit Attributes":
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_ui_on_geom_selected(self):
        """UI and Canvas behave correctly when geometry is selected"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878035.0, 5555256.0)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878132.1, 5555323.9)),
            delay=30,
        )
        QTest.qWait(10)
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())

        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "Current")
        self.assertEqual(
            self.edit_dialog.cmb_capture_method.currentText(), "Feature Extraction"
        )
        self.assertEqual(
            self.edit_dialog.cmb_capture_source.currentText(),
            u"1- Imagery One- NZ Aerial Imagery",
        )
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "Aro Valley")

    def test_reset_clicked(self):
        """Check comboboxes reset correctly when 'reset' called"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878132.1, 5555323.9)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.btn_edit_reset.click()
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "")
        self.assertFalse(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_capture_source.currentText(), "")
        self.assertFalse(self.edit_dialog.cmb_lifecycle_stage.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "")
        self.assertFalse(self.edit_dialog.cmb_ta.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "")
        self.assertFalse(self.edit_dialog.cmb_town.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "")
        self.assertFalse(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "")

    def test_save_clicked(self):
        """Check attributes are updated when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878137.41, 5555313.84)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.cmb_lifecycle_stage.setCurrentIndex(
            self.edit_dialog.cmb_lifecycle_stage.findText("Replaced")
        )
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText("Unknown")
        )
        self.edit_dialog.cmb_ta.setCurrentIndex(
            self.edit_dialog.cmb_ta.findText("Manawatu-Whanganui")
        )
        self.edit_dialog.cmb_town.setCurrentIndex(
            self.edit_dialog.cmb_town.findText("Palmerston North")
        )
        self.edit_dialog.cmb_suburb.setCurrentIndex(
            self.edit_dialog.cmb_suburb.findText("Hokowhitu")
        )

        self.edit_dialog.change_instance.edit_save_clicked(False)

        sql = "SELECT lifecycle_stage_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings.building_outlines WHERE building_outline_id = %s"
        result = db._execute(sql, (self.edit_dialog.building_outline_id,))
        result = result.fetchall()[0]
        # lifecycle_stage
        sql = (
            "SELECT value FROM buildings.lifecycle_stage WHERE lifecycle_stage_id = %s;"
        )
        lifecycle_stage = db._execute(sql, (result[0],))
        lifecycle_stage = lifecycle_stage.fetchall()[0][0]
        self.assertEqual("Replaced", lifecycle_stage)
        # capture method
        sql = "SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;"
        capture_method = db._execute(sql, (result[1],))
        capture_method = capture_method.fetchall()[0][0]
        self.assertEqual("Unknown", capture_method)
        # suburb
        sql = "SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;"
        suburb = db._execute(sql, (result[2],))
        suburb = suburb.fetchall()[0][0]
        self.assertEqual("Hokowhitu", suburb)
        # town
        sql = "SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;"
        town_city = db._execute(sql, (result[3],))
        town_city = town_city.fetchall()[0][0]
        self.assertEqual("Palmerston North", town_city)
        # territorial Authority
        sql = "SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;"
        territorial_authority = db._execute(sql, (result[4],))
        territorial_authority = territorial_authority.fetchall()[0][0]
        self.assertEqual("Manawatu-Whanganui", territorial_authority)

        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "")

        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.db.rollback_open_cursor()

    def test_edit_mutiple_attributes(self):
        """Checks Multiple outlines with the same attributes can be edited together"""
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878042, 5555668, 1878327, 5555358)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878149, 5555640)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878203, 5555640)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878203, 5555384)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878149, 5555384)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878203, 5555384)),
            delay=50,
        )
        QTest.qWait(100)
        self.edit_dialog.cmb_lifecycle_stage.setCurrentIndex(
            self.edit_dialog.cmb_lifecycle_stage.findText("Replaced")
        )
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText("Unknown")
        )
        self.edit_dialog.cmb_ta.setCurrentIndex(
            self.edit_dialog.cmb_ta.findText("Manawatu-Whanganui")
        )
        self.edit_dialog.cmb_town.setCurrentIndex(
            self.edit_dialog.cmb_town.findText("Palmerston North")
        )
        self.edit_dialog.cmb_suburb.setCurrentIndex(
            self.edit_dialog.cmb_suburb.findText("Hokowhitu")
        )

        self.edit_dialog.change_instance.edit_save_clicked(False)

        for i in self.edit_dialog.ids:
            sql = "SELECT lifecycle_stage_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings.building_outlines WHERE building_outline_id = %s;"
            result = db._execute(sql, (i,))
            result = result.fetchall()[0]
            # lifecycle_stage
            sql = "SELECT value FROM buildings.lifecycle_stage WHERE lifecycle_stage_id = %s;"
            lifecycle_stage = db._execute(sql, (result[0],))
            lifecycle_stage = lifecycle_stage.fetchall()[0][0]
            self.assertEqual("Replaced", lifecycle_stage)
            # capture method
            sql = "SELECT value FROM buildings_common.capture_method WHERE capture_method_id = %s;"
            capture_method = db._execute(sql, (result[1],))
            capture_method = capture_method.fetchall()[0][0]
            self.assertEqual("Unknown", capture_method)
            # suburb
            sql = "SELECT suburb_4th FROM buildings_reference.suburb_locality WHERE suburb_locality_id = %s;"
            suburb = db._execute(sql, (result[2],))
            suburb = suburb.fetchall()[0][0]
            self.assertEqual("Hokowhitu", suburb)
            # town
            sql = "SELECT name FROM buildings_reference.town_city WHERE town_city_id = %s;"
            town_city = db._execute(sql, (result[3],))
            town_city = town_city.fetchall()[0][0]
            self.assertEqual("Palmerston North", town_city)
            # territorial Authority
            sql = "SELECT name FROM buildings_reference.territorial_authority WHERE territorial_authority_id = %s;"
            territorial_authority = db._execute(sql, (result[4],))
            territorial_authority = territorial_authority.fetchall()[0][0]
            self.assertEqual("Manawatu-Whanganui", territorial_authority)
            self.assertEqual(len(self.edit_dialog.ids), 4)

        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "")

        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.db.rollback_open_cursor()

    def test_selection_change(self):
        """Check change only occurs on currently selected outlines.
        This test protects against a regression of #55."""
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878042, 5555668, 1878327, 5555358)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878149, 5555640)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878203, 5555640)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878203, 5555384)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878149, 5555384)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878203, 5555384)),
            delay=50,
        )
        QTest.qWait(100)
        iface.actionSelect().trigger()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878202.1, 5555618.9)),
            delay=50,
        )
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText("Unknown")
        )

        self.edit_dialog.change_instance.edit_save_clicked(False)

        sql = "SELECT capture_method_id FROM buildings.building_outlines WHERE building_outline_id = 1031;"
        result = db._execute(sql)
        self.assertEqual(result.fetchall()[0][0], 1)
        sql = "SELECT capture_method_id FROM buildings.building_outlines WHERE building_outline_id = 1030;"
        result = db._execute(sql)
        self.assertNotEqual(result.fetchall()[0][0], 1)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.db.rollback_open_cursor()

    def test_select_geom_before_edit(self):
        """UI and Canvas behave correctly when one geometry is selected before edits button clicked"""
        self.production_frame.edit_dialog.close()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878035.0, 5555256.0)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878132.1, 5555323.9)),
            delay=30,
        )
        QTest.qWait(10)
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())

        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "Current")
        self.assertEqual(
            self.edit_dialog.cmb_capture_method.currentText(), "Feature Extraction"
        )
        self.assertEqual(
            self.edit_dialog.cmb_capture_source.currentText(),
            u"1- Imagery One- NZ Aerial Imagery",
        )
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "Aro Valley")

    def test_select_multiple_geom_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before edits button clicked"""
        self.production_frame.edit_dialog.close()
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878053.0, 5555587.0, 1878315.0, 5555655.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878053, 5555631)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878053, 5555612)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878315, 5555612)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878315, 5555631)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878315, 5555631)),
            delay=50,
        )
        QTest.qWait(100)
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_lifecycle_stage.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())

        self.assertEqual(self.edit_dialog.cmb_lifecycle_stage.currentText(), "Current")
        self.assertEqual(
            self.edit_dialog.cmb_capture_method.currentText(), "Feature Extraction"
        )
        self.assertEqual(
            self.edit_dialog.cmb_capture_source.currentText(),
            u"1- Imagery One- NZ Aerial Imagery",
        )
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "Wellington")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "Kelburn")

    def test_cannot_select_nonidentical_multiple_geoms_before_edit(self):
        """UI and Canvas behave correctly when multiple geometries are selected before edits button clicked"""
        self.production_frame.edit_dialog.close()
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878155.0, 5555119.0, 1878219.0, 5555190.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878155, 5555190)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878155, 5555119)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878219, 5555612)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878219, 5555190)),
            delay=50,
        )
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878219, 5555190)),
            delay=50,
        )
        QTest.qWait(100)
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()
        self.edit_dialog.change_instance.error_dialog.close()
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_lifecycle_stage.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_ta.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_town.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_suburb.isEnabled())

    def test_end_lifespan_of_building_pass(self):
        """test that ending lifespan of removed building works"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878035.0, 5555256.0)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878038.1, 5555312.6)),
            delay=30,
        )

        btn_yes = self.edit_dialog.change_instance.msgbox_remove.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.edit_dialog.change_instance.end_lifespan(False)

        sql = "SELECT end_lifespan FROM buildings.building_outlines WHERE building_outline_id = 1006;"
        result = db._execute(sql)
        self.assertNotEqual(result.fetchone()[0], None)
        sql = "SELECT end_lifespan FROM buildings.buildings WHERE building_id = 10006;"
        result = db._execute(sql)
        self.assertNotEqual(result.fetchone()[0], None)
        sql = "SELECT count(*) FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = 1006;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], 0)
        sql = "SELECT count(*) FROM buildings_bulk_load.removed WHERE building_outline_id = 1006;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], 0)
        self.edit_dialog.db.rollback_open_cursor()
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.editing_layer.removeSelection()

    def test_end_lifespan_of_building_fails(self):
        """test that ending lifespan of related building fails"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1878035.0, 5555256.0)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878420.4, 5555426.8)),
            delay=30,
        )
        btn_yes = self.edit_dialog.change_instance.msgbox_remove.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.edit_dialog.change_instance.end_lifespan(False)
        self.edit_dialog.change_instance.error_dialog.close()
        sql = "SELECT end_lifespan FROM buildings.building_outlines WHERE building_outline_id = 1033;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], None)
        sql = "SELECT end_lifespan FROM buildings.buildings WHERE building_id = 10033;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], None)
        sql = "SELECT count(*) FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = 1033;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], 1)
        sql = "SELECT count(*) FROM buildings_bulk_load.related WHERE building_outline_id = 1033;"
        result = db._execute(sql)
        self.assertEquals(result.fetchone()[0], 2)
        self.edit_dialog.db.rollback_open_cursor()
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.editing_layer.removeSelection()

    def test_modified_date_on_save(self):
        """Check modified date is updated when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(
            widget,
            Qt.RightButton,
            pos=canvas_point(QgsPointXY(1747651, 5428152)),
            delay=50,
        )
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878137.41, 5555313.84)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.cmb_lifecycle_stage.setCurrentIndex(
            self.edit_dialog.cmb_lifecycle_stage.findText("Replaced")
        )
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText("Unknown")
        )
        self.edit_dialog.cmb_ta.setCurrentIndex(
            self.edit_dialog.cmb_ta.findText("Manawatu-Whanganui")
        )
        self.edit_dialog.cmb_town.setCurrentIndex(
            self.edit_dialog.cmb_town.findText("Palmerston North")
        )
        self.edit_dialog.cmb_suburb.setCurrentIndex(
            self.edit_dialog.cmb_suburb.findText("Hokowhitu")
        )

        self.edit_dialog.change_instance.edit_save_clicked(False)
        sql = "SELECT now()::timestamp;"
        result = db._execute(sql)
        time = result.fetchall()[0]

        # building_outline modified date
        sql = "SELECT last_modified FROM buildings.building_outlines WHERE building_outline_id = %s;"
        result = db._execute(sql, (self.edit_dialog.building_outline_id,))
        bo_modified_date = result.fetchall()[0]

        self.assertEqual(bo_modified_date, time)

        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.edit_dialog.db.rollback_open_cursor()
