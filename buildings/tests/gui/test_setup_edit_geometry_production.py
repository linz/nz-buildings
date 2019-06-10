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
from qgis.utils import plugins, iface


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
        self.edit_dialog = self.production_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == 'Edit Geometry':
                action.trigger()

    def tearDown(self):
        """Runs after each test."""
        self.production_frame.btn_exit.click()

    def test_production_gui_set_up(self):
        """ Initial set up of the frame """
        self.assertTrue(self.edit_dialog.isVisible())
        self.assertFalse(self.edit_dialog.layout_status.isVisible())
        self.assertTrue(self.edit_dialog.layout_capture_method.isVisible())
        self.assertFalse(self.edit_dialog.layout_lifecycle_stage.isVisible())
        self.assertFalse(self.edit_dialog.layout_general_info.isVisible())
        self.assertFalse(self.edit_dialog.layout_end_lifespan.isVisible())
        self.assertFalse(self.edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(self.edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(self.edit_dialog.cmb_capture_method.isEnabled())

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        layer_bool = False
        edit_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        names = [layer.layer().name() for layer in layers]
        if 'building_outlines' in names and 'historic_outlines' in names:
            layer_bool = True
        for layer in layers:
            if layer.layer().name() == 'building_outlines' and layer.layer().isEditable():
                edit_bool = True

        self.assertTrue(layer_bool)
        self.assertTrue(edit_bool)
