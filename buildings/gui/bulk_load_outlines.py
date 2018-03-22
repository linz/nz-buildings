# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal

import qgis

import processing

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "bulk_load_outlines.ui"))

db.connect()


class BulkLoadOutlines(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()
    # set up
    value = ''
    organistion = ''
    dataset_id = None
    layer = None

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(BulkLoadOutlines, self).__init__(parent)
        self.setupUi(self)
        self.populate_comboboxes()
        self.populate_field_combobox()
        # only enabled if radio button selected
        self.fcb_external_id.setDisabled(1)
        self.cmb_external_id.setDisabled(1)

        self.layer_registry = layer_registry

        # signals and slots
        self.mcb_imagery_layer.currentIndexChanged.connect(self.populate_field_combobox)
        self.fcb_imagery_field.currentIndexChanged.connect(self.populate_value_combobox)
        self.rad_external_source.toggled.connect(self.enable_external)
        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_comboboxes(self):
        """
        populates comboboxes
        Called on opening of frame
        """
        # populate organisation combobox
        sql = "SELECT value FROM buildings_bulk_load.organisation"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_organisation.addItem(item[0])
        # populate capture method combobox
        sql = "SELECT value FROM buildings_common.capture_method"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate capture source group
        sql = "SELECT value, description FROM buildings_common.capture_source_group"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1])
            self.cmb_capture_src_grp.addItem(text)

    def populate_external_id_cmb(self):
        """
        Called when radiobutton selected
        """
        # populate external id combobox
        sql = "SELECT external_source_id FROM buildings_common.capture_source"
        result = db._execute(sql)
        ls = result.fetchall()
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
        """
        populates combobox with fields of imagery layer
        Called when imagery layer is changed
        """
        if self.mcb_imagery_layer.currentLayer() is not None:
            self.fcb_imagery_field.setLayer(self.mcb_imagery_layer.currentLayer())
            self.cmb_imagery.clear()

    def populate_value_combobox(self):
        """
        populate combobox with imagery layer field values
        Called when imagery layer is changed
        """
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
        """
        Called when radio buttom is toggled
        """
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
        """
        Return comments from line edit, fail if empty or value too long
        """
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
        """
        Return the organisation id from the combo box
        """
        index = self.cmb_organisation.currentIndex()
        text = self.cmb_organisation.itemText(index)
        sql = "SELECT organisation_id FROM buildings_bulk_load.organisation o WHERE o.value = %s;"
        result= db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_method(self):
        """
        Return the capture method id from combo box
        """
        index = self.cmb_capture_method.currentIndex()
        text = self.cmb_capture_method.itemText(index)
        sql = "SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;"
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_source_group(self):
        """
        Return the capture source group id from combo box
        """
        index = self.cmb_capture_src_grp.currentIndex()
        text = self.cmb_capture_src_grp.itemText(index)
        text_ls = text.split('-')
        sql = "SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s;"
        result = db._execute(sql, data=(text_ls[0], ))
        return result.fetchall()[0][0]

    def get_external_id(self):
        """
        Returns external id from external id table
        if none gives error dialog
        """
        if self.rad_external_source.isChecked():
            index = self.cmb_external_id.currentIndex()
            ext_id = self.cmb_external_id.itemText(index)
            if ext_id == '':
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- NO EXTERNAL IDs -------------------- \n\n Please either uncheck the radio button or enter a new capture source")
                self.error_dialog.show()
                return
            return ext_id
        else:
            return None

    def get_layer(self):
        return self.ml_outlines_layer.currentLayer()

    def get_imagery_combobox_value(self):
        index = self.cmb_imagery.currentIndex()
        return self.cmb_imagery.itemText(index)

    def find_suburb(self):
        print 'suburb'
        """
        #TODO
        # Wont work as nz_localities is 4167 and building outlines 2193
        sql = "UPDATE buildings_bulk_load.bulk_load_outlines the_outlines "
        sql = sql + "set suburb_locality_id = the_suburb.id "
        sql = sql + " FROM("
        sql = sql + "SELECT DISTINCT ON (outlines.bulk_load_outline_id) "
        sql = sql + "outlines.bulk_load_outline_id AS id, suburbs.suburb_4th AS name, "
        sql = sql + "(ST_Area(ST_Intersection(outlines.shape,suburbs.shape))/ST_Area(outlines.shape)) AS proportion "
        sql = sql + "FROM buildings_bulk_load.bulk_load_outlines AS outlines, admin_bdys.nz_locality AS suburbs "
        sql = sql + "WHERE ST_Intersects(outlines.shape,suburbs.shape) "
        sql = sql + "ORDER BY outlines.bulk_load_outline_id, proportion desc) AS the_suburb "
        sql = sql + "WHERE the_outlines.bulk_load_outline_id = the_suburb.id"
        db.execute(sql)
        """

    def find_town_city(self):
        print 'town/city'
        """
        #TODO
        # Wont work as nz_localities is 4167 and building outlines 2193
        sql = "UPDATE buildings_bulk_load.bulk_load_outlines the_outlines "
        sql = sql + "set suburb_locality_id = the_suburb.city_id "
        sql = sql + "FROM( "
        sql = sql + "SELECT DISTINCT ON (outlines.bulk_load_outline_id) "
        sql = sql + "outlines.bulk_load_outline_id AS id, suburbs.suburb_4th AS name, suburbs.city_id as city_id, "
        sql = sql + "(ST_Area(ST_Intersection(outlines.shape,suburbs.shape))/ST_Area(outlines.shape)) AS proportion "
        sql = sql + "FROM buildings_bulk_load.bulk_load_outlines AS outlines, admin_bdys.nz_locality AS suburbs "
        sql = sql + "WHERE ST_Intersects(outlines.shape,suburbs.shape) "
        sql = sql + "ORDER BY outlines.bulk_load_outline_id, proportion desc) AS the_suburb "
        sql = sql + "WHERE the_outlines.bulk_load_outline_id = the_suburb.id "
        db.execute(sql)
        """

    def find_territorial_auth(self):
        print 'ta'
        """
        #TODO
        # Wont work as territorial authority is 4167 and building outlines 2193
        sql = "UPDATE buildings_bulk_load.bulk_load_outlines the_outlines "
        sql = sql + "set territorial_authority_id = the_ta.ta_id "
        sql = sql + "FROM( "
        sql = sql + "SELECT DISTINCT ON (outlines.bulk_load_outline_id) "
        sql = sql + "outlines.bulk_load_outline_id AS id, tas.name AS name, tas.ogc_fid as ta_id, "
        sql = sql + "(ST_Area(ST_Intersection(outlines.shape,tas.shape))/ST_Area(outlines.shape)) AS proportion "
        sql = sql + "FROM buildings_bulk_load.bulk_load_outlines AS outlines, admin_bdys.territorial_authority AS tas "
        sql = sql + "WHERE ST_Intersects(outlines.shape,tas.shape) "
        sql = sql + "ORDER BY outlines.bulk_load_outline_id, proportion desc) AS the_ta "
        sql = sql + "WHERE the_outlines.bulk_load_outline_id = the_ta.id "
        db.execute(sql)
        """

    def ok_clicked(self):
        # get value
        self.description = self.get_description()
        # get combobox values
        self.organisation = self.get_organisation()
        self.capture_method = self.get_capture_method()
        self.capture_source_group = self.get_capture_source_group()
        self.external_source_id = self.get_external_id()
        if self.external_source_id is None and self.rad_external_source.isChecked():
            # stop the code here
            return
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
            # find convex hull of self.layer
            result = processing.runalg("qgis:convexhull", self.layer, None, 0, None)
            convex_hull = processing.getObject(result['OUTPUT'])
            for feat in convex_hull.getFeatures():
                geom = feat.geometry()
                # convert to correct format
                wkt = geom.exportToWkt()
                sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
                result = db._execute(sql, data=(wkt, ))
                geom = result.fetchall()[0][0]
                # ensure outline SRID is 2193
                sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
                result = db._execute(sql, data=(geom, ))
                geom = result.fetchall()[0][0]
            # iterate through supplied datasets and find convex hulls
            dataset = 1
            while dataset <= self.dataset_id:
                sql = "SELECT transfer_date FROM buildings_bulk_load.supplied_datasets WHERE supplied_dataset_id = %s;"
                results = db._execute(sql, (dataset, ))
                date = results.fetchall()[0][0]
                if date is None:
                    sql = "SELECT * FROM buildings_bulk_load.bulk_load_outlines outlines WHERE ST_Intersects(%s, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));"
                    result = db._execute(sql, data=(geom, dataset))
                    results = result.fetchall()
                    if len(results) > 0:
                        self.bulk_overlap = True
                        break
                dataset = dataset + 1
            if self.bulk_overlap is True:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n ---------------- BULK LOAD OVERLAP ---------------- \n\n An unprocessed bulk loaded dataset with dataset id of {0} overlaps this input layer please process this first".format(dataset))
                self.error_dialog.show()
                return
            val = self.insert_supplied_outlines(self.dataset_id, self.layer, self.capture_method, self.capture_source_group, self.external_source_id)
            if val is None:
                # if insert_supplied_outlines function failed don't continue
                return
            # update the locality information fields of the bulk_load_outlines table
            self.find_suburb()
            self.find_town_city()
            self.find_territorial_auth()
            # TODO: way to check not reading in duplicates?
            # imagery that bulk outlines intersects with
            tile = str(self.get_imagery_combobox_value())
            # find geometry
            self.mcb_imagery_layer.currentLayer().selectByExpression("imagery = '{0}'".format(tile), 0)
            feature = self.mcb_imagery_layer.currentLayer().selectedFeatures()
            # convert to wkt to so can compare with sql shapes
            wkt = feature[0].geometry().exportToWkt()
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            result = db._execute(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            result = db._execute(sql, data=(geom, ))
            geom = result.fetchall()[0][0]
            # intersect imagery geom with building_outlines
            sql = "CREATE TEMP TABLE temp AS SELECT * FROM buildings.building_outlines WHERE ST_intersects(buildings.building_outlines.shape, %s);"
            db.execute(sql, data=(geom, ))
            # Has to deal with convex hull of bulk data otherwise will mark numerous building outlines as removed
            sql = "SELECT temp.* FROM temp WHERE ST_Intersects(temp.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));"
            result = db._execute(sql, data=(self.dataset_id, ))
            results = result.fetchall()
            if len(results) == 0:  # no existing outlines in this area
                print 'nothing \n'
                # all new outlines
            else:
                print 'something \n'
                # remove previous data from existing_subset_extracts
                sql = "DELETE FROM buildings_bulk_load.existing_subset_extracts;"
                db.execute(sql)
                for ls in results:
                    # insert relevant data into existing_subset_extract
                    # if the building was added during production 
                    sql = "SELECT bl.supplied_dataset_id FROM buildings_bulk_load.bulk_load_outlines bl, buildings_bulk_load.transferred t, buildings.building_outlines bo WHERE bo.building_outline_id = %s, bo.building_outline_id = t.new_building_outline_id AND t.bulk_load_outline_id = bl.building_outline_id;"
                    result = db._execute(sql, data=(ls[0], ))
                    if result is None:
                        sql = "INSERT INTO buildings_bulk_load.existing_subset_extracts(building_outline_id, supplied_dataset_id, shape) VALUES(%s, NULL, %s);"
                        db.execute(sql, data=(ls[0], ls[10]))
                    else:
                        dataset = result.fetchall()[0][0]
                        sql = "INSERT INTO buildings_bulk_load.existing_subset_extracts(building_outline_id, supplied_dataset_id, shape) VALUES(%s, %s, %s);"
                        db.execute(sql, data=(ls[0], dataset, ls[10]))
                # run comparisons function
                sql = "SELECT (buildings_bulk_load.compare_building_outlines(%s));"
                db.execute(sql, data=(self.dataset_id, ))
                # user checked data to buildings and building_outlines
            sql = "DISCARD TEMP;"
            db.execute(sql)  # remove temp files
            self.mcb_imagery_layer.currentLayer().removeSelection()  # remove selection

    def cancel_clicked(self):
        """
        Called when cancel button is clicked
        """
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

    def insert_supplied_dataset(self, organisation, description):
        """
        generates new supplied outline dataset for the incoming data
        """
        # generate supplied_outline_id
        sql = "SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets;"
        result = db._execute(sql)
        attributes = result.fetchall()
        length = len(attributes)
        if length == 0:
            id = 1  # this is the first dataset
        else:
            id = attributes[length - 1][0] + 1  # next dataset  id number
        self.dataset_id = id
        # insert new dataset info into buildings_bulk_load.supplied_datasets
        sql = "INSERT INTO buildings_bulk_load.supplied_datasets(supplied_dataset_id, description, supplier_id) VALUES(%s, %s, %s);"
        db.execute(sql, (self.dataset_id, description, organisation))

    def insert_supplied_outlines(self, dataset_id, layer, capture_method, capture_source_group, external_source_id):
        """
        inserts the new outlines into the bulk_load_outlines table
        """
        # find capture source id from capture source and external id
        capture_source = None
        if self.external_source_id is not None:
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs, buildings_common.capture_source_group csg WHERE cs.capture_source_group_id = %s AND cs.external_source_id = %s;"
            result = db._execute(sql, data=(self.capture_source_group, self.external_source_id))
            value = result.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- NO CAPTURE SOURCE EXISTS -------------------- \n\n No capture source with this capture source group and external id")
                self.error_dialog.show()
                return
            else:
                capture_source = value[0][0]
        else:
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s AND cs.external_source_id is Null;"
            result = db._execute(sql, data=(self.capture_source_group, ))
            value = result.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- NO CAPTURE SOURCE EXISTS -------------------- \n\n No capture source with this capture source group and a Null external id")
                self.error_dialog.show()
                return
            else:
                capture_source = value[0][0]
        # iterate through outlines in map layer
        external_field = str(self.fcb_external_id.currentField())
        for outline in layer.getFeatures():
            wkt = outline.geometry().exportToWkt()
            # convert to postgis shape and ensure outline is a multipolygon
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            result = db._execute(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            result = db._execute(sql, data=(geom, ))
            geom = result.fetchall()[0][0]
            # insert outline into buildings_bulk_load.supplied_outline
            if external_field == '':
                sql = "INSERT INTO buildings_bulk_load.bulk_load_outlines(supplied_dataset_id, bulk_load_status_id, capture_method_id, capture_source_id, shape)" + " VALUES(%s, %s, %s, %s, %s);"
                db.execute(sql, (dataset_id, 1, capture_method, capture_source, geom))
            else:
                external_id = outline.attribute(external_field)
                sql = "INSERT INTO buildings_bulk_load.bulk_load_outlines(supplied_dataset_id, external_outline_id, bulk_load_status_id, capture_method_id, capture_source_id, shape)" + " VALUES(%s, %s, %s, %s, %s, %s);"
                db.execute(sql, (dataset_id, external_id, 1, capture_method, capture_source, geom))
        self.le_data_description.clear()
        # returns 1 if function worked None if failed
        return 1
