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

from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from qgis.utils import plugins, iface


class SetUpAlterRelationshipsTest(unittest.TestCase):
    """
    Test Alter Building Relationship GUI initial
    setup confirm default settings
    """

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Bulk Load", Qt.MatchExactly)[0])
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
        self.assertFalse(self.alter_relationships_frame.cb_autosave.isChecked())
        self.assertFalse(self.alter_relationships_frame.btn_save.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_cancel.isEnabled())
        self.assertTrue(self.alter_relationships_frame.btn_exit.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_not_checked.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_refer2supplier.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_pending.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_okay.isEnabled())
        self.assertFalse(self.alter_relationships_frame.btn_qa_not_removed.isEnabled())

        self.assertEqual(self.alter_relationships_frame.lst_existing.count(), 0)
        self.assertEqual(self.alter_relationships_frame.lst_bulk.count(), 0)

        self.assertEqual(self.alter_relationships_frame.cmb_relationship.currentIndex(), 0)
        self.assertEqual(self.alter_relationships_frame.tbl_relationship.rowCount(), 0)

    def test_layer_registry(self):
        """ Layer registry has the correct components """
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Building Tool Layers")
        layers = group.findLayers()
        intended_layer_names = [
            "added_bulk_load_in_edit",
            "added_outlines",
            "bulk_load_outlines",
            "existing_subset_extracts",
            "facilities",
            "matched_bulk_load_in_edit",
            "matched_bulk_load_outlines",
            "matched_existing_in_edit",
            "matched_existing_outlines",
            "related_bulk_load_in_edit",
            "related_bulk_load_outlines",
            "related_existing_in_edit",
            "related_existing_outlines",
            "removed_existing_in_edit",
            "removed_outlines",
        ]
        actual_layer_names = sorted(l.layer().name() for l in layers)
        self.assertEqual(actual_layer_names, intended_layer_names)

    def test_has_toolbar(self):
        self.assertTrue(iface.building_toolbar.isVisible())
        actions = [action.text() for action in iface.building_toolbar.actions()]
        self.assertEquals(", ".join(actions), "Pan Map, Add Outline, Edit Geometry, Edit Attributes")

    def test_add_outline(self):
        edit_dialog = self.alter_relationships_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Add Outline":
                action.trigger()
        # edit dialog name is add outline
        self.assertTrue(edit_dialog.isVisible())
        self.assertEquals(edit_dialog.windowTitle(), "Add Outline")
        self.assertFalse(edit_dialog.layout_status.isVisible())
        self.assertTrue(edit_dialog.layout_capture_method.isVisible())
        self.assertTrue(edit_dialog.layout_general_info.isVisible())
        self.assertFalse(edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(edit_dialog.cmb_town.isEnabled())
        self.assertFalse(edit_dialog.cmb_suburb.isEnabled())
        self.assertFalse(edit_dialog.cmb_ta.isEnabled())

    def test_edit_geometry(self):
        edit_dialog = self.alter_relationships_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Geometry":
                action.trigger()
        # edit dialog name is Edit Geometry
        self.assertTrue(edit_dialog.isVisible())
        self.assertEquals(edit_dialog.windowTitle(), "Edit Geometry")
        self.assertFalse(edit_dialog.layout_status.isVisible())
        self.assertTrue(edit_dialog.layout_capture_method.isVisible())
        self.assertFalse(edit_dialog.layout_general_info.isVisible())
        self.assertFalse(edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(edit_dialog.cmb_capture_method.isEnabled())

    def test_edit_attribute(self):
        edit_dialog = self.alter_relationships_frame.edit_dialog
        for action in iface.building_toolbar.actions():
            if action.text() == "Edit Attributes":
                action.trigger()
        # edit dialog name is Edit Attributes
        self.assertTrue(edit_dialog.isVisible())
        self.assertEquals(edit_dialog.windowTitle(), "Edit Attribute")
        self.assertTrue(edit_dialog.layout_status.isVisible())
        self.assertTrue(edit_dialog.layout_capture_method.isVisible())
        self.assertTrue(edit_dialog.layout_general_info.isVisible())
        self.assertFalse(edit_dialog.btn_edit_save.isEnabled())
        self.assertFalse(edit_dialog.btn_edit_reset.isEnabled())
        self.assertFalse(edit_dialog.cmb_capture_method.isEnabled())
        self.assertFalse(edit_dialog.cmb_capture_source.isEnabled())
        self.assertFalse(edit_dialog.cmb_ta.isEnabled())
        self.assertFalse(edit_dialog.cmb_town.isEnabled())
        self.assertFalse(edit_dialog.cmb_suburb.isEnabled())
        self.assertFalse(edit_dialog.cmb_status.isEnabled())
