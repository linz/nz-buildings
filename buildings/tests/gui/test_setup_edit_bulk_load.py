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

from qgis.core import QgsProject
from qgis.utils import plugins

from buildings.utilities import database as db


class SetUpEditBulkLoad(unittest.TestCase):
    """
    Test edit bulk_load Outline GUI initial
    setup confirm default settings
    """
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        if not plugins.get('buildings'):
            pass
        else:
            db.connect()
            cls.building_plugin = plugins.get('buildings')
            cls.dockwidget = cls.building_plugin.dockwidget
            cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        pass

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger() 
        self.dockwidget = self.building_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.rad_edit.click()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_bulk_load_gui_set_up(self):
        """ Initial set up of the frame """
        self.assertFalse(self.bulk_load_frame.btn_edit_save.isEnabled())
        self.assertFalse(self.bulk_load_frame.btn_edit_reset.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_method_2.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_capture_source.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_ta.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_town.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_suburb.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_status.isEnabled())

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        layer_bool = False
        edit_bool = False
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        for layer in layers:
            if layer.layer().name() == 'bulk_load_outlines':
                layer_bool = True
                if layer.layer().isEditable():
                    edit_bool = True
        self.assertTrue(layer_bool)
        self.assertTrue(edit_bool)
