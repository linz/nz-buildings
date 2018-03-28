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

    Tests: New Entry GUI Processes

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins
from buildings.utilities import database as db


class SetUpNewEntryGuiTest(unittest.TestCase):
    """Test New Entry GUI Processes"""
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
        if cls.dockwidget.stk_options.count() == 4:
            cls.dockwidget.stk_options.setCurrentIndex(3)
            cls.dockwidget.stk_options.addWidget(cls.dockwidget.frames['menu_frame'])
            cls.dockwidget.current_frame = 'menu_frame'
            cls.dockwidget.stk_options.setCurrentIndex(4)
        else:
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
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_new_entry.click()
        self.new_entry_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.new_entry_frame.btn_cancel.click()

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
        sql = "DELETE FROM buildings_bulk_load.organisation WHERE organisation_id = (SELECT MAX(organisation_id) FROM buildings_bulk_load.organisation)"
        db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_bulk_load.organisation WHERE organisation_id = (SELECT MAX(organisation_id) FROM buildings_bulk_load.organisation)"
            db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_bulk_load.organisation WHERE organisation_id = (SELECT MAX(organisation_id) FROM buildings_bulk_load.organisation)"
            db.execute(sql)

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
        sql = "DELETE FROM buildings.lifecycle_stage WHERE lifecylce_stage_id = (SELECT MAX(lifecycle_stage_id) FROM buildings.lifecycle_stage)"
        db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings.lifecycle_stage WHERE lifecylce_stage_id = (SELECT MAX(lifecycle_stage_id) FROM buildings.lifecycle_stage)"
            db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings.lifecycle_stage WHERE lifecylce_stage_id = (SELECT MAX(lifecycle_stage_id) FROM buildings.lifecycle_stage)"
            db.execute(sql)

    def test_new_capture_method(self):
        # test correct new capture_method
        self.cmb_new_type_selection.setCurrentIndex(2)
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Test capture_method")
        self.new_entry_frame.btn_ok.click()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result + 1)
        sql = "DELETE FROM buildings_common.capture_method WHERE capture_method_id = (SELECT MAX(capture_method_id) FROM buildings_common.capture_method)"
        db.execute(sql)
        # test existing capture_method
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText("Derived")
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_method WHERE capture_method_id = (SELECT MAX(capture_method_id) FROM buildings_common.capture_method)"
            db.execute(sql)
        # test null capture_method
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.btn_ok.click()
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertTrue(result2=result)
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_method WHERE capture_method_id = (SELECT MAX(capture_method_id) FROM buildings_common.capture_method)"
            db.execute(sql)

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
        sql = "DELETE FROM buildings_common.capture_source_group WHERE capture_source_group_id = (SELECT MAX(capture_source_group_id) FROM buildings_common.capture_source_group)"
        db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_source_group WHERE capture_source_group_id = (SELECT MAX(capture_source_group_id) FROM buildings_common.capture_source_group)"
            db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_source_group WHERE capture_source_group_id = (SELECT MAX(capture_source_group_id) FROM buildings_common.capture_source_group)"
            db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_source_group WHERE capture_source_group_id = (SELECT MAX(capture_source_group_id) FROM buildings_common.capture_source_group)"
            db.execute(sql)
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
        if result != result2:
            sql = "DELETE FROM buildings_common.capture_source_group WHERE capture_source_group_id = (SELECT MAX(capture_source_group_id) FROM buildings_common.capture_source_group)"
            db.execute(sql)
