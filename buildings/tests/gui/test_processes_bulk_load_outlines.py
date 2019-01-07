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

    Tests: Bulk Load Outlines GUI processing

 ***************************************************************************/
"""

import os
import unittest

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QMessageBox
from qgis.core import QgsMapLayerRegistry
from qgis.utils import iface, plugins

from buildings.utilities import database as db


class ProcessBulkLoadTest(unittest.TestCase):
    """Test Bulk Load Outlines GUI processing"""

    @classmethod
    def setUpClass(cls):
        """Runs at TestCase init."""
        db.connect()

    @classmethod
    def tearDownClass(cls):
        """Runs at TestCase teardown."""
        db.close_connection()
        # remove temporary layers from canvas
        layers = iface.legendInterface().layers()
        for layer in layers:
            if 'test_bulk_load_shapefile' in str(layer.id()):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def setUp(self):
        """Runs before each test."""
        self.building_plugin = plugins.get('buildings')
        self.building_plugin.main_toolbar.actions()[0].trigger()
        self.dockwidget = self.building_plugin.dockwidget
        sub_menu = self.dockwidget.lst_sub_menu
        sub_menu.setCurrentItem(sub_menu.findItems(
            'Bulk Load', Qt.MatchExactly)[0])
        self.bulk_load_frame = self.dockwidget.current_frame
        self.bulk_load_frame.db.open_cursor()

        btn_yes = self.bulk_load_frame.msgbox_publish.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.publish_clicked(False)

    def tearDown(self):
        """Runs after each test."""
        self.bulk_load_frame.btn_exit.click()
        # rollback changes
        self.bulk_load_frame.db.rollback_open_cursor()

    def test_external_id_radiobutton(self):
        """external source fields enable when external id radio button is enabled"""
        # checks on starting the restrictions are in place
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        # click the radio button
        self.bulk_load_frame.rad_external_id.click()
        # check restrictions have been removed
        self.assertTrue(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        # check external source id value is correctly populated
        sql = 'SELECT COUNT(external_source_id) FROM buildings_common.capture_source;'
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), result3)
        # check external id combobox populated with fields of current layer
        vectorlayer = self.bulk_load_frame.ml_outlines_layer.currentLayer()
        fields = vectorlayer.pendingFields()
        self.assertEqual(self.bulk_load_frame.fcb_external_id.count(),
                         len(fields))
        # check on unclicking radio button the restrictions are restablished
        self.bulk_load_frame.rad_external_id.click()
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())

    def test_cmb_capture_src_grp_changed(self):
        """When cmb_capture_src_grp changes cmb_external_id is re-populated"""
        self.bulk_load_frame.db.open_cursor()
        sql = 'SELECT buildings_common.capture_source_group_insert(%s, %s);'
        result = self.bulk_load_frame.db.execute_no_commit(sql, ('Test value', 'Test description'))
        capture_source_group_id = result.fetchall()[0][0]

        sql = 'SELECT buildings_common.capture_source_insert(%s, %s);'
        result = self.bulk_load_frame.db.execute_no_commit(sql, (int(capture_source_group_id), '3'))

        count = self.bulk_load_frame.cmb_capture_src_grp.count()
        for i in range(count):
            self.bulk_load_frame.cmb_capture_src_grp.setCurrentIndex(i)
            text = self.bulk_load_frame.cmb_capture_src_grp.currentText()
            text = text.split('-')[0]
            if text == 'NZ Aerial Imagery':
                self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), 2)
            elif text == 'Test value':
                self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), 1)

    def test_bulk_load_save_clicked(self):
        """When save is clicked data is added to the correct tables"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'testdata/test_bulk_load_shapefile.shp')
        iface.addVectorLayer(path, '', 'ogr')
        count = self.bulk_load_frame.ml_outlines_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.ml_outlines_layer.layer(idx).name() == 'test_bulk_load_shapefile':
                self.bulk_load_frame.ml_outlines_layer.setLayer(self.bulk_load_frame.ml_outlines_layer.layer(idx))
                break
            idx = idx + 1
        # add description
        self.bulk_load_frame.le_data_description.setText('Test bulk load outlines')
        # add outlines
        btn_yes = self.bulk_load_frame.msgbox_bulk_load.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.bulk_load_save_clicked(False)
        # check outlines were added to bulk load outlines
        sql = 'SELECT count(*) FROM buildings_bulk_load.bulk_load_outlines;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.assertEqual(82, result)
        sql = 'SELECT count(*) FROM buildings_bulk_load.bulk_load_outlines WHERE bulk_load_status_id = 3;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        self.assertEqual(1, result)
        # check supplied dataset is added
        self.assertIsNotNone(self.bulk_load_frame.current_dataset)
