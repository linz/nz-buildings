# -*- coding: utf-8 -*-

import os

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QToolButton
from qgis.core import QgsFeatureRequest, QgsGeometry, QgsMapLayerRegistry
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import select_statements as select


class BulkLoadChanges:
    """
        Parent class of bulk Load changes (editing and adding outlines)
    """

    def __init__(self, bulk_load_frame):
        """Constructor."""
        # setup
        self.bulk_load_frame = bulk_load_frame
        iface.setActiveLayer(self.bulk_load_frame.bulk_load_layer)
        iface.actionToggleEditing().trigger()

    def populate_edit_comboboxes(self):
        """
            Populate editing combox fields
        """
        # bulk load status
        if self.bulk_load_frame.rad_edit.isChecked():
            result = self.bulk_load_frame.db._execute(select.bulk_load_status_value)
            ls = result.fetchall()
            for item in ls:
                self.bulk_load_frame.cmb_status.addItem(item[0])

        # populate capture method combobox
        result = self.bulk_load_frame.db._execute(select.capture_method_value)
        ls = result.fetchall()
        for item in ls:
            self.bulk_load_frame.cmb_capture_method_2.addItem(item[0])

        # populate capture source group
        result = self.bulk_load_frame.db._execute(select.capture_source_group_value_desc_external)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
            self.bulk_load_frame.cmb_capture_source.addItem(text)

        # populate territorial authority combobox
        result = self.bulk_load_frame.db._execute(
            select.territorial_authority_intersect_geom,
            (self.bulk_load_frame.geom,)
        )
        self.bulk_load_frame.ids_ta = []
        for (id_ta, name) in result.fetchall():
            self.bulk_load_frame.cmb_ta.addItem(name)
            self.bulk_load_frame.ids_ta.append(id_ta)

        # populate suburb combobox
        result = self.bulk_load_frame.db._execute(
            select.suburb_locality_intersect_geom,
            (self.bulk_load_frame.geom,)
        )
        self.bulk_load_frame.ids_suburb = []
        for (id_suburb, name) in result.fetchall():
            if name is not None:
                self.bulk_load_frame.cmb_suburb.addItem(name)
                self.bulk_load_frame.ids_suburb.append(id_suburb)

        # populate town combobox
        result = self.bulk_load_frame.db._execute(
            select.town_city_intersect_geom,
            (self.bulk_load_frame.geom,)
        )
        self.bulk_load_frame.cmb_town.addItem('')
        self.bulk_load_frame.ids_town = [None]
        for (id_town, name) in result.fetchall():
            if name is not None:
                self.bulk_load_frame.cmb_town.addItem(name)
                self.bulk_load_frame.ids_town.append(id_town)

    def get_comboboxes_values(self):

        # bulk load status
        if self.bulk_load_frame.rad_edit.isChecked():
            text = self.bulk_load_frame.cmb_status.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.bulk_load_status_id_by_value, (text,))
            bulk_load_status_id = result.fetchall()[0][0]
        else:
            bulk_load_status_id = None

        # capture method id
        text = self.bulk_load_frame.cmb_capture_method_2.currentText()
        result = self.bulk_load_frame.db.execute_no_commit(
            select.capture_method_ID_by_value, (text,))
        capture_method_id = result.fetchall()[0][0]

        # capture source
        text = self.bulk_load_frame.cmb_capture_source.currentText()
        # if there are no capture source entries
        if text == '':
            self.bulk_load_frame.error_dialog = ErrorDialog()
            self.bulk_load_frame.error_dialog.fill_report(
                '\n ---------------- NO CAPTURE SOURCE ---------'
                '------- \n\nThere are no capture source entries'
            )
            self.bulk_load_frame.error_dialog.show()
            self.disable_UI_functions()
            return
        text_ls = text.split('- ')
        result = self.bulk_load_frame.db.execute_no_commit(
            select.capture_srcgrp_by_value_and_description, (
                text_ls[0], text_ls[1]
            ))
        data = result.fetchall()[0][0]
        if text_ls[2] == 'None':
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrdID_is_null, (data,))
        else:
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrpID_and_externalSrcID, (
                    data, text_ls[2]
                ))
        capture_source_id = result.fetchall()[0][0]

        # suburb
        index = self.bulk_load_frame.cmb_suburb.currentIndex()
        suburb = self.bulk_load_frame.ids_suburb[index]

        # town
        index = self.bulk_load_frame.cmb_town.currentIndex()
        town = self.bulk_load_frame.ids_town[index]

        # territorial Authority
        index = self.bulk_load_frame.cmb_ta.currentIndex()
        t_a = self.bulk_load_frame.ids_ta[index]

        return bulk_load_status_id, capture_method_id, capture_source_id, suburb, town, t_a

    def enable_UI_functions(self):
        """
            Function called when comboboxes are to be enabled
        """
        self.bulk_load_frame.cmb_status.clear()
        if self.bulk_load_frame.rad_edit.isChecked():
            self.bulk_load_frame.cmb_status.setEnabled(1)
        self.bulk_load_frame.cmb_capture_method_2.clear()
        self.bulk_load_frame.cmb_capture_method_2.setEnabled(1)
        self.bulk_load_frame.cmb_capture_source.clear()
        self.bulk_load_frame.cmb_capture_source.setEnabled(1)
        self.bulk_load_frame.cmb_ta.clear()
        self.bulk_load_frame.cmb_ta.setEnabled(1)
        self.bulk_load_frame.cmb_town.clear()
        self.bulk_load_frame.cmb_town.setEnabled(1)
        self.bulk_load_frame.cmb_suburb.clear()
        self.bulk_load_frame.cmb_suburb.setEnabled(1)
        self.bulk_load_frame.btn_edit_save.setEnabled(1)
        self.bulk_load_frame.btn_edit_reset.setEnabled(1)
        self.bulk_load_frame.btn_edit_cancel.setEnabled(1)

    def disable_UI_functions(self):
        """
            Function called when comboboxes are to be disabled
        """
        self.bulk_load_frame.cmb_status.clear()
        self.bulk_load_frame.cmb_status.setDisabled(1)
        self.bulk_load_frame.cmb_capture_method_2.clear()
        self.bulk_load_frame.cmb_capture_method_2.setDisabled(1)
        self.bulk_load_frame.cmb_capture_source.clear()
        self.bulk_load_frame.cmb_capture_source.setDisabled(1)
        self.bulk_load_frame.le_deletion_reason.setDisabled(1)
        self.bulk_load_frame.cmb_ta.clear()
        self.bulk_load_frame.cmb_ta.setDisabled(1)
        self.bulk_load_frame.cmb_town.clear()
        self.bulk_load_frame.cmb_town.setDisabled(1)
        self.bulk_load_frame.cmb_suburb.clear()
        self.bulk_load_frame.cmb_suburb.setDisabled(1)
        self.bulk_load_frame.btn_edit_save.setDisabled(1)
        self.bulk_load_frame.btn_edit_reset.setDisabled(1)


