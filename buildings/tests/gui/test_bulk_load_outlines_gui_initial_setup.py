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
from qgis.utils import reloadPlugin

from buildings.utilities import database as db


class SetUpBulkLoadGuiTest(unittest.TestCase):
    """Test Bulk Load Outlines GUI initial setup confirm default settings"""
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
        self.road_plugin = plugins.get('roads')
        self.building_plugin = plugins.get('buildings')
        self.dockwidget = self.road_plugin.dockwidget
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_load_outlines.click()
        self.bulk_load_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_cancel.click()

    def test_external_defaults(self):
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), 0)

    def test_supplied_layer_combobox(self):
        # check layer combobox contains only the layer in the qgis legend
        layers = iface.legendInterface().layers()
        self.assertEqual(self.bulk_load_frame.ml_outlines_layer.count(), len(layers))
        
    def test_data_desc_default(self):
        # check data description is enabled and empty
        self.assertTrue(self.bulk_load_frame.le_data_description.isEnabled())
        self.assertEqual(self.bulk_load_frame.le_data_description.text(), '')

    def test_organisation_combobox(self):
        # check organisation combobox same size as table
        sql = 'SELECT COUNT(value) FROM buildings_bulk_load.organisation'
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_organisation.count(), result)
        
    def test_capture_method_combobox(self):
        # Check capture method combobox same size as table
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_method'
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_method.count(), result2)

    def test_capture_source_group(self):
        # Check capture source group combobox same size as table
        sql = 'SELECT COUNT(value) FROM buildings_common.capture_source_group'
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_src_grp.count(), result3)



suite = unittest.TestLoader().loadTestsFromTestCase(SetUpBulkLoadGuiTest)
unittest.TextTestRunner(verbosity=2).run(suite)
