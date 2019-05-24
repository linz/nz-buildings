# -*- coding: utf-8 -*-
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QToolButton
from qgis.core import QgsFeatureRequest, QgsGeometry
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_bulk_load_select_statements as bulk_load_select,
                           buildings_common_select_statements as common_select,
                           buildings_reference_select_statements as reference_select,
                           general_select_statements as general_select)


class BulkLoadChanges:
    """
        Parent class of bulk Load changes (editing and adding outlines)
    """

    def __init__(self, edit_dialog):
        """Constructor."""
        # setup
        self.edit_dialog = edit_dialog
        self.error_dialog = None
        self.parent_frame = self.edit_dialog.parent_frame
        self.editing_layer = self.edit_dialog.editing_layer
        iface.setActiveLayer(self.editing_layer)

    def populate_edit_comboboxes(self):
        """
            Populate editing combox fields
        """
        # bulk load status
        if self.edit_dialog.layout_status.isVisible():
            result = self.edit_dialog.db._execute(bulk_load_select.bulk_load_status_value)
            ls = result.fetchall()
            for item in ls:
                self.edit_dialog.cmb_status.addItem(item[0])

        if self.edit_dialog.layout_capture_method.isVisible():
            # populate capture method combobox
            result = self.edit_dialog.db._execute(common_select.capture_method_value)
            ls = result.fetchall()
            for item in ls:
                self.edit_dialog.cmb_capture_method.addItem(item[0])

        if self.edit_dialog.layout_general_info.isVisible():
            # populate capture source group
            result = self.edit_dialog.db._execute(common_select.capture_source_group_value_external)
            ls = result.fetchall()
            text_max = ''
            for item in ls:
                text = '- '.join(item)
                self.edit_dialog.cmb_capture_source.addItem(text)
                if len(text) > len(text_max):
                    text_max = text
            self.fix_truncated_dropdown(self.edit_dialog.cmb_capture_source, text_max)

            # populate territorial authority combobox
            result = self.edit_dialog.db._execute(
                reference_select.territorial_authority_intersect_geom,
                (self.edit_dialog.geom,)
            )
            self.edit_dialog.ids_ta = []
            for (id_ta, name) in result.fetchall():
                self.edit_dialog.cmb_ta.addItem(name)
                self.edit_dialog.ids_ta.append(id_ta)

            # populate suburb combobox
            result = self.edit_dialog.db._execute(
                reference_select.suburb_locality_intersect_geom,
                (self.edit_dialog.geom,)
            )
            self.edit_dialog.ids_suburb = []
            for (id_suburb, name) in result.fetchall():
                if name is not None:
                    self.edit_dialog.cmb_suburb.addItem(name)
                    self.edit_dialog.ids_suburb.append(id_suburb)

            # populate town combobox
            result = self.edit_dialog.db._execute(
                reference_select.town_city_intersect_geometry,
                (self.edit_dialog.geom,)
            )
            self.edit_dialog.cmb_town.addItem('')
            self.edit_dialog.ids_town = [None]
            for (id_town, name) in result.fetchall():
                if name is not None:
                    self.edit_dialog.cmb_town.addItem(name)
                    self.edit_dialog.ids_town.append(id_town)

    def get_comboboxes_values(self):

        # bulk load status
        if self.edit_dialog.layout_status.isVisible():
            text = self.edit_dialog.cmb_status.currentText()
            result = self.edit_dialog.db.execute_no_commit(
                bulk_load_select.bulk_load_status_id_by_value, (text,))
            bulk_load_status_id = result.fetchall()[0][0]
        else:
            bulk_load_status_id = None

        if self.edit_dialog.layout_capture_method.isVisible():
            # capture method id
            text = self.edit_dialog.cmb_capture_method.currentText()
            result = self.edit_dialog.db.execute_no_commit(
                common_select.capture_method_id_by_value, (text,))
            capture_method_id = result.fetchall()[0][0]
        else:
            capture_method_id = None

        if self.edit_dialog.layout_general_info.isVisible():
            # capture source
            text = self.edit_dialog.cmb_capture_source.currentText()
            text_ls = text.split('- ')
            result = self.edit_dialog.db.execute_no_commit(
                common_select.capture_source_group_id_by_value, (text_ls[2], ))
            data = result.fetchall()[0][0]
            if text_ls[0] == 'None':
                result = self.edit_dialog.db.execute_no_commit(
                    common_select.capture_source_id_by_capture_source_group_id_is_null, (data,))
            else:
                result = self.edit_dialog.db.execute_no_commit(
                    common_select.capture_source_id_by_capture_source_group_id_and_external_source_id, (
                        data, text_ls[0]
                    ))
            capture_source_id = result.fetchall()[0][0]

            # suburb
            index = self.edit_dialog.cmb_suburb.currentIndex()
            suburb = self.edit_dialog.ids_suburb[index]

            # town
            index = self.edit_dialog.cmb_town.currentIndex()
            town = self.edit_dialog.ids_town[index]

            # territorial Authority
            index = self.edit_dialog.cmb_ta.currentIndex()
            t_a = self.edit_dialog.ids_ta[index]
        else:
            capture_source_id, suburb, town, t_a = None, None, None, None
        return bulk_load_status_id, capture_method_id, capture_source_id, suburb, town, t_a

    def enable_UI_functions(self):
        """
            Function called when comboboxes are to be enabled
        """
        self.edit_dialog.cmb_status.clear()
        self.edit_dialog.cmb_status.setEnabled(1)
        self.edit_dialog.cmb_capture_method.clear()
        self.edit_dialog.cmb_capture_method.setEnabled(1)
        self.edit_dialog.cmb_capture_source.clear()
        self.edit_dialog.cmb_capture_source.setEnabled(1)
        self.edit_dialog.cmb_ta.clear()
        self.edit_dialog.cmb_ta.setEnabled(1)
        self.edit_dialog.cmb_town.clear()
        self.edit_dialog.cmb_town.setEnabled(1)
        self.edit_dialog.cmb_suburb.clear()
        self.edit_dialog.cmb_suburb.setEnabled(1)
        self.edit_dialog.btn_edit_save.setEnabled(1)
        self.edit_dialog.btn_edit_reset.setEnabled(1)

    def disable_UI_functions(self):
        """
            Function called when comboboxes are to be disabled
        """
        self.edit_dialog.cmb_status.clear()
        self.edit_dialog.cmb_status.setDisabled(1)
        self.edit_dialog.cmb_capture_method.clear()
        self.edit_dialog.cmb_capture_method.setDisabled(1)
        self.edit_dialog.cmb_capture_source.clear()
        self.edit_dialog.cmb_capture_source.setDisabled(1)
        self.edit_dialog.le_deletion_reason.setDisabled(1)
        self.edit_dialog.cmb_ta.clear()
        self.edit_dialog.cmb_ta.setDisabled(1)
        self.edit_dialog.cmb_town.clear()
        self.edit_dialog.cmb_town.setDisabled(1)
        self.edit_dialog.cmb_suburb.clear()
        self.edit_dialog.cmb_suburb.setDisabled(1)
        self.edit_dialog.btn_edit_save.setDisabled(1)
        self.edit_dialog.btn_edit_reset.setDisabled(1)

    def fix_truncated_dropdown(self, cmb, text):
        """
            Fix the trucated cmb dropdown in windows
        """
        w = cmb.fontMetrics().boundingRect(text).width()
        cmb.view().setFixedWidth(w + 30)


