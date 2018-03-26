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

from qgis.utils import plugins, iface

from buildings.utilities import database as db


class SetUpBulkLoadGuiTest(unittest.TestCase):
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
        self.menu_frame.btn_load_outlines.click()
        self.bulk_load_frame = self.dockwidget.widget()

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_cancel.click()

    def test_bulk_load_gui_set_up(self):
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        # check layer combobox contains only the layer in the qgis legend
        # check data description is enabled and empty
        self.assertTrue(self.bulk_load_frame.le_data_description.isEnabled())
        self.assertEquals(self.bulk_load_frame.le_data_description.text(), '')
        # check organisation combobox same size as table
        sql = "SELECT COUNT(organisation) FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEquals(self.bulk_load_frame.cmb_organisation.count(), result)
        # Check capture method combobox same size as table
        # Check capture source group combobox same size as table
        # check external id combobox same size as table
        # Check imagery layer comboboxes
        # TODO: what happens if no capture source entries?

    def test_external_id_radiobutton(self):
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        self.bulk_load_frame.rad_external_source.click()
        self.assertTrue(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        self.bulk_load_frame.rad_external_source.click()
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
