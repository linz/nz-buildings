# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_bulk_load_select_statements as bulk_load_select,
                           buildings_common_select_statements as common_select,
                           general_select_statements as general_select)


def populate_bulk_comboboxes(self):
    """
        Populate bulk load comboboxes
    """
    # organisation combobox
    self.cmb_organisation.clear()
    result = self.db._execute(bulk_load_select.organisation_value)
    ls = result.fetchall()
    for item in ls:
        self.cmb_organisation.addItem(item[0])

    # capture method combobox
    self.cmb_capture_method.clear()
    result = self.db._execute(common_select.capture_method_value)
    ls = result.fetchall()
    for item in ls:
        self.cmb_capture_method.addItem(item[0])

    # capture source group
    self.cmb_capture_src_grp.clear()
    self.ids_capture_src_grp = []
    result = self.db._execute(common_select.capture_source_group_id_value_description)
    ls = result.fetchall()
    for (id_capture_src_grp, value, description) in ls:
        text = str(value) + '- ' + str(description)
        self.cmb_capture_src_grp.addItem(text)
        self.ids_capture_src_grp.append(id_capture_src_grp)

    # capture source area combobox
    self.cmb_cap_src_area.clear()
    index = self.cmb_capture_src_grp.currentIndex()
    id_capture_src_grp = self.ids_capture_src_grp[index]
    result = self.db._execute(common_select.capture_source_external_id_and_area_title_by_group_id, (id_capture_src_grp, ))
    ls = result.fetchall()
    for (external_id, area_title) in reversed(ls):
        text = external_id + '- ' + area_title
        self.cmb_cap_src_area.addItem(text)


def load_current_fields(self):
    """
        Function to load fields related to the current supplied dataset
    """
    # capture method
    result = self.db._execute(
        common_select.capture_method_value_by_dataset_id, (
            self.current_dataset,)
    )
    result = result.fetchall()[0][0]
    self.cmb_capture_method.setCurrentIndex(
        self.cmb_capture_method.findText(result))

    # organisation
    result = self.db._execute(
        bulk_load_select.organisation_value_by_dataset_id, (self.current_dataset,))
    result = result.fetchall()[0][0]
    self.cmb_organisation.setCurrentIndex(
        self.cmb_organisation.findText(result))

    # data description
    result = self.db._execute(
        bulk_load_select.supplied_dataset_description_by_dataset_id, (self.current_dataset,))
    result = result.fetchall()[0][0]
    self.le_data_description.setText(result)

    # External Id/fields
    ex_result = self.db._execute(
        common_select.capture_source_external_source_id_by_dataset_id, (self.current_dataset,))
    ex_result = ex_result.fetchall()[0][0]
    if ex_result is not None:
        self.rad_external_id.setChecked(True)
        self.cmb_cap_src_area.setCurrentIndex(
            self.cmb_cap_src_area.findText(ex_result))

    # capture source group
    result = self.db._execute(
        common_select.capture_source_group_id_by_dataset_id, (
            self.current_dataset,))
    result = result.fetchall()[0][0]
    self.cmb_capture_src_grp.setCurrentIndex(result - 1)

    # outlines layer
    self.ml_outlines_layer.setCurrentIndex(
        self.ml_outlines_layer.findText('bulk_load_outlines'))


@pyqtSlot()
def enable_external_bulk(self):
    """
        Called when external source radio button is toggled
    """
    if self.rad_external_id.isChecked():
        self.fcb_external_id.setEnabled(1)
        self.fcb_external_id.setLayer(
            self.ml_outlines_layer.currentLayer())

    else:
        self.fcb_external_id.setDisabled(1)
        self.fcb_external_id.setLayer(None)


def populate_external_fcb(self):
    """
        Populate external field combobox
    """
    self.fcb_external_id.setLayer(
        self.ml_outlines_layer.currentLayer())


