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

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
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
        self.dockwidget.lst_options.setCurrentItem(self.dockwidget.lst_options.item(2))
        self.menu_frame = self.building_plugin.menu_frame
        self.menu_frame.btn_load_outlines.click()
        self.bulk_load_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_cancel.click()

    def test_bulk_load_gui_set_up(self):
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        # check layer combobox contains only the layer in the qgis legend
        layers = iface.legendInterface().layers()
        self.assertEqual(self.bulk_load_frame.ml_outlines_layer.count(), len(layers))
        # check data description is enabled and empty
        self.assertTrue(self.bulk_load_frame.le_data_description.isEnabled())
        self.assertEquals(self.bulk_load_frame.le_data_description.text(), "")
        # check organisation combobox same size as table
        sql = "SELECT COUNT(value) FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        self.assertEquals(self.bulk_load_frame.cmb_organisation.count(), result)
        # Check capture method combobox same size as table
        sql = "SELECT COUNT(value) FROM buildings_common.capture_method"
        result2 = db._execute(sql)
        result2 = result2.fetchall()[0][0]
        self.assertEquals(self.bulk_load_frame.cmb_capture_method.count(), result2)
        # Check capture source group combobox same size as table
        sql = "SELECT COUNT(value) FROM buildings_common.capture_source_group"
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEquals(self.bulk_load_frame.cmb_capture_src_grp.count(), result3)
        # check external id combobox on start up is empty
        self.assertEquals(self.bulk_load_frame.cmb_capture_external_id.count(), 0)

    def test_external_id_radiobutton(self):
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        self.bulk_load_frame.rad_external_source.click()
        self.assertTrue(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        # check external source id value is correctly populated
        sql = "SELECT COUNT(external_source_id) FROM buildings_common.capture_source"
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_capture_external_id.count(), result3)
        # check external id combobox populated with fields of current layer
        vectorlayer = self.bulk_load_frame.ml_outlines_layer.currentLayer()
        fields = vectorlayer.pendingFields()
        self.assertEqual(self.bulk_load_frame.fcb_external_id.count(), len(fields))
        self.bulk_load_frame.rad_external_source.click()
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())

    def test_imagery_layers(self):
        layers = iface.legendInterface().layers()
        self.assertEqual(self.bulk_load_frame.mcb_imagery_layer.count(), len(layers))
        imagery_vector_layer = self.bulk_load_frame.mcb_imagery_layer.currentLayer()
        fields = imagery_vector_layer.pendingFields()
        self.assertEqual(self.bulk_load_frame.fcb_imagery_field.count(), len(fields))
        self.bulk_load_frame.fcb_imagery_field.setField(fields[0].name())
        imagery_field = self.bulk_load_frame.fcb_imagery_field.currentField()
        idx = imagery_vector_layer.fieldNameIndex(fields[0].name())
        values = imagery_vector_layer.uniqueValues(idx)
        assertEqual(self.bulk_load_frame.cmb_imagery.count(), len(values))