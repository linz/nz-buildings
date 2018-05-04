# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

import qgis
from qgis.core import QgsVectorLayer, QgsFeatureRequest
from qgis.utils import iface

from buildings.utilities import database as db
from buildings.utilities import layers
from buildings.gui.error_dialog import ErrorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'new_outline_bulk.ui'))


class BulkNewOutline(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(BulkNewOutline, self).__init__(parent)
        self.setupUi(self)
        db.connect()
        self.cursor = None
        self.database = db
        self.populate_lookup_comboboxes()
        self.populate_area_comboboxes()
        # disable comboboxes and save button
        # until feature is added
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        # set up
        self.building_layer = QgsVectorLayer()
        self.geom = None
        self.added_building_ids = []
        self.layer_registry = layer_registry
        # supplied dataset to add to canvas
        # find data with most recent datasat id
        sql = 'SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets'
        result = db._execute(sql)
        result = result.fetchall()
        if len(result) == 0:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report('\n ---------------- NO SUPPLIED DATASETS ---------------- \n\n There are no supplied datasets please load some outlines first')
                self.error_dialog.show()
                self.btn_reset.setDisabled(1)
                self.btn_save.setDisabled(1)
                self.cmb_supplied_dataset.setDisabled(1)
                self.btn_exit.clicked.connect(self.fail_exit_clicked)
        else:
            self.populate_dataset_combobox()
            text = self.cmb_supplied_dataset.currentText()
            text_list = text.split('-')
            self.dataset_id = text_list[0]
            self.layer_registry.remove_layer(self.building_layer)
            # add the bulk_load_outlines to the layer registry
            self.add_outlines()
            # set up signals
            self.outline_id = None
            self.btn_save.clicked.connect(self.save_clicked)
            self.btn_save.setDisabled(1)
            self.btn_reset.setDisabled(1)
            self.btn_reset.clicked.connect(self.reset_clicked)
            self.cmb_supplied_dataset.currentIndexChanged.connect(self.add_outlines)
            self.btn_exit.clicked.connect(self.exit_clicked)

    def reload_setup(self):
        self.populate_dataset_combobox()
        text = self.cmb_supplied_dataset.currentText()
        text_list = text.split('-')
        self.dataset_id = text_list[0]
        self.layer_registry.remove_layer(self.building_layer)
        self.reset_clicked()
        # add the bulk_load_outlines to the layer registry
        self.add_outlines()
        # set up signals
        self.outline_id = None
        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_save.setDisabled(1)
        self.btn_reset.setDisabled(1)
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.cmb_supplied_dataset.currentIndexChanged.connect(self.add_outlines)
        self.btn_exit.clicked.connect(self.exit_clicked)

    def populate_dataset_combobox(self):
        sql = 'SELECT supplied_dataset_id, description FROM buildings_bulk_load.supplied_datasets sd WHERE sd.processed_date is NULL;'
        results = db._execute(sql)
        datasets = results.fetchall()
        for dset in datasets:
            text = '{0}-{1}'.format(dset[0], dset[1])
            self.cmb_supplied_dataset.addItem(text)

    def add_outlines(self):
        """Called when supplied dataset index is changed"""
        text = self.cmb_supplied_dataset.currentText()
        text_list = text.split('-')
        self.dataset_id = text_list[0]
        self.layer_registry.remove_layer(self.building_layer)
        self.supplied_reset()
        # add the bulk_load_outlines to the layer registry
        self.building_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.dataset_id)
        )
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_admin_bdys', '', ''
        )
        # change style of TAs
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})
        self.building_layer.featureAdded.connect(self.creator_feature_added)
        self.building_layer.featureDeleted.connect(self.creator_feature_deleted)

        # enable editing
        iface.setActiveLayer(self.building_layer)
        iface.actionToggleEditing().trigger()
        # set editing to add polygon
        iface.actionAddFeature().trigger()

    def populate_lookup_comboboxes(self):
        """
        method called on opening of frame to populate the lookup table
        comboboxes
        """
        # populate capture method combobox
        sql = 'SELECT value FROM buildings_common.capture_method;'
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate capture source group
        sql = 'SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs WHERE cs.capture_source_group_id = csg.capture_source_group_id;'
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1] + '- ' + str(item[2]))
            self.cmb_capture_source.addItem(text)

    def populate_area_comboboxes(self):
        """
        method called on opening of trame to populate area
        comboboxes
        """
        # populate suburb combobox
        sql = 'SELECT DISTINCT suburb_4th FROM buildings_admin_bdys.nz_locality'
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_suburb.addItem(item[0])

        # populate town combobox
        sql = 'SELECT DISTINCT city_name FROM buildings_admin_bdys.nz_locality'
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_town.addItem(item[0])
        # populate territorial authority combobox
        sql = 'SELECT DISTINCT name FROM buildings_admin_bdys.territorial_authority'
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_ta.addItem(item[0])

    def get_capture_method_id(self):
        """
        returns capture method id of input combobox
        """
        text = self.cmb_capture_method.currentText()
        sql = 'SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;'
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_source_id(self):
        """
        returns capture source id of input combobox
        """
        text = self.cmb_capture_source.currentText()
        if text == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report('\n ---------------- NO CAPTURE SOURCE ---------------- \n\n There are no capture source entries')
            self.error_dialog.show()
            return
        text_ls = text.split('- ')
        sql = 'SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;'
        result = db._execute(sql, data=(text_ls[0], text_ls[1]))
        data = result.fetchall()[0][0]
        if text_ls[2] == 'None':
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id is NULL;'
            result = db._execute(sql, data=(data,))
        else:
            sql = 'SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;'
            result = db._execute(sql, data=(data, text_ls[2]))
        return result.fetchall()[0][0]

    def get_suburb(self):
        """
        returns suburb entered
        """
        text = self.cmb_suburb.currentText()
        sql = 'SELECT id FROM buildings_admin_bdys.nz_locality WHERE buildings_admin_bdys.nz_locality.suburb_4th = %s;'
        result = db._execute(sql, (text, ))
        return result.fetchall()[0][0]

    def get_town(self):
        """
        returns town/city entered
        """
        text = self.cmb_town.currentText()
        sql = 'SELECT city_id FROM buildings_admin_bdys.nz_locality WHERE buildings_admin_bdys.nz_locality.city_name = %s;'
        result = db._execute(sql, (text, ))
        return result.fetchall()[0][0]

    def get_t_a(self):
        """
        returns territorial authority entered
        """
        text = self.cmb_ta.currentText()
        sql = 'SELECT ogc_fid FROM buildings_admin_bdys.territorial_authority WHERE buildings_admin_bdys.territorial_authority.name = %s;'
        result = db._execute(sql, (text, ))
        return result.fetchall()[0][0]

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
        new_feature = next(self.building_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = 'SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));'
        result = db._execute(sql, data=(wkt, ))
        geom = result.fetchall()[0][0]
        sql = 'SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)'
        result = db._execute(sql, data=(geom, ))
        self.geom = result.fetchall()[0][0]
        # enable comboboxes
        self.cmb_capture_method.setEnabled(1)
        self.cmb_capture_source.setEnabled(1)
        self.cmb_ta.setEnabled(1)
        self.cmb_town.setEnabled(1)
        self.cmb_suburb.setEnabled(1)
        # enable save
        self.btn_save.setEnabled(1)
        self.btn_reset.setEnabled(1)

    def creator_feature_deleted(self, qgsfId):
        """
        Called when a Feature is Deleted

        @param qgsfId:      Id of deleted feature
        @type  qgsfId:      qgis.core.QgsFeature.QgsFeatureId
        """
        if qgsfId in self.added_building_ids:
            self.added_building_ids.remove(qgsfId)
            if self.added_building_ids == []:
                self.cmb_capture_method.setDisabled(1)
                self.cmb_capture_source.setDisabled(1)
                self.cmb_ta.setDisabled(1)
                self.cmb_town.setDisabled(1)
                self.cmb_suburb.setDisabled(1)
                # disable save
                self.btn_save.setDisabled(1)
                self.btn_reset.setDisabled(1)

    def save_clicked(self, built_in=False, commit_status=True):
        """
        Called when save clicked
        """
        # get combobox values
        self.capture_source_id = self.get_capture_source_id()
        if self.capture_source_id is None:
            return
        self.capture_method_id = self.get_capture_method_id()
        self.suburb = self.get_suburb()
        self.town = self.get_town()
        self.t_a = self.get_t_a()
        db.open_cursor()
        # call function to insert into bulk_load_outlines table
        sql = 'SELECT buildings_bulk_load.fn_bulk_load_outlines_insert(%s, NULL, 2, %s, %s, %s, %s, %s, %s)'
        result = db.execute_no_commit(sql, (self.dataset_id,
                                            self.capture_method_id,
                                            self.capture_source_id,
                                            self.suburb,
                                            self.town, self.t_a, self.geom))
        self.outline_id = result.fetchall()[0][0]
        # TODO:
        # insert the new outline to its comparison table (i.e- added/removed/etc)
        # not yet done as nz-building-outlines comparison script does not allow for
        # comparing single outlines

        if commit_status:
            db.commit_open_cursor()

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
        self.btn_save.setDisabled(1)
        self.btn_reset.setDisabled(1)

    def exit_clicked(self):
        """
        Called when exit button is clicked
        """
        db.close_connection()
        # remove unsaved edits and stop editing layer
        iface.actionCancelEdits().trigger()
        # remove bulk_load_outlines from canvas
        if self.building_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.building_layer)
        if self.territorial_auth in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.territorial_auth)
        # change frame
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

    def fail_exit_clicked(self):
        """
        Called when exit button is clicked if failed to load any data
        """
        # change frame
        db.close_connection()
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

    def supplied_reset(self):
        """
        Called when supplied dataset combobox index changed
        """
        # reset combo boxes and disable
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
        self.btn_save.setDisabled(1)
        self.btn_reset.setDisabled(1)

    def reset_clicked(self):
        """
        Called when reset button is clicked
        """
        # remove current edit
        iface.actionCancelEdits().trigger()
        # restart editing
        iface.actionToggleEditing().trigger()
        iface.actionAddFeature().trigger()
        # reset combo boxes and disable
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
        self.btn_save.setDisabled(1)
        self.btn_reset.setDisabled(1)
