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

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsPoint, QgsGeometry, QgsField, QgsCoordinateReferenceSystem, QgsRectangle
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
        self.menu_frame.cmb_add_outline.setCurrentIndex(self.menu_frame.cmb_add_outline.findText('Add Outlines'))
        self.menu_frame.cmb_add_outline.setCurrentIndex(self.menu_frame.cmb_add_outline.findText('Alter Building Relationships'))
        self.alter_relationships_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.alter_relationships_frame.btn_cancel.click()
        self.menu_frame.cmb_add_outline.setCurrentIndex(self.menu_frame.cmb_add_outline.findText('Add Outlines'))

    def test_select_added_and_removed_outlines(self):

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates

        selectedcrs = "EPSG:2193"
        target_crs = QgsCoordinateReferenceSystem()
        target_crs.createFromUserInput(selectedcrs)
        canvas = iface.mapCanvas()
        canvas.setDestinationCrs(target_crs)
        zoom_rectangle = QgsRectangle(1878028.94, 5555123.14,
                                      1878449.89, 5555644.95)
        canvas.setExtent(zoom_rectangle)
        canvas.refresh()

        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878228, 5555333)),
                         delay=300)

        # Table is displaying correct segments
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertTrue(row_count == 1)
        index = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        self.assertTrue(index.data() == 2003)

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878222, 5555325)),
                         delay=300)

        # Table is displaying correct segments
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertTrue(row_count == 2)
        index = self.alter_relationships_frame.tbl_original.model().index(1, 0)
        self.assertTrue(index.data() == 1004)

    def test_select_matched_outlines(self):

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878187, 5555327)),
                         delay=300)

        # Table is displaying correct segments
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertTrue(row_count == 1)
        index1 = self.alter_relationships_frame.tbl_original.model().index(0, 0)
        index2 = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        self.assertTrue(index1.data() == 1003 & index2.data() == 2002)

    def test_select_related_outlines(self):

        widget = iface.mapCanvas().viewport()
        canvas_point = QgsMapTool(iface.mapCanvas()).toCanvasCoordinates
        QTest.mouseClick(widget,
                         Qt.LeftButton,
                         pos=canvas_point(QgsPoint(1878183, 5555288)),
                         delay=300)

        # Table is displaying correct segments
        row_count = self.alter_relationships_frame.tbl_original.model().rowCount(QModelIndex())
        self.assertTrue(row_count == 2)
        index11 = self.alter_relationships_frame.tbl_original.model().index(0, 0)
        index12 = self.alter_relationships_frame.tbl_original.model().index(0, 1)
        index21 = self.alter_relationships_frame.tbl_original.model().index(1, 0)
        index22 = self.alter_relationships_frame.tbl_original.model().index(1, 1)
        self.assertTrue(index11.data() == 1008 & index12.data() == 2005 &
                        index21.data() == 1007 & index22.data() == 2005)


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessAlterRelationshipsTest)
unittest.TextTestRunner(verbosity=2).run(suite)
