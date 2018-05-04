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


class SetUpCaptureSourceTest(unittest.TestCase):
    """Test New Capture Source GUI initial setup confirm default settings"""
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
        self.capture_frame.btn_cancel.click()

    def test_external_source_default(self):
        """External source line edit is disabled and radiobutton is not checked"""
        self.assertFalse(self.capture_frame.le_external_source_id.isEnabled())
        self.assertFalse(self.capture_frame.rad_external_source.isChecked())

    def test_capture_source_dropdowns(self):
        """Number of options in dropdown = number of entries in table"""
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(self.capture_frame.cmb_capture_source_group.count(),
                         result)
        self.capture_frame.rad_external_source.click()


suite = unittest.TestLoader().loadTestsFromTestCase(SetUpCaptureSourceTest)
unittest.TextTestRunner(verbosity=2).run(suite)
