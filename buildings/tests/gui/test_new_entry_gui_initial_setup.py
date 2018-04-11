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
from qgis.utils import reloadPlugin


class SetUpNewEntryGuiTest(unittest.TestCase):
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
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_new_entry.click()
        self.new_entry_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.new_entry_frame.btn_cancel.click()

    def test_combobox_default(self):
        # initial combobox text is organisation
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(self.new_entry_frame.cmb_new_type_selection.currentIndex()), 'Organisation')

    def test_combobox_options(self):
        # has four options in combobox
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.count(), 4)
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(1), 'Lifecycle Stage')
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(2), 'Capture Method')
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(3), 'Capture Source Group')

    def test_value_enabled(self):
        # value is enabled on start up
        self.assertTrue(self.new_entry_frame.le_new_entry.isEnabled())

    def test_description_disabled(self):
        # description is disbaled on startup
        self.assertFalse(self.new_entry_frame.le_description.isEnabled())

    def test_desc_enabled_on_capture_srcgrp(self):
        # change to capture source group option description becomes enabled
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.assertTrue(self.new_entry_frame.le_description.isEnabled())


suite = unittest.TestLoader().loadTestsFromTestCase(SetUpNewEntryGuiTest)
unittest.TextTestRunner(verbosity=2).run(suite)
