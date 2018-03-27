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

from buildings.utilities import database as db


class SetUpCaptureSourceGuiTest(unittest.TestCase):
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
            else:
                cls.dockwidget = cls.road_plugin.dockwidget
            if not plugins.get("buildings"):
                pass
            else:
                cls.building_plugin = plugins.get("buildings")
        cls.dockwidget.stk_options.setCurrentIndex(4)
        cls.dockwidget.lst_options.setCurrentItem(cls.dockwidget.lst_options.item(2))

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
        self.menu_frame.btn_add_capture_source.click()
        self.capture_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_frame.btn_cancel.click()

    def test_new_capture_source_gui_set_up(self):
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())
        self.assertFalse(self.capture_frame.rad_external_source.isChecked())
        # check number of options in dropdown is the same as number of
        # entries in capture_source_group table
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(self.capture_frame.cmb_capture_source_group.count(), result)
        self.capture_frame.rad_external_source.click()
        self.assertTrue(self.new_entry_frame.le_new_entry.isEnabled())
        self.assertFalse(self.new_entry_frame.le_description.isEnabled())

    def test_radio_button(self):
        self.capture_frame.rad_external_source.click()
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.capture_frame.rad_external_source.click()
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())

    def test_add_new_capture_source(self):
        # add valid capture source no external id
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.capture_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # add duplicate capture source no external id
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.capture_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # add capture source external radio button checked and no external id
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.capture_frame.rad_external_source.click()
        self.capture_frame.btn_ok.click()
        self.capture_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # add capture source with valid external id
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.capture_frame.rad_external_source.click()
        self.capture_frame.le_external_source_id.setText("Test Ext Source")
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # add duplicate capture source and external id
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.capture_frame.rad_external_source.click()
        self.capture_frame.le_external_source_id.setText("Test Ext Source")
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)

