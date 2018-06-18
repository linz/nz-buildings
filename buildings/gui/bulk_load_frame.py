# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QColor

import qgis
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsFeatureRequest

import processing

from buildings.utilities import database as db
from buildings.utilities import layers
from buildings.gui.error_dialog import ErrorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load.ui'))


class BulkLoadFrame(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(BulkLoadFrame, self).__init__(parent)
        self.setupUi(self)
        self.layer_registry = layer_registry
        self.bulk_load_layer = QgsVectorLayer()
        self.territorial_auth = QgsVectorLayer()
        self.added_building_ids = []
        self.geoms = {}
        self.select_changed = False
        self.geom_changed = False
        self.edit_status = None
        self.db = db
        db.connect()
        iface.mapCanvas().setSelectionColor(QColor("Yellow"))

        sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL;'
        result = self.db._execute(sql)
        result = result.fetchall()[0][0]
        if result == 1:
            sql = 'SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL;'
            p_result = self.db._execute(sql)
            self.current_dataset = p_result.fetchall()[0][0]
            self.add_outlines()
            self.display_current_bl_not_compared()
        else:
            sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE transfer_date is NULL;'
            result2 = self.db._execute(sql)
            result2 = result2.fetchall()[0][0]
            if result2 == 1:
                sql = 'SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE transfer_date is NULL;'
                t_result = self.db._execute(sql)
                # Current compared dataset but not published
                self.current_dataset = t_result.fetchall()[0][0]
                self.add_outlines()
                self.display_not_published()
            else:
                # No current dataset is being worked on
                self.current_dataset = None
                self.display_no_bulk_load()

        # set up signals and slots
        self.rad_external_source.toggled.connect(self.enable_external_bulk)
        self.ml_outlines_layer.currentIndexChanged.connect(self.populate_external_fcb)
        self.btn_bl_ok.clicked.connect(self.bulk_load_ok_clicked)
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)
        self.btn_compare_outlines.clicked.connect(self.compare_outlines_clicked)
        self.rad_add.toggled.connect(self.canvas_add_outline)
        self.rad_edit.toggled.connect(self.canvas_edit_outlines)
        self.btn_edit_ok.clicked.connect(self.edit_ok_clicked)
        self.btn_edit_reset.clicked.connect(self.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.edit_cancel_clicked)
        self.btn_alter_rel.clicked.connect(self.alter_relationships_clicked)
        self.btn_publish.clicked.connect(self.publish_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)

    def display_no_bulk_load(self):
        self.current_dataset = None
        self.grpb_edits.hide()
        self.btn_bl_ok.show()
        self.btn_bl_reset.show()
        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)
        self.populate_bulk_comboboxes()
        self.cmb_capture_method.setEnabled(1)
        self.cmb_organisation.setEnabled(1)
        self.ml_outlines_layer.setEnabled(1)
        self.rad_external_source.setEnabled(1)
        self.cmb_capture_src_grp.setEnabled(1)
        self.le_data_description.setEnabled(1)

    def display_not_published(self):
        self.btn_bl_ok.hide()
        self.btn_bl_reset.hide()
        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_source.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.btn_compare_outlines.setDisabled(1)
        self.grpb_edits.show()
        self.btn_edit_ok.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        self.btn_alter_rel.show()
        self.btn_publish.setEnabled(1)
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.populate_bulk_comboboxes()
        self.bulk_load_current_fields()

    def display_current_bl_not_compared(self):
        self.btn_bl_ok.hide()
        self.btn_bl_reset.hide()
        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_source.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.grpb_edits.show()
        self.btn_edit_ok.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        self.btn_compare_outlines.show()
        self.btn_compare_outlines.setEnabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.populate_bulk_comboboxes()
        self.bulk_load_current_fields()

    def add_outlines(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.layer_registry.remove_layer(self.bulk_load_layer)
        # add the bulk_load_outlines to the layer registry
        self.bulk_load_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.current_dataset))
        self.bulk_load_layer.loadNamedStyle(path + 'building_yellow.qml')
        iface.setActiveLayer(self.bulk_load_layer)

    def populate_bulk_comboboxes(self):
        """Populate bulk load comboboxes"""
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

    def bulk_load_current_fields(self):
        # capture method
        sql = 'SELECT value FROM buildings_common.capture_method cm, buildings_bulk_load.bulk_load_outlines blo WHERE blo.capture_method_id = cm.capture_method_id AND blo.supplied_dataset_id = %s;'
        result = self.db._execute(sql, (self.current_dataset,))
        result = result.fetchall()[0][0]
        self.cmb_capture_method.setCurrentIndex(self.cmb_capture_method.findText(result))
        # organisation
        sql = 'SELECT value FROM buildings_bulk_load.organisation o, buildings_bulk_load.bulk_load_outlines blo, buildings_bulk_load.supplied_datasets sd WHERE blo.supplied_dataset_id = 2 AND blo.supplied_dataset_id = sd.supplied_dataset_id AND sd.supplier_id = o.organisation_id;'
        result = self.db._execute(sql, (self.current_dataset,))
        result = result.fetchall()[0][0]
        self.cmb_organisation.setCurrentIndex(self.cmb_organisation.findText(result))
        # data description
        sql = 'SELECT description FROM buildings_bulk_load.supplied_datasets sd WHERE sd.supplied_dataset_id = %s;'
        result = self.db._execute(sql, (self.current_dataset,))
        result = result.fetchall()[0][0]
        self.le_data_description.setText(result)
        # External Id/fields
        sql = 'SELECT cs.external_source_id FROM buildings_common.capture_source cs, buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = 2 AND blo.capture_source_id = cs.capture_source_id;'
        ex_result = self.db._execute(sql, (self.current_dataset,))
        ex_result = ex_result.fetchall()[0][0]
        if ex_result is not None:
            self.rad_external_source.setChecked(True)
            self.cmb_external_id.setCurrentIndex(self.cmb_external_id.findText(ex_result))
        # capture source group
        sql = 'SELECT cs.capture_source_group_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs, buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = 2 AND blo.capture_source_id = cs.capture_source_id AND cs.capture_source_group_id = csg.capture_source_group_id;'
        result = self.db._execute(sql, (self.current_dataset,))
        result = result.fetchall()[0][0]
        self.cmb_capture_src_grp.setCurrentIndex(result-1)

    def enable_external_bulk(self):
        """Called when radio button is toggled"""
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

    def populate_external_id_cmb(self):
        """Called when radiobutton selected"""
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

    def populate_external_fcb(self):
        self.fcb_external_id.setLayer(self.ml_outlines_layer.currentLayer())

    def bulk_load_ok_clicked(self):
        self.bulk_load()
        self.add_outlines()
        # find if adding was sucessful
        sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL AND transfer_date is NULL;'
        result = self.db._execute(sql)
        result = result.fetchall()[0][0]
        if result == 1:
            self.add_outlines()
            self.display_current_bl_not_compared()

    def bulk_load(self, commit_status=True):
        # description
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
        description = self.le_data_description.text()
        # organisation
        text = self.cmb_organisation.currentText()
        sql = 'SELECT organisation_id FROM buildings_bulk_load.organisation o WHERE o.value = %s;'
        result = self.db._execute(sql, data=(text, ))
        organisation = result.fetchall()[0][0]
        # capture method
        text = self.cmb_capture_method.currentText()
        sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
        result = self.db._execute(sql, data=(text, ))
        capture_method = result.fetchall()[0][0]
        # capture source group
        text = self.cmb_capture_src_grp.currentText()
        text_ls = text.split('-')
        sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s;'
        result = self.db._execute(sql, data=(text_ls[0], ))
        capture_source_group = result.fetchall()[0][0]
        # external source
        if self.rad_external_source.isChecked():
            external_source_id = self.cmb_external_id.currentText()
        else:
            # sets id to None
            external_source_id = None
        # if user checks radio button then does not enter a field error
        if external_source_id is None and self.rad_external_source.isChecked():
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
        # bulk_load_layer
        bulk_load_layer = self.ml_outlines_layer.currentLayer()
        self.current_dataset = self.insert_supplied_dataset(organisation,
                                                            description,
                                                            commit_status)
        val = self.insert_supplied_outlines(self.current_dataset,
                                            bulk_load_layer,
                                            capture_method,
                                            capture_source_group,
                                            external_source_id,
                                            commit_status)
        if val is None:
            # if insert_supplied_outlines function failed don't continue
            return
        if commit_status:
            self.db.commit_open_cursor()

    def insert_supplied_dataset(self, organisation, description,
                                commit_status):
        """generates new supplied outline dataset for the incoming data"""
        if self.db._open_cursor is None:
            self.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.supplied_datasets_insert(%s, %s);'
        results = self.db.execute_no_commit(sql, (description, organisation))
        return results.fetchall()[0][0]

    def insert_supplied_outlines(self, dataset_id, layer, capture_method,
                                 capture_source_group, external_source_id,
                                 commit_status):
        """inserts the new outlines into the bulk_load_outlines table"""
        # find capture source id from capture source and external id
        capture_source = None
        self.inserted_values = 0
        if len(self.cmb_external_id.currentText()) is not 0:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs, buildings_common.capture_source_group csg WHERE cs.capture_source_group_id = %s AND cs.external_source_id = %s;'
            result = self.db.execute_no_commit(sql,
                                               data=(capture_source_group,
                                                     external_source_id))
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
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # suburb
            sql = 'SELECT buildings.suburb_locality_intersect_polygon(%s);'
            result = self.db.execute_no_commit(sql, (geom, ))
            suburb = result.fetchall()[0][0]
            # town city
            sql = 'SELECT buildings.town_city_intersect_polygon(%s);'
            result = self.db.execute_no_commit(sql, (geom, ))
            town_city = result.fetchall()[0][0]
            # Territorial Authority
            sql = 'SELECT buildings.territorial_authority_intersect_polygon(%s);'
            result = self.db.execute_no_commit(sql, (geom, ))
            territorial_authority = result.fetchall()[0][0]
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
            if territorial_authority is None:
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
                                                capture_source, suburb,
                                                town_city,
                                                territorial_authority,
                                                geom))
            else:
                external_id = outline.attribute(external_field)
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, 1, %s, %s, %s, %s, %s, %s);'
                self.db.execute_no_commit(sql, (dataset_id, external_id,
                                                capture_method, capture_source,
                                                suburb, town_city,
                                                territorial_authority,
                                                geom))
        self.le_data_description.clear()
        # returns 1 if function worked None if failed
        return 1

    def bulk_load_reset_clicked(self):
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_source.setChecked(False)

    def compare_outlines_clicked(self):
        self.compare()
        self.btn_publish.setEnabled(1)
        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setEnabled(1)

    def compare(self, commit_status=True):
        self.db.open_cursor()
        # find convex hull of supplied dataset outlines
        result = processing.runalg('qgis:convexhull', self.bulk_load_layer,
                                   None, 0, None)
        convex_hull = processing.getObject(result['OUTPUT'])
        for feat in convex_hull.getFeatures():
            geom = feat.geometry()
            wkt = geom.exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
        sql = 'SELECT * FROM buildings.building_outlines bo WHERE ST_Intersects(bo.shape, (SELECT ST_ConvexHull(ST_Collect(buildings_bulk_load.bulk_load_outlines.shape)) FROM buildings_bulk_load.bulk_load_outlines WHERE buildings_bulk_load.bulk_load_outlines.supplied_dataset_id = %s)) AND bo.building_outline_id NOT IN (SELECT building_outline_id FROM buildings_bulk_load.removed);'
        result = self.db.execute_no_commit(sql, data=(self.current_dataset, ))
        results = result.fetchall()
        if len(results) == 0:  # no existing outlines in this area
            # all new outlines
            sql = "SELECT bulk_load_outline_id FROM buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s;"
            results = self.db.execute_no_commit(sql, (self.current_dataset, ))
            bulk_loaded_ids = results.fetchall()
            for id in bulk_loaded_ids:
                sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 1);'
                self.db.execute_no_commit(sql, (id[0], ))
            sql = 'UPDATE buildings_bulk_load.supplied_datasets SET processed_date = now() WHERE supplied_dataset_id = %s;'
            result = self.db.execute_no_commit(sql, (self.current_dataset,))
        else:
            for ls in results:
                sql = 'SELECT building_outline_id FROM buildings_bulk_load.existing_subset_extracts WHERE building_outline_id = %s;'
                result = self.db.execute_no_commit(sql, (ls[0], ))
                result = result.fetchall()
                if len(result) == 0:
                    # insert relevant data into existing_subset_extract
                    sql = 'SELECT buildings_bulk_load.existing_subset_extracts_insert(%s, %s, %s);'
                    result = self.db.execute_no_commit(sql, data=(ls[0],
                                                       self.current_dataset,
                                                       ls[10]))
                else:
                    sql = 'UPDATE buildings_bulk_load.existing_subset_extracts SET supplied_dataset_id = %s WHERE building_outline_id = %s;'
                    self.db.execute_no_commit(sql, (self.current_dataset,
                                                    ls[0]))
            # run comparisons function
            sql = 'SELECT buildings_bulk_load.compare_building_outlines(%s);'
            self.db.execute_no_commit(sql, data=(self.current_dataset, ))
        if commit_status:
            self.db.commit_open_cursor()

    def canvas_add_outline(self):
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        # change style of TAs
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})
        self.bulk_load_layer.featureAdded.connect(self.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(self.creator_feature_deleted)
        # enable editing
        iface.setActiveLayer(self.bulk_load_layer)
        iface.actionToggleEditing().trigger()
        # set editing to add polygon
        iface.actionAddFeature().trigger()

    def creator_feature_added(self, qgsfId):
        """
        Called when feature is added
        @param qgsfId:      Id of added feature
        @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        # TODO handle when user tries to add multiple new geoms
        if qgsfId not in self.added_building_ids:
            self.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.bulk_load_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = self.db._execute(sql, data=(wkt, ))
        self.geom = result.fetchall()[0][0]
        # enable comboboxes
        self.cmb_capture_method_2.setEnabled(1)
        self.cmb_capture_source.setEnabled(1)
        self.cmb_ta.setEnabled(1)
        self.cmb_town.setEnabled(1)
        self.cmb_suburb.setEnabled(1)
        # enable save
        self.btn_edit_ok.setEnabled(1)
        self.btn_edit_reset.setEnabled(1)
        self.populate_edit_comboboxes()

    def creator_feature_deleted(self, qgsfId):
        """
        Called when a Feature is Deleted
        @param qgsfId:      Id of deleted feature
        @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.added_building_ids:
            self.added_building_ids.remove(qgsfId)
            if self.added_building_ids == []:
                self.cmb_capture_method_2.setDisabled(1)
                self.cmb_capture_source.setDisabled(1)
                self.cmb_ta.setDisabled(1)
                self.cmb_town.setDisabled(1)
                self.cmb_suburb.setDisabled(1)
                # disable save
                self.btn_edit_ok.setDisabled(1)
                self.btn_edit_reset.setDisabled(1)

    def canvas_edit_outlines(self):
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        # change style of TAs
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})
        self.bulk_load_layer.selectionChanged.connect(self.selection_changed)
        self.bulk_load_layer.geometryChanged.connect(self.feature_changed)
        # enable editing
        iface.setActiveLayer(self.bulk_load_layer)
        iface.actionToggleEditing().trigger()
        # set editing to edit polygon
        iface.actionNodeTool().trigger()

    def feature_changed(self, qgsfId, geom):
        """
        Called when feature is changed
        @param qgsfId:      Id of added feature
        @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        @param geom:        geometry of added feature
        @type  geom:        qgis.core.QgsGeometry
        """

        # get new feature geom and convert to correct format
        wkt = geom.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
        result = self.db._execute(sql, data=(wkt, ))
        self.geom = result.fetchall()[0][0]
        sql = 'SELECT shape from buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s;'
        result = self.db._execute(sql, (qgsfId, ))
        result = result.fetchall()[0][0]
        if self.geom == result:
            if qgsfId in self.geoms.keys():
                del self.geoms[qgsfId]
        else:
            self.geoms[qgsfId] = self.geom
        self.geom_changed = True
        self.btn_edit_ok.setEnabled(1)
        self.btn_edit_reset.setEnabled(1)

    def selection_changed(self, added, removed, cleared):
        """Called when feature is selected"""
        # if only one outline is selected
        if len(self.bulk_load_layer.selectedFeatures()) == 1:
            self.bulk_load_outline_id = [feat.id() for feat in self.bulk_load_layer.selectedFeatures()][0]
            self.cmb_capture_method_2.setEnabled(1)
            self.cmb_capture_source.setEnabled(1)
            self.cmb_status.setEnabled(1)
            self.cmb_capture_method_2.clear()
            self.cmb_capture_source.clear()
            self.cmb_status.clear()
            self.cmb_ta.setEnabled(1)
            self.cmb_town.setEnabled(1)
            self.cmb_suburb.setEnabled(1)
            self.cmb_ta.clear()
            self.cmb_town.clear()
            self.cmb_suburb.clear()
            self.populate_edit_comboboxes()
            # enable save and reset
            self.btn_edit_ok.setEnabled(1)
            self.btn_edit_reset.setEnabled(1)
            self.select_changed = True
        # if more than one outline is selected
        if len(self.bulk_load_layer.selectedFeatures()) > 1:
            feats = []
            self.ids = [feat.id() for feat in self.bulk_load_layer.selectedFeatures()]
            for feature in self.bulk_load_layer.selectedFeatures():
                ls = []
                ls.append(feature.attributes()[3])
                ls.append(feature.attributes()[4])
                ls.append(feature.attributes()[5])
                ls.append(feature.attributes()[6])
                ls.append(feature.attributes()[7])
                ls.append(feature.attributes()[8])
                if ls not in feats:
                    feats.append(ls)
            # if features with different attributes have been selected (not allowed)
            if len(feats) > 1:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n ---- MULTIPLE NON'
                                              ' IDENTICAL FEATURES SELECTED '
                                              '---- \n\n Can only edit attributes'
                                              ' of multiple features when all'
                                              ' existing attributes are '
                                              'identical.'
                                              )
                self.error_dialog.show()
                self.bulk_load_outline_id = None
                self.cmb_capture_method_2.clear()
                self.cmb_capture_method_2.setDisabled(1)
                self.cmb_capture_source.clear()
                self.cmb_capture_source.setDisabled(1)
                self.cmb_status.clear()
                self.cmb_status.setEnabled(1)
                self.cmb_ta.clear()
                self.cmb_ta.setDisabled(1)
                self.cmb_town.clear()
                self.cmb_town.setDisabled(1)
                self.cmb_suburb.clear()
                self.cmb_suburb.setDisabled(1)
                self.btn_edit_ok.setDisabled(1)
                self.btn_edit_reset.setDisabled(1)
                iface.activeLayer().removeSelection()
                self.select_changed = False
            # if all selected features have the same attributes (allowed)
            elif len(feats) == 1:
                self.bulk_load_outline_id = [feat.id() for feat in self.bulk_load_layer.selectedFeatures()][0]
                self.cmb_capture_method_2.setEnabled(1)
                self.cmb_capture_source.setEnabled(1)
                self.cmb_status.setEnabled(1)
                self.cmb_capture_method_2.clear()
                self.cmb_capture_source.clear()
                self.cmb_status.clear()
                self.cmb_ta.setEnabled(1)
                self.cmb_town.setEnabled(1)
                self.cmb_suburb.setEnabled(1)
                self.cmb_ta.clear()
                self.cmb_town.clear()
                self.cmb_suburb.clear()
                self.populate_edit_comboboxes()
                # enable save and reset
                self.btn_edit_ok.setEnabled(1)
                self.btn_edit_reset.setEnabled(1)
                self.select_changed = True
        # If no outlines are selected
        if len(self.bulk_load_layer.selectedFeatures()) == 0:
            self.bulk_load_outline_id = None
            self.cmb_capture_method_2.clear()
            self.cmb_capture_method_2.setDisabled(1)
            self.cmb_capture_source.clear()
            self.cmb_capture_source.setDisabled(1)
            self.cmb_status.setDisabled(1)
            self.cmb_status.clear()
            self.cmb_ta.clear()
            self.cmb_ta.setDisabled(1)
            self.cmb_town.clear()
            self.cmb_town.setDisabled(1)
            self.cmb_suburb.clear()
            self.cmb_suburb.setDisabled(1)
            self.btn_edit_ok.setDisabled(1)
            self.btn_edit_reset.setDisabled(1)
            self.select_changed = False

    def populate_edit_comboboxes(self):
        # populate capture method combobox
        sql = 'SELECT value FROM buildings_common.capture_method;'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method_2.addItem(item[0])
        # populate capture source group
        sql = 'SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs WHERE cs.capture_source_group_id = csg.capture_source_group_id;'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
            self.cmb_capture_source.addItem(text)
        # populate suburb combobox
        sql = 'SELECT DISTINCT suburb_4th FROM buildings_reference.suburb_locality'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_suburb.addItem(item[0])
        # populate town combobox
        sql = 'SELECT DISTINCT name FROM buildings_reference.town_city'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_town.addItem(item[0])
        # populate territorial authority combobox
        sql = 'SELECT DISTINCT name FROM buildings_reference.territorial_authority'
        result = self.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_ta.addItem(item[0])
        if self.rad_edit.isChecked():
            # bulk load status
            sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status;'
            result = self.db._execute(sql)
            ls = result.fetchall()
            for item in ls:
                self.cmb_status.addItem(item[0])
            sql = 'SELECT value FROM buildings_bulk_load.bulk_load_status bls, buildings_bulk_load.bulk_load_outlines blo WHERE blo.bulk_load_status_id = bls.bulk_load_status_id AND blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0][0]
            self.cmb_status.setCurrentIndex(self.cmb_status.findText(result))
            # capture method
            sql = 'SELECT value FROM buildings_common.capture_method cm, buildings_bulk_load.bulk_load_outlines blo WHERE blo.capture_method_id = cm.capture_method_id AND blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0][0]
            self.cmb_capture_method_2.setCurrentIndex(self.cmb_capture_method_2.findText(result))
            # capture source
            sql = 'SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs WHERE cs.capture_source_group_id = csg.capture_source_group_id;'
            result = self.db._execute(sql)
            ls = result.fetchall()
            sql = 'SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs, buildings_bulk_load.bulk_load_outlines blo WHERE csg.capture_source_group_id = cs.capture_source_group_id AND blo.capture_source_id = cs.capture_source_id and blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0]
            value_index = 0
            for index, item in enumerate(ls):
                if item == result:
                    value_index = index
            self.cmb_capture_source.setCurrentIndex(value_index)
            # suburb
            sql = 'SELECT suburb_4th FROM buildings_reference.suburb_locality sl, buildings_bulk_load.bulk_load_outlines blo WHERE sl.suburb_locality_id = blo.suburb_locality_id AND blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0][0]
            self.cmb_suburb.setCurrentIndex(self.cmb_suburb.findText(result))
            # town city
            sql = 'SELECT name FROM buildings_reference.town_city tc, buildings_bulk_load.bulk_load_outlines blo WHERE tc.town_city_id = blo.town_city_id AND blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0][0]
            self.cmb_town.setCurrentIndex(self.cmb_town.findText(result))
            # territorial Authority
            sql = 'SELECT name FROM buildings_reference.territorial_authority ta, buildings_bulk_load.bulk_load_outlines blo WHERE ta.territorial_authority_id = blo.territorial_authority_id AND blo.bulk_load_outline_id = %s;'
            result = self.db._execute(sql, (self.bulk_load_outline_id,))
            result = result.fetchall()[0][0]
            self.cmb_ta.setCurrentIndex(self.cmb_ta.findText(result))

    def edit_ok_clicked(self, holder, commit_status=True):
        if self.rad_add.isChecked():
            self.db.open_cursor()
            # capture method id
            text = self.cmb_capture_method_2.currentText()
            sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
            result = self.db.execute_no_commit(sql, data=(text, ))
            capture_method_id = result.fetchall()[0][0]
            # capture source
            text = self.cmb_capture_source.currentText()
            if text == '':
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n ---------------- '
                                              'NO CAPTURE SOURCE --'
                                              '-------------- \n\n '
                                              'There are no capture '
                                              'source entries'
                                              )
                self.error_dialog.show()
                return
            text_ls = text.split('- ')
            sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;'
            result = self.db.execute_no_commit(sql, data=(text_ls[0], text_ls[1]))
            data = result.fetchall()[0][0]
            if text_ls[2] == 'None':
                sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id is NULL;'
                result = self.db.execute_no_commit(sql, data=(data,))
            else:
                sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;'
                result = self.db.execute_no_commit(sql, data=(data, text_ls[2]))
            capture_source_id = result.fetchall()[0][0]
            # suburb
            text = self.cmb_suburb.currentText()
            sql = 'SELECT suburb_locality_id FROM buildings_reference.suburb_locality WHERE buildings_reference.suburb_locality.suburb_4th = %s;'
            result = self.db.execute_no_commit(sql, (text, ))
            suburb = result.fetchall()[0][0]
            # town
            text = self.cmb_town.currentText()
            sql = 'SELECT town_city_id FROM buildings_reference.town_city WHERE buildings_reference.town_city.name = %s;'
            result = self.db.execute_no_commit(sql, (text, ))
            town = result.fetchall()[0][0]
            # territorial Authority
            text = self.cmb_ta.currentText()
            sql = 'SELECT territorial_authority_id FROM buildings_reference.territorial_authority WHERE buildings_reference.territorial_authority.name = %s;'
            result = self.db.execute_no_commit(sql, (text, ))
            t_a = result.fetchall()[0][0]
            # call function to insert into bulk_load_outlines table
            sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s);'
            result = self.db.execute_no_commit(sql, (self.current_dataset,
                                                     capture_method_id,
                                                     capture_source_id,
                                                     suburb,
                                                     town, t_a, self.geom))
            self.outline_id = result.fetchall()[0][0]
            sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 2);'
            self.db.execute_no_commit(sql, (self.outline_id, ))

            if commit_status:
                self.db.commit_open_cursor()

            # reset comboboxes for next outline
            self.cmb_capture_method.setCurrentIndex(0)
            self.cmb_capture_method.setDisabled(1)
            self.cmb_capture_source.setCurrentIndex(0)
            self.cmb_capture_source.setDisabled(1)
            self.cmb_ta.setCurrentIndex(0)
            self.cmb_ta.setDisabled(1)
            self.cmb_town.setCurrentIndex(0)
            self.cmb_town.setDisabled(1)
            self.cmb_suburb.setCurrentIndex(0)
            self.cmb_suburb.setDisabled(1)
            self.btn_edit_ok.setDisabled(1)
            self.btn_edit_reset.setDisabled(1)

        elif self.rad_edit.isChecked():
            self.btn_edit_ok.setDisabled(1)
            self.btn_edit_reset.setDisabled(1)
            self.db.open_cursor()
            # if only geometries are changed
            if self.geom_changed and not self.select_changed:
                for key in self.geoms:
                    sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET shape = %s WHERE bulk_load_outline_id = %s;'
                    self.db.execute_no_commit(sql, (self.geoms[key],
                                                    key))
            # if only attributes are changed
            if self.select_changed and not self.geom_changed:
                # bulk load status
                text = self.cmb_status.currentText()
                sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_status bls WHERE bls.value = %s;'
                result = self.db.execute_no_commit(sql, data=(text, ))
                bulk_load_status_id = result.fetchall()[0][0]
                # capture method
                text = self.cmb_capture_method_2.currentText()
                sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
                result = self.db.execute_no_commit(sql, data=(text, ))
                capture_method_id = result.fetchall()[0][0]
                # capture source
                text = self.cmb_capture_source.currentText()
                if text == '':
                    self.error_dialog = ErrorDialog()
                    self.error_dialog.fill_report('\n ---------------- '
                                                  'NO CAPTURE SOURCE --'
                                                  '-------------- \n\n '
                                                  'There are no capture '
                                                  'source entries.'
                                                  )
                    self.error_dialog.show()
                    return
                text_ls = text.split('- ')
                sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;'
                result = self.db.execute_no_commit(sql, data=(text_ls[0], text_ls[1]))
                data = result.fetchall()[0][0]
                if text_ls[2] == 'None':
                    sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id is NULL;'
                    result = self.db.execute_no_commit(sql, data=(data,))
                else:
                    sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;'
                    result = self.db.execute_no_commit(sql, data=(data, text_ls[2]))
                capture_source_id = result.fetchall()[0][0]
                # suburb
                text = self.cmb_suburb.currentText()
                sql = 'SELECT suburb_locality_id FROM buildings_reference.suburb_locality WHERE buildings_reference.suburb_locality.suburb_4th = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                suburb = result.fetchall()[0][0]
                # town
                text = self.cmb_town.currentText()
                sql = 'SELECT town_city_id FROM buildings_reference.town_city WHERE buildings_reference.town_city.name = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                town = result.fetchall()[0][0]
                # territorial authority
                text = self.cmb_ta.currentText()
                sql = 'SELECT territorial_authority_id FROM buildings_reference.territorial_authority WHERE buildings_reference.territorial_authority.name = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                t_a = result.fetchall()[0][0]
                if len(self.ids) > 0:
                    # if there is more than one feature to update
                    for i in self.ids:
                        sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = %s, capture_method_id = %s, capture_source_id = %s, suburb_locality_id = %s, town_city_id = %s, territorial_authority_id = %s WHERE bulk_load_outline_id = %s;'
                        self.db.execute_no_commit(sql, (bulk_load_status_id,
                                                        capture_method_id,
                                                        capture_source_id,
                                                        suburb,
                                                        town, t_a,
                                                        i))
                else:
                    sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = %s, capture_method_id = %s, capture_source_id = %s, suburb_locality_id = %s, town_city_id = %s, territorial_authority_id = %s WHERE bulk_load_outline_id = %s;'
                    self.db.execute_no_commit(sql, (bulk_load_status_id,
                                                    capture_method_id,
                                                    capture_source_id,
                                                    suburb,
                                                    town, t_a,
                                                    self.bulk_load_outline_id))
            # if both geometries and attributes are changed
            if self.geom_changed and self.select_changed:
                for key in self.geoms:
                    sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET shape = %s WHERE bulk_load_outline_id = %s;'
                    self.db.execute_no_commit(sql, (self.geoms[key],
                                                    key))
                # bulk load status
                text = self.cmb_status.currentText()
                sql = 'SELECT bulk_load_status_id FROM buildings_bulk_load.bulk_load_status bls WHERE bls.value = %s;'
                result = self.db.execute_no_commit(sql, data=(text, ))
                bulk_load_status_id = result.fetchall()[0][0]
                # capture method
                text = self.cmb_capture_method_2.currentText()
                sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
                result = self.db.execute_no_commit(sql, data=(text, ))
                capture_method_id = result.fetchall()[0][0]
                # capture source
                text = self.cmb_capture_source.currentText()
                if text == '':
                    self.error_dialog = ErrorDialog()
                    self.error_dialog.fill_report('\n ---------------- '
                                                  'NO CAPTURE SOURCE --'
                                                  '-------------- \n\n '
                                                  'There are no capture '
                                                  'source entries.'
                                                  )
                    self.error_dialog.show()
                    return
                text_ls = text.split('- ')
                sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;'
                result = self.db.execute_no_commit(sql, data=(text_ls[0], text_ls[1]))
                data = result.fetchall()[0][0]
                if text_ls[2] == 'None':
                    sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id is NULL;'
                    result = self.db.execute_no_commit(sql, data=(data,))
                else:
                    sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;'
                    result = self.db.execute_no_commit(sql, data=(data, text_ls[2]))
                capture_source_id = result.fetchall()[0][0]
                # suburb
                text = self.cmb_suburb.currentText()
                sql = 'SELECT suburb_locality_id FROM buildings_reference.suburb_locality WHERE buildings_reference.suburb_locality.suburb_4th = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                suburb = result.fetchall()[0][0]
                # town
                text = self.cmb_town.currentText()
                sql = 'SELECT town_city_id FROM buildings_reference.town_city WHERE buildings_reference.town_city.name = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                town = result.fetchall()[0][0]
                # territorial authority
                text = self.cmb_ta.currentText()
                sql = 'SELECT territorial_authority_id FROM buildings_reference.territorial_authority WHERE buildings_reference.territorial_authority.name = %s;'
                result = self.db.execute_no_commit(sql, (text, ))
                t_a = result.fetchall()[0][0]
                if len(self.ids) > 0:
                    # if there is more than one feature to update
                    for i in self.ids:
                        sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = %s, capture_method_id = %s, capture_source_id = %s, suburb_locality_id = %s, town_city_id = %s, territorial_authority_id = %s WHERE bulk_load_outline_id = %s;'
                        self.db.execute_no_commit(sql, (bulk_load_status_id,
                                                        capture_method_id,
                                                        capture_source_id,
                                                        suburb,
                                                        town, t_a,
                                                        i))
                else:
                        sql = 'UPDATE buildings_bulk_load.bulk_load_outlines SET bulk_load_status_id = %s, capture_method_id = %s, capture_source_id = %s, suburb_locality_id = %s, town_city_id = %s, territorial_authority_id = %s WHERE bulk_load_outline_id = %s;'
                        self.db.execute_no_commit(sql, (bulk_load_status_id,
                                                        capture_method_id,
                                                        capture_source_id,
                                                        suburb,
                                                        town, t_a,
                                                        self.bulk_load_outline_id))
            if commit_status:
                self.geoms = {}
                self.ids = []
                self.geom_changed = False
                self.select_changed = False
                self.db.commit_open_cursor()

    def edit_reset_clicked(self):
        iface.actionCancelEdits().trigger()
        if self.rad_add.isChecked():
            # restart editing
            iface.actionToggleEditing().trigger()
            iface.actionAddFeature().trigger()
        elif self.rad_edit.isChecked():
            self.geoms = {}
            self.geom_changed = False
            self.select_changed = False
            # restart editing
            iface.actionToggleEditing().trigger()
            iface.actionNodeTool().trigger()
            iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        self.cmb_capture_method_2.clear()
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.clear()
        self.cmb_capture_source.setDisabled(1)
        self.cmb_status.setDisabled(1)
        self.cmb_status.clear()
        self.cmb_ta.clear()
        self.cmb_ta.setDisabled(1)
        self.cmb_town.clear()
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.clear()
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_ok.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)

    def edit_cancel_clicked(self):
        iface.actionCancelEdits().trigger()
        self.rad_edit.setAutoExclusive(False)
        self.rad_edit.setChecked(False)
        self.rad_edit.setAutoExclusive(True)
        self.rad_add.setAutoExclusive(False)
        self.rad_add.setChecked(False)
        self.rad_add.setAutoExclusive(True)
        if self.territorial_auth in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.territorial_auth)
        if self.bulk_load_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.bulk_load_layer)
        self.add_outlines()
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        self.btn_edit_ok.setDisabled(1)

    def alter_relationships_clicked(self):
        self.db.close_connection()
        if self.bulk_load_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.bulk_load_layer)
        if self.territorial_auth in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.territorial_auth)
        from buildings.gui.alter_building_relationships import AlterRelationships
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(self.layer_registry))

    def publish_clicked(self, commit_status=True):
        self.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.load_building_outlines(%s);'
        self.db.execute_no_commit(sql, (self.current_dataset,))
        'SELECT buildings_lds.populate_buildings_lds();'
        self.db.execute_no_commit(sql)
        if commit_status:
            self.db.commit_open_cursor()
        self.display_no_bulk_load()
        self.current_dataset = None
        if self.territorial_auth in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.territorial_auth)
        if self.bulk_load_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.bulk_load_layer)

    def exit_clicked(self):
        iface.actionCancelEdits().trigger()
        if self.bulk_load_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.bulk_load_layer)
        if self.territorial_auth in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.territorial_auth)
        from buildings.gui.start_up import StartUpFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(StartUpFrame(self.layer_registry))