class AddBulkLoad(BulkLoadChanges):
    """
        Class to add outlines to buildings_bulk_load.bulk_load_outlines
        Inherits BulkLoadChanges
    """

    def __init__(self, bulk_load_frame):
        """Constructor"""
        BulkLoadChanges.__init__(self, bulk_load_frame)
        # set editing to add polygon
        iface.actionAddFeature().trigger()
        # setup toolbar
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == 'Select Feature(s)':
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # editing actions
        iface.building_toolbar.addSeparator()
        for dig in iface.digitizeToolBar().actions():
            if dig.objectName() in [
                'mActionAddFeature'
            ]:
                iface.building_toolbar.addAction(dig)
        # advanced Actions
        iface.building_toolbar.addSeparator()
        for adv in iface.advancedDigitizeToolBar().actions():
            if adv.objectName() in [
                'mActionUndo', 'mActionRedo'
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

    @pyqtSlot(bool)
    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.bulk_load_frame.db.open_cursor()

        _, capture_method_id, capture_source_id, suburb, town, t_a = self.get_comboboxes_values()

        # insert into bulk_load_outlines table
        sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s);'
        result = self.bulk_load_frame.db.execute_no_commit(
            sql, (self.bulk_load_frame.current_dataset, capture_method_id,
                  capture_source_id, suburb, town, t_a,
                  self.bulk_load_frame.geom)
        )
        self.bulk_load_frame.outline_id = result.fetchall()[0][0]

        # insert into added table
        result = self.bulk_load_frame.db._execute(
            select.dataset_processed_date_by_datasetID, (
                self.bulk_load_frame.current_dataset, )
        )
        processed_date = result.fetchall()[0][0]

        if processed_date:
            sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 1);'
            self.bulk_load_frame.db.execute_no_commit(
                sql, (self.bulk_load_frame.outline_id,))

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles/')
        self.bulk_load_frame.layer_registry.remove_layer(
            QgsMapLayerRegistry.instance().mapLayersByName('added_outlines')[0])
        self.bulk_load_frame.bulk_load_added = self.bulk_load_frame.layer_registry.add_postgres_layer(
            'added_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0} AND bulk_load_status_id = 2'.format(self.bulk_load_frame.current_dataset))
        self.bulk_load_frame.bulk_load_added.loadNamedStyle(path + 'building_green.qml')
        if commit_status:
            self.bulk_load_frame.db.commit_open_cursor()

        # reset and disable comboboxes
        self.disable_UI_functions()

        self.bulk_load_frame.geom = None
        self.bulk_load_frame.added_building_ids = []

    @pyqtSlot()
    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        iface.actionCancelEdits().trigger()
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()
        # reset and disable comboboxes
        self.disable_UI_functions()

        self.bulk_load_frame.geom = None
        self.bulk_load_frame.added_building_ids = []

    @pyqtSlot(int)
    def creator_feature_added(self, qgsfId):
        """
           Called when feature is added
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId not in self.bulk_load_frame.added_building_ids:
            self.bulk_load_frame.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.bulk_load_frame.bulk_load_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = self.bulk_load_frame.db._execute(sql, (wkt,))
        self.bulk_load_frame.geom = result.fetchall()[0][0]
        # enable & populate comboboxes
        self.enable_UI_functions()
        self.populate_edit_comboboxes()
        self.select_comboboxes_value()

    @pyqtSlot(int)
    def creator_feature_deleted(self, qgsfId):
        """
            Called when a Feature is Deleted
            @param qgsfId:      Id of deleted feature
            @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.bulk_load_frame.added_building_ids:
            self.bulk_load_frame.added_building_ids.remove(qgsfId)
            if self.bulk_load_frame.added_building_ids == []:
                self.disable_UI_functions()
                self.bulk_load_frame.geom = None

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # capture method
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(
            self.bulk_load_frame.cmb_capture_method_2.findText('Trace Orthophotography'))

        # territorial authority
        sql = 'SELECT buildings.territorial_authority_intersect_polygon(%s);'
        result = self.bulk_load_frame.db._execute(sql,
                                                  (self.bulk_load_frame.geom,))
        index = self.bulk_load_frame.ids_ta.index(result.fetchall()[0][0])
        self.bulk_load_frame.cmb_ta.setCurrentIndex(index)

        # town locality
        sql = 'SELECT buildings.town_city_intersect_polygon(%s);'
        result = self.bulk_load_frame.db._execute(sql,
                                                  (self.bulk_load_frame.geom,))
        index = self.bulk_load_frame.ids_town.index(result.fetchall()[0][0])
        self.bulk_load_frame.cmb_town.setCurrentIndex(index)

        # suburb locality
        sql = 'SELECT buildings.suburb_locality_intersect_polygon(%s);'
        result = self.bulk_load_frame.db._execute(sql,
                                                  (self.bulk_load_frame.geom,))
        index = self.bulk_load_frame.ids_suburb.index(result.fetchall()[0][0])
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(index)


