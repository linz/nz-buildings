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

    Tests: Add New Bulk Outline GUI processes

 ***************************************************************************/
"""

import unittest

from qgis.core import QgsProject
from qgis.utils import plugins


class SetUpBulkAddTest(unittest.TestCase):
    """Test Add New Bulk Outline GUI processes"""
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
                cls.building_plugin = plugins.get('buildings')
                cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.startup_frame = self.building_plugin.startup_frame
        self.startup_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.rad_add.click()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_bulk_load_gui_set_up(self):
        """Buttons and comboboxes correctly enabled/disables on startup"""
        self.assertFalse(self.bulk_load_frame.btn_edit_ok.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_edit_cancel.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())

    def test_layer_registry(self):
        """Bulk load outlines table added to canvas when frame opened"""
        layer_bool = False
        edit_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        for layer in layers:
            if layer.layer().name() == 'bulk_load_outlines':
                layer_bool = True
                if layer.layer().isEditable():
                    edit_bool = True
        self.assertTrue(layer_bool)
        self.assertTrue(edit_bool)
