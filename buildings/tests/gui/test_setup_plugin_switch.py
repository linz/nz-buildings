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

    Tests: Edit Bulk Loaded Outlines GUI Processes

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest
from qgis.core import QgsRectangle, QgsPoint, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapTool
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class ProcessBulkLoadEditOutlinesTest(unittest.TestCase):
    """Test Edit Bulk Outline GUI Processes"""
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
                db.connect()
                cls.building_plugin = plugins.get('buildings')
                cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_switching_non_editing(self):
        """Check still editing when switched to Roads and Back"""
        self.bulk_load_frame.rad_edit.click()
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(1))
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(2))
        self.assertTrue(self.bulk_load_frame.bulk_load_layer.isEditable())

    def test_switching_editing(self):
        """Check not editing when switched to Roads and Back"""
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(1))
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(2))
        self.assertFalse(self.bulk_load_frame.bulk_load_layer.isEditable())
