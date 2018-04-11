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
from qgis.utils import reloadPlugin

from buildings.utilities import database as db


class ProcessCaptureSourceGuiTest(unittest.TestCase):
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
                cls.building_plugin = plugins.get('buildings')
                reloadPlugin('buildings')
                if cls.dockwidget.stk_options.count() == 4:
                    cls.dockwidget.stk_options.setCurrentIndex(3)
                    cls.dockwidget.stk_options.addWidget(cls.dockwidget.frames['menu_frame'])
                    cls.dockwidget.current_frame = cls.dockwidget.frames['menu_frame']
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
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_add_capture_source.click()
        self.capture_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.capture_frame.btn_cancel.click()

    def test_external_radio_button(self):
        self.capture_frame.rad_external_source.click()
        self.assertTrue(self.capture_frame.le_external_source_id.isEnabled())
        self.capture_frame.rad_external_source.click()
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())

    def test_add_valid_capture_source_no_EID(self):
        # add valid capture source no external id
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.btn_ok.click()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        sql = 'SELECT buildings_common.fn_capture_source_delete(%s)'
        db.execute(sql, (self.capture_frame.capture_source_id, ))

    def test_add_duplicate_capture_source(self):
        # add duplicate capture source no external id
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.btn_ok.click()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.btn_ok.click()
        self.capture_frame.error_dialog.close()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        sql = 'SELECT buildings_common.fn_capture_source_delete(%s)'
        db.execute(sql, (self.capture_frame.capture_source_id, ))

    def test_add_blank_external_id_line_edit(self):
        # add capture source external radio button checked and no external id
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.btn_ok.click()
        self.capture_frame.error_dialog.close()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, result)
        if result != result2:
            sql = 'SELECT buildings_common.fn_capture_source_delete(%s)'
            db.execute(sql, (self.capture_frame.capture_source_id, ))

    def test_add_valid_capture_source_with_EID(self):
        # add capture source with valid external id
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.capture_frame.cmb_capture_source_group.setCurrentIndex(0)
        self.capture_frame.rad_external_source.click()
        self.capture_frame.le_external_source_id.setText('Test Ext Source')
        self.capture_frame.btn_ok.click()
        sql = 'SELECT COUNT(capture_source_id) FROM buildings_common.capture_source'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            result2 = result2.fetchall()[0][0]
        self.assertEqual(result2, (result + 1))
        sql = 'SELECT buildings_common.fn_capture_source_delete(%s)'
        db.execute(sql, (self.capture_frame.capture_source_id, ))


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessCaptureSourceGuiTest)
unittest.TextTestRunner(verbosity=2).run(suite)
