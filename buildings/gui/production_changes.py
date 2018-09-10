# -*- coding: utf-8 -*-

from PyQt4.QtGui import QToolButton

from qgis.core import QgsFeatureRequest
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import select_statements as select


class ProductionChanges:
    """
        Parent class of Production changes (editing and adding outlines)
    """

    def __init__(self, production_frame):
        """Constructor."""
        # setup
        self.production_frame = production_frame
        iface.setActiveLayer(self.production_frame.building_layer)
        iface.actionToggleEditing().trigger()

    def populate_edit_comboboxes(self):
        """
            Populate editing combox fields
        """
        # populate capture method combobox
        result = self.production_frame.db._execute(select.capture_method_value)
        ls = result.fetchall()
        for item in ls:
            self.production_frame.cmb_capture_method.addItem(item[0])

        # populate capture source group
        result = self.production_frame.db._execute(select.capture_source_group_value_desc_external)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
            self.production_frame.cmb_capture_source.addItem(text)

        # populate lifecycle stage combobox
        result = self.production_frame.db._execute(select.lifecycle_stage_value)
        ls = result.fetchall()
        for item in ls:
            self.production_frame.cmb_lifecycle_stage.addItem(item[0])

        # populate suburb combobox
        result = self.production_frame.db._execute(select.suburb_locality_suburb_4th)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.production_frame.cmb_suburb.addItem(item[0])

        # populate town combobox
        result = self.production_frame.db._execute(select.town_city_name)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.production_frame.cmb_town.addItem(item[0])

        # populate territorial authority combobox
        result = self.production_frame.db._execute(select.territorial_authority_name)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.production_frame.cmb_ta.addItem(item[0])
        # set to currently selected outline
        if self.production_frame.rad_edit.isChecked():
            # lifeycle stage
            result = self.production_frame.db._execute(
                select.lifecycle_stage_value_by_outlineID, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0][0]
            self.production_frame.cmb_lifecycle_stage.setCurrentIndex(
                self.production_frame.cmb_lifecycle_stage.findText(result))

            # capture method
            result = self.production_frame.db._execute(
                select.capture_method_value_by_building_outlineID, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0][0]
            self.production_frame.cmb_capture_method.setCurrentIndex(
                self.production_frame.cmb_capture_method.findText(result))

            # capture source
            result = self.production_frame.db._execute(
                select.capture_source_group_value_desc_external)
            ls = result.fetchall()
            result = self.production_frame.db._execute(
                select.capture_source_group_value_desc_external_by_building_outlineID, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0]
            value_index = 0
            for index, item in enumerate(ls):
                if item == result:
                    value_index = index
            self.production_frame.cmb_capture_source.setCurrentIndex(
                value_index)

            # suburb
            result = self.production_frame.db._execute(
                select.suburb_locality_suburb_4th_by_building_outlineID, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0][0]
            self.production_frame.cmb_suburb.setCurrentIndex(
                self.production_frame.cmb_suburb.findText(result))

            # town city
            result = self.production_frame.db._execute(
                select.town_city_name_by_building_outlineID, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0][0]
            self.production_frame.cmb_town.setCurrentIndex(
                self.production_frame.cmb_town.findText(result))

            # territorial Authority
            result = self.production_frame.db._execute(
                select.territorial_authority_name_by_building_outline_id, (
                    self.production_frame.building_outline_id,
                ))
            result = result.fetchall()[0][0]
            self.production_frame.cmb_ta.setCurrentIndex(
                self.production_frame.cmb_ta.findText(result))

    def enable_UI_functions(self):
        """
            Function called when comboboxes are to be enabled
        """
        self.production_frame.cmb_capture_method.setEnabled(1)
        self.production_frame.cmb_capture_source.setEnabled(1)
        self.production_frame.cmb_lifecycle_stage.setEnabled(1)
        self.production_frame.cmb_capture_method.clear()
        self.production_frame.cmb_capture_source.clear()
        self.production_frame.cmb_lifecycle_stage.clear()
        self.production_frame.cmb_ta.setEnabled(1)
        self.production_frame.cmb_town.setEnabled(1)
        self.production_frame.cmb_suburb.setEnabled(1)
        self.production_frame.cmb_ta.clear()
        self.production_frame.cmb_town.clear()
        self.production_frame.cmb_suburb.clear()
        self.populate_edit_comboboxes()

    def disable_UI_functions(self):
        """
            Function called when comboboxes are to be disabled
        """
        self.production_frame.cmb_capture_method.clear()
        self.production_frame.cmb_capture_method.setDisabled(1)
        self.production_frame.cmb_capture_source.clear()
        self.production_frame.cmb_capture_source.setDisabled(1)
        self.production_frame.cmb_lifecycle_stage.clear()
        self.production_frame.cmb_lifecycle_stage.setDisabled(1)
        self.production_frame.cmb_ta.clear()
        self.production_frame.cmb_ta.setDisabled(1)
        self.production_frame.cmb_town.clear()
        self.production_frame.cmb_town.setDisabled(1)
        self.production_frame.cmb_suburb.clear()
        self.production_frame.cmb_suburb.setDisabled(1)
        self.production_frame.btn_save.setDisabled(1)
        self.production_frame.btn_reset.setDisabled(1)


