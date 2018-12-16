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

    Tests: Edit Production Outline GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from qgis.core import QgsProject
from qgis.utils import plugins


class SetUpEditProduction(unittest.TestCase):
    """
    Test Edit Outline GUI initial
    setup confirm default settings
    """

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Edit Outlines', Qt.MatchExactly)[0])
        self.production_frame = self.dockwidget.current_frame
        self.production_frame.tbtn_edits.setDefaultAction(self.production_frame.action_edit_attribute)
        self.production_frame.tbtn_edits.click()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_production_gui_set_up(self):
        """ Initial set up of the frame """
        self.assertTrue(self.production_frame.layout_capture_method.isVisible())
        self.assertTrue(self.production_frame.layout_general_info.isVisible())
        self.assertFalse(self.production_frame.btn_save.isEnabled())
        self.assertFalse(self.production_frame.btn_reset.isEnabled())
        self.assertTrue(self.production_frame.btn_exit_edits.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_method.isEnabled())
        self.assertFalse(self.production_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.production_frame.cmb_ta.isEnabled())
        self.assertFalse(self.production_frame.cmb_town.isEnabled())
        self.assertFalse(self.production_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.production_frame.cmb_lifecycle_stage.isEnabled())

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        layer_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        names = [layer.layer().name() for layer in layers]
        if 'building_outlines' in names and 'historic_outlines' in names:
            layer_bool = True
        self.assertTrue(layer_bool)