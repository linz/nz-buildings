# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QColor

import qgis
from qgis.utils import iface
from qgis.core import QgsVectorLayer

from buildings.utilities import database as db
from buildings.utilities import layers
from buildings.gui import bulkLoad
from buildings.gui import comparisons
from buildings.gui import changes

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
        self.change_instance = None
        self.bulk_load = bulkLoad.BulkLoad(self)
        self.comparison = comparisons.Comparisons(self)
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
        self.btn_bl_ok.clicked.connect(self.bulk_load_ok_clicked)
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)
        self.btn_compare_outlines.clicked.connect(self.compare_outlines_clicked)
        self.rad_add.toggled.connect(self.canvas_add_outline)
        self.rad_edit.toggled.connect(self.canvas_edit_outlines)
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
        self.bulk_load.populate_bulk_comboboxes()
        self.cmb_capture_method.setEnabled(1)
        self.cmb_capture_method.setCurrentIndex(0)
        self.cmb_organisation.setEnabled(1)
        self.cmb_organisation.setCurrentIndex(0)
        self.ml_outlines_layer.setEnabled(1)
        self.rad_external_source.setEnabled(1)
        self.rad_external_source.setChecked(False)
        self.cmb_capture_src_grp.setEnabled(1)
        self.cmb_capture_src_grp.setCurrentIndex(0)
        self.le_data_description.setEnabled(1)
        self.le_data_description.clear()

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
        self.bulk_load.populate_bulk_comboboxes()
        self.bulk_load.bulk_load_current_fields()

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
        self.bulk_load.populate_bulk_comboboxes()
        self.bulk_load.bulk_load_current_fields()

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

    def bulk_load_ok_clicked(self):
        self.bulk_load.bulk_load()
        # find if adding was sucessful
        sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL AND transfer_date is NULL;'
        result = self.db._execute(sql)
        result = result.fetchall()[0][0]
        if result == 1:
            self.add_outlines()
            self.display_current_bl_not_compared()

    def bulk_load_reset_clicked(self):
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_source.setChecked(False)

    def compare_outlines_clicked(self):
        self.comparison.compare_outlines()
        sql = 'SELECT buildings_bulk_load.create_building_relationship_view();'
        self.db._execute(sql)
        self.btn_publish.setEnabled(1)
        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setEnabled(1)

    def canvas_add_outline(self):
        iface.actionCancelEdits().trigger()
        # from buildings.gui import changes
        self.change_instance = changes.AddBulkLoad(self)
        self.btn_edit_ok.clicked.connect(self.change_instance.edit_ok_clicked)
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.change_instance.edit_cancel_clicked)
        iface.activeLayer().removeSelection()
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
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        # change style of TAs
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

        self.bulk_load_layer.featureAdded.connect(self.change_instance.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(self.change_instance.creator_feature_deleted)

    def canvas_edit_outlines(self):
        iface.actionCancelEdits().trigger()
        # from buildings.gui import changes
        self.change_instance = changes.EditBulkLoad(self)
        self.btn_edit_ok.clicked.connect(self.change_instance.edit_ok_clicked)
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.change_instance.edit_cancel_clicked)
        iface.activeLayer().removeSelection()
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
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        # change style of TAs
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})
        self.bulk_load_layer.selectionChanged.connect(self.change_instance.selection_changed)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.feature_changed)

    def alter_relationships_clicked(self):
        self.db.close_connection()
        self.layer_registry.remove_all_layers()
        from buildings.gui.alter_building_relationships import AlterRelationships
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(self.layer_registry))

    def publish_clicked(self, commit_status=True):
        # self.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.load_building_outlines(%s);'
        self.db._execute(sql, (self.current_dataset,))
        sql = 'SELECT buildings_lds.populate_buildings_lds();'
        self.db._execute(sql)
        # if commit_status:
        #     self.db.commit_open_cursor()
        self.display_no_bulk_load()
        self.current_dataset = None
        self.layer_registry.remove_all_layers()

    def exit_clicked(self):
        iface.actionCancelEdits().trigger()
        self.layer_registry.remove_all_layers()
        from buildings.gui.start_up import StartUpFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(StartUpFrame(self.layer_registry))
