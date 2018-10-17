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

    Tests: New Capture Source GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins
from qgis.core import QgsProject
from PyQt4.QtCore import Qt

from buildings.utilities import database as db


class SetUpCaptureSourceTest(unittest.TestCase):
    """Test New Capture Source GUI initial setup confirm default settings"""
    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        db.connect()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Capture Sources', Qt.MatchExactly)[0])
        self.capture_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_frame.btn_exit.click()

    def test_capture_source_dropdowns(self):
        """Number of options in dropdown = number of entries in table"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(self.capture_frame.cmb_capture_source_group.count(),
                         result)

    def test_capture_source_area_layer_registry(self):
        """Capture source area layer is added to layer registry"""
        layer_bool = True
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        layer_name = ['capture_source_area']
        for layer in layers:
            if layer.layer().name() not in layer_name:
                layer_bool = False

        self.assertEqual(len([layer for layer in layers]), len(layer_name))
        self.assertTrue(layer_bool)
