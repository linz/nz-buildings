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

    Tests: Edit Bulk Load Outline GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from qgis.utils import plugins, iface


class SetUpEditBulkLoad(unittest.TestCase):
    """
    Test edit bulk_load Outline GUI initial
    setup confirm default settings
    """

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Bulk Load", Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.edit_dialog = self.bulk_load_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_bulk_load_gui_set_up(self):
        """ Initial set up of the frame """
        self.assertTrue(self.edit_dialog.isVisible())
        self.assertTrue(self.edit_dialog.layout_status.isVisible())
        self.assertTrue(self.edit_dialog.layout_capture_method.isVisible())
        self.assertFalse(self.edit_dialog.layout_lifecycle_stage.isVisible())
        self.assertTrue(self.edit_dialog.layout_general_info.isVisible())
        self.assertFalse(self.edit_dialog.layout_end_lifespan.isVisible())
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_ta.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_town.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_suburb.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_status.isEnabled())

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        layer_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Building Tool Layers")
        layers = group.findLayers()
        for layer in layers:
            if layer.layer().name() == "bulk_load_outlines":
                layer_bool = True
        self.assertTrue(layer_bool)
