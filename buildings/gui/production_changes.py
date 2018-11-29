# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QToolButton
from qgis.core import QgsFeatureRequest, QgsGeometry
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_common_select_statements as common_select,
                           buildings_select_statements as buildings_select,
                           buildings_reference_select_statements as reference_select,
                           general_select_statements as general_select)


class ProductionChanges:
    """
        Parent class of Production changes (editing and adding outlines)
    """

    def __init__(self, production_frame):
        """Constructor."""
        # setup
        self.production_frame = production_frame
        iface.setActiveLayer(self.production_frame.building_layer)

    def populate_edit_comboboxes(self):
        """
            Populate editing combox fields
        """
        if self.production_frame.layout_capture_method.isVisible():
            # populate capture method combobox
            result = self.production_frame.db._execute(common_select.capture_method_value)
            ls = result.fetchall()
            for item in ls:
                self.production_frame.cmb_capture_method.addItem(item[0])

        if self.production_frame.layout_general_info.isVisible():
            # populate capture source group
            result = self.production_frame.db._execute(common_select.capture_source_group_value_description_external)
            ls = result.fetchall()
            for item in ls:
                text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
                self.production_frame.cmb_capture_source.addItem(text)

            # populate lifecycle stage combobox
            result = self.production_frame.db._execute(buildings_select.lifecycle_stage_value)
            ls = result.fetchall()
            for item in ls:
                self.production_frame.cmb_lifecycle_stage.addItem(item[0])

            # populate territorial authority combobox
            result = self.production_frame.db._execute(
                reference_select.territorial_authority_intersect_geom,
                (self.production_frame.geom,)
            )
            self.production_frame.ids_ta = []
            for (id_ta, name) in result.fetchall():
                self.production_frame.cmb_ta.addItem(name)
                self.production_frame.ids_ta.append(id_ta)

            # populate suburb combobox
            result = self.production_frame.db._execute(
                reference_select.suburb_locality_intersect_geom,
                (self.production_frame.geom,)
            )
            self.production_frame.ids_suburb = []
            for (id_suburb, name) in result.fetchall():
                if name is not None:
                    self.production_frame.cmb_suburb.addItem(name)
                    self.production_frame.ids_suburb.append(id_suburb)

            # populate town combobox
            result = self.production_frame.db._execute(
                reference_select.town_city_intersect_geometry,
                (self.production_frame.geom,)
            )
            self.production_frame.cmb_town.addItem('')
            self.production_frame.ids_town = [None]
            for (id_town, name) in result.fetchall():
                if name is not None:
                    self.production_frame.cmb_town.addItem(name)
                    self.production_frame.ids_town.append(id_town)

    def get_comboboxes_values(self):
        if self.production_frame.layout_capture_method.isVisible():
            # capture method id
            text = self.production_frame.cmb_capture_method.currentText()
            result = self.production_frame.db.execute_no_commit(
                common_select.capture_method_id_by_value, (text,))
            capture_method_id = result.fetchall()[0][0]
        else:
            capture_method_id = None

        if self.production_frame.layout_general_info.isVisible():
            # capture source
            text = self.production_frame.cmb_capture_source.currentText()
            text_ls = text.split('- ')
            result = self.production_frame.db.execute_no_commit(
                common_select.capture_source_group_by_value_and_description, (
                    text_ls[0], text_ls[1]
                ))
            data = result.fetchall()[0][0]
            if text_ls[2] == 'None':
                result = self.production_frame.db.execute_no_commit(
                    common_select.capture_source_id_by_capture_source_group_id_is_null, (data,))
            else:
                result = self.production_frame.db.execute_no_commit(
                    common_select.capture_source_id_by_capture_source_group_id_and_external_source_id, (
                        data, text_ls[2]
                    ))
            capture_source_id = result.fetchall()[0][0]

            # lifecycle stage
            text = self.production_frame.cmb_lifecycle_stage.currentText()
            result = self.production_frame.db.execute_no_commit(
                buildings_select.lifecycle_stage_id_by_value, (text,))
            lifecycle_stage_id = result.fetchall()[0][0]

            # suburb
            index = self.production_frame.cmb_suburb.currentIndex()
            suburb = self.production_frame.ids_suburb[index]

            # town
            index = self.production_frame.cmb_town.currentIndex()
            town = self.production_frame.ids_town[index]

            # territorial Authority
            index = self.production_frame.cmb_ta.currentIndex()
            t_a = self.production_frame.ids_ta[index]
        else:
            capture_source_id, lifecycle_stage_id, suburb, town, t_a = None, None, None, None, None
        return capture_method_id, capture_source_id, lifecycle_stage_id, suburb, town, t_a

    def enable_UI_functions(self):
        """
            Function called when comboboxes are to be enabled
        """
        self.production_frame.cmb_capture_method.clear()
        self.production_frame.cmb_capture_method.setEnabled(1)
        self.production_frame.cmb_capture_source.clear()
        self.production_frame.cmb_capture_source.setEnabled(1)
        self.production_frame.cmb_lifecycle_stage.clear()
        self.production_frame.cmb_lifecycle_stage.setEnabled(1)
        self.production_frame.cmb_ta.clear()
        self.production_frame.cmb_ta.setEnabled(1)
        self.production_frame.cmb_town.clear()
        self.production_frame.cmb_town.setEnabled(1)
        self.production_frame.cmb_suburb.clear()
        self.production_frame.cmb_suburb.setEnabled(1)
        self.production_frame.btn_save.setEnabled(1)
        self.production_frame.btn_reset.setEnabled(1)

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
        iface.actionToggleEditing().trigger()
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
                'mActionAddFeature', 'mActionNodeTool',
                'mActionMoveFeature'
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
        self.disable_UI_functions()

    @pyqtSlot(bool)
    def save_clicked(self, commit_status):
        """
            When building frame btn_save clicked
        """
        self.production_frame.db.open_cursor()

        capture_method_id, capture_source_id, lifecycle_stage_id, suburb, town, t_a = self.get_comboboxes_values()

        # insert into buildings
        sql = 'SELECT buildings.buildings_insert();'
        result = self.production_frame.db.execute_no_commit(sql)
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
            self.production_frame.geom = None
            self.production_frame.added_building_ids = []
        # reset and disable comboboxes
        self.disable_UI_functions()

    @pyqtSlot()
    def reset_clicked(self):
        """
            When production frame btn_reset clicked
        """
        self.production_frame.building_layer.geometryChanged.disconnect(self.creator_geometry_changed)
        iface.actionCancelEdits().trigger()
        self.production_frame.building_layer.geometryChanged.connect(self.creator_geometry_changed)
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()
        # reset and disable comboboxes
        self.disable_UI_functions()

        self.production_frame.geom = None
        self.production_frame.added_building_ids = []

    @pyqtSlot(int)
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
        sql = general_select.convert_geometry
        result = self.production_frame.db._execute(sql, (wkt,))
        self.production_frame.geom = result.fetchall()[0][0]
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
        if qgsfId in self.production_frame.added_building_ids:
            self.production_frame.added_building_ids.remove(qgsfId)
            if self.production_frame.added_building_ids == []:
                self.disable_UI_functions()
                self.production_frame.geom = None

    @pyqtSlot(int, QgsGeometry)
    def creator_geometry_changed(self, qgsfId, geom):
        """
           Called when feature is changed
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
           @param geom:        geometry of added feature
           @type  geom:        qgis.core.QgsGeometry
        """
        if qgsfId in self.production_frame.added_building_ids:
            wkt = geom.exportToWkt()
            if not wkt:
                self.disable_UI_functions()
                self.production_frame.geom = None
                return
            sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);'
            result = self.production_frame.db._execute(sql, (wkt,))
            self.production_frame.geom = result.fetchall()[0][0]
        else:
            self.production_frame.error_dialog = ErrorDialog()
            self.production_frame.error_dialog.fill_report(
                '\n -------------------- WRONG GEOMETRY EDITED ------'
                '-------------- \n\nOnly current added outline can '
                'be edited. Please go to [Edit Geometry] to edit '
                'existing outlines.'
            )
            self.production_frame.error_dialog.show()

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # capture method
        self.production_frame.cmb_capture_method.setCurrentIndex(
            self.production_frame.cmb_capture_method.findText('Trace Orthophotography'))

        # capture source
        result = self.production_frame.db._execute(reference_select.capture_source_area_intersect_geom,
                                                   (self.production_frame.geom,))
        result = result.fetchall()
        if len(result) == 0:
            iface.messageBar().pushMessage(
                'Capture Source',
                'The new outline overlaps with no capture source area, please manually choose one.',
                level=QgsMessageBar.WARNING,
                duration=10
            )
        elif len(result) > 1:
            iface.messageBar().pushMessage(
                'Capture Source',
                'The new outline overlaps with multiple capture source areas, please manually choose one.',
                level=QgsMessageBar.WARNING,
                duration=10
            )
        else:
            for index in range(self.production_frame.cmb_capture_source.count()):
                text = self.production_frame.cmb_capture_source.itemText(index)
                if int(text.split('-')[-1]) == result[0][0]:
                    break
            self.production_frame.cmb_capture_source.setCurrentIndex(index)

        # territorial authority
        sql = 'SELECT buildings_reference.territorial_authority_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        index = self.production_frame.ids_ta.index(result.fetchall()[0][0])
        self.production_frame.cmb_ta.setCurrentIndex(index)

        # town locality
        sql = 'SELECT buildings_reference.town_city_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        index = self.production_frame.ids_town.index(result.fetchall()[0][0])
        self.production_frame.cmb_town.setCurrentIndex(index)

        # suburb locality
        sql = 'SELECT buildings_reference.suburb_locality_intersect_polygon(%s);'
        result = self.production_frame.db._execute(sql,
                                                   (self.production_frame.geom,))
        index = self.production_frame.ids_suburb.index(result.fetchall()[0][0])
        self.production_frame.cmb_suburb.setCurrentIndex(index)


