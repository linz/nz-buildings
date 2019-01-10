# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2019 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

    Tests: Bulk Load Outlines with the wrong projection

 ***************************************************************************/
"""

import os
import unittest

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QMessageBox
from qgis.core import QgsMapLayerRegistry
from qgis.utils import iface, plugins

from buildings.utilities import database as db


class ProcessWrongProjectionTest(unittest.TestCase):
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
            if 'test_wrong_projection' in str(layer.id()):
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

    def test_bulk_load_wrong_projection(self):
        """When save is clicked data is added to the correct tables"""
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'testdata/test_wrong_projection.shp')
        iface.addVectorLayer(path, '', 'ogr')
        count = self.bulk_load_frame.ml_outlines_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.ml_outlines_layer.layer(idx).name() == 'test_wrong_projection':
                self.bulk_load_frame.ml_outlines_layer.setLayer(self.bulk_load_frame.ml_outlines_layer.layer(idx))
                break
            idx = idx + 1
        # add description
        self.bulk_load_frame.le_data_description.setText('Test wrong projection')
        # add outlines
        btn_yes = self.bulk_load_frame.msgbox_bulk_load.button(QMessageBox.Yes)
        QTimer.singleShot(500, btn_yes.click)
        self.bulk_load_frame.bulk_load_save_clicked(False)

        self.assertIn(
            'INCORRECT CRS',
            self.bulk_load_frame.error_dialog.tb_error_report.toPlainText()
        )
        self.bulk_load_frame.error_dialog.close()
