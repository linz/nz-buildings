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

    Tests: Menu GUI setup confirm default settings

 ***************************************************************************/
"""
from qgis.utils import plugins, iface

import unittest

class SetUpMenuGuiTest(unittest.TestCase):
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

                if not plugins.get("buildings"):
                    pass
                else:
                    cls.building_plugin = plugins.get("buildings")
        cls.dockwidget.stk_options.setCurrentIndex(4)

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get("roads")
        self.dockwidget = self.road_plugin.dockwidget
        self.dockwidget.stk_options.setCurrentIndex(4)
        self.menu_frame = self.building_plugin.menu_frame

    def tearDown(self):
        """Runs after each test"""
        # Do nothing

    def test_plugin_is_active(self):
        print 'nothing'
        # TODO: add .is_active field to buildings plugin

    def test_menu_gui_set_up(self):
        # buttons are enabled
        self.assertTrue(self.menu_frame.btn_new_entry.isEnabled())
        self.assertTrue(self.menu_frame.btn_add_capture_source.isEnabled())
        self.assertTrue(self.menu_frame.btn_load_outlines.isEnabled())
        # combo box index is add outlines
        self.assertEquals(self.menu_frame.cmb_add_outline.itemText(self.menu_frame.cmb_add_outline.currentIndex()), "Add Outlines")
        # combo box has three options
        self.assertEquals(self.menu_frame.cmb_add_outline.count(), 3)
        self.assertEquals(self.menu_frame.cmb_add_outline.itemText(1), "Add New Outline to Supplied Dataset")
        self.assertEquals(self.menu_frame.cmb_add_outline.itemText(2), "Add New Outline to Production")


if __name__ == "__main__":
    unittest.main()