class EditAttribute(ProductionChanges):
    """
        Class to edit attributes in buildings.building_outlines
        Inherits ProductionChanges
    """

    def __init__(self, production_frame):
        """Constructor"""
        ProductionChanges.__init__(self, production_frame)
        # set editing to edit polygon
        iface.actionSelect().trigger()
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == 'Select Feature(s)':
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        iface.building_toolbar.show()

        self.disable_UI_functions()

        if len(self.production_frame.building_layer.selectedFeatures()) > 0:
            if self.is_correct_selections():
                self.get_selections()
                self.enable_UI_functions()
                self.populate_edit_comboboxes()
                self.select_comboboxes_value()
            else:
                self.production_frame.ids = []
                self.production_frame.building_outline_id = None
                self.disable_UI_functions()

    @pyqtSlot(bool)
    def save_clicked(self, commit_status):
        """
            When production frame btn_save clicked
        """
        self.production_frame.db.open_cursor()

        capture_method_id, capture_source_id, lifecycle_stage_id, suburb, town, t_a = self.get_comboboxes_values()

        if len(self.production_frame.ids) > 0:
            for i in self.production_frame.ids:
                sql = 'SELECT buildings.building_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                self.production_frame.db.execute_no_commit(
                    sql, (i, capture_method_id,
                          capture_source_id, lifecycle_stage_id,
                          suburb, town, t_a))
        self.disable_UI_functions()

        if commit_status:
            self.production_frame.db.commit_open_cursor()
            self.production_frame.ids = []
            self.production_frame.building_outline_id = None

    @pyqtSlot()
    def reset_clicked(self):
        """
            When production frame btn_reset clicked
        """
        self.production_frame.ids = []
        self.production_frame.building_outline_id = None
        # restart editing
        iface.actionSelect().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        self.disable_UI_functions()

    @pyqtSlot(list, list, bool)
    def selection_changed(self, added, removed, cleared):
        """
           Called when feature is selected
        """
        # If no outlines are selected the function will return
        if len(self.production_frame.building_layer.selectedFeatures()) == 0:
            self.production_frame.ids = []
            self.production_frame.building_outline_id = None
            self.disable_UI_functions()
            return
        if self.is_correct_selections():
            self.get_selections()
            self.enable_UI_functions()
            self.populate_edit_comboboxes()
            self.select_comboboxes_value()
        else:
            self.production_frame.ids = []
            self.production_frame.building_outline_id = None
            self.disable_UI_functions()

    def is_correct_selections(self):
        """
            Check if the selections meet the requirement
        """
        feats = []
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
            return False
        # if all selected features have the same attributes (allowed)
        elif len(feats) == 1:
            return True
        return False

    def get_selections(self):
        """
            Return the selection values
        """
        self.production_frame.ids = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()]
        self.production_frame.building_outline_id = [feat.id() for feat in self.production_frame.building_layer.selectedFeatures()][0]
        building_feat = [feat for feat in self.production_frame.building_layer.selectedFeatures()][0]
        building_geom = building_feat.geometry()
        # convert to correct format
        wkt = building_geom.exportToWkt()
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = self.production_frame.db._execute(sql, (wkt,))
        self.production_frame.geom = result.fetchall()[0][0]

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # lifeycle stage
        result = self.production_frame.db._execute(
            buildings_select.lifecycle_stage_value_by_building_outline_id, (
                self.production_frame.building_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.production_frame.cmb_lifecycle_stage.setCurrentIndex(
            self.production_frame.cmb_lifecycle_stage.findText(result))

        # capture method
        result = self.production_frame.db._execute(
            common_select.capture_method_value_by_building_outline_id, (
                self.production_frame.building_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.production_frame.cmb_capture_method.setCurrentIndex(
            self.production_frame.cmb_capture_method.findText(result))

        # capture source
        result = self.production_frame.db._execute(
            common_select.capture_source_group_value_description_external_by_bulk_outline_id,
            (self.production_frame.building_outline_id,)
        )
        result = result.fetchall()[0]
        text = str(result[0]) + '- ' + str(result[1] + '- ' + str(result[2]))
        self.production_frame.cmb_capture_source.setCurrentIndex(
            self.production_frame.cmb_capture_source.findText(text))

        # suburb
        result = self.production_frame.db._execute(
            reference_select.suburb_locality_suburb_4th_by_building_outline_id, (
                self.production_frame.building_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.production_frame.cmb_suburb.setCurrentIndex(
            self.production_frame.cmb_suburb.findText(result))

        # town city
        result = self.production_frame.db._execute(
            reference_select.town_city_name_by_building_outline_id, (
                self.production_frame.building_outline_id,
            ))
        result = result.fetchall()
        if result:
            self.production_frame.cmb_town.setCurrentIndex(
                self.production_frame.cmb_town.findText(result[0][0]))
        else:
            self.production_frame.cmb_town.setCurrentIndex(0)

        # territorial Authority
        result = self.production_frame.db._execute(
            reference_select.territorial_authority_name_by_building_outline_id, (
                self.production_frame.building_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.production_frame.cmb_ta.setCurrentIndex(
            self.production_frame.cmb_ta.findText(result))


class EditGeometry(ProductionChanges):
    """
        Class to edit outlines in buildings.building_outlines
        Inherits ProductionChanges
    """

    def __init__(self, production_frame):
        """Constructor"""
        ProductionChanges.__init__(self, production_frame)
        iface.actionToggleEditing().trigger()
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

        self.disable_UI_functions()

    @pyqtSlot(bool)
    def save_clicked(self, commit_status):
        """
            When production frame btn_save clicked
        """
        self.production_frame.db.open_cursor()

        capture_method_id, _, _, _, _, _ = self.get_comboboxes_values()

        for key in self.production_frame.geoms:
            sql = 'SELECT buildings.building_outlines_update_shape(%s, %s);'
            self.production_frame.db.execute_no_commit(
                sql, (self.production_frame.geoms[key], key))

            self.production_frame.db.execute_no_commit(
                'SELECT buildings.building_outlines_update_capture_method(%s, %s)',
                (key, capture_method_id)
            )
        self.disable_UI_functions()
        if commit_status:
            self.production_frame.db.commit_open_cursor()
            self.production_frame.geoms = {}

    @pyqtSlot()
    def reset_clicked(self):
        """
            When production frame btn_reset clicked
        """
        self.production_frame.building_layer.geometryChanged.disconnect(self.geometry_changed)
        iface.actionCancelEdits().trigger()
        self.production_frame.building_layer.geometryChanged.connect(self.geometry_changed)
        self.production_frame.geoms = {}
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionNodeTool().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        self.disable_UI_functions()

    @pyqtSlot(int, QgsGeometry)
    def geometry_changed(self, qgsfId, geom):
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
            buildings_select.building_outline_shape_by_building_outline_id, (qgsfId,))
        result = result.fetchall()[0][0]
        if self.production_frame.geom == result:
            if qgsfId in self.production_frame.geoms.keys():
                del self.production_frame.geoms[qgsfId]
            self.disable_UI_functions()
        else:
            self.production_frame.geoms[qgsfId] = self.production_frame.geom
            self.enable_UI_functions()
            self.populate_edit_comboboxes()
            self.select_comboboxes_value()

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        self.production_frame.cmb_capture_method.setCurrentIndex(
            self.production_frame.cmb_capture_method.findText('Trace Orthophotography'))
