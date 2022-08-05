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

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtTest import QTest
from qgis.core import QgsRectangle, QgsPointXY, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkAddOutlinesTest(unittest.TestCase):
    """Test Add New Bulk Outline GUI Processes"""

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
            if action.text() == "Add Outline":
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_ui_on_geometry_drawn(self):
        """UI comboboxes enable when geometry is drawn"""
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEquals(self.edit_dialog.cmb_capture_method.currentText(), "Trace Orthophotography")
        self.assertEquals(self.edit_dialog.cmb_capture_source.currentText(), "1- Imagery One- NZ Aerial Imagery")
        self.assertEquals(self.edit_dialog.cmb_ta.currentText(), "Wellington")
        self.assertEquals(self.edit_dialog.cmb_suburb.currentText(), "Newtown")
        self.assertEquals(self.edit_dialog.cmb_town.currentText(), "Wellington")
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_draw_circle_option(self):
        """Allows user to draw circle using circle button"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()

        for action in iface.building_toolbar.actions():
            if action.text() == "Draw Circle":
                action.trigger()

        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878300.4, 5555365.6)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878301.7, 5555367.3)), delay=-1)
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEquals(self.edit_dialog.cmb_capture_method.currentText(), "Trace Orthophotography")

        self.edit_dialog.close()

    def test_reset_clicked(self):
        """Indexes are reset and comboxes disabled when reset is called"""
        # add geom to canvas
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEquals(self.edit_dialog.cmb_capture_method.currentText(), "Trace Orthophotography")

        # change indexes of comboboxes
        self.edit_dialog.cmb_capture_method.setCurrentIndex(1)
        self.edit_dialog.cmb_capture_source.setCurrentIndex(0)
        self.edit_dialog.cmb_ta.setCurrentIndex(1)
        self.edit_dialog.cmb_town.setCurrentIndex(0)
        self.edit_dialog.cmb_suburb.setCurrentIndex(1)
        # click reset button
        self.edit_dialog.btn_edit_reset.click()
        # check geom removed from canvas
        self.assertEquals(len(list(self.edit_dialog.added_geoms.keys())), 0)
        # check comboxbox indexes reset to 0
        self.assertEquals(self.edit_dialog.cmb_capture_method.currentIndex(), -1)
        self.assertEquals(self.edit_dialog.cmb_capture_source.currentIndex(), -1)
        self.assertEquals(self.edit_dialog.cmb_ta.currentIndex(), -1)
        self.assertEquals(self.edit_dialog.cmb_town.currentIndex(), -1)
        self.assertEquals(self.edit_dialog.cmb_suburb.currentIndex(), -1)
        # check comboboxes disabled
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_ta.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_town.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_suburb.isEnabled())
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_new_outline_insert(self):
        """Data added to correct tables when save clicked"""
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;"
        added_result = db._execute(sql)
        added_result = added_result.fetchall()[0][0]
        # add geom
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.qWait(1)
        # tests
        self.assertTrue(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertTrue(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_ta.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_town.isEnabled())
        self.assertTrue(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertEquals(self.edit_dialog.cmb_capture_method.currentText(), "Trace Orthophotography")
        # change indexes of comboboxes
        self.edit_dialog.cmb_capture_source.setCurrentIndex(0)
        self.edit_dialog.cmb_ta.setCurrentIndex(0)
        self.edit_dialog.cmb_town.setCurrentIndex(0)
        self.edit_dialog.cmb_suburb.setCurrentIndex(0)
        self.edit_dialog.change_instance.edit_save_clicked(False)
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEquals(result2, result + 1)
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;"
        added_result2 = db._execute(sql)
        added_result2 = added_result2.fetchall()[0][0]
        self.assertEquals(added_result2, added_result + 1)
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_edit_new_outline(self):
        """Geometry successfully saved when newly created geometry changed."""
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;"
        added_result = db._execute(sql)
        added_result = added_result.fetchall()[0][0]
        # add geom
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseDClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
        canvas = iface.mapCanvas()
        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555290)), delay=-1)
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.qWait(1)

        iface.actionVertexTool().trigger()
        QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
        QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878200, 5555350)), delay=-1)
        QTest.qWait(1)

        self.bulk_load_frame.change_instance.edit_save_clicked(False)
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.bulk_load_outlines;"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEquals(result2, result + 1)
        sql = "SELECT COUNT(bulk_load_outline_id) FROM buildings_bulk_load.added;"
        added_result2 = db._execute(sql)
        added_result2 = added_result2.fetchall()[0][0]
        self.assertEquals(added_result2, added_result + 1)
        self.bulk_load_frame.db.rollback_open_cursor()

    # def test_edit_existing_outline_fails(self):
    #     """Editing fails when the existing outlines geometry changed."""
    #     # add geom
    #     widget = iface.mapCanvas().viewport()
    #     canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
    #     QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1747520, 5428152)), delay=-1)
    #     canvas = iface.mapCanvas()
    #     selectedcrs = "EPSG:2193"
    #     target_crs = QgsCoordinateReferenceSystem()
    #     target_crs.createFromUserInput(selectedcrs)
    #     canvas.setDestinationCrs(target_crs)
    #     zoom_rectangle = QgsRectangle(1878035.0, 5555256.0, 1878345.0, 5555374.0)
    #     canvas.setExtent(zoom_rectangle)
    #     canvas.refresh()
    #     QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555314)), delay=-1)
    #     QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878262, 5555290)), delay=-1)
    #     QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555290)), delay=-1)
    #     QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
    #     QTest.mouseClick(widget, Qt.RightButton, pos=canvas_point(QgsPointXY(1878223, 5555314)), delay=-1)
    #     QTest.qWait(1)

    #     iface.actionVertexTool().trigger()
    #     QTest.mouseClick(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878231.71, 5555331.38)), delay=-1)
    #     QTest.mousePress(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878231.71, 5555331.38)), delay=-1)
    #     QTest.mouseRelease(widget, Qt.LeftButton, pos=canvas_point(QgsPointXY(1878250, 5555350)), delay=-1)
    #     QTest.qWait(10)
    #     self.assertTrue(
    #         iface.messageBar().currentItem().text(),
    #         "Only the currently added outline can be edited. Please go to edit geometry to edit existing outlines",
    #     )
    #     iface.messageBar().popWidget()

    def test_disabled_on_layer_removed(self):
        """When key layer is removed from registry check options are disabled (#87)"""
        layer = QgsProject.instance().mapLayersByName("bulk_load_outlines")[0]
        QgsProject.instance().removeMapLayer(layer.id())
        for action in iface.building_toolbar.actions():
            if action.text() == ["Add Outline", "Edit Geometry", "Edit Attributes"]:
                self.assertFalse(action.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_alter_rel.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_publish.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_compare_outlines.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_exit.isEnabled())
        iface.messageBar().popWidget()