class AddProduction(ProductionChanges):
    """
        Class to add outlines to buildings.building_outlines
        Inherits ProductionChanges
    """

    def __init__(self, production_frame):
        """Constructor"""
        ProductionChanges.__init__(self, production_frame)
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

    def save_clicked(self, commit_status):
        """
            When building frame btn_save clicked
        """
        self.production_frame.db.open_cursor()
        # capture method id
        text = self.production_frame.cmb_capture_method.currentText()
        result = self.production_frame.db.execute_no_commit(
            select.capture_method_ID_by_value, (text,))
        capture_method_id = result.fetchall()[0][0]

        # capture source
        text = self.production_frame.cmb_capture_source.currentText()
        # if there are no capture source entries
        if text == '':
            self.production_frame.error_dialog = ErrorDialog()
            self.production_frame.error_dialog.fill_report(
                '\n ---------------- NO CAPTURE SOURCE ---------'
                '------- \n\nThere are no capture source entries'
            )
            self.production_frame.error_dialog.show()
            return
        text_ls = text.split('- ')
        result = self.production_frame.db.execute_no_commit(
            select.capture_srcgrp_by_value_and_description, (
                text_ls[0], text_ls[1]
            ))
        data = result.fetchall()[0][0]
        if text_ls[2] == 'None':
            result = self.production_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrdID_is_null, (data,))
        else:
            result = self.production_frame.db.execute_no_commit(
                select.capture_source_ID_by_capsrcgrpID_and_externalSrcID, (
                    data, text_ls[2]
                ))
        capture_source_id = result.fetchall()[0][0]

        # lifecycle stage
        text = self.production_frame.cmb_lifecycle_stage.currentText()
        result = self.production_frame.db.execute_no_commit(
            select.lifecycle_stage_ID_by_value, (text,))
        lifecycle_stage_id = result.fetchall()[0][0]

        # suburb
        text = self.production_frame.cmb_suburb.currentText()
        result = self.production_frame.db.execute_no_commit(
            select.suburb_locality_id_by_suburb_4th, (text,))
        suburb = result.fetchall()[0][0]

        # town
        text = self.production_frame.cmb_town.currentText()
        result = self.production_frame.db.execute_no_commit(
            select.town_city_ID_by_name, (text,))
        town = result.fetchall()[0][0]

        # territorial Authority
        text = self.production_frame.cmb_ta.currentText()
        result = self.production_frame.db.execute_no_commit(
            select.territorial_authority_ID_by_name, (text,))
        t_a = result.fetchall()[0][0]

        # insert into buildings
        sql = 'SELECT buildings.buildings_insert();'
        building_id = self.production_frame.db.execute_no_commit(sql)
        building_id = result.fetchall()[0][0]
        # insert into building_outlines table
        sql = 'SELECT buildings.building_outlines_insert(%s, %s, %s, %s, %s, %s, %s, now()::timestamp, %s);'
        result = self.production_frame.db.execute_no_commit(
            sql, (building_id, capture_method_id,
                  capture_source_id, lifecycle_stage_id,
                  suburb, town, t_a,
                  self.production_frame.geom)
        )
        self.production_frame.outline_id = result.fetchall()[0][0]

        if commit_status:
            self.production_frame.db.commit_open_cursor()

        # reset comboboxes for next outline
        self.production_frame.cmb_capture_method.setCurrentIndex(0)
        self.production_frame.cmb_capture_method.setDisabled(1)
        self.production_frame.cmb_capture_source.setCurrentIndex(0)
        self.production_frame.cmb_capture_source.setDisabled(1)
        self.production_frame.cmb_lifecycle_stage.setDisabled(1)
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(0)
        self.production_frame.cmb_ta.setCurrentIndex(0)
        self.production_frame.cmb_ta.setDisabled(1)
        self.production_frame.cmb_town.setCurrentIndex(0)
        self.production_frame.cmb_town.setDisabled(1)
        self.production_frame.cmb_suburb.setCurrentIndex(0)
        self.production_frame.cmb_suburb.setDisabled(1)
        self.production_frame.btn_save.setDisabled(1)
        self.production_frame.btn_reset.setDisabled(1)

    def reset_clicked(self):
        """
            When production frame btn_reset clicked
        """
        iface.actionCancelEdits().trigger()
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()
        # reset and disable comboboxes
        ProductionChanges.disable_UI_functions(self)

    def creator_feature_added(self, qgsfId):
        """
           Called when feature is added
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId not in self.production_frame.added_building_ids:
            self.production_frame.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.production_frame.building_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = self.production_frame.db._execute(sql, (wkt,))
        self.production_frame.geom = result.fetchall()[0][0]
        # enable & populate comboboxes
        self.populate_edit_comboboxes()
        self.production_frame.cmb_capture_method.setEnabled(1)
        self.production_frame.cmb_capture_source.setEnabled(1)
        self.production_frame.cmb_lifecycle_stage.setEnabled(1)
        # territorial authority
        sql = 'SELECT buildings.territorial_authority_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        ta = self.production_frame.db._execute(
            select.territorial_authority_name_by_id,
            (result.fetchall()[0][0],)
        )
        self.production_frame.cmb_ta.setCurrentIndex(
            self.production_frame.cmb_ta.findText(ta.fetchall()[0][0]))
        self.production_frame.cmb_ta.setEnabled(1)
        # town locality
        sql = 'SELECT buildings.town_city_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        town = self.production_frame.db._execute(
            select.town_city_name_by_id,
            (result.fetchall()[0][0],)
        )
        self.production_frame.cmb_town.setCurrentIndex(
            self.production_frame.cmb_town.findText(town.fetchall()[0][0]))
        self.production_frame.cmb_town.setEnabled(1)
        # suburb locality
        sql = 'SELECT buildings.suburb_locality_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        suburb = self.production_frame.db._execute(
            select.suburb_locality_suburb_4th_by_id,
            (result.fetchall()[0][0],)
        )
        self.production_frame.cmb_suburb.setCurrentIndex(
            self.production_frame.cmb_suburb.findText(suburb.fetchall()[0][0]))
        self.production_frame.cmb_suburb.setEnabled(1)
        # enable save
        self.production_frame.btn_save.setEnabled(1)
        self.production_frame.btn_reset.setEnabled(1)

    def creator_feature_deleted(self, qgsfId):
        """
            Called when a Feature is Deleted
            @param qgsfId:      Id of deleted feature
            @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.production_frame.added_building_ids:
            self.production_frame.added_building_ids.remove(qgsfId)
            if self.production_frame.added_building_ids == []:
                self.production_frame.cmb_capture_method.setDisabled(1)
                self.production_frame.cmb_capture_source.setDisabled(1)
                self.production_frame.cmb_lifecycle_stage.setDisabled(1)
                self.production_frame.cmb_ta.setDisabled(1)
                self.production_frame.cmb_town.setDisabled(1)
                self.production_frame.cmb_suburb.setDisabled(1)
                # disable save
                self.production_frame.btn_save.setDisabled(1)
                self.production_frame.btn_reset.setDisabled(1)


