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

    Tests: Alter Building Relationships GUI processing

 ***************************************************************************/
"""

import unittest

from qgis.core import QgsPoint, QgsCoordinateReferenceSystem, QgsRectangle, QgsMapLayerRegistry
from qgis.utils import plugins, iface
from buildings.utilities import database as db

from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt, QModelIndex
from qgis.gui import QgsMapTool


class ProcessAlterRelationshipsTest(unittest.TestCase):
    """Test Alter Building Relationships GUI processing"""
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
        self.bulk_load_frame.btn_alter_rel.click()
        self.alter_relationships_frame = self.dockwidget.current_frame

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        # right click in order to activate the canvas
        QTest.mouseClick(widget,
                         Qt.RightButton,
                         pos=canvas_point(QgsPoint(1878334, 5555224)),
                         delay=-1)
        QTest.qWait(1)

        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas = iface.mapCanvas()
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878028.94, 5555123.14,
                                      1878449.89, 5555644.95)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()

    def tearDown(self):
        """Runs after each test."""
        self.alter_relationships_frame.btn_cancel.click()
        self.alter_relationships_frame.db.rollback_open_cursor()

    def test_alter_relationship_to_added_or_removed(self):
        """When save is clicked buildings in matched are moved to added/removed"""
        sql = 'SELECT count(*)::integer FROM buildings_bulk_load.added'
        result = db._execute(sql)
        result_original = result.fetchone()[0]

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878177.80, 5555336.00)),
                         delay=-1)
        QTest.qWait(1)

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)
        index1 = self.alter_relationships_frame.tbl_original.model().index(0, 0)
        index2 = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        self.assertEqual(index1.data(), '1003')
        self.assertEqual(index2.data(), '2002')

        self.alter_relationships_frame.btn_unlink_all.click()

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)
        row_count = self.alter_relationships_frame.lst_existing.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)
        row_count = self.alter_relationships_frame.lst_bulk.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql)
        self.assertEqual(result.fetchone()[0], result_original + 1)

        self.alter_relationships_frame.db.rollback_open_cursor()

    def test_alter_relationship_to_matched(self):
        """When save is clicked buildings in added/removed are moved to matched"""
        sql = 'SELECT count(*)::integer FROM buildings_bulk_load.matched'
        result = db._execute(sql)
        result_original = result.fetchone()[0]

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878229.15, 5555335.28)),
                         delay=-1)
        QTest.qWait(1)

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)
        index = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        self.assertEqual(index.data(), '2003')
        layerList = QgsMapLayerRegistry.instance().mapLayersByName("existing_subset_extracts")
        iface.setActiveLayer(layerList[0])
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223.60, 5555320.54)),
                         delay=-1)
        QTest.qWait(1)

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 2)
        index = self.alter_relationships_frame.tbl_original.model().index(1, 0)
        self.assertEqual(index.data(), '1004')

        self.alter_relationships_frame.btn_unlink_all.click()

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)
        row_count = self.alter_relationships_frame.lst_existing.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)
        row_count = self.alter_relationships_frame.lst_bulk.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)

        self.alter_relationships_frame.lst_existing.item(0).setSelected(True)
        self.alter_relationships_frame.lst_bulk.item(0).setSelected(True)

        self.alter_relationships_frame.btn_matched.click()
        self.assertFalse(self.alter_relationships_frame.btn_matched.isEnabled())

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql)
        self.assertEqual(result.fetchone()[0], result_original + 1)

        self.alter_relationships_frame.db.rollback_open_cursor()

    def test_alter_relationship_to_related(self):
        """When save is clicked buildings in added/removed are moved to related"""
        sql = 'SELECT count(*)::integer FROM buildings_bulk_load.related'
        result = db._execute(sql)
        result_original = result.fetchone()[0]

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878229.15, 5555335.28)),
                         delay=-1)
        QTest.qWait(1)

        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878033.55, 5555355.73)),
                         delay=-1)
        QTest.qWait(1)

        layerList = QgsMapLayerRegistry.instance().mapLayersByName("existing_subset_extracts")
        iface.setActiveLayer(layerList[0])
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878223.60, 5555320.54)),
                         delay=-1)
        QTest.qWait(1)

        self.alter_relationships_frame.btn_unlink_all.click()

        self.alter_relationships_frame.lst_existing.item(0).setSelected(True)
        self.alter_relationships_frame.lst_bulk.item(0).setSelected(True)
        self.alter_relationships_frame.lst_bulk.item(1).setSelected(True)

        self.alter_relationships_frame.btn_related.click()
        self.assertFalse(self.alter_relationships_frame.btn_related.isEnabled())

        self.alter_relationships_frame.save_clicked(commit_status=False)

        result = db._execute(sql)
        self.assertEqual(result.fetchone()[0], result_original + 2)

        self.alter_relationships_frame.db.rollback_open_cursor()

    def test_remove_button(self):
        """When remove button is clicked the building ids in tablewidget are removed"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878185.10, 5555290.52)),
                         delay=-1)
        QTest.qWait(1)

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 2)
        index11 = self.alter_relationships_frame.tbl_original.model().index(0, 0)
        index12 = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        index21 = self.alter_relationships_frame.tbl_original.model().index(1, 0)
        index22 = self.alter_relationships_frame.tbl_original.model().index(1, 1)
        self.assertEqual(index11.data(), '1008')
        self.assertEqual(index12.data(), '2005')
        self.assertEqual(index21.data(), '1007')
        self.assertEqual(index22.data(), '2005')

        self.alter_relationships_frame.btn_remove_all.click()
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)

        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878185.10, 5555290.52)),
                         delay=-1)
        QTest.qWait(1)

        self.alter_relationships_frame.tbl_original.item(0, 0).setSelected(True)
        self.alter_relationships_frame.btn_remove_slt.click()
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)

    def test_relink_button(self):
        """When relink button is clicked the building ids in listwidget are moved back to tablewidget"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878182.7, 5555332.0)),
                         delay=-1)
        QTest.qWait(1)

        self.alter_relationships_frame.btn_unlink_all.click()

        self.alter_relationships_frame.btn_relink_all.click()

        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 1)
        row_count = self.alter_relationships_frame.lst_existing.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)
        row_count = self.alter_relationships_frame.lst_bulk.model().rowCount(QModelIndex())
        self.assertEqual(row_count, 0)

    def test_clear_selection_button(self):
        """When clear_selection button is clicked the selections get cleared"""
        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878182.7, 5555332.0)),
                         delay=-1)
        QTest.qWait(1)

        self.assertTrue(self.alter_relationships_frame.tbl_original.item(0, 0).isSelected())

        self.alter_relationships_frame.btn_clear_slt.click()

        self.assertFalse(self.alter_relationships_frame.tbl_original.item(0, 0).isSelected())
