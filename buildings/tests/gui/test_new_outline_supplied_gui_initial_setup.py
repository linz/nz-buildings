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

    Tests: Bulk Load Outlines GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class SetUpBulkLoadGuiTest(unittest.TestCase):
    """Test Edit Road Geometry GUI initial setup confirm default settings"""
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
        cls.dockwidget.stk_options.setCurrentIndex(4)
        cls.dockwidget.lst_options.setCurrentItem(cls.dockwidget.lst_options.item(2))

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get("roads")
        self.dockwidget = self.road_plugin.dockwidget
        self.dockwidget.stk_options.setCurrentIndex(4)
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(2))
        self.menu_frame = self.building_plugin.menu_frame
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
            self.assertFalse(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_suburb.isEnabled())
            # check editing is not on
        # test for if no_supplied_data is false
        else:
            self.assertFalse(self.new_bulk_frame.btn_save.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertFalse(self.new_bulk_frame.cmb_suburb.isEnabled())
            # check editing is enabled

    def test_ui_on_geom_drawn(self):
        if self.no_supplied_data is False:
            # add geom to canvas
            self.assertTrue(self.new_bulk_frame.btn_save.isEnabled())
            self.assertTrue(self.new_bulk_frame.btn_reset.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_capture_method.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_capture_source.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_ta.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_town.isEnabled())
            self.assertTrue(self.new_bulk_frame.cmb_suburb.isEnabled())

    def test_reset_button(self):
        if self.no_supplied_data is False:
            # add geom to canvas
            # change indexes of comboboxes
            self.new_bulk_frame.btn_reset.click()
            # check geom removed from canvas
            # check comboxbox indexes reset to 0
            # check comboboxes disabled

    def test_insert(self):
        # check that data is input into bulk load table 

    def test_layer_registry(self):
        # check only the most recent supplied dataset is loaded into the map canvas
        