class EditBulkLoad(BulkLoadChanges):
    """
        Class to edit outlines in buildings_bulk_load.bulk_load_outlines
        Inherits BulkLoadChanges
    """

    def __init__(self, bulk_load_frame):
        """Constructor"""
        BulkLoadChanges.__init__(self, bulk_load_frame)
        # set editing to edit polygon
        iface.actionNodeTool().trigger()
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == 'Select Feature(s)':
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # editing actions
        iface.building_toolbar.addSeparator()
        for dig in iface.digitizeToolBar().actions():
            if dig.objectName() in [
                'mActionNodeTool', 'mActionMoveFeature'
            ]:
                iface.building_toolbar.addAction(dig)
        # advanced Actions
        iface.building_toolbar.addSeparator()
        for adv in iface.advancedDigitizeToolBar().actions():
            if adv.objectName() in [
                'mActionUndo', 'mActionRedo',
                'mActionReshapeFeatures', 'mActionOffsetCurve'
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

        self.bulk_load_frame.select_changed = False
        if len(iface.activeLayer().selectedFeatures()) > 0:
            self.select_features()
            if self.bulk_load_frame.select_changed:
                self.populate_edit_comboboxes()
                self.select_comboboxes_value()

    @pyqtSlot(bool)
    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.bulk_load_frame.btn_edit_save.setDisabled(1)
        self.bulk_load_frame.btn_edit_reset.setDisabled(1)
        self.bulk_load_frame.db.open_cursor()
        # if only geometries are changed
        if self.bulk_load_frame.geom_changed:
            for key in self.bulk_load_frame.geoms:
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_shape(%s, %s);'
                self.bulk_load_frame.db.execute_no_commit(
                    sql, (self.bulk_load_frame.geoms[key], key))
        # if only attributes are changed
        if self.bulk_load_frame.select_changed:

            bulk_load_status_id, capture_method_id, capture_source_id, suburb, town, t_a = self.get_comboboxes_values()

            # bulk load status
            ls_relationships = {'added': [], 'matched': [], 'related': []}
            if self.bulk_load_frame.cmb_status.currentText() == 'Deleted During QA':
                # can only delete outlines if no relationship
                self.bulk_load_frame.description_del = self.bulk_load_frame.le_deletion_reason.text()
                if len(self.bulk_load_frame.description_del) == 0:
                    self.bulk_load_frame.error_dialog = ErrorDialog()
                    self.bulk_load_frame.error_dialog.fill_report(
                        '\n -------------------- EMPTY VALUE FIELD ------'
                        '-------------- \n\n There are no "reason for deletion" entries '
                    )
                    self.bulk_load_frame.error_dialog.show()
                    self.disable_UI_functions()
                    return
                ls_relationships = self.remove_compared_outlines()
                if len(ls_relationships['matched']) == 0 and len(ls_relationships['related']) == 0:
                    if len(self.bulk_load_frame.ids) > 0:
                        for i in self.bulk_load_frame.ids:
                            sql = 'SELECT buildings_bulk_load.deletion_description_insert(%s, %s);'
                            self.bulk_load_frame.db.execute_no_commit(sql, (i, self.bulk_load_frame.description_del))
                            # remove outline from added table
                            sql = 'SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);'
                            self.bulk_load_frame.db.execute_no_commit(sql, (i,))
                            sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                            self.bulk_load_frame.db.execute_no_commit(
                                sql, (i, bulk_load_status_id, capture_method_id,
                                      capture_source_id, suburb, town, t_a))
                        self.bulk_load_frame.bulk_load_layer.removeSelection()
            else:
                for i in self.bulk_load_frame.ids:
                    # change attributes
                    sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                    self.bulk_load_frame.db.execute_no_commit(
                        sql, (i, bulk_load_status_id, capture_method_id,
                              capture_source_id, suburb, town, t_a))
            self.disable_UI_functions()
            self.bulk_load_frame.completer_box()
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles/')
        self.bulk_load_frame.layer_registry.remove_layer(
            QgsMapLayerRegistry.instance().mapLayersByName('removed_outlines')[0])
        self.bulk_load_frame.bulk_load_removed = self.bulk_load_frame.layer_registry.add_postgres_layer(
            'removed_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0} AND bulk_load_status_id = 3'.format(
                self.bulk_load_frame.current_dataset
            ))
        self.bulk_load_frame.bulk_load_removed.loadNamedStyle(
            path + 'building_red.qml')
        if commit_status:
            self.bulk_load_frame.db.commit_open_cursor()
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.ids = []
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False

    @pyqtSlot()
    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        iface.actionCancelEdits().trigger()
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.ids = []
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionNodeTool().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        self.disable_UI_functions()

    @pyqtSlot(int, QgsGeometry)
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
        result = self.bulk_load_frame.db._execute(sql, (wkt,))
        self.bulk_load_frame.geom = result.fetchall()[0][0]
        result = self.bulk_load_frame.db._execute(
            select.bulk_load_outline_shape_by_id, (qgsfId,))
        result = result.fetchall()[0][0]
        if self.bulk_load_frame.geom == result:
            if qgsfId in self.bulk_load_frame.geoms.keys():
                del self.bulk_load_frame.geoms[qgsfId]
        else:
            self.bulk_load_frame.geoms[qgsfId] = self.bulk_load_frame.geom
        self.bulk_load_frame.geom_changed = True
        self.bulk_load_frame.btn_edit_save.setEnabled(1)
        self.bulk_load_frame.btn_edit_reset.setEnabled(1)
        self.bulk_load_frame.btn_edit_cancel.setEnabled(1)

    @pyqtSlot(list, list, bool)
    def selection_changed(self, added, removed, cleared):
        """
           Called when feature is selected
        """
        # If no outlines are selected the function will return
        self.bulk_load_frame.select_changed = False
        if len(self.bulk_load_frame.bulk_load_layer.selectedFeatures()) == 0:
            self.bulk_load_frame.ids = []
            self.bulk_load_frame.building_outline_id = None
            self.disable_UI_functions()
            return
        self.select_features()
        if self.bulk_load_frame.select_changed:
            self.populate_edit_comboboxes()
            self.select_comboboxes_value()

    def select_features(self):
        self.bulk_load_frame.ids = [feat.id() for feat in self.bulk_load_frame.bulk_load_layer.selectedFeatures()]
        self.bulk_load_frame.bulk_load_outline_id = self.bulk_load_frame.ids[0]
        bulk_load_feat = [feat for feat in self.bulk_load_frame.bulk_load_layer.selectedFeatures()][0]
        bulk_load_geom = bulk_load_feat.geometry()
        # convert to correct format
        wkt = bulk_load_geom.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = self.bulk_load_frame.db._execute(sql, (wkt,))
        self.bulk_load_frame.geom = result.fetchall()[0][0]

        feats = []
        for feature in self.bulk_load_frame.bulk_load_layer.selectedFeatures():
            ls = []
            ls.append(feature.attributes()[3])
            ls.append(feature.attributes()[4])
            ls.append(feature.attributes()[5])
            ls.append(feature.attributes()[6])
            ls.append(feature.attributes()[7])
            ls.append(feature.attributes()[8])
            if ls not in feats:
                feats.append(ls)
        # if selected features have different attributes (not allowed)
        if len(feats) > 1:
            self.bulk_load_frame.error_dialog = ErrorDialog()
            self.bulk_load_frame.error_dialog.fill_report(
                '\n ---- MULTIPLE NON IDENTICAL FEATURES SELEC'
                'TED ---- \n\n Can only edit attributes of mul'
                'tiple features when all existing attributes a'
                're identical.'
            )
            self.bulk_load_frame.error_dialog.show()
            self.disable_UI_functions()
            self.bulk_load_frame.select_changed = False
        # if all selected features have the same attributes (allowed)
        elif len(feats) == 1:
            deleted = False
            for feature in self.bulk_load_frame.bulk_load_layer.selectedFeatures():
                sql = 'SELECT bulk_load_status_id from buildings_bulk_load.bulk_load_outlines WHERE bulk_load_outline_id = %s'
                result = self.bulk_load_frame.db._execute(sql, (feature['bulk_load_outline_id'], ))
                bl_status = result.fetchall()[0][0]
                if bl_status == 3:
                    deleted = True
            if deleted:
                self.bulk_load_frame.error_dialog = ErrorDialog()
                self.bulk_load_frame.error_dialog.fill_report(
                    '\n ---- SELECTED A DELETED FEATURE ---- \n\n'
                    'Can only edit attributes of'
                    ' features that have not been deleted.'
                )
                self.bulk_load_frame.error_dialog.show()
                self.bulk_load_frame.ids = []
                self.bulk_load_frame.building_outline_id = None
                self.disable_UI_functions()
                self.bulk_load_frame.select_changed = False
            else:
                self.enable_UI_functions()
                self.bulk_load_frame.select_changed = True

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # bulk load status
        result = self.bulk_load_frame.db._execute(
            select.bulk_load_status_value_by_outlineID, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.bulk_load_frame.cmb_status.setCurrentIndex(
            self.bulk_load_frame.cmb_status.findText(result))

        # capture method
        result = self.bulk_load_frame.db._execute(
            select.capture_method_value_by_bulk_outlineID, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(
            self.bulk_load_frame.cmb_capture_method_2.findText(result))

        # capture source
        result = self.bulk_load_frame.db._execute(
            select.capture_source_group_value_desc_external)
        ls = result.fetchall()
        result = self.bulk_load_frame.db._execute(
            select.capture_source_group_value_desc_external_by_bulk_outlineID, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()[0]
        value_index = 0
        for index, item in enumerate(ls):
            if item == result:
                value_index = index
        self.bulk_load_frame.cmb_capture_source.setCurrentIndex(
            value_index)

        # suburb
        result = self.bulk_load_frame.db._execute(
            select.suburb_locality_suburb_4th_by_bulk_outlineID, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(
            self.bulk_load_frame.cmb_suburb.findText(result))

        # town city
        result = self.bulk_load_frame.db._execute(
            select.town_city_name_by_bulk_outlineID, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()
        if result:
            self.bulk_load_frame.cmb_town.setCurrentIndex(
                self.bulk_load_frame.cmb_town.findText(result[0][0]))
        else:
            self.bulk_load_frame.cmb_town.setCurrentIndex(0)

        # territorial Authority
        result = self.bulk_load_frame.db._execute(
            select.territorial_authority_name_by_bulk_outline_id, (
                self.bulk_load_frame.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.bulk_load_frame.cmb_ta.setCurrentIndex(
            self.bulk_load_frame.cmb_ta.findText(result))

    def remove_compared_outlines(self):
        """
            called to check can mark outline for deletion
        """
        added_outlines = self.bulk_load_frame.db.execute_no_commit(
            select.current_added_outlines, (
                self.bulk_load_frame.current_dataset,))
        added_outlines = added_outlines.fetchall()
        matched_outlines = self.bulk_load_frame.db.execute_no_commit(
            select.current_matched_outlines, (
                self.bulk_load_frame.current_dataset,))
        matched_outlines = matched_outlines.fetchall()
        related_outlines = self.bulk_load_frame.db.execute_no_commit(
            select.current_related_outlines, (
                self.bulk_load_frame.current_dataset,))
        related_outlines = related_outlines.fetchall()
        if len(self.bulk_load_frame.ids) > 0:
            # if there is more than one feature to update
            ls_relationships = {'added': [], 'matched': [], 'related': []}
            for item in self.bulk_load_frame.ids:
                # added
                if (item, ) in added_outlines:
                    ls_relationships['added'].append(item)
                # matched
                if (item, ) in matched_outlines:
                    self.bulk_load_frame.error_dialog = ErrorDialog()
                    self.bulk_load_frame.error_dialog.fill_report(
                        '\n --------------- RELATIONSHIP EXISTS ---------'
                        '-------\n\nCan only mark for deletion outline if'
                        ' no relationship exists'
                    )
                    self.bulk_load_frame.error_dialog.show()
                    ls_relationships['matched'].append(item)
                    break
                # related
                if (item, ) in related_outlines:
                    self.bulk_load_frame.error_dialog = ErrorDialog()
                    self.bulk_load_frame.error_dialog.fill_report(
                        '\n ------------------- RELATIONSHIP EXISTS ---------'
                        '---------- \n\nCan only mark for deletion outline if'
                        ' no relationship exists'
                    )
                    self.bulk_load_frame.error_dialog.show()
                    ls_relationships['related'].append(item)
                    break
        return ls_relationships
