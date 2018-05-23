
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

    Tests: New Capture Source GUI Processes

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins

from buildings.utilities import database as db


class ProcessCaptureSourceTest(unittest.TestCase):
    """Test New Capture Source GUI Processes"""
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
        self.menu_frame.btn_add_capture_source.click()
        self.capture_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_frame.btn_exit.click()

    def test_external_radio_button(self):
        """External source line edit enabled when external source radiobutton selected"""
        self.capture_frame.rad_external_source.click()
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.capture_frame.rad_external_source.click()
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())

    def test_add_valid_capture_source_no_external_id(self):
        """Valid capture source added when ok clicked"""
        # add valid capture source no external id
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]

        # Add a capture source group for testing
        self.capture_frame.db.open_cursor()
        sql = "INSERT INTO buildings_common.capture_source_group (value, description) VALUES ('Test Source', 'Test Source');"
        self.capture_frame.db.execute_no_commit(sql)
        # populate the combobox including the test data
        self.capture_frame.cmb_capture_source_group.clear()
        self.capture_frame.populate_combobox()

        self.capture_frame.cmb_capture_source_group.setCurrentIndex(self.capture_frame.cmb_capture_source_group.findText('Test Source- Test Source'))
        self.capture_frame.ok_clicked(commit_status=False)
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        self.capture_frame.db.rollback_open_cursor()

    def test_add_blank_external_id_line_edit(self):
        """Error dialog when external radio button checked and no external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.ok_clicked(commit_status=False)
        if self.capture_frame.error_dialog is not None:
            self.capture_frame.error_dialog.close()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        if result != result2:
            if self.capture_frame.error_dialog is not None:
                self.capture_frame.error_dialog.close()
        self.capture_frame.db.rollback_open_cursor()

    def test_add_valid_capture_source_with_external_id(self):
        """Valid capture source with valid external id"""
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.le_external_source_id.setText('Test Ext Source')
        self.capture_frame.ok_clicked(commit_status=False)
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source;'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        self.capture_frame.db.rollback_open_cursor()


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessCaptureSourceTest)
unittest.TextTestRunner(verbosity=2).run(suite)
