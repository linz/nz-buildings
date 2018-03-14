# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import psycopg2
import qgis

from buildings.gui.error_dialog import ErrorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "bulk_load_outlines.ui"))

# TODO: fix database connection process
conn = psycopg2.connect(database='building_outlines_test')
# create cursor
cur = conn.cursor()


class BulkLoadOutlines(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()
    value = ''
    organistion = ''
    dataset_id = None
    layer = None

    def __init__(self, parent=None):
        """Constructor."""
        super(BulkLoadOutlines, self).__init__(parent)
        self.setupUi(self)
        self.populate_comboboxes()
        self.populate_field_combobox()
        self.fcb_external_id.setDisabled(1)
        self.cmb_external_id.setDisabled(1)

        self.mcb_imagery_layer.currentIndexChanged.connect(self.populate_field_combobox)
        self.fcb_imagery_field.currentIndexChanged.connect(self.populate_value_combobox)
        self.rad_external_source.toggled.connect(self.enable_external)
        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_comboboxes(self):
        # populate organisation combobox
        sql = "SELECT value FROM buildings_bulk_load.organisation"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_organisation.addItem(item[0])
        # populate capture method combobox
        sql = "SELECT value FROM buildings_common.capture_method"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate capture source group
        sql = "SELECT value FROM buildings_common.capture_source_group"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_capture_src_grp.addItem(item[0])

    def populate_external_id_cmb(self):
        # populate external id combobox
        sql = "SELECT external_source_id FROM buildings_common.capture_source"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            if item[0] is not None:
                count = 0
                exists = False
                while count < self.cmb_external_id.count():
                    if self.cmb_external_id.itemText(count) == str(item[0]):
                        exists = True
                    count = count + 1
                if exists is False:
                    self.cmb_external_id.addItem(item[0])
    
    def populate_field_combobox(self):
        if self.mcb_imagery_layer.currentLayer() is not None:
            self.fcb_imagery_field.setLayer(self.mcb_imagery_layer.currentLayer())
            self.cmb_imagery.clear()

    def populate_value_combobox(self):
        layer_index = self.mcb_imagery_layer.currentIndex()
        self.cmb_imagery.clear()
        for feature in self.mcb_imagery_layer.layer(layer_index).getFeatures():
            idx = self.mcb_imagery_layer.layer(layer_index).fieldNameIndex(self.fcb_imagery_field.currentField())
            value = feature.attributes()[idx]
            count = 0
            exists = False
            while count < self.cmb_imagery.count():
                if self.cmb_imagery.itemText(count) == str(value):
                    exists = True
                count = count + 1
            if not exists:
                self.cmb_imagery.addItem(str(value))

    def enable_external(self):
        if self.rad_external_source.isChecked():
            self.fcb_external_id.setEnabled(1)
            self.fcb_external_id.setLayer(self.ml_outlines_layer.currentLayer())
            self.cmb_external_id.setEnabled(1)
            self.populate_external_id_cmb()
        else:
            self.fcb_external_id.setDisabled(1)
            self.fcb_external_id.setLayer(None)
            self.cmb_external_id.setDisabled(1)
            self.cmb_external_id.clear()

    def get_description(self):
        # Get comments from comment box, fail if empty or value too long
        if self.le_data_description.text() == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- EMPTY DECRIPTION FIELD -------------------- \n\n Null decriptions not allowed")
            self.error_dialog.show()
            return
        if len(self.le_data_description.text()) >= 40:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- VALUE TOO LONG -------------------- \n\n Enter less than 250 characters")
            self.error_dialog.show()
            return
        return self.le_data_description.text()

    def get_organisation(self):
        # Get the type from the combo box
        index = self.cmb_organisation.currentIndex()
        text = self.cmb_organisation.itemText(index)
        sql = "SELECT organisation_id FROM buildings_bulk_load.organisation o WHERE o.value = %s;"
        cur.execute(sql, (text, ))
        return cur.fetchall()[0][0]

    def get_capture_method(self):
        # Get the type from combo box
        index = self.cmb_capture_method.currentIndex()
        text = self.cmb_capture_method.itemText(index)
        sql = "SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;"
        cur.execute(sql, (text, ))
        return cur.fetchall()[0][0]

    def get_capture_source_group(self):
        # Get the type from combo box
        index = self.cmb_capture_src_grp.currentIndex()
        text = self.cmb_capture_src_grp.itemText(index)
        sql = "SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s;"
        cur.execute(sql, (text, ))
        return cur.fetchall()[0][0]

    def get_external_id(self):
        if self.rad_external_source.isChecked():
            index = self.cmb_external_id.currentIndex()
            return self.cmb_external_id.itemText(index)
        else:
            return None

    def get_imagery_combobox_value(self): 
        index = self.cmb_imagery.currentIndex() 
        return self.cmb_imagery.itemText(index)

    def get_layer(self):
        return self.ml_outlines_layer.currentLayer()

    def ok_clicked(self):
        # get value
        self.description = self.get_description()
        # get combobox values
        self.organisation = self.get_organisation()
        self.capture_method = self.get_capture_method()
        self.capture_source_group = self.get_capture_source_group()
        self.external_source_id = self.get_external_id()
        # get layer
        self.layer = self.get_layer()
        # check imagery field and value are not null
        if str(self.fcb_imagery_field.currentField()) is '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n ---------------- IMAGERY FIELD IS NULL ---------------- \n\n Please enter an imagery field and value")
            self.error_dialog.show()
            return
        if str(self.fcb_imagery_field.currentField()) is '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n ---------------- IMAGERY VALUE IS NULL ---------------- \n\n Please enter an imagery value")
            self.error_dialog.show()
            return
        
        # run sql
        if self.description is not None:
            self.insert_supplied_dataset(self.organisation, self.description)
            self.insert_supplied_outlines(self.dataset_id, self.layer, self.capture_method, self.capture_source_group, self.external_source_id)
            
            # TODO: way to check not reading in duplicates?
            # imagery that bulk outlines intersects with
            tile = str(self.get_imagery_combobox_value())
            # find geometry
            self.mcb_imagery_layer.currentLayer().selectByExpression("imagery = '{0}'".format(tile), 0)
            feature = self.mcb_imagery_layer.currentLayer().selectedFeatures()
            # convert to wkt to so can compare with sql shapes
            wkt = feature[0].geometry().exportToWkt()
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            cur.execute(sql, (wkt, ))
            geom = cur.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            cur.execute(sql, (geom, ))
            geom = cur.fetchall()[0][0]
            # intersect imagery geom with building_outlines
            sql = "CREATE TEMP TABLE temp AS SELECT * FROM buildings.building_outlines WHERE ST_intersects(buildings.building_outlines.shape, %s);"
            cur.execute(sql, (geom, ))
            # Has to deal with convex hull of bulk data otherwise will mark numerous building outlines as removed
            sql = "SELECT temp.* FROM temp WHERE ST_Intersects(temp.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));"
            cur.execute(sql, (self.dataset_id, ))
            results = cur.fetchall()
            if len(results) == 0:  # no existing outlines in this area
                print 'nothing \n'
                # all new outlines
            else:
                print 'something \n'
                # remove previous data from existing_subset_extracts
                sql = "DELETE FROM buildings_bulk_load.existing_subset_extracts;"
                cur.execute(sql)
                for ls in results:
                    # insert relevant data into existing_subset_extract
                    sql = "SELECT bl.supplied_dataset_id FROM buildings_bulk_load.bulk_load_outlines bl, buildings_bulk_load.transferred t, buildings.building_outlines bo WHERE bo.building_outline_id = %s, bo.building_outline_id = t.new_building_outline_id AND t.bulk_load_outline_id = bl.building_outline_id;"
                    cur.execute(sql, (ls[0], ))
                    dataset = cur.fetchall()[0][0]
                    sql = "INSERT INTO buildings_bulk_load.existing_subset_extracts(building_outline_id, supplied_dataset_id, shape) VALUES(%s, %s, %s);"
                    cur.execute(sql, (ls[0], dataset, ls[10]))
                # run comparisons function to uncomment when comparisons function updated
                # sql = "SELECT (buildings_bulk_load.compare_building_outlines(%s));"
                # cur.execute(sql, (self.dataset_id, ))
                # user checked data to buildings and building_outlines
            sql = "DISCARD TEMP;"
            cur.execute(sql)  # remove temp files
            conn.commit()
            self.mcb_imagery_layer.currentLayer().removeSelection()

    def cancel_clicked(self):
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame)

    def insert_supplied_dataset(self, organisation, description):
        # find organisation id value from buildings.organisation table

        # generate supplied_outline_id
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets;"
        cur.execute(sql)
        attributes = cur.fetchall()
        length = len(attributes)
        if length == 0:
            id = 1
        else:
            id = attributes[length - 1][0] + 1  # id for new dataset
        self.dataset_id = id
        # insert new supplied dataset info into buildings_bulk_load.supplied_datasets
        sql = "INSERT INTO buildings_bulk_load.supplied_datasets(supplied_dataset_id, description, supplier_id) VALUES(%s, %s, %s)"
        cur.execute(sql, (self.dataset_id, description, organisation))
        conn.commit()

    def insert_supplied_outlines(self, dataset_id, layer, capture_method, capture_source_group, external_source_id):
        # find capture source id
        capture_source = None
        if self.external_source_id is not None:
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs, buildings_common.capture_source_group csg WHERE cs.capture_source_group_id = %s AND cs.external_source_id = %s;"
            cur.execute(sql, (self.capture_source_group, self.external_source_id))
            value = cur.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- NO CAPTURE SOURCE EXISTS -------------------- \n\n No capture source with this capture source group and external id exists")
                self.error_dialog.show()
                return
            else:
                capture_source =  value[0][0]
        else:
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s AND cs.external_source_id is Null;"
            cur.execute(sql, (self.capture_source_group, ))
            value = cur.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- NO CAPTURE SOURCE EXISTS -------------------- \n\n No capture source with this capture source group and a Null external id exists")
                self.error_dialog.show()
                return
            else:
                capture_source =  value[0][0]
        # find bulk load status
        # iterate through outlines in map layer
        external_field = str(self.fcb_external_id.currentField())
        for outline in layer.getFeatures():
            wkt = outline.geometry().exportToWkt()
            # convert to postgis shape and ensure outline geometry is a multipolygon
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            cur.execute(sql, (wkt, ))
            geom = cur.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            cur.execute(sql, (geom, ))
            geom = cur.fetchall()[0][0]
            # insert outline into buildings_bulk_load.supplied_outline
            if external_field == '':
                sql = "INSERT INTO buildings_bulk_load.bulk_load_outlines(supplied_dataset_id, bulk_load_status_id, capture_method_id, capture_source_id, shape)" + " VALUES(%s, %s, %s, %s, %s);"
                cur.execute(sql, (dataset_id, 1, capture_method, capture_source, geom))
            else: 
                external_id = outline.attribute(external_field)
                sql = "INSERT INTO buildings_bulk_load.bulk_load_outlines(supplied_dataset_id, external_outline_id, bulk_load_status_id, capture_method_id, capture_source_id, shape)" + " VALUES(%s, %s, %s, %s, %s, %s);"
                cur.execute(sql, (dataset_id, external_id, 1, capture_method, capture_source, geom))
        conn.commit()
        self.le_data_description.clear()
