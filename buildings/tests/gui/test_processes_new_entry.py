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


class ProcessNewEntryTest(unittest.TestCase):
    """Test New Entry GUI Processes"""
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
        self.menu_frame.btn_new_entry.click()
        self.new_entry_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.new_entry_frame.btn_exit.click()

    def test_valid_new_organisation(self):
        """New organisation added"""
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText('Test Organisation')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_duplicate_organisation(self):
        """Gives error when adding duplicate organisation"""
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.le_new_entry.setText('Ecopia')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_null_organisation(self):
        """Gives error when adding null organisation"""
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_valid_new_lifecycle_stage(self):
        """New lifecycle stage added"""
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(1)
        self.new_entry_frame.le_new_entry.setText('Test lifecycle Stage')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_duplicate_lifecycle_stage(self):
        """Gives error when duplicate lifecycle stage added"""
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(1)
        self.new_entry_frame.le_new_entry.setText('Current')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_null_lifecycle_stage(self):
        """Gives error when null lifecycle stage added"""
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(1)
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings.lifecycle_stage'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_valid_new_capture_method(self):
        """New capture method added"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(2)
        self.new_entry_frame.le_new_entry.setText('Test Capture Method')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_duplicate_capture_method(self):
        """Gives error when duplicate capture method added"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(2)
        self.new_entry_frame.le_new_entry.setText('Derived')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_null_capture_method(self):
        """gives error when null capture method added"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(2)
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_valid_new_capture_source_group(self):
        """New capture source group added"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.new_entry_frame.le_new_entry.setText('Test Capture Source Group')
        self.new_entry_frame.le_description.setText('Test Description')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result + 1)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_duplicate_capture_source_group(self):
        """gives error when duplicate capture source group added"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.new_entry_frame.le_new_entry.setText('NZ Aerial Imagery')
        self.new_entry_frame.le_description.setText('Replace with link to LDS table...')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_capture_source_group_null_value_complete_desc(self):
        """gives error when null value & complete description"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.new_entry_frame.le_new_entry.setText('')
        self.new_entry_frame.le_description.setText('Test description two')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_capture_source_group_complete_value_null_desc(self):
        """gives error when complete value & null description"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.new_entry_frame.le_new_entry.setText('Test CSG 2')
        self.new_entry_frame.le_description.setText('')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()

    def test_capture_source_group_null(self):
        """Gives error when null value & null description"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.new_entry_frame.cmb_new_type_selection.setCurrentIndex(3)
        self.new_entry_frame.le_new_entry.setText('')
        self.new_entry_frame.le_description.setText('')
        self.new_entry_frame.ok_clicked(built_in=False, commit_status=False)
        self.assertTrue(self.new_entry_frame.error_dialog is not None)
        self.new_entry_frame.error_dialog.close()
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        self.new_entry_frame.db.rollback_open_cursor()


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessNewEntryTest)
unittest.TextTestRunner(verbosity=2).run(suite)