class EditProduction(ProductionChanges):
    """
        Class to edit outlines in buildings.building_outlines
        Inherits ProductionChanges
    """

    def __init__(self, production_frame):
        """Constructor"""
        ProductionChanges.__init__(self, production_frame)
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
        if len(self.production_frame.building_layer.selectedFeatures()) > 0:
            if len(self.production_frame.building_layer.selectedFeatures()) == 1:
                # ProductionChanges.enable_UI_functions(self)
                self.production_frame.building_outline_id = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()][0]
                self.enable_UI_functions()
                # enable save and reset
                self.production_frame.btn_save.setEnabled(1)
                self.production_frame.btn_reset.setEnabled(1)
                self.production_frame.select_changed = True
                self.production_frame.ids = []
            # if more than one outline is selected
            if len(self.production_frame.building_layer.selectedFeatures()) > 1:
                feats = []
                self.production_frame.ids = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()]
                for feature in self.production_frame.building_layer.selectedFeatures():
                    ls = []
                    ls.append(feature.attributes()[2])
                    ls.append(feature.attributes()[3])
                    ls.append(feature.attributes()[4])
                    ls.append(feature.attributes()[5])
                    ls.append(feature.attributes()[6])
                    ls.append(feature.attributes()[7])
                    if ls not in feats:
                        feats.append(ls)
                # if selected features have different attributes (not allowed)
                if len(feats) > 1:
                    self.production_frame.error_dialog = ErrorDialog()
                    self.production_frame.error_dialog.fill_report(
                        '\n ---- MULTIPLE NON IDENTICAL FEATURES SELEC'
                        'TED ---- \n\n Can only edit attributes of mul'
                        'tiple features when all existing attributes a'
                        're identical.'
                    )
                    self.production_frame.error_dialog.show()
                    self.production_frame.building_outline_id = None
                    self.disable_UI_functions()
                    self.production_frame.select_changed = False
                # if all selected features have the same attributes (allowed)
                elif len(feats) == 1:
                    self.production_frame.building_outline_id = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()][0]
                    self.enable_UI_functions()
                    # enable save and reset
                    self.production_frame.btn_save.setEnabled(1)
                    self.production_frame.btn_reset.setEnabled(1)
                    self.production_frame.select_changed = True

    def save_clicked(self, commit_status):
        """
            When production frame btn_save clicked
        """
        self.production_frame.btn_save.setDisabled(1)
        self.production_frame.btn_reset.setDisabled(1)
        self.production_frame.db.open_cursor()
        # if only geometries are changed
        if self.production_frame.geom_changed:
            for key in self.production_frame.geoms:
                sql = 'SELECT buildings.building_outlines_update_shape(%s, %s);'
                self.production_frame.db.execute_no_commit(
                    sql, (self.production_frame.geoms[key], key))
        # if only attributes are changed
        if self.production_frame.select_changed:
            # lifecycle stage
            text = self.production_frame.cmb_lifecycle_stage.currentText()
            result = self.production_frame.db.execute_no_commit(
                select.lifecycle_stage_ID_by_value, (text,))
            lifecycle_stage_id = result.fetchall()[0][0]

            # capture method
            text = self.production_frame.cmb_capture_method.currentText()
            result = self.production_frame.db.execute_no_commit(
                select.capture_method_ID_by_value, (text,))
            capture_method_id = result.fetchall()[0][0]

            # capture source
            text = self.production_frame.cmb_capture_source.currentText()
            if text == '':
                self.production_frame.error_dialog = ErrorDialog()
                self.production_frame.error_dialog.fill_report(
                    '\n ---------------- NO CAPTURE SOURCE -----------'
                    '-----\n\n There are no capture source entries.'
                )
                self.production_frame.error_dialog.show()
                self.disable_UI_functions()
                return
            text_ls = text.split('- ')
            result = self.production_frame.db.execute_no_commit(
                select.capture_srcgrp_by_value_and_description, (
                    text_ls[0], text_ls[1]
                ))
            data = result.fetchall()[0][0]
            if text_ls[2] == 'None':
                result = self.production_frame.db.execute_no_commit(
                    select.capture_source_ID_by_capsrcgrdID_is_null, (
                        data,
                    ))
            else:
                result = self.production_frame.db.execute_no_commit(
                    select.capture_source_ID_by_capsrcgrpID_and_externalSrcID,
                    (data, text_ls[2])
                )
            capture_source_id = result.fetchall()[0][0]

            # suburb
            text = self.production_frame.cmb_suburb.currentText()
            result = self.production_frame.db.execute_no_commit(
                select.suburb_locality_id_by_suburb_4th, (text,))
            suburb = result.fetchall()[0][0]

            # town
            text = self.production_frame.cmb_town.currentText()
            result = self.production_frame.db.execute_no_commit(
                select.town_city_ID_by_name, (text,))
            town = result.fetchall()[0][0]

            # territorial authority
            text = self.production_frame.cmb_ta.currentText()
            result = self.production_frame.db.execute_no_commit(
                select.territorial_authority_ID_by_name, (text,))
            t_a = result.fetchall()[0][0]

            if len(self.production_frame.ids) > 0:
                # if there is more than one feature to update
                for i in self.production_frame.ids:
                    sql = 'SELECT buildings.building_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                    self.production_frame.db.execute_no_commit(
                        sql, (i, capture_method_id,
                              capture_source_id, lifecycle_stage_id,
                              suburb, town, t_a))
            else:
                # one feature to update
                sql = 'SELECT buildings.building_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                self.production_frame.db.execute_no_commit(
                    sql, (self.production_frame.building_outline_id,
                          capture_method_id, capture_source_id,
                          lifecycle_stage_id, suburb, town, t_a)
                )
            self.disable_UI_functions()

        if commit_status:
            self.production_frame.geoms = {}
            self.production_frame.ids = []
            self.production_frame.geom_changed = False
            self.production_frame.select_changed = False
            self.production_frame.db.commit_open_cursor()

    def reset_clicked(self):
        """
            When production frame btn_reset clicked
        """
        iface.actionCancelEdits().trigger()
        self.production_frame.geoms = {}
        self.production_frame.geom_changed = False
        self.production_frame.select_changed = False
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionNodeTool().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        ProductionChanges.disable_UI_functions(self)

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
        result = self.production_frame.db._execute(sql, (wkt,))
        self.production_frame.geom = result.fetchall()[0][0]
        result = self.production_frame.db._execute(
            select.building_outline_shape_by_id, (qgsfId,))
        result = result.fetchall()[0][0]
        if self.production_frame.geom == result:
            if qgsfId in self.production_frame.geoms.keys():
                del self.production_frame.geoms[qgsfId]
        else:
            self.production_frame.geoms[qgsfId] = self.production_frame.geom
        self.production_frame.geom_changed = True
        self.production_frame.btn_save.setEnabled(1)
        self.production_frame.btn_reset.setEnabled(1)

    def selection_changed(self, added, removed, cleared):
        """
           Called when feature is selected
        """
        # if only one outline is selected
        if len(self.production_frame.building_layer.selectedFeatures()) == 1:
            # ProductionChanges.enable_UI_functions(self)
            self.production_frame.building_outline_id = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()][0]
            ProductionChanges.enable_UI_functions(self)
            # enable save and reset
            self.production_frame.btn_save.setEnabled(1)
            self.production_frame.btn_reset.setEnabled(1)
            self.production_frame.select_changed = True
            self.production_frame.ids = []
        # if more than one outline is selected
        if len(self.production_frame.building_layer.selectedFeatures()) > 1:
            feats = []
            self.production_frame.ids = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()]
            for feature in self.production_frame.building_layer.selectedFeatures():
                ls = []
                ls.append(feature.attributes()[2])
                ls.append(feature.attributes()[3])
                ls.append(feature.attributes()[4])
                ls.append(feature.attributes()[5])
                ls.append(feature.attributes()[6])
                ls.append(feature.attributes()[7])
                if ls not in feats:
                    feats.append(ls)
            # if selected features have different attributes (not allowed)
            if len(feats) > 1:
                self.production_frame.error_dialog = ErrorDialog()
                self.production_frame.error_dialog.fill_report(
                    '\n ---- MULTIPLE NON IDENTICAL FEATURES SELEC'
                    'TED ---- \n\n Can only edit attributes of mul'
                    'tiple features when all existing attributes a'
                    're identical.'
                )
                self.production_frame.error_dialog.show()
                self.production_frame.building_outline_id = None
                ProductionChanges.disable_UI_functions(self)
                self.production_frame.select_changed = False
            # if all selected features have the same attributes (allowed)
            elif len(feats) == 1:
                self.production_frame.building_outline_id = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()][0]
                ProductionChanges.enable_UI_functions(self)
                # enable save and reset
                self.production_frame.btn_save.setEnabled(1)
                self.production_frame.btn_reset.setEnabled(1)
                self.production_frame.select_changed = True
        # if no outlines are selected
        if len(self.production_frame.building_layer.selectedFeatures()) == 0:
            self.production_frame.building_outline_id = None
            ProductionChanges.disable_UI_functions(self)
            self.production_frame.select_changed = False
