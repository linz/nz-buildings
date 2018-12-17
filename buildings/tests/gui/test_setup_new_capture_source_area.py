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

    Tests: New Capture Source GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins
from qgis.core import QgsProject
from PyQt4.QtCore import Qt

from buildings.utilities import database as db


class SetUpCaptureSourceAreaTest(unittest.TestCase):
    """Test New Capture Source Area GUI initial setup confirm default settings"""
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
            'Capture Sources', Qt.MatchExactly)[0])
        self.capture_frame = self.dockwidget.current_frame
        self.capture_frame.btn_new_geometry.click()
        self.capture_area_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_area_frame.btn_exit.click()

    def test_capture_source_area_gui_set_up(self):
        """Buttons and comboboxes correctly enabled/disables on startup"""
        self.assertTrue(self.capture_area_frame.rb_select_from_layer.isEnabled())
        self.assertFalse(self.capture_area_frame.mcb_selection_layer.isEnabled())
        self.assertFalse(self.capture_area_frame.le_area_title.isEnabled())
        self.assertFalse(self.capture_area_frame.le_external_id.isEnabled())
        self.assertEqual(self.capture_area_frame.tbl_capture_source_area.rowCount(), 3)

    def test_capture_source_area_layer_registry(self):
        """Capture source area layer is added to layer registry"""
        layer_bool = True
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        layer_name = ['capture_source_area']
        for layer in layers:
            if layer.layer().name() not in layer_name:
                layer_bool = False

        self.assertEqual(len([layer for layer in layers]), len(layer_name))
        self.assertTrue(layer_bool)
