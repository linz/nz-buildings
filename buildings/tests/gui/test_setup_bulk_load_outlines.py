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

    Tests: Bulk Load Outlines GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import Qt
from qgis.utils import plugins, iface

from buildings.utilities import database as db


class SetUpBulkLoadTest(unittest.TestCase):
    """Test Bulk Load Outlines GUI initial setup confirm default settings"""
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
            'Bulk Load', Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.db.open_cursor()
        self.bulk_load_frame.publish_clicked(False)

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_external_defaults(self):
        """External source comboboxes disabled on setup"""
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), 0)

    def test_supplied_layer_combobox(self):
        """Bulk load layer combobox contains only the layers in the qgis legend"""
        layers = iface.legendInterface().layers()
        self.assertEqual(self.bulk_load_frame.ml_outlines_layer.count(),
                         len(layers))

    def test_data_description_default(self):
        """Data description is enabled and empty"""
        self.assertTrue(self.bulk_load_frame.le_data_description.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_data_description.text(), '')

    def test_organisation_combobox(self):
        """Organisation combobox same size as table"""
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_organisation.count(), result)

    def test_capture_method_combobox(self):
        """Capture method combobox same size as table"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_method.count(),
                         result2)

    def test_capture_source_group(self):
        """Capture source group combobox same size as table"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_src_grp.count(),
                         result3)
