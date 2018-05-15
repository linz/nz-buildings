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


class SetUpMenuTest(unittest.TestCase):
    """Test Menu GUI initial setup confirm default settings"""
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
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame

    def tearDown(self):
        """Runs after each test"""
        # Do nothing
        self.road_plugin.dockwidget.close()

    def test_menu_gui_buttons_enabled(self):
        """Buttons are enabled"""
        self.assertTrue(self.menu_frame.btn_new_entry.isEnabled())
        self.assertTrue(self.menu_frame.btn_add_capture_source.isEnabled())
        self.assertTrue(self.menu_frame.btn_load_outlines.isEnabled())

    def test_menu_gui_button_names(self):
        """Buttons have correct names"""
        self.assertEqual(self.menu_frame.btn_new_entry.text(), 'New Entry')
        self.assertEqual(self.menu_frame.btn_add_capture_source.text(),
                         'Add Capture Source')
        self.assertEqual(self.menu_frame.btn_load_outlines.text(),
                         'Bulk Load Outlines')

    def test_menu_gui_combo_default(self):
        """Combo box index is 'add outlines' and enabled"""
        self.assertTrue(self.menu_frame.cmb_add_outline.isEnabled())
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(0),
                         'Add Outlines')
        self.assertEqual(self.menu_frame.cmb_add_outline.currentIndex(), 0)

    def test_menu_gui_combo_options(self):
        """Combo box has three options"""
        self.assertEqual(self.menu_frame.cmb_add_outline.count(), 4)
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(1),
                         'Alter Building Relationships')
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(2),
                         'Add New Outline to Bulk Load Dataset')
        self.assertEqual(self.menu_frame.cmb_add_outline.itemText(3),
                         'Add New Outline to Production')


suite = unittest.TestLoader().loadTestsFromTestCase(SetUpMenuTest)
unittest.TextTestRunner(verbosity=2).run(suite)