class AddBulkLoad(BulkLoadChanges):
    """
        Class to add outlines to buildings_bulk_load.bulk_load_outlines
        Inherits BulkLoadChanges
    """

    def __init__(self, edit_dialog):
        """Constructor"""
        BulkLoadChanges.__init__(self, edit_dialog)
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
    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.edit_dialog.db.open_cursor()

        _, capture_method_id, capture_source_id, suburb, town, t_a = self.get_comboboxes_values()

        # insert into bulk_load_outlines table
        sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s);'
        result = self.edit_dialog.db.execute_no_commit(
            sql, (self.edit_dialog.current_dataset, capture_method_id,
                  capture_source_id, suburb, town, t_a,
                  self.edit_dialog.geom)
        )
        self.edit_dialog.outline_id = result.fetchall()[0][0]

        # insert into added table
        result = self.edit_dialog.db._execute(
            bulk_load_select.supplied_dataset_processed_date_by_dataset_id, (
                self.edit_dialog.current_dataset, )
        )
        processed_date = result.fetchall()[0][0]

        if processed_date:
            sql = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s, %s);'
            self.edit_dialog.db.execute_no_commit(
                sql, (self.edit_dialog.outline_id, 1))

        if commit_status:
            self.edit_dialog.db.commit_open_cursor()
            self.edit_dialog.geom = None
            self.edit_dialog.added_building_ids = []
        # reset and disable comboboxes
        if self.parent_frame.polyline:
            self.parent_frame.polyline.reset()
        if self.parent_frame.__class__.__name__ == 'AlterRelationships':
            self.parent_frame.repaint_view()
        iface.mapCanvas().refresh()
        self.disable_UI_functions()

    @pyqtSlot()
    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        self.editing_layer.geometryChanged.disconnect(self.creator_geometry_changed)
        iface.actionCancelEdits().trigger()
        self.editing_layer.geometryChanged.connect(self.creator_geometry_changed)
        # restart editing
        iface.actionToggleEditing().trigger()
        if not self.parent_frame.circle_action.isChecked():
            iface.actionAddFeature().trigger()

        # reset and disable comboboxes
        self.disable_UI_functions()
        if self.parent_frame.polyline:
            self.parent_frame.polyline.reset()
        self.edit_dialog.geom = None
        self.edit_dialog.added_building_ids = []

    @pyqtSlot(int)
    def creator_feature_added(self, qgsfId):
        """
           Called when feature is added
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if self.edit_dialog.added_building_ids != []:
            iface.messageBar().pushMessage("WARNING",
                                           "You've drawn multiple outlines, only the LAST outline you've drawn will be saved.",
                                           level=QgsMessageBar.WARNING, duration=3)
        if qgsfId not in self.edit_dialog.added_building_ids:
            self.edit_dialog.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.editing_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # calculate area
        area = new_geometry.area()
        if area < 10:
            iface.messageBar().pushMessage("INFO",
                                           "You've drawn an outline that is less than 10sqm, are you sure this is correct?",
                                           level=QgsMessageBar.INFO, duration=3)
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = general_select.convert_geometry
        result = self.edit_dialog.db._execute(sql, (wkt,))
        self.edit_dialog.geom = result.fetchall()[0][0]
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
        if qgsfId in self.edit_dialog.added_building_ids:
            self.edit_dialog.added_building_ids.remove(qgsfId)
            if self.parent_frame.polyline is not None:
                self.parent_frame.polyline.reset()
            if self.edit_dialog.added_building_ids == []:
                self.disable_UI_functions()
                self.edit_dialog.geom = None

    @pyqtSlot(int, QgsGeometry)
    def creator_geometry_changed(self, qgsfId, geom):
        """
           Called when feature is changed
           @param qgsfId:      Id of added feature
           @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
           @param geom:        geometry of added feature
           @type  geom:        qgis.core.QgsGeometry
        """
        if qgsfId in self.edit_dialog.added_building_ids:
            wkt = geom.exportToWkt()
            if not wkt:
                self.disable_UI_functions()
                self.edit_dialog.geom = None
                return
            sql = general_select.convert_geometry
            result = self.edit_dialog.db._execute(sql, (wkt,))
            self.edit_dialog.geom = result.fetchall()[0][0]
            area = geom.area()
            if area < 10:
                iface.messageBar().pushMessage("INFO",
                                               "You've edited the outline to less than 10sqm, are you sure this is correct?",
                                               level=QgsMessageBar.INFO, duration=3)
        else:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n -------------------- WRONG GEOMETRY EDITED ------'
                '-------------- \n\nOnly current added outline can '
                'be edited. Please go to [Edit Geometry] to edit '
                'existing outlines.'
            )
            self.error_dialog.show()

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # capture method
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText('Trace Orthophotography'))

        # capture source
        result = self.edit_dialog.db._execute(
            common_select.capture_source_group_value_external_by_dataset_id,
            (self.edit_dialog.current_dataset, )
        )
        result = result.fetchall()[0]
        text = '- '.join(result)
        self.edit_dialog.cmb_capture_source.setCurrentIndex(
            self.edit_dialog.cmb_capture_source.findText(text))

        # territorial authority
        sql = 'SELECT buildings_reference.territorial_authority_intersect_polygon(%s);'
        result = self.edit_dialog.db._execute(sql,
                                              (self.edit_dialog.geom,))
        index = self.edit_dialog.ids_ta.index(result.fetchall()[0][0])
        self.edit_dialog.cmb_ta.setCurrentIndex(index)

        # town locality
        sql = 'SELECT buildings_reference.town_city_intersect_polygon(%s);'
        result = self.edit_dialog.db._execute(sql,
                                              (self.edit_dialog.geom,))
        index = self.edit_dialog.ids_town.index(result.fetchall()[0][0])
        self.edit_dialog.cmb_town.setCurrentIndex(index)

        # suburb locality
        sql = 'SELECT buildings_reference.suburb_locality_intersect_polygon(%s);'
        result = self.edit_dialog.db._execute(sql,
                                              (self.edit_dialog.geom,))
        index = self.edit_dialog.ids_suburb.index(result.fetchall()[0][0])
        self.edit_dialog.cmb_suburb.setCurrentIndex(index)


class EditAttribute(BulkLoadChanges):
    """
        Class to edit Attribute in buildings_bulk_load.bulk_load_outlines
        Inherits BulkLoadChanges
    """

    def __init__(self, edit_dialog):
        """Constructor"""
        BulkLoadChanges.__init__(self, edit_dialog)
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
        if len(iface.activeLayer().selectedFeatures()) > 0:
            if self.is_correct_selections():
                self.get_selections()
                self.enable_UI_functions()
                self.populate_edit_comboboxes()
                self.select_comboboxes_value()
            else:
                self.edit_dialog.ids = []
                self.edit_dialog.building_outline_id = None
                self.disable_UI_functions()

    @pyqtSlot(bool)
    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.edit_dialog.db.open_cursor()

        bulk_load_status_id, capture_method_id, capture_source_id, suburb, town, t_a = self.get_comboboxes_values()

        # bulk load status
        ls_relationships = {'added': [], 'matched': [], 'related': []}
        if self.edit_dialog.cmb_status.currentText() == 'Deleted During QA':
            # can only delete outlines if no relationship
            self.edit_dialog.description_del = self.edit_dialog.le_deletion_reason.text()
            if len(self.edit_dialog.description_del) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- EMPTY VALUE FIELD ------'
                    '-------------- \n\n There are no "reason for deletion" entries '
                )
                self.error_dialog.show()
                self.disable_UI_functions()
                return
            ls_relationships = self.remove_compared_outlines()
            if len(ls_relationships['matched']) == 0 and len(ls_relationships['related']) == 0:
                if len(self.edit_dialog.ids) > 0:
                    for i in self.edit_dialog.ids:
                        # check current status of building
                        sql = bulk_load_select.bulk_load_status_id_by_outline_id
                        current_status = self.edit_dialog.db.execute_no_commit(sql, (i,))
                        current_status = current_status.fetchall()
                        if current_status[0][0] == 3:
                            sql = 'SELECT buildings_bulk_load.delete_deleted_description(%s);'
                            self.edit_dialog.db.execute_no_commit(sql, (i,))
                        sql = 'SELECT buildings_bulk_load.deletion_description_insert(%s, %s);'
                        self.edit_dialog.db.execute_no_commit(sql, (i, self.edit_dialog.description_del))
                        # remove outline from added table
                        sql = 'SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);'
                        self.edit_dialog.db.execute_no_commit(sql, (i,))
                        sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                        self.edit_dialog.db.execute_no_commit(
                            sql, (i, bulk_load_status_id, capture_method_id,
                                  capture_source_id, suburb, town, t_a))
                    self.editing_layer.removeSelection()
        else:
            for i in self.edit_dialog.ids:
                # check current status of building
                sql = bulk_load_select.bulk_load_status_id_by_outline_id
                current_status = self.edit_dialog.db.execute_no_commit(sql, (i,))
                current_status = current_status.fetchall()
                if current_status[0][0] == 3:
                    sql = 'SELECT buildings_bulk_load.delete_deleted_description(%s);'
                    self.edit_dialog.db.execute_no_commit(sql, (i,))
                # change attributes
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_attributes(%s, %s, %s, %s, %s, %s, %s);'
                self.edit_dialog.db.execute_no_commit(
                    sql, (i, bulk_load_status_id, capture_method_id,
                          capture_source_id, suburb, town, t_a))
            self.editing_layer.removeSelection()
        self.disable_UI_functions()
        self.edit_dialog.completer_box()

        if commit_status:
            self.edit_dialog.db.commit_open_cursor()
            self.edit_dialog.ids = []
            self.edit_dialog.building_outline_id = None

    @pyqtSlot()
    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        self.edit_dialog.ids = []
        self.edit_dialog.building_outline_id = None
        iface.actionSelect().trigger()
        iface.activeLayer().removeSelection()
        # reset and disable comboboxes
        self.edit_dialog.circle_tool = None
        self.disable_UI_functions()

    @pyqtSlot(list, list, bool)
    def selection_changed(self, added, removed, cleared):
        """
           Called when feature is selected
        """
        # If no outlines are selected the function will return
        if len(self.editing_layer.selectedFeatures()) == 0:
            self.edit_dialog.ids = []
            self.edit_dialog.building_outline_id = None
            self.disable_UI_functions()
            return
        if self.is_correct_selections():
            self.get_selections()
            self.enable_UI_functions()
            self.populate_edit_comboboxes()
            self.select_comboboxes_value()
        else:
            self.edit_dialog.ids = []
            self.edit_dialog.building_outline_id = None
            self.disable_UI_functions()

    def is_correct_selections(self):
        """
            Check if the selections meet the requirement
        """
        feats = []
        for feature in self.editing_layer.selectedFeatures():
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
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n ---- MULTIPLE NON IDENTICAL FEATURES SELEC'
                'TED ---- \n\n Can only edit attributes of mul'
                'tiple features when all existing attributes a'
                're identical.'
            )
            self.error_dialog.show()
            return False
        # if all selected features have the same attributes (allowed)
        elif len(feats) == 1:
            deleted = 0
            reasons = []
            for feature in self.editing_layer.selectedFeatures():
                sql = bulk_load_select.bulk_load_status_id_by_outline_id
                result = self.edit_dialog.db._execute(sql, (feature['bulk_load_outline_id'], ))
                bl_status = result.fetchall()[0][0]
                if bl_status == 3:
                    deleted = deleted + 1
                    sql = bulk_load_select.deletion_description_by_bulk_load_id
                    result = self.edit_dialog.db._execute(sql, (feature['bulk_load_outline_id'], ))
                    reason = result.fetchall()[0][0]
                    if reason not in reasons:
                        reasons.append(reason)
            if deleted > 0:
                if deleted == len(self.editing_layer.selectedFeatures()):
                    if self.parent_frame.btn_compare_outlines.isEnabled():
                        if len(reasons) <= 1:
                            return True
                        else:
                            self.error_dialog = ErrorDialog()
                            self.error_dialog.fill_report(
                                '\n ---- DIFFERING DELETION REASONS ---- \n\n'
                                'Cannot edit deleted features as have differing'
                                ' reasons for deletion. Please edit individually.\n'
                            )
                            self.error_dialog.show()
                            return False
                    else:
                        self.error_dialog = ErrorDialog()
                        self.error_dialog.fill_report(
                            '\n ---- CANNOT EDIT DELETED FEATURE ---- \n\n'
                            'Cannot edit deleted feature after comparison has been'
                            ' run, instead please add this feature manually.\n'
                            'Note: Don\'t forget to update the relationship too!'
                        )
                        self.error_dialog.show()
                        return False
            else:
                return True
        return False

    def get_selections(self):
        """
            Return the selection values
        """
        self.edit_dialog.ids = [feat.id() for feat in self.editing_layer.selectedFeatures()]
        self.edit_dialog.bulk_load_outline_id = self.edit_dialog.ids[0]
        bulk_load_feat = [feat for feat in self.editing_layer.selectedFeatures()][0]
        bulk_load_geom = bulk_load_feat.geometry()
        # convert to correct format
        wkt = bulk_load_geom.exportToWkt()
        sql = general_select.convert_geometry
        result = self.edit_dialog.db._execute(sql, (wkt,))
        self.edit_dialog.geom = result.fetchall()[0][0]

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        # bulk load status
        result = self.edit_dialog.db._execute(
            bulk_load_select.bulk_load_status_value_by_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.edit_dialog.cmb_status.setCurrentIndex(
            self.edit_dialog.cmb_status.findText(result))

        # reason for deletion
        if self.edit_dialog.cmb_status.currentText() == 'Deleted During QA':
            reason = bulk_load_select.deletion_description_by_bulk_load_id
            reason = self.edit_dialog.db._execute(reason, (self.edit_dialog.bulk_load_outline_id,))
            reason = reason.fetchall()[0][0]
            self.edit_dialog.le_deletion_reason.setText(reason)

        # capture method
        result = self.edit_dialog.db._execute(
            common_select.capture_method_value_by_bulk_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText(result))

        # capture source
        result = self.edit_dialog.db._execute(
            common_select.capture_source_group_value_external_by_bulk_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()[0]
        text = '- '.join(result)
        self.edit_dialog.cmb_capture_source.setCurrentIndex(
            self.edit_dialog.cmb_capture_source.findText(text))

        # suburb
        result = self.edit_dialog.db._execute(
            reference_select.suburb_locality_suburb_4th_by_bulk_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.edit_dialog.cmb_suburb.setCurrentIndex(
            self.edit_dialog.cmb_suburb.findText(result))

        # town city
        result = self.edit_dialog.db._execute(
            reference_select.town_city_name_by_bulk_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()
        if result:
            self.edit_dialog.cmb_town.setCurrentIndex(
                self.edit_dialog.cmb_town.findText(result[0][0]))
        else:
            self.edit_dialog.cmb_town.setCurrentIndex(0)

        # territorial Authority
        result = self.edit_dialog.db._execute(
            reference_select.territorial_authority_name_by_bulk_outline_id, (
                self.edit_dialog.bulk_load_outline_id,
            ))
        result = result.fetchall()[0][0]
        self.edit_dialog.cmb_ta.setCurrentIndex(
            self.edit_dialog.cmb_ta.findText(result))

    def remove_compared_outlines(self):
        """
            called to check can mark outline for deletion
        """
        added_outlines = self.edit_dialog.db.execute_no_commit(
            bulk_load_select.added_outlines_by_dataset_id, (
                self.edit_dialog.current_dataset,))
        added_outlines = added_outlines.fetchall()
        matched_outlines = self.edit_dialog.db.execute_no_commit(
            bulk_load_select.matched_outlines_by_dataset_id, (
                self.edit_dialog.current_dataset,))
        matched_outlines = matched_outlines.fetchall()
        related_outlines = self.edit_dialog.db.execute_no_commit(
            bulk_load_select.related_outlines_by_dataset_id, (
                self.edit_dialog.current_dataset,))
        related_outlines = related_outlines.fetchall()
        if len(self.edit_dialog.ids) > 0:
            # if there is more than one feature to update
            ls_relationships = {'added': [], 'matched': [], 'related': []}
            for item in self.edit_dialog.ids:
                # added
                if (item, ) in added_outlines:
                    ls_relationships['added'].append(item)
                # matched
                if (item, ) in matched_outlines:
                    self.error_dialog = ErrorDialog()
                    self.error_dialog.fill_report(
                        '\n --------------- RELATIONSHIP EXISTS ---------'
                        '-------\n\nCan only mark for deletion outline if'
                        ' no relationship exists'
                    )
                    self.error_dialog.show()
                    ls_relationships['matched'].append(item)
                    break
                # related
                if (item, ) in related_outlines:
                    self.error_dialog = ErrorDialog()
                    self.error_dialog.fill_report(
                        '\n ------------------- RELATIONSHIP EXISTS ---------'
                        '---------- \n\nCan only mark for deletion outline if'
                        ' no relationship exists'
                    )
                    self.error_dialog.show()
                    ls_relationships['related'].append(item)
                    break
        return ls_relationships


class EditGeometry(BulkLoadChanges):
    """
        Class to edit outline's geometry in buildings_bulk_load.bulk_load_outlines
        Inherits BulkLoadChanges
    """

    def __init__(self, edit_dialog):
        """Constructor"""
        BulkLoadChanges.__init__(self, edit_dialog)
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
                'mActionReshapeFeatures', 'mActionOffsetCurve',
                'mActionSplitFeatures'
            ]:
                iface.building_toolbar.addAction(adv)
        iface.building_toolbar.show()

        self.disable_UI_functions()
        self.new_attrs = []

    @pyqtSlot(bool)
    def edit_save_clicked(self, commit_status):
        """
            When bulk load frame btn_edit_save clicked
        """
        self.edit_dialog.db.open_cursor()

        _, capture_method_id, _, _, _, _ = self.get_comboboxes_values()

        if len(self.edit_dialog.split_geoms) > 0:
            capture_source_id = self.new_attrs[5]
            suburb = self.new_attrs[6]
            town = self.new_attrs[7]
            t_a = self.new_attrs[8]

            # insert into bulk_load_outlines table
            for geom in self.edit_dialog.split_geoms:
                sql = 'SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s);'
                result = self.edit_dialog.db.execute_no_commit(
                    sql, (self.edit_dialog.current_dataset, capture_method_id,
                          capture_source_id, suburb, town, t_a,
                          geom)
                )
                self.edit_dialog.outline_id = result.fetchall()[0][0]

                # insert into added table
                result = self.edit_dialog.db._execute(
                    bulk_load_select.supplied_dataset_processed_date_by_dataset_id, (
                        self.edit_dialog.current_dataset, )
                )
                processed_date = result.fetchall()[0][0]

                if processed_date:
                    sql = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s, %s);'
                    self.edit_dialog.db.execute_no_commit(
                        sql, (self.edit_dialog.outline_id, 1))

        for key in self.edit_dialog.geoms:
            sql = 'SELECT buildings_bulk_load.bulk_load_outlines_update_shape(%s, %s);'
            self.edit_dialog.db.execute_no_commit(
                sql,
                (self.edit_dialog.geoms[key], key)
            )
            self.edit_dialog.db.execute_no_commit(
                'SELECT buildings_bulk_load.bulk_load_outlines_update_capture_method(%s, %s)',
                (key, capture_method_id)
            )
        if self.parent_frame.__class__.__name__ == 'AlterRelationships':
            self.parent_frame.repaint_view()

        self.disable_UI_functions()

        if commit_status:
            self.edit_dialog.db.commit_open_cursor()
            self.edit_dialog.geoms = {}
            self.edit_dialog.split_geoms = []
            self.edit_dialog.added_building_ids = []
            iface.actionCancelEdits().trigger()
            iface.actionToggleEditing().trigger()

    @pyqtSlot()
    def edit_reset_clicked(self):
        """
            When bulk load frame btn_reset_save clicked
        """
        self.editing_layer.geometryChanged.disconnect(self.geometry_changed)
        iface.actionCancelEdits().trigger()
        self.editing_layer.geometryChanged.connect(self.geometry_changed)
        self.edit_dialog.geoms = {}
        self.edit_dialog.split_geoms = []
        self.edit_dialog.added_building_ids = []
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
        sql = general_select.convert_geometry
        result = self.edit_dialog.db._execute(sql, (wkt,))
        self.edit_dialog.geom = result.fetchall()[0][0]
        result = self.edit_dialog.db._execute(
            bulk_load_select.bulk_load_outline_shape_by_id,
            (qgsfId,)
        )
        area = geom.area()
        if area < 10:
            iface.messageBar().pushMessage("INFO",
                                           "You've edited the outline to less than 10sqm, are you sure this is correct?",
                                           level=QgsMessageBar.INFO, duration=3)
        result = result.fetchall()
        if len(result) == 0:
            iface.messageBar().pushMessage("INFO",
                                           "You've tried to split the same feature twice, you must save the changes to the db between splitting the same feature.",
                                           level=QgsMessageBar.INFO, duration=5)
            self.disable_UI_functions()
            self.edit_dialog.btn_edit_reset.setEnabled(1)
            return
        else:
            result = result[0][0]
            if self.edit_dialog.geom == result:
                if qgsfId in self.edit_dialog.geoms.keys():
                    del self.edit_dialog.geoms[qgsfId]
                self.disable_UI_functions()
            else:
                self.edit_dialog.geoms[qgsfId] = self.edit_dialog.geom
                self.enable_UI_functions()
                self.populate_edit_comboboxes()
                self.select_comboboxes_value()

    @pyqtSlot(int)
    def creator_feature_added(self, qgsfId):
        if qgsfId not in self.edit_dialog.added_building_ids:
            self.edit_dialog.added_building_ids.append(qgsfId)
        # get new feature geom
        request = QgsFeatureRequest().setFilterFid(qgsfId)
        new_feature = next(self.editing_layer.getFeatures(request))
        self.new_attrs = new_feature.attributes()
        if not self.new_attrs[5]:
            iface.messageBar().pushMessage("INFO",
                                           "You've added a new feature, this can't be done in edit geometry, please switch to add outline.",
                                           level=QgsMessageBar.INFO, duration=5)
            self.disable_UI_functions()
            self.edit_dialog.btn_edit_reset.setEnabled(1)
            return
        new_geometry = new_feature.geometry()
        # calculate area
        area = new_geometry.area()
        if area < 10:
            iface.messageBar().pushMessage("INFO",
                                           "You've created an outline that is less than 10sqm, are you sure this is correct?",
                                           level=QgsMessageBar.INFO, duration=3)

        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = general_select.convert_geometry
        result = self.edit_dialog.db._execute(sql, (wkt,))
        self.edit_dialog.split_geoms.append(result.fetchall()[0][0])

    def select_comboboxes_value(self):
        """
            Select the correct combobox value for the geometry
        """
        self.edit_dialog.cmb_capture_method.setCurrentIndex(
            self.edit_dialog.cmb_capture_method.findText('Trace Orthophotography'))
