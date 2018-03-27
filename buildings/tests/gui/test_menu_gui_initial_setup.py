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
from qgis.utils import plugins

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
        # buttons have correct names
        self.assertEqual(self.menu_frame.btn_new_entry.text(), "New Entry")
        self.assertEqual(self.menu_frame.btn_add_capture_source.text(), "Add Capture Source")
        self.assertEqual(self.menu_frame.btn_new_entry.text(), "Bulk Load Outlines")
        # combo box index is add outlines and enabled
        self.assertEquals(self.menu_frame.cmb_add_outline.isEnabled())
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(self.menu_frame.cmb_add_outline.currentIndex()), "Add Outlines")
        # combo box has three options
        self.assertEqual(self.menu_frame.cmb_add_outline.count(), 3)
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(1), "Add New Outline to Supplied Dataset")
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(2), "Add New Outline to Production")

    def test_menu_gui_on_click(self):
        # new entry
        self.menu_frame.btn_new_entry.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), "f_new_entry")
        self.dockwidget.current_frame.btn_cancel.click()
        # new capture source
        self.menu_frame.btn_add_capture_source.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), "f_new_capture_source")
        self.dockwidget.current_frame.btn_cancel.click()
        # Bulk load outlines
        self.menu_frame.btn_load_outlines.click()
        self.assertEqual(self.dockwidget.current_frame.objectName(), "f_new_supplied_outlines")
        self.dockwidget.current_frame.btn_cancel.click()
        # Bulk create outline
        self.menu_frame.cmb_add_outline.setCurrentIndex(1)
        self.assertEqual(self.dockwidget.current_frame.objectName(), "f_bulk_new_outline")
        # self.dockwidget.current_frame.btn_cancel.click()
        self.menu_frame.cmb_add_outline.setCurrentIndex(2)
        self.assertEqual(self.dockwidget.current_frame.objectName(), "f_production_new_outline")
        self.dockwidget.current_frame.btn_cancel.click()

if __name__ == "__main__":
    unittest.main()
