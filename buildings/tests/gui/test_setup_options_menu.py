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

    Tests: Menu GUI menu confirm default settings

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QListWidgetItem
from qgis.utils import plugins


class SetUpOptionsTest(unittest.TestCase):
    """Test Menu GUI initial menu confirm default settings"""

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget

    def tearDown(self):
        """Runs after each test"""
        self.dockwidget.close()

    def test_option_menu(self):
        """Buildings option menu item exists"""
        self.assertIsInstance(
            self.dockwidget.lst_options.findItems("Buildings", Qt.MatchExactly)[0],
            QListWidgetItem,
        )

    def test_sub_option_menu(self):
        """Sub menu options exist"""
        self.assertIsInstance(
            self.dockwidget.lst_sub_menu.findItems("Capture Sources", Qt.MatchExactly)[
                0
            ],
            QListWidgetItem,
        )
        self.assertIsInstance(
            self.dockwidget.lst_sub_menu.findItems("Bulk Load", Qt.MatchExactly)[0],
            QListWidgetItem,
        )
        self.assertIsInstance(
            self.dockwidget.lst_sub_menu.findItems("Edit Outlines", Qt.MatchExactly)[0],
            QListWidgetItem,
        )
        self.assertIsInstance(
            self.dockwidget.lst_sub_menu.findItems("Settings", Qt.MatchExactly)[0],
            QListWidgetItem,
        )
