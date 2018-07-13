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

    Tests: New Entry GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins


class SetUpNewEntryTest(unittest.TestCase):
    """Test New Entry GUI initial setup confirm default settings"""
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
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_new_entry.click()
        self.new_entry_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.new_entry_frame.btn_exit.click()

    def test_combobox_default(self):
        """Initial combobox text is organisation"""
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(
                          self.new_entry_frame.cmb_new_type_selection.currentIndex()),
                          'Organisation')

    def test_combobox_options(self):
        """Four options in combobox"""
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.count(), 4)
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(1), 'Lifecycle Stage')
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(2), 'Capture Method')
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(3), 'Capture Source Group')

    def test_value_enabled(self):
        """Line edit: value is enabled on start up"""
        self.assertTrue(self.new_entry_frame.le_new_entry.isEnabled())

    def test_description_disabled(self):
        """Line edit: description is disabled on startup"""
        self.assertFalse(self.new_entry_frame.le_description.isEnabled())

    def test_description_enabled_on_capture_source_group(self):
        """Description enabled when change to capture source group option"""
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.assertTrue(self.new_entry_frame.le_description.isEnabled())
