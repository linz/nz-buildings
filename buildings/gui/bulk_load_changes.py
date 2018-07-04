from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import select_statements as select

from qgis.core import QgsFeatureRequest
from qgis.utils import iface

from PyQt4.QtGui import QToolButton


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

    def edit_cancel_clicked(self):
        """
            When cancel clicked
        """
        iface.actionCancelEdits().trigger()
        # deselect both comboboxes
        self.bulk_load_frame.rad_edit.setAutoExclusive(False)
        self.bulk_load_frame.rad_edit.setChecked(False)
        self.bulk_load_frame.rad_edit.setAutoExclusive(True)
        self.bulk_load_frame.rad_add.setAutoExclusive(False)
        self.bulk_load_frame.rad_add.setChecked(False)
        self.bulk_load_frame.rad_add.setAutoExclusive(True)
        # reload layers
        self.bulk_load_frame.layer_registry.remove_all_layers()
        self.bulk_load_frame.add_outlines()
        # disable comboboxes
        self.bulk_load_frame.cmb_status.setDisabled(1)
        self.bulk_load_frame.cmb_capture_method_2.setDisabled(1)
        self.bulk_load_frame.cmb_capture_source.setDisabled(1)
        self.bulk_load_frame.cmb_ta.setDisabled(1)
        self.bulk_load_frame.cmb_town.setDisabled(1)
        self.bulk_load_frame.cmb_suburb.setDisabled(1)
        self.bulk_load_frame.btn_edit_reset.setDisabled(1)
        self.bulk_load_frame.btn_edit_save.setDisabled(1)
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

    def populate_edit_comboboxes(self):
        """
            Populate editing combox fields
        """
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

        # populate suburb combobox
        result = self.bulk_load_frame.db._execute(select.suburb_locality_suburb_4th)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.bulk_load_frame.cmb_suburb.addItem(item[0])

        # populate town combobox
        result = self.bulk_load_frame.db._execute(select.town_city_name)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.bulk_load_frame.cmb_town.addItem(item[0])

        # populate territorial authority combobox
        result = self.bulk_load_frame.db._execute(select.territorial_authority_name)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.bulk_load_frame.cmb_ta.addItem(item[0])

        # set to currently selected outline
        if self.bulk_load_frame.rad_edit.isChecked():
            # bulk load status
            result = self.bulk_load_frame.db._execute(select.bulk_load_status_value)
            ls = result.fetchall()
            for item in ls:
                self.bulk_load_frame.cmb_status.addItem(item[0])
            result = self.bulk_load_frame.db._execute(
                select.bulk_load_status_value_by_outlineID.format(
                    self.bulk_load_frame.bulk_load_outline_id
                ))
            result = result.fetchall()[0][0]
            self.bulk_load_frame.cmb_status.setCurrentIndex(
                self.bulk_load_frame.cmb_status.findText(result))

            # capture method
            result = self.bulk_load_frame.db._execute(
                select.capture_method_value_by_bulk_outlineID.format(
                    self.bulk_load_frame.bulk_load_outline_id
                ))
            result = result.fetchall()[0][0]
            self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(
                self.bulk_load_frame.cmb_capture_method_2.findText(result))

            # capture source
            result = self.bulk_load_frame.db._execute(
                select.capture_source_group_value_desc_external)
            ls = result.fetchall()
            result = self.bulk_load_frame.db._execute(
                select.capture_source_group_value_desc_external_by_bulk_outlineID.format(
                    self.bulk_load_frame.bulk_load_outline_id
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
                select.suburb_locality_suburb_4th_by_bulk_outlineID.format(
                    self.bulk_load_frame.bulk_load_outline_id
                ))
            result = result.fetchall()[0][0]
            self.bulk_load_frame.cmb_suburb.setCurrentIndex(
                self.bulk_load_frame.cmb_suburb.findText(result))

            # town city
            result = self.bulk_load_frame.db._execute(
                select.town_city_name_by_bulk_outlineID.format(
                    self.bulk_load_frame.bulk_load_outline_id
                ))
            result = result.fetchall()[0][0]
            self.bulk_load_frame.cmb_town.setCurrentIndex(
                self.bulk_load_frame.cmb_town.findText(result))

            # territorial Authority
            result = self.bulk_load_frame.db._execute(
                select.territorial_authority_name_by_bulk_outline_id.format(
                    self.bulk_load_frame.bulk_load_outline_id
                ))
            result = result.fetchall()[0][0]
            self.bulk_load_frame.cmb_ta.setCurrentIndex(
                self.bulk_load_frame.cmb_ta.findText(result))

    def enable_UI_functions(self):
        """
            Function called when comboboxes are to be enabled
        """
        self.bulk_load_frame.bulk_load_outline_id = [feat.id() for feat in self.bulk_load_frame.bulk_load_layer.selectedFeatures()][0]
        self.bulk_load_frame.cmb_capture_method_2.setEnabled(1)
        self.bulk_load_frame.cmb_capture_source.setEnabled(1)
        self.bulk_load_frame.cmb_status.setEnabled(1)
        self.bulk_load_frame.cmb_capture_method_2.clear()
        self.bulk_load_frame.cmb_capture_source.clear()
        self.bulk_load_frame.cmb_status.clear()
        self.bulk_load_frame.cmb_ta.setEnabled(1)
        self.bulk_load_frame.cmb_town.setEnabled(1)
        self.bulk_load_frame.cmb_suburb.setEnabled(1)
        self.bulk_load_frame.cmb_ta.clear()
        self.bulk_load_frame.cmb_town.clear()
        self.bulk_load_frame.cmb_suburb.clear()
        self.populate_edit_comboboxes()

    def disbale_UI_functions(self):
        """
            Function called when comboboxes are to be disabled
        """
        self.bulk_load_frame.cmb_capture_method_2.clear()
        self.bulk_load_frame.cmb_capture_method_2.setDisabled(1)
        self.bulk_load_frame.cmb_capture_source.clear()
        self.bulk_load_frame.cmb_capture_source.setDisabled(1)
        self.bulk_load_frame.cmb_status.clear()
        self.bulk_load_frame.cmb_status.setDisabled(1)
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
            if sel.text() == "Select Feature(s)":
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # editing actions
        iface.building_toolbar.addSeparator()
        for dig in iface.digitizeToolBar().actions():
            if dig.objectName() in [
                "mActionAddFeature"
            ]:
                iface.building_toolbar.addAction(dig)
        # advanced Actions
        iface.building_toolbar.addSeparator()
        for adv in iface.advancedDigitizeToolBar().actions():
            if adv.objectName() in [
                "mActionUndo", "mActionRedo"
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.bulk_load_frame.db.open_cursor()
        # capture method id
        text = self.bulk_load_frame.cmb_capture_method_2.currentText()
        result = self.bulk_load_frame.db.execute_no_commit(
            select.capture_method_ID_by_value.format(text))
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
            return
        text_ls = text.split('- ')
        result = self.bulk_load_frame.db.execute_no_commit(
            select.capture_srcgrp_by_value_and_description.format(
                text_ls[0], text_ls[1]
            ))
        data = result.fetchall()[0][0]
        if text_ls[2] == 'None':
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrdID_is_null.format(data))
        else:
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrpID_and_externalSrcID.format(
                    data, text_ls[2]
                ))
        capture_source_id = result.fetchall()[0][0]

        # suburb
        text = self.bulk_load_frame.cmb_suburb.currentText()
        result = self.bulk_load_frame.db.execute_no_commit(
            select.suburb_locality_id_by_suburb_4th.format(text))
        suburb = result.fetchall()[0][0]

        # town
        text = self.bulk_load_frame.cmb_town.currentText()
        result = self.bulk_load_frame.db.execute_no_commit(select.town_city_ID_by_name.format(text))
        town = result.fetchall()[0][0]

        # territorial Authority
        text = self.bulk_load_frame.cmb_ta.currentText()
        result = self.bulk_load_frame.db.execute_no_commit(
            select.territorial_authority_ID_by_name.format(text))
        t_a = result.fetchall()[0][0]

        # insert into bulk_load_outlines table
        sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s);'
        result = self.bulk_load_frame.db.execute_no_commit(
            sql, (self.bulk_load_frame.current_dataset, capture_method_id,
                  capture_source_id, suburb, town, t_a,
                  self.bulk_load_frame.geom)
        )
        self.bulk_load_frame.outline_id = result.fetchall()[0][0]
        # insert into added table
        sql = 'INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id) VALUES(%s, 2);'
        self.bulk_load_frame.db.execute_no_commit(
            sql, (self.bulk_load_frame.outline_id,))

        if commit_status:
            self.bulk_load_frame.db.commit_open_cursor()

        # reset comboboxes for next outline
        self.bulk_load_frame.cmb_capture_method_2.setCurrentIndex(0)
        self.bulk_load_frame.cmb_capture_method_2.setDisabled(1)
        self.bulk_load_frame.cmb_capture_source.setCurrentIndex(0)
        self.bulk_load_frame.cmb_capture_source.setDisabled(1)
        self.bulk_load_frame.cmb_ta.setCurrentIndex(0)
        self.bulk_load_frame.cmb_ta.setDisabled(1)
        self.bulk_load_frame.cmb_town.setCurrentIndex(0)
        self.bulk_load_frame.cmb_town.setDisabled(1)
        self.bulk_load_frame.cmb_suburb.setCurrentIndex(0)
        self.bulk_load_frame.cmb_suburb.setDisabled(1)
        self.bulk_load_frame.btn_edit_save.setDisabled(1)
        self.bulk_load_frame.btn_edit_reset.setDisabled(1)

    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        iface.actionCancelEdits().trigger()
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()
        # reset and disable comboboxes
        BulkLoadChanges.disbale_UI_functions(self)

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
        # enable comboboxes
        self.bulk_load_frame.cmb_capture_method_2.setEnabled(1)
        self.bulk_load_frame.cmb_capture_source.setEnabled(1)
        self.bulk_load_frame.cmb_ta.setEnabled(1)
        self.bulk_load_frame.cmb_town.setEnabled(1)
        self.bulk_load_frame.cmb_suburb.setEnabled(1)
        # enable save
        self.bulk_load_frame.btn_edit_save.setEnabled(1)
        self.bulk_load_frame.btn_edit_reset.setEnabled(1)
        self.populate_edit_comboboxes()

    def creator_feature_deleted(self, qgsfId):
        """
            Called when a Feature is Deleted
            @param qgsfId:      Id of deleted feature
            @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.bulk_load_frame.added_building_ids:
            self.bulk_load_frame.added_building_ids.remove(qgsfId)
            if self.bulk_load_frame.added_building_ids == []:
                self.bulk_load_frame.cmb_capture_method_2.setDisabled(1)
                self.bulk_load_frame.cmb_capture_source.setDisabled(1)
                self.bulk_load_frame.cmb_ta.setDisabled(1)
                self.bulk_load_frame.cmb_town.setDisabled(1)
                self.bulk_load_frame.cmb_suburb.setDisabled(1)
                # disable save
                self.bulk_load_frame.btn_edit_save.setDisabled(1)
                self.bulk_load_frame.btn_edit_reset.setDisabled(1)


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
            if sel.text() == "Select Feature(s)":
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # editing actions
        iface.building_toolbar.addSeparator()
        for dig in iface.digitizeToolBar().actions():
            if dig.objectName() in [
                "mActionNodeTool", "mActionMoveFeature"
            ]:
                iface.building_toolbar.addAction(dig)
        # advanced Actions
        iface.building_toolbar.addSeparator()
        for adv in iface.advancedDigitizeToolBar().actions():
            if adv.objectName() in [
                "mActionUndo", "mActionRedo",
                "mActionReshapeFeatures", "mActionOffsetCurve"
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

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
            # bulk load status
            text = self.bulk_load_frame.cmb_status.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.bulk_load_status_id_by_value.format(text))
            bulk_load_status_id = result.fetchall()[0][0]

            # capture method
            text = self.bulk_load_frame.cmb_capture_method_2.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_method_ID_by_value.format(text))
            capture_method_id = result.fetchall()[0][0]

            # capture source
            text = self.bulk_load_frame.cmb_capture_source.currentText()
            if text == '':
                self.bulk_load_frame.error_dialog = ErrorDialog()
                self.bulk_load_frame.error_dialog.fill_report(
                    '\n ---------------- NO CAPTURE SOURCE -----------'
                    '-----\n\n There are no capture source entries.'
                )
                self.bulk_load_frame.error_dialog.show()
                return
            text_ls = text.split('- ')
            result = self.bulk_load_frame.db.execute_no_commit(
                select.capture_srcgrp_by_value_and_description.format(
                    text_ls[0], text_ls[1]
                ))
            data = result.fetchall()[0][0]
            if text_ls[2] == 'None':
                result = self.bulk_load_frame.db.execute_no_commit(
                    select.capture_source_ID_by_capsrcgrdID_is_null.format(
                        data
                    ))
            else:
                result = self.bulk_load_frame.db.execute_no_commit(
                    select.capture_source_ID_by_capsrcgrpID_and_externalSrcID.format(data, text_ls[2]))
            capture_source_id = result.fetchall()[0][0]

            # suburb
            text = self.bulk_load_frame.cmb_suburb.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.suburb_locality_id_by_suburb_4th.format(text))
            suburb = result.fetchall()[0][0]

            # town
            text = self.bulk_load_frame.cmb_town.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.town_city_ID_by_name.format(text))
            town = result.fetchall()[0][0]

            # territorial authority
            text = self.bulk_load_frame.cmb_ta.currentText()
            result = self.bulk_load_frame.db.execute_no_commit(
                select.territorial_authority_ID_by_name.format(text))
            t_a = result.fetchall()[0][0]
            if len(self.bulk_load_frame.ids) > 0:
                # if there is more than one feature to update
                for i in self.bulk_load_frame.ids:
                    sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                    self.bulk_load_frame.db.execute_no_commit(
                        sql, (i, bulk_load_status_id, capture_method_id,
                              capture_source_id, suburb, town, t_a))
            else:
                # one feature to update
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                self.bulk_load_frame.db.execute_no_commit(
                    sql, (self.bulk_load_frame.bulk_load_outline_id,
                          bulk_load_status_id, capture_method_id,
                          capture_source_id, suburb, town, t_a)
                )
        if commit_status:
            self.bulk_load_frame.geoms = {}
            self.bulk_load_frame.ids = []
            self.bulk_load_frame.geom_changed = False
            self.bulk_load_frame.select_changed = False
            self.bulk_load_frame.db.commit_open_cursor()

    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        iface.actionCancelEdits().trigger()
        self.bulk_load_frame.geoms = {}
        self.bulk_load_frame.geom_changed = False
        self.bulk_load_frame.select_changed = False
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionNodeTool().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        BulkLoadChanges.disbale_UI_functions(self)

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
            select.bulk_load_outline_shape_by_id.format(qgsfId))
        result = result.fetchall()[0][0]
        if self.bulk_load_frame.geom == result:
            if qgsfId in self.bulk_load_frame.geoms.keys():
                del self.bulk_load_frame.geoms[qgsfId]
        else:
            self.bulk_load_frame.geoms[qgsfId] = self.bulk_load_frame.geom
        self.bulk_load_frame.geom_changed = True
        self.bulk_load_frame.btn_edit_save.setEnabled(1)
        self.bulk_load_frame.btn_edit_reset.setEnabled(1)

    def selection_changed(self, added, removed, cleared):
        """
           Called when feature is selected
        """
        # if only one outline is selected
        if len(self.bulk_load_frame.bulk_load_layer.selectedFeatures()) == 1:
            BulkLoadChanges.enable_UI_functions(self)
            # enable save and reset
            self.bulk_load_frame.btn_edit_save.setEnabled(1)
            self.bulk_load_frame.btn_edit_reset.setEnabled(1)
            self.bulk_load_frame.select_changed = True
        # if more than one outline is selected
        if len(self.bulk_load_frame.bulk_load_layer.selectedFeatures()) > 1:
            feats = []
            self.bulk_load_frame.ids = [feat.id() for feat in self.bulk_load_frame.bulk_load_layer.selectedFeatures()]
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
                self.bulk_load_frame.bulk_load_outline_id = None
                BulkLoadChanges.disbale_UI_functions(self)
                self.bulk_load_frame.select_changed = False
                iface.activeLayer().removeSelection()
            # if all selected features have the same attributes (allowed)
            elif len(feats) == 1:
                BulkLoadChanges.enable_UI_functions(self)
                # enable save and reset
                self.bulk_load_frame.btn_edit_save.setEnabled(1)
                self.bulk_load_frame.btn_edit_reset.setEnabled(1)
                self.bulk_load_frame.select_changed = True
        # If no outlines are selected
        if len(self.bulk_load_frame.bulk_load_layer.selectedFeatures()) == 0:
            self.bulk_load_frame.bulk_load_outline_id = None
            BulkLoadChanges.disbale_UI_functions(self)
            self.bulk_load_frame.select_changed = False
