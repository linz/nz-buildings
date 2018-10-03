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

    Tests: Alter Building Relationship GUI setup confirm default settings

 ***************************************************************************/
"""

import unittest

from PyQt4.QtCore import QModelIndex, Qt
from qgis.core import QgsProject
from qgis.utils import plugins


class SetUpAlterRelationshipsTest(unittest.TestCase):
    """
    Test Alter Building Relationship GUI initial
    setup confirm default settings
    """

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Bulk Load', Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.btn_alter_rel.click()
        self.alter_relationships_frame = self.dockwidget.current_frame

    def tearDown(self):
        """Runs after each test."""
        self.alter_relationships_frame.btn_exit.click()

    def test_bulk_load_gui_set_up(self):
        """ Initial set up of the frame """
        self.assertFalse(self.alter_relationships_frame.btn_unlink.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_matched.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_related.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_cancel.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_exit.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_not_checked.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_refer2supplier.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_pending.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_qa_okay.isEnabled())

        self.assertEqual(self.alter_relationships_frame.lst_existing.count(), 0)
        self.assertEqual(self.alter_relationships_frame.lst_bulk.count(), 0)

        self.assertEqual(self.alter_relationships_frame.cmb_relationship.currentIndex(), 0)
        self.assertEqual(self.alter_relationships_frame.tbl_relationship.rowCount(), 0)

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        layer_bool = True
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup('Building Tool Layers')
        layers = group.findLayers()
        layer_name = ['added_bulk_load_in_edit', 'removed_existing_in_edit',
                      'matched_existing_in_edit', 'matched_bulk_load_in_edit',
                      'related_existing_in_edit', 'related_bulk_load_in_edit',
                      'added_outlines', 'removed_outlines', 'matched_existing_outlines',
                      'matched_bulk_load_outlines', 'related_existing_outlines',
                      'related_bulk_load_outlines', 'bulk_load_outlines', 'existing_subset_extracts']
        for layer in layers:
            if layer.layer().name() not in layer_name:
                layer_bool = False

        self.assertEqual(len([layer for layer in layers]), len(layer_name))
        self.assertTrue(layer_bool)
