# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import psycopg2
import qgis

from buildings.gui.error_dialog import ErrorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "insert_buildings.ui"))

# TODO: fix database connection process
conn = psycopg2.connect(database='building_outlines_test')
# create cursor
cur = conn.cursor()


class InsertBuildings(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()

    supplied_dataset = ''
    capture_source = ''
    capture_method = ''
    lifecycle_stage = ''
    dataset_id = None
    layer = None

    def __init__(self, parent=None):
        """Constructor."""
        super(InsertBuildings, self).__init__(parent)
        self.setupUi(self)
        self.populate_supplied_dataset()
        self.populate_capture_method()
        self.populate_capture_source_group()
        self.populate_external_source()
        self.populate_lifecycle_stage()

        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_supplied_dataset(self):
        sql = "SELECT description FROM buildings_stage.supplied_datasets"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_supplied_dataset.addItem(item[0])

    def populate_capture_method(self):
        sql = "SELECT value FROM buildings.capture_method"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])

    def populate_capture_source_group(self):
        sql = "SELECT value FROM buildings.capture_source_group"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_capture_source.addItem(item[0])

    def populate_external_source(self):
        self.cmb_external_source.addItem("Null")
        sql = "SELECT external_source_id FROM buildings.capture_source"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_external_source.addItem(item[0])

    def populate_lifecycle_stage(self):
        sql = "SELECT value FROM buildings.lifecycle_stage"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_lifecycle_stage.addItem(item[0])

    def ok_clicked(self):
        self.dataset_id = self.get_supplied_dataset()
        self.capture_method = self.get_capture_method()
        self.lifecycle_stage = self.get_lifecycle_stage()
        self.layer = self.ml_building_layer.currentLayer()
        self.capture_source = self.get_capture_source()
        if self.capture_source is not None:
            self.insert_buildings()

    def get_supplied_dataset(self):
        # find supplied dataset id
        index = self.cmb_supplied_dataset.currentIndex()
        supplied_dataset_value = self.cmb_supplied_dataset.itemText(index)
        sql = "SELECT supplied_dataset_id FROM buildings_stage.supplied_datasets WHERE buildings_stage.supplied_datasets.description = %s;"
        cur.execute(sql, (supplied_dataset_value,))
        return cur.fetchall()[0][0]

    def get_capture_method(self):
        index = self.cmb_capture_method.currentIndex()
        capture_method_value = self.cmb_capture_method.itemText(index)
        sql = "SELECT capture_method_id FROM buildings.capture_method WHERE buildings.capture_method.value = %s;"
        cur.execute(sql, (capture_method_value,))
        return cur.fetchall()[0][0]

    def get_capture_source_group(self):
        index = self.cmb_capture_source.currentIndex()
        capture_source_value = self.cmb_capture_source.itemText(index)
        sql = "SELECT capture_source_group_id FROM buildings.capture_source_group WHERE buildings.capture_source_group.value = %s;"
        cur.execute(sql, (capture_source_value,))
        return cur.fetchall()[0][0]

    def get_lifecycle_stage(self):
        index = self.cmb_lifecycle_stage.currentIndex()
        lifecycle_stage_value = self.cmb_lifecycle_stage.itemText(index)
        sql = "SELECT lifecycle_stage_id FROM buildings.lifecycle_stage WHERE buildings.lifecycle_stage.value = %s;"
        cur.execute(sql, (lifecycle_stage_value,))
        return cur.fetchall()[0][0]

    def get_external_source(self):
        index = self.cmb_external_source.currentIndex()
        return self.cmb_external_source.itemText(index)

    def get_capture_source(self):
        capture_source_group_id = self.get_capture_source_group()
        external_source_id = self.get_external_source()
        if external_source_id == 'Null':
            external_source_id = None
            sql = "SELECT capture_source_id FROM buildings.capture_source WHERE buildings.capture_source.capture_source_group_id = %s AND buildings.capture_source.external_source_id is %s"
            cur.execute(sql, (capture_source_group_id, external_source_id))
        else:
            sql = "SELECT capture_source_id FROM buildings.capture_source WHERE buildings.capture_source.capture_source_group_id = %s AND buildings.capture_source.external_source_id = %s"
            cur.execute(sql, (capture_source_group_id, external_source_id))
        ls = cur.fetchall()
        if len(ls) == 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- NULL CAPTURE SOURCE -------------------- \n\n No capture source with this capture source group and external source id")
            self.error_dialog.show()
            return
        else:
            return ls[0][0]

    def insert_buildings(self):
        # generate building_outline_id for building_outlines_table
        sql = "SELECT building_outline_id FROM buildings.building_outlines;"
        cur.execute(sql)
        attributes = cur.fetchall()
        length = len(attributes)
        if length == 0:
            id = 1
        else:
            id = attributes[length - 1][0]
        # iterate through outlines in input layer
        for outline in self.layer.getFeatures():
            attrs = outline.attributes()
            wkt = outline.geometry().exportToWkt()
            # convert to postgis shape and ensure outline is multipolygon
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            cur.execute(sql, (wkt, ))
            geom = cur.fetchall()[0][0]
            # ensure SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            cur.execute(sql, (geom, ))
            geom = cur.fetchall()[0][0]
            # insert related data into buildings.buildings
            sql = "INSERT INTO buildings.buildings(building_id) VALUES(%s);"
            cur.execute(sql, (int(attrs[0]), ))
            # insert related data into buildings.building_outlines
            sql = "INSERT INTO buildings.building_outlines(building_outline_id, building_id, capture_method_id, capture_source_id, lifecycle_stage_id, shape) VALUES(%s, %s, %s, %s, %s, %s) "
            cur.execute(sql, (id, int(attrs[0]), self.capture_method, self.capture_source, self.lifecycle_stage, geom))
            id = id + 1

        conn.commit()

    def cancel_clicked(self):
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame)
