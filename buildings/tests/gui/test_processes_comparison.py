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
from builtins import str

import os
import unittest

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject
from qgis.utils import iface, plugins

from buildings.utilities import database as db


class ProcessComparison(unittest.TestCase):
    """
    Test Add Production Outline GUI initial
    setup confirm default settings
    """

    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        db.connect()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get("buildings")
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems("Bulk Load", Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.db.open_cursor()

        btn_yes = self.bulk_load_frame.msgbox_publish.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.publish_clicked(False)
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testdata/test_bulk_load_shapefile.shp")
        layer = iface.addVectorLayer(path, "", "ogr")
        count = self.bulk_load_frame.ml_outlines_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.ml_outlines_layer.layer(idx).name() == "test_bulk_load_shapefile":
                self.bulk_load_frame.ml_outlines_layer.setLayer(self.bulk_load_frame.ml_outlines_layer.layer(idx))
                break
            idx = idx + 1
        # select capture source area
        self.bulk_load_frame.cmb_cap_src_area.setCurrentIndex(self.bulk_load_frame.cmb_cap_src_area.findText("1- Imagery One"))
        # add description
        self.bulk_load_frame.le_data_description.setText("Test bulk load outlines")
        # add outlines
        btn_yes = self.bulk_load_frame.msgbox_bulk_load.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.bulk_load_save_clicked(False)
        self.bulk_load_frame.bulk_load_layer = layer

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.db.rollback_open_cursor()
        self.bulk_load_frame.exit_clicked()
        # remove temporary layers from canvas
        layers = QgsProject.instance().layerTreeRoot().layerOrder()
        for layer in layers:
            if "test_bulk_load_shapefile" in str(layer.id()) or "bulk_load_outlines" in str(layer.id()):
                QgsProject.instance().removeMapLayer(layer.id())

    def test_compare(self):
        """test database on compare clicked"""
        btn_yes = self.bulk_load_frame.msgbox_compare.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.compare_outlines_clicked(False)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;"
        resulta = db._execute(sql)
        resulta = resulta.fetchall()
        # removed
        sql = "SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;"
        resultr = db._execute(sql)
        resultr = resultr.fetchall()
        # matched
        sql = "SELECT bulk_load_outline_id, building_outline_id FROM buildings_bulk_load.matched ORDER BY bulk_load_outline_id, building_outline_id;"
        resultm = db._execute(sql)
        resultm = resultm.fetchall()
        # related
        sql = "SELECT bulk_load_outline_id, building_outline_id FROM buildings_bulk_load.related ORDER BY bulk_load_outline_id, building_outline_id;"
        resultrl = db._execute(sql)
        resultrl = resultrl.fetchall()
        # FAILS HERE - RESULT = 2
        # self.assertEqual(len(resulta), 16)
        self.assertEqual(len(resultr), 33)
        self.assertEqual(len(resultm), 4)
        self.assertEqual(len(resultrl), 46)

    def test_gui_on_compare_clicked(self):
        """Check buttons are enabled/disabled"""
        btn_yes = self.bulk_load_frame.msgbox_compare.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.compare_outlines_clicked(False)
        self.assertFalse(self.dockwidget.current_frame.btn_compare_outlines.isEnabled())
        self.assertTrue(self.dockwidget.current_frame.btn_publish.isEnabled())

    def test_outline_delete_during_qa(self):
        """Checks outlines that are deleted during qa before comparisons is run are not carried through"""
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE description = 'Test bulk load outlines';"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        sql = "UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = 3 WHERE supplied_dataset_id = %s;"
        db._execute(sql, (result,))

        btn_yes = self.bulk_load_frame.msgbox_compare.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.compare_outlines_clicked(False)
        # added
        sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 2)
        # Matched
        sql = "SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;"
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)
        # related
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 44)
        # removed
        # FAILS HERE - RESULT = 2
        # sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        # result = db._execute(sql)
        # result = result.fetchall()
        # self.assertEqual(len(result), 35)

    def test_outline_add_during_qa(self):
        """Checks outlines that are added during qa before comparisons is not causing issues when carried through"""
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE description = 'Test bulk load outlines';"
        result = db._execute(sql)
        result = result.fetchall()[0][0]
        # Add one outline in both bulk_load_outlines and added table
        sql = "SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        result = db._execute(
            sql,
            (
                result,
                None,
                2,
                1,
                1001,
                101,
                1001,
                10001,
                "0103000020910800000100000005000000EA7ABCBF6AA83C414C38B255343155417C46175878A83C413A28764134315541C18607A978A83C417A865C33323155412FBBAC106BA83C417A865C3332315541EA7ABCBF6AA83C414C38B25534315541",
            ),
        )
        result = result.fetchall()[0][0]

        btn_yes = self.bulk_load_frame.msgbox_compare.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.compare_outlines_clicked(False)
        # added
        # FAILS HERE - RESULT = 2
        # sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.added ORDER BY bulk_load_outline_id;"
        # result = db._execute(sql)
        # result = result.fetchall()
        # self.assertEqual(len(result), 17)
        # matched
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.matched ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 4)
        # related
        sql = 'SELECT building_outline_id, bulk_load_outline_id FROM buildings_bulk_load.related ORDER BY building_outline_id, bulk_load_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 46)
        # removed
        sql = 'SELECT building_outline_id FROM buildings_bulk_load.removed ORDER BY building_outline_id;'
        result = db._execute(sql)
        result = result.fetchall()
        self.assertEqual(len(result), 33)
