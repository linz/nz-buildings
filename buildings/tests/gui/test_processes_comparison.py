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

    Tests: Compare Outlines Button Click Confirm Processes

 ***************************************************************************/
"""

import unittest

from qgis.utils import plugins

from buildings.utilities import database as db


class SetUpEditBulkLoad(unittest.TestCase):
    """
    Test Add Production Outline GUI initial
    setup confirm default settings
    """
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
                cls.building_plugin.main_toolbar.actions()[0].trigger()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        cls.road_plugin.dockwidget.close()

    def setUp(self):
        """Runs before each test."""
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.setup_frame = self.building_plugin.setup_frame
        self.setup_frame.btn_bulk_load.click()
        self.bulk_load_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()

    def test_compare_added(self):
        """"""
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 2003)
        self.assertEqual(result[1][0], 2010)
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_compare_removed(self):
        """"""
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 1004)
        self.assertEqual(result[1][0], 1006)
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_compare_matched(self):
        """"""
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], (1001, 2031))
        self.assertEqual(result[1], (1002, 2001))
        self.assertEqual(result[2], (1003, 2002))
        self.assertEqual(result[3], (1005, 2004))
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_compare_related(self):
        """"""
        self.bulk_load_frame.compare_outlines_clicked(False)
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 43)
        self.assertEqual(result[0], (1007, 2005))
        self.assertEqual(result[1], (1008, 2005))
        self.assertEqual(result[2], (1009, 2006))
        self.assertEqual(result[3], (1010, 2006))
        self.assertEqual(result[4], (1011, 2006))
        self.assertEqual(result[5], (1012, 2007))
        self.assertEqual(result[6], (1013, 2007))
        self.assertEqual(result[7], (1014, 2007))
        self.assertEqual(result[8], (1015, 2007))
        self.assertEqual(result[9], (1016, 2008))
        self.assertEqual(result[10], (1017, 2008))
        self.assertEqual(result[11], (1018, 2008))
        self.assertEqual(result[12], (1019, 2008))
        self.assertEqual(result[13], (1020, 2008))
        self.assertEqual(result[14], (1021, 2009))
        self.assertEqual(result[15], (1022, 2009))
        self.assertEqual(result[16], (1023, 2009))
        self.assertEqual(result[17], (1024, 2009))
        self.assertEqual(result[18], (1025, 2009))
        self.assertEqual(result[19], (1026, 2009))
        self.assertEqual(result[20], (1027, 2011))
        self.assertEqual(result[21], (1027, 2012))
        self.assertEqual(result[22], (1028, 2013))
        self.assertEqual(result[23], (1028, 2014))
        self.assertEqual(result[24], (1028, 2015))
        self.assertEqual(result[25], (1029, 2016))
        self.assertEqual(result[26], (1029, 2017))
        self.assertEqual(result[27], (1029, 2018))
        self.assertEqual(result[28], (1029, 2019))
        self.assertEqual(result[29], (1030, 2020))
        self.assertEqual(result[30], (1030, 2021))
        self.assertEqual(result[31], (1030, 2022))
        self.assertEqual(result[32], (1030, 2023))
        self.assertEqual(result[33], (1030, 2024))
        self.assertEqual(result[34], (1031, 2025))
        self.assertEqual(result[35], (1031, 2026))
        self.assertEqual(result[36], (1031, 2027))
        self.assertEqual(result[37], (1031, 2028))
        self.assertEqual(result[38], (1031, 2029))
        self.assertEqual(result[39], (1031, 2030))
        self.assertEqual(result[40], (1032, 2032))
        self.assertEqual(result[41], (1032, 2033))
        self.assertEqual(result[42], (1033, 2033))
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_gui_on_compare_clicked(self):
        """"""
        self.bulk_load_frame.compare_outlines_clicked(False)
        self.assertFalse(self.bulk_load_frame.btn_compare_outlines.isEnabled())
        self.assertTrue(self.bulk_load_frame.btn_publish.isEnabled())
