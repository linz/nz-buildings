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

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
from qgis.utils import plugins, iface


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
                cls.road_toolbar = iface.road_toolbar

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
        self.menu_frame.btn_new_entry.click()
        # save instance of new entry frame?
        self.new_entry_frame = None

    def tearDown(self):
        """Runs after each test."""
        self.entry_frame.btn_cancel.click()

    def test_new_entry_gui_set_up(self):
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(self.new_entry_frame.cmb_new_type_selection.currentIndex()), "Organisation")
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.count(), 4)
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(1), "Lifecycle Stage")
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(2), "Capture Method")
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(1), "Capture Source Group")
        self.assertTrue(self.new_entry_frame.le_new_entry.isEnabled())
        self.assertFalse(self.new_entry_frame.le_description.isEnabled())
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.assertTrue(self.new_entry_frame.le_description.isEnabled())
