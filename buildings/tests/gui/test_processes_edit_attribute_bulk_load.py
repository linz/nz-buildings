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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpression,
    QgsFeatureRequest,
    QgsPointXY,
    QgsRectangle,
)
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
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Bulk Load", Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.edit_dialog = self.bulk_load_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def _clear_message_bar(self):
        """Deletes all messages in a message bar"""

        layout = self.edit_dialog.message_bar.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                raise RuntimeError('Unclear what "self" was intended to refer to here - see source')
                # self.clear_layout(child.layout())

    def test_ui_on_geom_selected(self):
        """UI and Canvas behave correctly when geometry is selected"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.assertTrue(self.edit_dialog.cmb_status.isEnabled())
        self.assertFalse(self.edit_dialog.le_deletion_reason.isEnabled())
        self.assertEqual(self.edit_dialog.le_deletion_reason.text(), "")
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())

        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "Supplied")
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

    def test_select_geom_before_edit(self):
        """UI and Canvas behave correctly when geometry is selected before edits button clicked"""
        self.bulk_load_frame.edit_dialog.close()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.assertTrue(self.edit_dialog.cmb_status.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())

        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "Supplied")
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
        self.bulk_load_frame.edit_dialog.close()
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.assertTrue(self.edit_dialog.cmb_status.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "Supplied")
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
        self.edit_dialog.close()
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self._clear_message_bar()
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_status.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_ta.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_town.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_suburb.isEnabled())

    def test_reset_clicked(self):
        """Check comboboxes reset correctly when 'reset' called"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.assertFalse(self.edit_dialog.cmb_status.isEnabled())
        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "")
        self.assertFalse(self.edit_dialog.le_deletion_reason.isEnabled())
        self.assertEqual(self.edit_dialog.le_deletion_reason.text(), "")
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
        QTest.mouseDClick(
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
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Added During QA")
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
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = "SELECT bulk_load_status_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s"
        result = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = "SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;"
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual("Added During QA", status)
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

        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "")

        self.bulk_load_frame.ids = []
        self.bulk_load_frame.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_edit_mutiple_attributes(self):
        """Checks Multiple outlines with the same attributes can be edited together"""
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Added During QA")
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
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        for i in self.edit_dialog.ids:
            sql = "SELECT bulk_load_status_id, capture_method_id, suburb_locality_id, town_city_id, territorial_authority_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;"
            result = db._execute(sql, (i,))
            result = result.fetchall()[0]
            # status
            sql = "SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;"
            status = db._execute(sql, (result[0],))
            status = status.fetchall()[0][0]
            self.assertEqual("Added During QA", status)
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
            self.assertEqual(len(self.bulk_load_frame.ids), 6)

        self.assertEqual(self.edit_dialog.cmb_status.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_capture_method.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_suburb.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_town.currentText(), "")
        self.assertEqual(self.edit_dialog.cmb_ta.currentText(), "")

        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_geom(self):
        """Check geom 'deleted' when save clicked
        This test protects against a regression of #59"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
            pos=canvas_point(QgsPointXY(1878037.5, 5555349.2)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.assertTrue(self.edit_dialog.le_deletion_reason.isEnabled())
        self.assertEqual(self.edit_dialog.le_deletion_reason.text(), "")
        self.edit_dialog.le_deletion_reason.setText("Reason for deletion")

        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = "SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;"
        result = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = "SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;"
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual("Deleted During QA", status)
        # deletion description
        sql = "SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;"
        reason = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        reason = reason.fetchall()[0][0]
        self.assertEqual("Reason for deletion", reason)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2010;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [])
        selection = len(self.edit_dialog.editing_layer.selectedFeatures())
        self.assertEqual(selection, 0)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_multiple_deleted_geom(self):
        """Check multiple geoms 'deleted' when save clicked
        This test protects against a regression of #59"""
        expr = QgsExpression("bulk_load_outline_id=2010 or bulk_load_outline_id =2003")
        it = self.edit_dialog.editing_layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.edit_dialog.editing_layer.selectByIds(ids)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.edit_dialog.le_deletion_reason.setText("Reason for deletion")
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = "SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2010 OR bulk_load_outline_id = 2003;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result[0][0], 3)
        self.assertEqual(result[1][0], 3)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2010 OR bulk_load_outline_id = 2003;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [])
        selection = len(self.edit_dialog.editing_layer.selectedFeatures())
        self.assertEqual(selection, 0)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails(self):
        """Check 'deleting' geom fails when save clicked"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
            pos=canvas_point(QgsPointXY(1878090.9, 5555322.0)),
            delay=30,
        )
        QTest.qWait(100)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.edit_dialog.le_deletion_reason.setText("Reason for deletion")
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self._clear_message_bar()
        sql = "SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;"
        result = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = "SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;"
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual("Supplied", status)
        # deletion description
        sql = "SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;"
        reason = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        reason = reason.fetchall()
        self.assertEqual([], reason)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = 2031;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result, [(2031,)])
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails_reason(self):
        """Check 'delete' fail when enter none in 'reason for deletion' """
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
            pos=canvas_point(QgsPointXY(1878228.6, 5555334.9)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.edit_dialog.le_deletion_reason.setText("Reason for deletion")
        self.bulk_load_frame.change_instance.edit_save_clicked(False)

        QTest.mouseClick(
            widget,
            Qt.LeftButton,
            pos=canvas_point(QgsPointXY(1878037.5, 5555349.2)),
            delay=30,
        )
        QTest.qWait(10)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.assertTrue(self.edit_dialog.le_deletion_reason.isEnabled())
        self.edit_dialog.le_deletion_reason.setText("")

        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self._clear_message_bar()

        sql = "SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;"
        result = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        result = result.fetchall()[0]
        # status
        sql = "SELECT value FROM buildings_bulk_load.bulk_load_status WHERE bulk_load_status_id = %s;"
        status = db._execute(sql, (result[0],))
        status = status.fetchall()[0][0]
        self.assertEqual("Supplied", status)
        # deletion description
        sql = "SELECT description FROM buildings_bulk_load.deletion_description WHERE bulk_load_outline_id = %s;"
        reason = db._execute(sql, (self.edit_dialog.bulk_load_outline_id,))
        reason = reason.fetchall()
        self.assertEqual([], reason)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual([(2010,)], result)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_deleted_fails_multiple_selection(self):
        """Check nothing is changed when correct and incorrect outlines are deleted
        This test protects against a regression of #59"""
        expr = QgsExpression("bulk_load_outline_id=2003 or bulk_load_outline_id =2004")
        it = self.edit_dialog.editing_layer.getFeatures(QgsFeatureRequest(expr))
        ids = [i.id() for i in it]
        self.edit_dialog.editing_layer.selectByIds(ids)
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText("Deleted During QA")
        )
        self.edit_dialog.le_deletion_reason.setText("Reason for deletion")
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        self._clear_message_bar()
        sql = "SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2003 OR bulk_load_outline_id = 2004;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(result[0][0], 1)
        self.assertEqual(result[1][0], 1)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added WHERE bulk_load_outline_id = 2003;"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(result, 2003)
        # matched
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.matched WHERE bulk_load_outline_id = 2004;"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(result, 2004)
        # selection
        selection = len(self.edit_dialog.editing_layer.selectedFeatures())
        self.assertEqual(selection, 2)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_selection_change(self):
        """Check change only occurs on currently selected outlines.
        This test protects against a regression of #55."""
        iface.actionSelectPolygon().trigger()
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(
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
        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = "SELECT capture_method_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2027;"
        result = db._execute(sql)
        self.assertEqual(result.fetchall()[0][0], 1)
        sql = "SELECT capture_method_id FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = 2025;"
        result = db._execute(sql)
        self.assertNotEqual(result.fetchall()[0][0], 1)
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        self.bulk_load_frame.db.rollback_open_cursor()