def bulk_load(self, commit_status):
    """
        Begins the process of bulk load data into buildings_bulk_load.
        bulk_load_outlines Called when bulk load outlines ok button
        is clicked
    """
    if self.le_data_description.text() == '':
        # if no data description
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------------- EMPTY DESCRIPTION FIELD ---------'
            '----------- \n\n Null descriptions not allowed'
        )
        self.error_dialog.show()
        return
    if len(self.le_data_description.text()) >= 40:
        # if description is too long
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------------- VALUE TOO LONG -------------------- '
            '\n\n Enter less than 250 characters'
        )
        self.error_dialog.show()
        return

    # description
    description = self.le_data_description.text()

    # organisation
    text = self.cmb_organisation.currentText()
    result = self.db._execute(bulk_load_select.organisation_id_by_value, (text,))
    organisation = result.fetchall()[0][0]

    # capture method
    text = self.cmb_capture_method.currentText()
    result = self.db._execute(common_select.capture_method_id_by_value, (text,))
    capture_method = result.fetchall()[0][0]

    # capture source group
    text = self.cmb_capture_src_grp.currentText()
    text_ls = text.split('-')
    result = self.db._execute(
        common_select.capture_source_group_id_by_value, (text_ls[0],))
    capture_source_group = result.fetchall()[0][0]

    # capture source area

    if self.cmb_cap_src_area.count() == 0:
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------- NO CAPTURE SOURCE ENTRY EXISTS-------'
            '-------- \n\nPlease create capture source entries for the '
            'capture source group first.'
        )
        self.error_dialog.show()
        return
    text = str(self.cmb_cap_src_area.currentText())
    external_source_id = text.split('- ')[0]

    # capture source
    result = self.db._execute(
        common_select.capture_source_id_by_capture_source_group_id_and_external_source_id, (
            capture_source_group, external_source_id,
        ))
    capture_source = result.fetchall()
    if len(capture_source) == 0:
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------------- NO CAPTURE SOURCE EXISTS------------'
            '-------- \n\nCapture source entry is not exist, please check.'
        )
        self.error_dialog.show()
        return
    capture_source = capture_source[0][0]

    # if user checks radio button then does not enter a field, error
    if self.fcb_external_id.currentField() is None and self.rad_external_id.isChecked():
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------------- NO EXTERNAL ID FIELD-------------'
            '------- \n\nPlease either uncheck the radio button or enter'
            ' an external id field'
        )
        self.error_dialog.show()
        return

    # bulk load Layer
    bulk_load_layer = self.ml_outlines_layer.currentLayer()
    if bulk_load_layer.crs().authid() != 'EPSG:2193':
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n -------------------- INCORRECT CRS-------------'
            '------- \n\nThe Coordinate Reference System is not NTZM 2000. '
            'Please resolve and reattempt.'
        )
        self.error_dialog.show()
        return

    # Generate new Supplied Dataset
    self.current_dataset = insert_supplied_dataset(
        self, organisation, description,)
    self.lb_dataset_id.setText(str(self.current_dataset))

    # Bulk Load Outlines
    val = insert_supplied_outlines(
        self, self.current_dataset, bulk_load_layer)
    # if insert_bulk_load_outlines function failed
    if val is None:
        return

    val = insert_bulk_load_outlines(
        self, self.current_dataset, capture_method, capture_source)
    # if insert_bulk_load_outlines function failed
    if val is None:
        return

    if commit_status:
        self.db.commit_open_cursor()


def insert_supplied_dataset(self, organisation, description):
    """
        Generates new supplied outline dataset for incoming data
    """
    if self.db._open_cursor is None:
        self.db.open_cursor()
    sql = 'SELECT buildings_bulk_load.supplied_datasets_insert(%s, %s);'
    results = self.db.execute_no_commit(
        sql, (description, organisation))
    return results.fetchall()[0][0]


def insert_supplied_outlines(self, dataset_id, layer):
    """
        Inserts new outlines into buildings_bulk_load.supplied_outlines table
    """
    # external field
    external_field = str(self.fcb_external_id.currentField())

    # iterate through outlines in map layer
    for outline in layer.getFeatures():
        # outline geometry
        wkt = outline.geometry().exportToWkt()
        sql = general_select.convert_geometry
        result = self.db.execute_no_commit(sql, (wkt, ))
        geom = result.fetchall()[0][0]

        # insert outlines
        if external_field is '':
            # if no external field
            sql = 'SELECT buildings_bulk_load.supplied_outlines_insert(%s, NULL, %s);'
            self.db.execute_no_commit(
                sql, (dataset_id, geom))
        else:
            # if external field
            external_id = outline.attribute(external_field)
            sql = 'SELECT buildings_bulk_load.supplied_outlines_insert(%s, %s, %s);'
            self.db.execute_no_commit(
                sql, (dataset_id, external_id, geom))

    # return 1 if function worked
    return 1


def insert_bulk_load_outlines(self, dataset_id, capture_method, capture_source):
    """
        Inserts new outlines into buildings_bulk_load.bulk_load_outlines table
    """
    sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert_supplied(%s, 1, %s, %s);'
    self.db.execute_no_commit(
        sql, (dataset_id, capture_method, capture_source))

    # Remove small buildings

    sql = 'SELECT buildings_bulk_load.bulk_load_outlines_remove_small_buildings(%s);'
    self.db.execute_no_commit(sql, (dataset_id, ))
    # insert into deletion_description
    results = self.db.execute_no_commit(
        bulk_load_select.bulk_load_removed_outline_ids_by_dataset_id, (dataset_id,))
    bulk_loaded_ids = results.fetchall()
    for bulk_loaded_id in bulk_loaded_ids:
        sql = 'SELECT buildings_bulk_load.deletion_description_insert(%s, %s);'
        self.db.execute_no_commit(sql, (bulk_loaded_id, 'Building outlines smaller than 10m2'))

    self.le_data_description.clear()
    # return 1 if function worked
    return 1
