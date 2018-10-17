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

    Tests: Compare Outlines Button Click Confirm Processes

 ***************************************************************************/
"""

import os
import unittest

from PyQt4.QtCore import Qt
from qgis.core import QgsMapLayerRegistry
from qgis.utils import iface, plugins

from buildings.utilities import database as db


class ProcessComparisonNotIntersectTest(unittest.TestCase):
    """
    Test comparison process for outlines that not intersect with previous dataset
    These tests protect against a regression of #62
    """
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
        self.bulk_load_frame.db.open_cursor()
        self.bulk_load_frame.publish_clicked(False)
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'testdata/test_bulk_load_shapefile2.shp')
        layer = iface.addVectorLayer(path, '', 'ogr')
        count = self.bulk_load_frame.ml_outlines_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.ml_outlines_layer.layer(idx).name() == 'test_bulk_load_shapefile2':
                self.bulk_load_frame.ml_outlines_layer.setLayer(self.bulk_load_frame.ml_outlines_layer.layer(idx))
                break
            idx = idx + 1
        # add description
        self.bulk_load_frame.le_data_description.setText('Test bulk load outlines')
        # add outlines
        self.bulk_load_frame.bulk_load_save_clicked(False)
        self.bulk_load_frame.bulk_load_layer = layer

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.db.rollback_open_cursor()
        # remove temporary layers from canvas
        layers = iface.legendInterface().layers()
        for layer in layers:
            if 'test_bulk_load_shapefile' in str(layer.id()):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        self.bulk_load_frame.layer_registry.remove_all_layers()
        self.bulk_load_frame.btn_exit.click()

    def test_compare_added(self):
        """Check correct number of ids are determined as 'Added'"""
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 5)

    def test_compare_removed(self):
        """Check correct number of ids are determined as 'Removed'"""
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)

    def test_compare_matched(self):
        """Check correct number of ids are determined as 'Matched'"""
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)

    def test_compare_related(self):
        """Check correct number of ids are determined as 'Related'"""
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 44)

    def test_delete_during_qa(self):
        """Checks outlines that are deleted during qa before comparisons is run are not carried through"""
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE description = 'Test bulk load outlines';"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = 3 WHERE supplied_dataset_id = %s;'
        db._execute(sql, (result,))
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)
        # Matched
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)
        # related
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 44)
        # removed
        sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)

    def test_add_during_qa(self):
        """
        Checks outlines that are added during qa before comparisons is not causing issues when carried through
        The test protects against a regression of #63
        """
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE description = 'Test bulk load outlines';"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        # Add one outline in both bulk_load_outlines and added table
        sql = "SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        result = db._execute(sql, (result, None, 2, 1, 1, 4, 400, 1,
                                   '0103000020910800000100000005000000F311221BB7AA3C41046171A564315541D2712DB1CCAA3C41046171A56431554115066169CDAA3C41E20FFCA060315541751FEF95B7AA3C414353AFBF60315541F311221BB7AA3C41046171A564315541'))
        result = result.fetchall()[0][0]
        self.bulk_load_frame.cmb_capture_source_area.setCurrentIndex(self.bulk_load_frame.cmb_capture_source_area.findText("Imagery Two"))
        self.bulk_load_frame.compare_outlines_clicked(False)
        # added
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 6)
        # Matched
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)
        # related
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 44)
        # removed
        sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)
