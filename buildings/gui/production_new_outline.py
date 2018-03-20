# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

import qgis
from qgis.core import QgsVectorLayer, QgsProject, QgsFeatureRequest
from qgis.utils import iface

from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_outline_production.ui"))

db.connect()


class ProductionNewOutline(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(ProductionNewOutline, self).__init__(parent)
        self.setupUi(self)
        self.populate_lookup_comboboxes()
        self.populate_area_comboboxes()
        # disable comboboxes and save button 
        # until feature added
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_lifecycle_stage.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_save.setDisabled(1)
        # set up
        self.create_building_layer = QgsVectorLayer()
        self.geom = None
        self.added_building_ids = []
        self.layer_registry = layer_registry
        # building outline dataset to add to canvas
        # find most recent dataset
        self.layer_registry.add_postgres_layer(
            "building_outlines", "building_outlines",
            "shape", "buildings", "", ""
        )
        # find the existing buildings group
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Building Tool Layers")
        layers = group.findLayers()
        for layer in layers:
            if layer.name() == "building_outlines":
                # save layer
                self.create_building_layer = layer.layer()
        # enable editing
        iface.setActiveLayer(self.create_building_layer)
        iface.actionToggleEditing().trigger()
        # set editing to add polygon
        iface.actionAddFeature().trigger()
        # zoom to the active layer
        iface.actionZoomToLayer().trigger()

        # set up signals
        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_reset.clicked.connect(self.reset_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.create_building_layer.featureAdded.connect(self.creator_feature_added)
        self.create_building_layer.featureDeleted.connect(self.creator_feature_deleted)

    def populate_lookup_comboboxes(self):
        """
        method called on opening of frame to populate the lookup table
        comboboxes
        """
        # populate capture method combobox
        sql = "SELECT value FROM buildings_common.capture_method;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_capture_method.addItem(item[0])
        # populate lifecycle stage combobox
        sql = "SELECT value FROM buildings.lifecycle_stage;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            self.cmb_lifecycle_stage.addItem(item[0])
        # populate capture source group
        sql = "SELECT csg.value, csg.description, cs.external_source_id FROM buildings_common.capture_source_group csg, buildings_common.capture_source cs WHERE cs.capture_source_group_id = csg.capture_source_group_id;"
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
        # TODO is only Wellington??
        # populate suburb combobox
        sql = "SELECT DISTINCT alias_name FROM admin_bdys.suburb_alias;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_suburb.addItem(item[0])

        # populate town combobox
        sql = "SELECT DISTINCT city_name FROM admin_bdys.nz_locality;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_town.addItem(item[0])
        # populate territorial authority combobox
        sql = "SELECT DISTINCT name FROM admin_bdys.territorial_authority;"
        result = db._execute(sql)
        ls = result.fetchall()
        for item in ls:
            if item[0] is not None:
                self.cmb_ta.addItem(item[0])

    def get_capture_method_id(self):
        """
        returns capture method id of input combobox
        """
        index = self.cmb_capture_method.currentIndex()
        text = self.cmb_capture_method.itemText(index)
        sql = "SELECT capture_method_id FROM buildings_common.capture_method cm WHERE cm.value = %s;"
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_lifecycle_stage_id(self):
        """
        returns lifecycle stage id of input
        """
        index = self.cmb_lifecycle_stage.currentIndex()
        text = self.cmb_lifecycle_stage.itemText(index)
        sql = "SELECT lifecycle_stage_id FROM buildings.lifecycle_stage ls WHERE ls.value = %s;"
        result = db._execute(sql, data=(text, ))
        return result.fetchall()[0][0]

    def get_capture_source_id(self):
        """
        returns capture source id of input combobox
        """
        index = self.cmb_capture_source.currentIndex()
        text = self.cmb_capture_source.itemText(index)
        text_ls = text.split('- ')
        sql = "SELECT capture_source_group_id FROM buildings_common.capture_source_group csg WHERE csg.value = %s AND csg.description = %s;"
        result = db._execute(sql, data=(text_ls[0], text_ls[1]))
        data = result.fetchall()[0][0]
        if text_ls[2] == "None":
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id is NULL;"
            result = db._execute(sql, data=(data,))
        else:
            sql = "SELECT capture_source_id FROM buildings_common.capture_source cs WHERE cs.capture_source_group_id = %s and cs.external_source_id = %s;"
            result = db._execute(sql, data=(data, text_ls[2]))
        return result.fetchall()[0][0]

    def get_suburb(self):
        """
        returns suburb entered
        """
        index = self.cmb_suburb.currentIndex()
        text = self.cmb_suburb.itemText(index)
        sql = "SELECT locality_id FROM admin_bdys.suburb_alias WHERE admin_bdys.suburb_alias.alias_name = %s;"
        result = db._execute(sql, (text, ))
        return result.fetchall()[0][0]

    def get_town(self):
        """
        returns town/city entered
        """
        index = self.cmb_town.currentIndex()
        text = self.cmb_town.itemText(index)
        sql = "SELECT city_id FROM admin_bdys.nz_locality WHERE admin_bdys.nz_locality.city_name = %s;"
        result = db._execute(sql, (text, ))
        return result.fetchall()[0][0]

    def get_t_a(self):
        """
        returns territorial authority entered
        """
        index = self.cmb_ta.currentIndex()
        text = self.cmb_ta.itemText(index)
        sql = "SELECT ogc_fid FROM admin_bdys.territorial_authority WHERE admin_bdys.territorial_authority.name = %s;"
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
        new_feature = next(self.create_building_layer.getFeatures(request))
        new_geometry = new_feature.geometry()
        # convert to correct format
        wkt = new_geometry.exportToWkt()
        sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
        result = db._execute(sql, data=(wkt, ))
        geom = result.fetchall()[0][0]
        # ensure outline SRID is 2193
        sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193);"
        result = db._execute(sql, data=(geom, ))
        self.geom = result.fetchall()[0][0]

        # enable comboboxes
        self.cmb_capture_method.setEnabled(1)
        self.cmb_capture_source.setEnabled(1)
        self.cmb_lifecycle_stage.setEnabled(1)
        self.cmb_ta.setEnabled(1)
        self.cmb_town.setEnabled(1)
        self.cmb_suburb.setEnabled(1)
        # enable save
        self.btn_save.setEnabled(1)

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
                self.cmb_lifecycle_stage.setDisabled(1)
                self.cmb_ta.setDisabled(1)
                self.cmb_town.setDisabled(1)
                self.cmb_suburb.setDisabled(1)
                # disable save
                self.btn_save.setDisabled(1)

    def save_clicked(self):
        """
        Called when save clicked
        """
        # get combobox values
        self.capture_source_id = self.get_capture_source_id()
        self.lifecycle_stage_id = self.get_lifecycle_stage_id()
        self.capture_method_id = self.get_capture_method_id()
        self.suburb = self.get_suburb()
        self.town = self.get_town()
        self.t_a = self.get_t_a()

        # insert into buildings table
        sql = "INSERT INTO buildings.buildings(begin_lifespan) VALUES(now());"
        db.execute(sql)
        sql = "SELECT MAX(building_id) FROM buildings.buildings;"
        result = db._execute(sql)
        building_id = result.fetchall()[0][0]
        # insert into bulk_load_outlines table
        sql = "INSERT INTO buildings.building_outlines(building_id, capture_method_id, capture_source_id, lifecycle_stage_id, suburb_locality_id, town_city_id, territorial_authority_id, begin_lifespan, shape) VALUES(%s, %s, %s, %s, %s, %s, %s, now(), %s);"
        db.execute(sql, (building_id, self.capture_method_id, self.capture_source_id, self.lifecycle_stage_id, self.suburb, self.town, self.t_a, self.geom))
        self.cmb_capture_method.setCurrentIndex(0)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.setCurrentIndex(0)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_lifecycle_stage.setCurrentIndex(0)
        self.cmb_lifecycle_stage.setDisabled(1)
        self.cmb_ta.setCurrentIndex(0)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setCurrentIndex(0)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setCurrentIndex(0)
        self.cmb_suburb.setDisabled(1)
        self.btn_save.setDisabled(1)
        # empty saved_building_ids
        self.saved_building_ids = []

    def cancel_clicked(self):
        """
        Called when cancel button is clicked
        """
        # remove unsaved edits and stop editing layer
        iface.actionCancelEdits().trigger()
        # remove bulk_load_outlines from canvas
        if self.create_building_layer in self.layer_registry.layers.values():
            self.layer_registry.remove_layer(self.create_building_layer)
        # change frame
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))

    def reset_clicked(self):
        """
        Called when reset button is clicked
        """
        # remove current edit
        iface.actionCancelEdits().trigger()
        # restart editing
        iface.actionToggleEditing().trigger()
        # reset combo boxes and disable
        self.cmb_capture_method.setCurrentIndex(0)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.setCurrentIndex(0)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_lifecycle_stage.setCurrentIndex(0)
        self.cmb_lifecycle_stage.setDisabled(1)
        self.cmb_ta.setCurrentIndex(0)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setCurrentIndex(0)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setCurrentIndex(0)
        self.cmb_suburb.setDisabled(1)
        self.btn_save.setDisabled(1)
