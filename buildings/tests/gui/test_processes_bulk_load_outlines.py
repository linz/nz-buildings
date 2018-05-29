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

import unittest
from PyQt4.QtCore import *
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsPoint, QgsGeometry, QgsField
from qgis.utils import plugins, iface
from buildings.utilities import database as db


class ProcessBulkLoadTest(unittest.TestCase):
    """Test Bulk Load Outlines GUI processing"""

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
        # remove temporary layers from canvas
        layers = iface.legendInterface().layers()
        for layer in layers:
            if 'temporary' in str(layer.id()):
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

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
        self.bulk_load_frame.btn_exit.click()

    def test_external_id_radiobutton(self):
        """external source fields enable when external id radio button is enabled"""
        # checks on starting the restrictions are in place
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())
        # click the radio button
        self.bulk_load_frame.rad_external_source.click()
        # check restrictions have been removed
        self.assertTrue(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertTrue(self.bulk_load_frame.cmb_external_id.isEnabled())
        # check external source id value is correctly populated
        sql = 'SELECT COUNT(external_source_id) FROM buildings_common.capture_source'
        result3 = db._execute(sql)
        result3 = result3.fetchall()[0][0]
        self.assertEqual(self.bulk_load_frame.cmb_external_id.count(), result3)
        # check external id combobox populated with fields of current layer
        vectorlayer = self.bulk_load_frame.ml_outlines_layer.currentLayer()
        fields = vectorlayer.pendingFields()
        self.assertEqual(self.bulk_load_frame.fcb_external_id.count(),
                         len(fields))
        # check on unclicking radio button the restrictions are restablished
        self.bulk_load_frame.rad_external_source.click()
        self.assertFalse(self.bulk_load_frame.fcb_external_id.isEnabled())
        self.assertFalse(self.bulk_load_frame.cmb_external_id.isEnabled())

    def test_bulk_load_ok_clicked(self):
        """When save is clicked data is added to the correct tables"""
        # create temporary outlines layer
        sql = 'SELECT count(*) FROM buildings_bulk_load.bulk_load_outlines;'
        result = db._execute(sql)
        if result is None:
            result = 0
        else:
            result = result.fetchall()[0][0]
        layer = QgsVectorLayer("Polygon?crs=epsg:2193",
                               "temporary_outlines", "memory")
        layer.dataProvider().addAttributes([QgsField('id', QVariant.Int)])
        layer.updateFields()
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # feature one
        feature_one = QgsFeature()
        feature_one.setAttributes([1])
        points = [QgsPoint(1878056, 5555250), QgsPoint(1878056, 5555300),
                  QgsPoint(1878100, 5555300), QgsPoint(1878100, 5555250)]
        feature_one.setGeometry(QgsGeometry.fromPolygon([points]))
        # add outlines to temporary layer
        layer.startEditing()
        layer.addFeature(feature_one, True)
        layer.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # create temporary imagery layer
        imagery_layer = QgsVectorLayer("Polygon?crs=epsg:2193",
                                       "temporary_imagery", "memory")
        imagery_layer.dataProvider().addAttributes([QgsField('id',
                                                             QVariant.String)])
        imagery_layer.updateFields()
        outline = QgsFeature()
        outline.setAttributes(['1'])
        points = points = [QgsPoint(1878000, 5555400),
                           QgsPoint(1878000, 5554999),
                           QgsPoint(1878300, 5554999),
                           QgsPoint(1878300, 5555400)]
        outline.setGeometry(QgsGeometry.fromPolygon([points]))
        imagery_layer.startEditing()
        imagery_layer.addFeature(outline, True)
        imagery_layer.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(imagery_layer)
        # set combobox values
        count = self.bulk_load_frame.ml_outlines_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.ml_outlines_layer.layer(idx).name() == 'temporary_outlines':
                self.bulk_load_frame.ml_outlines_layer.setLayer(self.bulk_load_frame.ml_outlines_layer.layer(idx))
                break
            idx = idx + 1
        # add description
        self.bulk_load_frame.le_data_description.setText('Test bulk load outlines')
        # set imagery layer
        count = self.bulk_load_frame.mcb_imagery_layer.count()
        idx = 0
        while idx < count:
            if self.bulk_load_frame.mcb_imagery_layer.layer(idx).name() == 'temporary_imagery':
                self.bulk_load_frame.mcb_imagery_layer.setLayer(self.bulk_load_frame.mcb_imagery_layer.layer(idx))
                break
            idx = idx + 1
        # set imagery field
        self.bulk_load_frame.fcb_imagery_field.setCurrentIndex(0)
        # add outlines
        self.bulk_load_frame.ok_clicked(commit_status=False)
        # check 1 outlines were added to bulk load outlines
        sql = 'SELECT count(*) FROM buildings_bulk_load.bulk_load_outlines;'
        result2 = db._execute(sql)
        if result2 is None:
            result2 = 0
        else:
            resultT = result2.fetchall()[0][0]
        self.assertEqual(result + 1, resultT)
        # rollback changes
        self.bulk_load_frame.db.rollback_open_cursor()
        # check supplied dataset is added
        self.assertIsNotNone(self.bulk_load_frame.dataset_id)


suite = unittest.TestLoader().loadTestsFromTestCase(ProcessBulkLoadTest)
unittest.TextTestRunner(verbosity=2).run(suite)
