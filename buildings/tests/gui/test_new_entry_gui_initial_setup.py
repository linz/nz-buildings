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

    Tests: New Entry GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins
from buildings.utilities import database as db


class SetUpNewEntryGuiTest(unittest.TestCase):
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
        self.menu_frame.btn_new_entry.click()
        self.new_entry_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.new_entry_frame.btn_cancel.click()

    def test_new_entry_gui_set_up(self):
        # initial combobox text is organisation
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(self.new_entry_frame.cmb_new_type_selection.currentIndex()), "Organisation")
        # has four options in combobox
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.count(), 4)
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(1), "Lifecycle Stage")
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(2), "Capture Method")
        self.assertEquals(self.new_entry_frame.cmb_new_type_selection.itemText(3), "Capture Source Group")
        # value is enabled on start up
        self.assertTrue(self.new_entry_frame.le_new_entry.isEnabled())
        # description is disbaled on startup
        self.assertFalse(self.new_entry_frame.le_description.isEnabled())
        # change to capture source group option description becomes enabled
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.assertTrue(self.new_entry_frame.le_description.isEnabled())

    def test_new_organisation(self):
        # test correct new organisation
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test Organisation")
        self.new_entry_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # test existing organisation
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Ecopia")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test null organisation
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)

    def test_new_lifecycle_stage(self):
        # test correct new lifecycle_stage
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test lifecycle_stage")
        self.new_entry_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # test existing lifecycle_stage
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Current")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test null lifecycle_stage
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings.lifecycle_stage"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)

    def test_new_capture_method(self):
        # test correct new capture_method
        self.cmb_new_type_selection.setCurrentIndex(2)
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test capture_method")
        self.new_entry_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM building_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # test existing capture_method
        sql = "SELECT COUNT(value) FROM building_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Derived")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM building_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test null capture_method
        sql = "SELECT COUNT(value) FROM building_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM building_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)

    def test_new_capture_source_group(self):
        # test correct new capture_source_group
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test capture_source_group")
        self.new_entry_frame.le_description.setTest("Test description")
        self.new_entry_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        # test existing capture_source_group
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("NZ Aerial Imagery")
        self.new_entry_frame.le_description.setTest("Replace with link to LDS table...")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test capture_source_group null value & complete description
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("")
        self.new_entry_frame.le_description.setTest("Test description two")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test capture_source_group complete value & null description
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test capture source group two")
        self.new_entry_frame.le_description.setTest("")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        # test capture_source_group null value & null description
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("")
        self.new_entry_frame.le_description.setTest("")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)

