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
from qgis.utils import reloadPlugin


class SetUpBulkNewGuiTest(unittest.TestCase):
    """Test Add New Bulk Outline GUI processes"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get("roads"):
            pass
        else:
            cls.road_plugin = plugins.get("roads")
            if cls.road_plugin.is_active is False:
                cls.road_plugin.main_toolbar.actions()[0].trigger()
                cls.dockwidget = cls.road_plugin.dockwidget
            else:
                cls.dockwidget = cls.road_plugin.dockwidget
            if not plugins.get("buildings"):
                pass
            else:
                cls.building_plugin = plugins.get("buildings")
                reloadPlugin('buildings')
                if cls.dockwidget.stk_options.count() == 4:
                    cls.dockwidget.stk_options.setCurrentIndex(3)
                    cls.dockwidget.stk_options.addWidget(cls.dockwidget.frames['menu_frame'])
                    cls.dockwidget.current_frame = 'menu_frame'
                    cls.dockwidget.stk_options.setCurrentIndex(4)
                else:
                    cls.dockwidget.stk_options.setCurrentIndex(4)
                cls.dockwidget.lst_options.setCurrentItem(cls.dockwidget.lst_options.item(2))

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get("roads")
        self.building_plugin = plugins.get("buildings")
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.cmb_add_outline.setCurrentIndex(0)
        self.menu_frame.cmb_add_outline.setCurrentIndex(1)
        self.new_bulk_frame = self.dockwidget.current_frame
        if self.new_bulk_frame.error_dialog is not None:
            self.no_supplied_data = True
            self.new_bulk_frame.error_dialog.close()
        else:
            self.no_supplied_data = False

    def tearDown(self):
        """Runs after each test."""
        self.new_bulk_frame.btn_cancel.click()

    def test_bulk_load_gui_set_up(self):
        # tests for if no_supplied_data is true
        if self.no_supplied_data:
            self.assertFalse(self.new_bulk_frame.btn_save.isEnabled())
            self.assertFalse(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_cancel.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_suburb.isEnabled())
        else:
            self.assertFalse(self.new_bulk_frame.btn_save.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_cancel.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_suburb.isEnabled())

    def test_layer_registry(self):
        # TODO: 
        # check only the most recent supplied dataset is loaded into the map canvas
        layer_bool = False
        edit_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Building Tool Layers")
        layers = group.findLayers()
        for layer in layers:
            if layer.layer().name() == "bulk_load_outlines":
                layer_bool = True
                if layer.layer().isEditable():
                    edit_bool = True
        if self.no_supplied_data:
            self.assertFalse(layer_bool)
            self.assertFalse(edit_bool)
        elif self.no_supplied_data is False:
            self.assertTrue(layer_bool)
            self.assertTrue(edit_bool)

suite = unittest.TestLoader().loadTestsFromTestCase(SetUpBulkNewGuiTest)
unittest.TextTestRunner(verbosity=2).run(suite)