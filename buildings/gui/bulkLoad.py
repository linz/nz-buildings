from buildings.gui.error_dialog import ErrorDialog


class BulkLoad:
    def __init__(self, bulk_load_frame):
        self.bulk_lf = bulk_load_frame
        self.bulk_lf.rad_external_source.toggled.connect(self.enable_external_bulk)
        self.bulk_lf.ml_outlines_layer.currentIndexChanged.connect(self.populate_external_fcb)

    def populate_bulk_comboboxes(self):
        """Populate bulk load comboboxes"""
        # populate organisation combobox
        sql = 'SELECT value FROM buildings_bulk_load.organisation;'
        result = self.bulk_lf.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.bulk_lf.cmb_organisation.addItem(item[0])
        # populate capture method combobox
        sql = 'SELECT value FROM buildings_common.capture_method;'
        result = self.bulk_lf.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.bulk_lf.cmb_capture_method.addItem(item[0])
        # populate capture source group
        sql = 'SELECT value, description FROM buildings_common.capture_source_group;'
        result = self.bulk_lf.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1])
            self.bulk_lf.cmb_capture_src_grp.addItem(text)

    def bulk_load_current_fields(self):
        # capture method
        sql = 'SELECT value FROM buildings_common.capture_method cm, buildings_bulk_load.bulk_load_outlines blo WHERE blo.capture_method_id = cm.capture_method_id AND blo.supplied_dataset_id = %s;'
        result = self.bulk_lf.db._execute(sql, (self.bulk_lf.current_dataset,))
        result = result.fetchall()[0][0]
        self.bulk_lf.cmb_capture_method.setCurrentIndex(self.bulk_lf.cmb_capture_method.findText(result))
        # organisation
        sql = 'SELECT value FROM buildings_bulk_load.organisation o, buildings_bulk_load.bulk_load_outlines blo, buildings_bulk_load.supplied_datasets sd WHERE blo.supplied_dataset_id = %s AND blo.supplied_dataset_id = sd.supplied_dataset_id AND sd.supplier_id = o.organisation_id;'
        result = self.bulk_lf.db._execute(sql, (self.bulk_lf.current_dataset,))
        result = result.fetchall()[0][0]
        self.bulk_lf.cmb_organisation.setCurrentIndex(self.bulk_lf.cmb_organisation.findText(result))
        # data description
        sql = 'SELECT description FROM buildings_bulk_load.supplied_datasets sd WHERE sd.supplied_dataset_id = %s;'
        result = self.bulk_lf.db._execute(sql, (self.bulk_lf.current_dataset,))
        result = result.fetchall()[0][0]
        self.bulk_lf.le_data_description.setText(result)
        # External Id/fields
        sql = 'SELECT cs.external_source_id FROM buildings_common.capture_source cs, buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s AND blo.capture_source_id = cs.capture_source_id;'
        ex_result = self.bulk_lf.db._execute(sql, (self.bulk_lf.current_dataset,))
        ex_result = ex_result.fetchall()[0][0]
        if ex_result is not None:
            self.bulk_lf.rad_external_source.setChecked(True)
            self.bulk_lf.cmb_external_id.setCurrentIndex(self.bulk_lf.cmb_external_id.findText(ex_result))
        # capture source group
        sql = 'SELECT cs.capture_source_group_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs, buildings_bulk_load.bulk_load_outlines blo WHERE blo.supplied_dataset_id = %s AND blo.capture_source_id = cs.capture_source_id AND cs.capture_source_group_id = csg.capture_source_group_id;'
        result = self.bulk_lf.db._execute(sql, (self.bulk_lf.current_dataset,))
        result = result.fetchall()[0][0]
        self.bulk_lf.cmb_capture_src_grp.setCurrentIndex(result - 1)
        # outlines layer
        self.bulk_lf.ml_outlines_layer.setCurrentIndex(self.bulk_lf.ml_outlines_layer.findText('bulk_load_outlines'))

    def enable_external_bulk(self):
        """Called when radio button is toggled"""
        if self.bulk_lf.rad_external_source.isChecked():
            self.bulk_lf.fcb_external_id.setEnabled(1)
            self.bulk_lf.fcb_external_id.setLayer(self.bulk_lf.ml_outlines_layer.currentLayer())
            self.bulk_lf.cmb_external_id.setEnabled(1)
            self.bulk_lf.populate_external_id_cmb()
        else:
            self.bulk_lf.fcb_external_id.setDisabled(1)
            self.bulk_lf.fcb_external_id.setLayer(None)
            self.bulk_lf.cmb_external_id.setDisabled(1)
            self.bulk_lf.cmb_external_id.clear()

    def populate_external_id_cmb(self):
        """Called when radiobutton selected"""
        # populate external id combobox
        sql = 'SELECT external_source_id FROM buildings_common.capture_source;'
        result = self.bulk_lf.db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                count = 0
                exists = False
                while count < self.bulk_lf.cmb_external_id.count():
                    if self.bulk_lf.cmb_external_id.itemText(count) == str(item[0]):
                        exists = True
                    count = count + 1
                if exists is False:
                    self.bulk_lf.cmb_external_id.addItem(item[0])

    def populate_external_fcb(self):
        self.bulk_lf.fcb_external_id.setLayer(self.bulk_lf.ml_outlines_layer.currentLayer())

    def bulk_load(self, commit_status=True):
        # description
        if self.bulk_lf.le_data_description.text() == '':
            self.bulk_lf.error_dialog = ErrorDialog()
            self.bulk_lf.error_dialog.fill_report('\n -------------------- EMPTY '
                                                  'DESCRIPTION FIELD ------------'
                                                  '-------- \n\n Null descriptions'
                                                  ' not allowed'
                                                  )
            self.bulk_lf.error_dialog.show()
            return
        if len(self.bulk_lf.le_data_description.text()) >= 40:
            self.bulk_lf.error_dialog = ErrorDialog()
            self.bulk_lf.error_dialog.fill_report('\n -------------------- VALUE '
                                                  'TOO LONG -------------------- '
                                                  '\n\n Enter less than 250 '
                                                  'characters'
                                                  )
            self.bulk_lf.error_dialog.show()
            return
        description = self.bulk_lf.le_data_description.text()
        # organisation
        text = self.bulk_lf.cmb_organisation.currentText()
        sql = 'SELECT organisation_id FROM buildings_bulk_load.organisation o WHERE o.value = %s;'
        result = self.bulk_lf.db._execute(sql, data=(text, ))
        organisation = result.fetchall()[0][0]
        # capture method
        text = self.bulk_lf.cmb_capture_method.currentText()
        sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
        result = self.bulk_lf.db._execute(sql, data=(text, ))
        capture_method = result.fetchall()[0][0]
        # capture source group
        text = self.bulk_lf.cmb_capture_src_grp.currentText()
        text_ls = text.split('-')
        sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s;'
        result = self.bulk_lf.db._execute(sql, data=(text_ls[0], ))
        capture_source_group = result.fetchall()[0][0]
        # external source
        if self.bulk_lf.rad_external_source.isChecked():
            external_source_id = self.bulk_lf.cmb_external_id.currentText()
        else:
            # sets id to None
            external_source_id = None
        # if user checks radio button then does not enter a field error
        if external_source_id is None and self.bulk_lf.rad_external_source.isChecked():
            self.bulk_lf.error_dialog = ErrorDialog()
            self.bulk_lf.error_dialog.fill_report('\n -------------------- NO EXTERNAL'
                                                  ' ID -------------------- \n\n'
                                                  ' Please either uncheck the radio'
                                                  ' button or enter a new capture '
                                                  ' source or External Source Id'
                                                  )
            self.bulk_lf.error_dialog.show()
            # stop the code here
            return
        if self.bulk_lf.fcb_external_id.currentField() is None and self.bulk_lf.rad_external_source.isChecked():
            self.bulk_lf.error_dialog = ErrorDialog()
            self.bulk_lf.error_dialog.fill_report('\n -------------------- NO EXTERNAL'
                                                  ' ID FIELD-------------------- \n\n'
                                                  ' Please either uncheck the radio'
                                                  ' button or enter an external id'
                                                  ' field'
                                                  )
            self.bulk_lf.error_dialog.show()
            # stop the code here
            return
        # bulk_load_layer
        bulk_load_layer = self.bulk_lf.ml_outlines_layer.currentLayer()
        self.bulk_lf.current_dataset = self.insert_supplied_dataset(organisation,
                                                                    description,
                                                                    commit_status)
        val = self.insert_supplied_outlines(self.bulk_lf.current_dataset,
                                            bulk_load_layer,
                                            capture_method,
                                            capture_source_group,
                                            external_source_id,
                                            commit_status)
        if val is None:
            # if insert_supplied_outlines function failed don't continue
            return
        if commit_status:
            self.bulk_lf.db.commit_open_cursor()

    def insert_supplied_dataset(self, organisation, description,
                                commit_status):
        """generates new supplied outline dataset for the incoming data"""
        if self.bulk_lf.db._open_cursor is None:
            self.bulk_lf.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.supplied_datasets_insert(%s, %s);'
        results = self.bulk_lf.db.execute_no_commit(sql, (description, organisation))
        return results.fetchall()[0][0]

    def insert_supplied_outlines(self, dataset_id, layer, capture_method,
                                 capture_source_group, external_source_id,
                                 commit_status):
        """inserts the new outlines into the bulk_load_outlines table"""
        # find capture source id from capture source and external id
        capture_source = None
        self.bulk_lf.inserted_values = 0
        if len(self.bulk_lf.cmb_external_id.currentText()) is not 0:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs, buildings_common.capture_source_group csg WHERE cs.capture_source_group_id = %s AND cs.external_source_id = %s;'
            result = self.bulk_lf.db.execute_no_commit(sql,
                                                       data=(capture_source_group,
                                                       external_source_id))
            value = result.fetchall()
            if len(value) == 0:
                self.bulk_lf.error_dialog = ErrorDialog()
                self.bulk_lf.error_dialog.fill_report('\n -------------------- NO '
                                                      'CAPTURE SOURCE EXISTS -----'
                                                      '--------------- \n\n No '
                                                      'capture source with this '
                                                      'capture source group and '
                                                      'external id'
                                                      )
                self.bulk_lf.error_dialog.show()
                self.bulk_lf.db.rollback_open_cursor()
                return
            else:
                capture_source = value[0][0]
        else:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s AND cs.external_source_id is Null;'
            result = self.bulk_lf.db.execute_no_commit(sql,
                                               data=(capture_source_group,))
            value = result.fetchall()
            if len(value) == 0:
                self.bulk_lf.error_dialog = ErrorDialog()
                self.bulk_lf.error_dialog.fill_report('\n -------------------- NO '
                                                      'CAPTURE SOURCE EXISTS ------'
                                                      '-------------- \n\n No capture '
                                                      'source with this capture source'
                                                      ' group and a Null external id'
                                                      )
                self.bulk_lf.error_dialog.show()
                self.bulk_lf.db.rollback_open_cursor()
                return
            else:
                capture_source = value[0][0]
        # iterate through outlines in map layer
        external_field = str(self.bulk_lf.fcb_external_id.currentField())
        for outline in layer.getFeatures():
            wkt = outline.geometry().exportToWkt()
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.bulk_lf.db.execute_no_commit(sql, data=(wkt, ))
            geom = result.fetchall()[0][0]
            # suburb
            sql = 'SELECT buildings.suburb_locality_intersect_polygon(%s);'
            result = self.bulk_lf.db.execute_no_commit(sql, (geom, ))
            suburb = result.fetchall()[0][0]
            # town city
            sql = 'SELECT buildings.town_city_intersect_polygon(%s);'
            result = self.bulk_lf.db.execute_no_commit(sql, (geom, ))
            town_city = result.fetchall()[0][0]
            # Territorial Authority
            sql = 'SELECT buildings.territorial_authority_intersect_polygon(%s);'
            result = self.bulk_lf.db.execute_no_commit(sql, (geom, ))
            territorial_authority = result.fetchall()[0][0]
            if suburb is None:
                self.bulk_lf.error_dialog = ErrorDialog()
                self.bulk_lf.error_dialog.fill_report('\n -------------------- No '
                                                      'Suburb Admin Boundary ------'
                                                      '-------------- \n\n Data will'
                                                      ' not be added to table as has '
                                                      'null suburb Id')
                self.bulk_lf.error_dialog.show()
                self.bulk_lf.db.rollback_open_cursor()
                return
            if territorial_authority is None:
                self.bulk_lf.error_dialog = ErrorDialog()
                self.bulk_lf.error_dialog.fill_report('\n -------------------- No '
                                                      'TA Admin Boundary ------'
                                                      '-------------- \n\n Data will'
                                                      ' not be added to table as has '
                                                      'null TA Id'
                                                      )
                self.bulk_lf.error_dialog.show()
                self.bulk_lf.db.rollback_open_cursor()
                return
            self.bulk_lf.inserted_values = self.bulk_lf.inserted_values + 1
            # insert outline into buildings_bulk_load.supplied_outline
            if external_source_id is None:
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 1, %s, %s, %s, %s, %s, %s);'
                self.bulk_lf.db.execute_no_commit(sql, (dataset_id, capture_method,
                                                        capture_source, suburb,
                                                        town_city,
                                                        territorial_authority,
                                                        geom))
            else:
                external_id = outline.attribute(external_field)
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, 1, %s, %s, %s, %s, %s, %s);'
                self.bulk_lf.db.execute_no_commit(sql, (dataset_id, external_id,
                                                        capture_method, capture_source,
                                                        suburb, town_city,
                                                        territorial_authority,
                                                        geom))
        self.bulk_lf.le_data_description.clear()
        # returns 1 if function worked None if failed
        return 1
