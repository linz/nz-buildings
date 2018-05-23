# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

import qgis

import processing

from functools import partial

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load_outlines.ui'))


class BulkLoadOutlines(QFrame, FORM_CLASS):

    # set up
    value = ''
    organisation = ''
    dataset_id = None
    layer = None
    inserted_values = 0

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(BulkLoadOutlines, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

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
        self.ml_outlines_layer.currentIndexChanged.connect(self.populate_external_fcb)
        self.btn_ok.clicked.connect(partial(self.ok_clicked,
                                            commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)

    def populate_comboboxes(self):
        """
        populates comboboxes
        Called on opening of frame
        """
        # populate organisation combobox
        sql = 'SELECT value FROM buildings_bulk_load.organisation;'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_organisation.addItem(item[0])
        # populate capture method combobox
        sql = 'SELECT value FROM buildings_common.capture_method;'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate capture source group
        sql = 'SELECT value, description FROM buildings_common.capture_source_group;'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1])
            self.cmb_capture_src_grp.addItem(text)

    def populate_external_id_cmb(self):
        """
        Called when radiobutton selected
        """
        # populate external id combobox
        sql = 'SELECT external_source_id FROM buildings_common.capture_source;'
        result = self.db._execute(sql)
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

    def populate_external_fcb(self):
        self.fcb_external_id.setLayer(self.ml_outlines_layer.currentLayer())

    def enable_external(self):
        """
        Called when radio button is toggled
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
            self.error_dialog.fill_report('\n -------------------- EMPTY '
                                          'DESCRIPTION FIELD ------------'
                                          '-------- \n\n Null descriptions'
                                          ' not allowed'
                                          )
            self.error_dialog.show()
            return
        if len(self.le_data_description.text()) >= 40:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n -------------------- VALUE '
                                          'TOO LONG -------------------- '
                                          '\n\n Enter less than 250 '
                                          'characters'
                                          )
            self.error_dialog.show()
            return
        return self.le_data_description.text()

    def get_organisation(self):
        """
        Return the organisation id from the combo box
        """
        text = self.cmb_organisation.currentText()
        sql = 'SELECT organisation_id FROM buildings_bulk_load.organisation o WHERE o.value = %s;'
        result = self.db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_method(self):
        """
        Return the capture method id from combo box
        """
        text = self.cmb_capture_method.currentText()
        sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
        result = self.db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_source_group(self):
        """
        Return the capture source group id from combo box
        """
        text = self.cmb_capture_src_grp.currentText()
        text_ls = text.split('-')
        sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s;'
        result = self.db._execute(sql, data=(text_ls[0], ))
        return result.fetchall()[0][0]

    def get_external_id(self):
        """
        Returns external id from external id table
        """
        return self.cmb_external_id.currentText()

    def get_layer(self):
        return self.ml_outlines_layer.currentLayer()

    def get_imagery_combobox_value(self):
        return self.cmb_imagery.currentText()

    def find_suburb(self, geom):
        sql = 'SELECT buildings.suburb_locality_intersect_polygon(%s);'
        result = self.db.execute_no_commit(sql, (geom, ))
        return result.fetchall()[0][0]

    def find_town_city(self, geom):
        sql = 'SELECT buildings.town_city_intersect_polygon(%s);'
        result = self.db.execute_no_commit(sql, (geom, ))
        return result.fetchall()[0][0]

    def find_territorial_auth(self, geom):
        sql = 'SELECT buildings.territorial_authority_intersect_polygon(%s);'
        result = self.db.execute_no_commit(sql, (geom, ))
        return result.fetchall()[0][0]

    def ok_clicked(self, commit_status):
        # get value
        self.description = self.get_description()
        # get combobox values
        self.organisation = self.get_organisation()
        self.capture_method = self.get_capture_method()
        self.capture_source_group = self.get_capture_source_group()
        # if radio button checked gets text of combobox
        if self.rad_external_source.isChecked():
            self.external_source_id = self.get_external_id()
        else:
            # sets id to None
            self.external_source_id = None
        # if user checks radio button then does not enter a field error
        if self.external_source_id is None and self.rad_external_source.isChecked():
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n -------------------- NO EXTERNAL'
                                          ' ID -------------------- \n\n'
                                          ' Please either uncheck the radio'
                                          ' button or enter a new capture '
                                          ' source or External Source Id'
                                          )
            self.error_dialog.show()
            # stop the code here
            return
        if self.fcb_external_id.currentField() is None and self.rad_external_source.isChecked():
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n -------------------- NO EXTERNAL'
                                          ' ID FIELD-------------------- \n\n'
                                          ' Please either uncheck the radio'
                                          ' button or enter an external id'
                                          ' field'
                                          )
            self.error_dialog.show()
            # stop the code here
            return
        # get layer
        self.layer = self.get_layer()
        # check imagery field and value are not null
        if str(self.fcb_imagery_field.currentField()) is '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n ---------------- IMAGERY FIELD'
                                          ' IS NULL ---------------- \n\n '
                                          'Please enter an imagery field and'
                                          ' value'
                                          )
            self.error_dialog.show()
            return
        if str(self.fcb_imagery_field.currentField()) is '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n ---------------- IMAGERY VALUE '
                                          'IS NULL ---------------- \n\n '
                                          'Please enter an imagery value'
                                          )
            self.error_dialog.show()
            return

        # run sql
        if self.description is not None:
            self.insert_supplied_dataset(self.organisation, self.description,
                                         commit_status)
            # find convex hull of self.layer
            result = processing.runalg('qgis:convexhull', self.layer,
                                       None, 0, None)
            convex_hull = processing.getObject(result['OUTPUT'])
            for feat in convex_hull.getFeatures():
                geom = feat.geometry()
                # convert to correct format
                wkt = geom.exportToWkt()
                sql = 'SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));'
                result = self.db.execute_no_commit(sql, data=(wkt, ))
                geom = result.fetchall()[0][0]
                # ensure outline SRID is 2193
                sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
                result = self.db.execute_no_commit(sql, data=(geom, ))
                geom = result.fetchall()[0][0]
            # iterate through supplied datasets and find convex hulls
            dataset = 1
            self.bulk_overlap = False
            while dataset <= self.dataset_id:
                sql = 'SELECT transfer_date FROM buildings_bulk_load.supplied_datasets WHERE supplied_dataset_id = %s;'
                results = self.db.execute_no_commit(sql, (dataset, ))
                t_date = results.fetchall()
                if t_date:
                    if t_date[0][0] is None:
                        sql = 'SELECT * FROM buildings_bulk_load.bulk_load_outlines outlines WHERE ST_Intersects(%s, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));'
                        result = self.db.execute_no_commit(sql, data=(geom,
                                                                      dataset))
                        results = result.fetchall()
                        if len(results) > 0:
                            self.bulk_overlap = True
                            break
                dataset = dataset + 1
            if self.bulk_overlap is True:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n ---------------- BULK '
                                              'LOAD OVERLAP ------------'
                                              '---- \n\n An unprocessed '
                                              'bulk loaded dataset with '
                                              'dataset id of {0} overlaps '
                                              'this input layer please process'
                                              ' this first'.format(dataset)
                                              )
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
            val = self.insert_supplied_outlines(self.dataset_id, self.layer,
                                                self.capture_method,
                                                self.capture_source_group,
                                                self.external_source_id,
                                                commit_status)
            if val is None:
                # if insert_supplied_outlines function failed don't continue
                return
            # TODO: way to check not reading in duplicates?
            # imagery that bulk outlines intersects with
            tile = str(self.get_imagery_combobox_value())
            field = str(self.fcb_imagery_field.currentText())
            # find geometry
            self.mcb_imagery_layer.currentLayer().selectByExpression("{0} = '{1}'".format(field, tile), 0)
            feature = self.mcb_imagery_layer.currentLayer().selectedFeatures()
            # convert to wkt to so can compare with sql shapes
            wkt = feature[0].geometry().exportToWkt()
            sql = 'SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));'
            result = self.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
            result = self.db.execute_no_commit(sql, data=(geom, ))
            geom = result.fetchall()[0][0]
            # intersect imagery geom with building_outlines
            sql = 'CREATE TEMP TABLE temp AS SELECT * FROM buildings.building_outlines WHERE ST_intersects(buildings.building_outlines.shape, %s);'
            self.db.execute_no_commit(sql, data=(geom, ))
            # convex hull else will mark numerous building outlines as removed
            sql = 'SELECT temp.* FROM temp WHERE ST_Intersects(temp.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s));'
            result = self.db.execute_no_commit(sql, data=(self.dataset_id, ))
            results = result.fetchall()
            if len(results) == 0:  # no existing outlines in this area
                # all new outlines
                sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s;"
                results = self.db.execute_no_commit(sql, (self.dataset_id, ))
                bulk_loaded_ids = results.fetchall()
                for id in bulk_loaded_ids:
                    sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 1);'
                    self.db.execute_no_commit(sql, (id[0], ))
            else:
                for ls in results:
                    sql = 'SELECT building_outline_id FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = %s;'
                    result = self.db.execute_no_commit(sql, (ls[0], ))
                    result = result.fetchall()
                    if len(result) == 0:
                        # insert relevant data into existing_subset_extract
                        sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                        result = self.db.execute_no_commit(sql, data=(ls[0],
                                                                      self.dataset_id,
                                                                      ls[10]))
                    else:
                        sql = 'UPDATE buildings_bulk_load.existing_subset_extracts SET supplied_dataset_id = %s WHERE building_outline_id = %s;'
                        self.db.execute_no_commit(sql, (self.dataset_id, ls[0]))
                # run comparisons function
                # sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
                # self.db.execute_no_commit(sql, data=(self.dataset_id, ))
            sql = 'DISCARD TEMP;'
            self.db.execute_no_commit(sql)  # remove temp files
            if commit_status:
                self.db.commit_open_cursor()
            # update the locality fields
            self.mcb_imagery_layer.currentLayer().removeSelection()

    def exit_clicked(self):
        """
        Called when exit button is clicked
        """
        self.db.close_connection()
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

    def insert_supplied_dataset(self, organisation, description,
                                commit_status):
        """
        generates new supplied outline dataset for the incoming data
        """
        # if self.cursor is None:
        # if self.db._open_cursor is None:
        if self.db._open_cursor is None:
            self.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.supplied_datasets_insert(%s, %s);'
        results = self.db.execute_no_commit(sql, (description, organisation))
        self.dataset_id = results.fetchall()[0][0]

    def insert_supplied_outlines(self, dataset_id, layer, capture_method,
                                 capture_source_group, external_source_id,
                                 commit_status):
        """
        inserts the new outlines into the bulk_load_outlines table
        """
        # find capture source id from capture source and external id
        capture_source = None
        self.inserted_values = 0
        if self.external_source_id is not None:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs, buildings_common.capture_source_group csg WHERE cs.capture_source_group_id = %s AND cs.external_source_id = %s;'
            result = self.db.execute_no_commit(sql,
                                               data=(self.capture_source_group,
                                                     self.external_source_id))
            value = result.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n -------------------- NO '
                                              'CAPTURE SOURCE EXISTS -----'
                                              '--------------- \n\n No '
                                              'capture source with this '
                                              'capture source group and '
                                              'external id'
                                              )
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
            else:
                capture_source = value[0][0]
        else:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s AND cs.external_source_id is Null;'
            result = self.db.execute_no_commit(sql,
                                               data=(capture_source_group,))
            value = result.fetchall()
            if len(value) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n -------------------- NO '
                                              'CAPTURE SOURCE EXISTS ------'
                                              '-------------- \n\n No capture '
                                              'source with this capture source'
                                              ' group and a Null external id'
                                              )
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
            else:
                capture_source = value[0][0]
        # iterate through outlines in map layer
        external_field = str(self.fcb_external_id.currentField())
        for outline in layer.getFeatures():
            wkt = outline.geometry().exportToWkt()
            # convert to postgis shape and ensure outline is a multipolygon
            sql = 'SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));'
            result = self.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.db.execute_no_commit(sql, data=(geom, ))
            geom = result.fetchall()[0][0]
            suburb = self.find_suburb(geom)
            town_city = self.find_town_city(geom)
            TA = self.find_territorial_auth(geom)
            if suburb is None:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n -------------------- No '
                                              'Suburb Admin Boundary ------'
                                              '-------------- \n\n Data will'
                                              ' not be added to table as has '
                                              'null suburb Id')
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
            if TA is None:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n -------------------- No '
                                              'TA Admin Boundary ------'
                                              '-------------- \n\n Data will'
                                              ' not be added to table as has '
                                              'null TA Id'
                                              )
                self.error_dialog.show()
                self.db.rollback_open_cursor()
                return
            self.inserted_values = self.inserted_values + 1
            # insert outline into buildings_bulk_load.supplied_outline
            if external_source_id is None:
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 1, %s, %s, %s, %s, %s, %s);'
                self.db.execute_no_commit(sql, (dataset_id, capture_method,
                                                capture_source, suburb, town_city,
                                                TA, geom))
            else:
                external_id = outline.attribute(external_field)
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, 1, %s, %s, %s, %s, %s, %s);'
                self.db.execute_no_commit(sql, (dataset_id, external_id,
                                                capture_method, capture_source,
                                                suburb, town_city, TA, geom))
        self.le_data_description.clear()
        # returns 1 if function worked None if failed
        return 1
