# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QColor

import qgis
from qgis.utils import iface
from qgis.core import QgsVectorLayer

from functools import partial

from buildings.utilities import database as db
from buildings.utilities import layers
from buildings.gui import bulkLoad
from buildings.gui import comparisons
from buildings.gui import bulk_load_changes

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load.ui'))


class BulkLoadFrame(QFrame, FORM_CLASS):
    """ Bulk Load outlines frame class
    """

    def __init__(self, layer_registry, parent=None):
        """Constructor"""
        super(BulkLoadFrame, self).__init__(parent)
        self.setupUi(self)
        # Frame fields
        self.layer_registry = layer_registry
        self.bulk_load_layer = QgsVectorLayer()
        self.territorial_auth = QgsVectorLayer()
        # Bulk loadings & editing fields
        self.added_building_ids = []
        self.ids = []
        self.geoms = {}
        self.bulk_load_outline_id = None
        self.select_changed = False
        self.geom_changed = False
        self.edit_status = None
        # processing class instances
        self.change_instance = None
        self.bulk_load = bulkLoad.BulkLoad(self)
        self.comparison = comparisons.Comparisons(self)
        # database setup
        self.db = db
        db.connect()
        # selection colour
        iface.mapCanvas().setSelectionColor(QColor("Yellow"))

        # Find current supplied dataset
        sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL;'
        result = self.db._execute(sql)
        result = result.fetchall()[0][0]

        # if there is an unprocessed dataset
        if result == 1:
            sql = 'SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL;'
            p_result = self.db._execute(sql)
            self.current_dataset = p_result.fetchall()[0][0]
            self.lb_dataset_id.setText(str(self.current_dataset))
            self.add_outlines()
            self.display_current_bl_not_compared()

        # if all datasets are processed
        else:
            sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE transfer_date is NULL;'
            result2 = self.db._execute(sql)
            result2 = result2.fetchall()[0][0]

            # if there is a processed but not transerred dataset
            if result2 == 1:
                sql = 'SELECT supplied_dataset_id FROM buildings_bulk_load.supplied_datasets WHERE transfer_date is NULL;'
                t_result = self.db._execute(sql)
                self.current_dataset = t_result.fetchall()[0][0]
                self.lb_dataset_id.setText(str(self.current_dataset))
                self.add_outlines()
                self.display_not_published()

            # No current dataset is being worked on
            else:
                self.current_dataset = None
                self.lb_dataset_id.setText('None')
                self.display_no_bulk_load()

        # set up signals and slots
        self.btn_bl_ok.clicked.connect(partial(self.bulk_load_ok_clicked, True))
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)

        self.btn_compare_outlines.clicked.connect(partial(self.compare_outlines_clicked, True))

        self.rad_add.toggled.connect(self.canvas_add_outline)
        self.rad_edit.toggled.connect(self.canvas_edit_outlines)

        self.btn_alter_rel.clicked.connect(self.alter_relationships_clicked)

        self.btn_publish.clicked.connect(partial(self.publish_clicked, True))

        self.btn_exit.clicked.connect(self.exit_clicked)

    def display_no_bulk_load(self):
        """UI Display When there is no Current dataset
        """
        self.bulk_load.populate_bulk_comboboxes()
        self.ml_outlines_layer.setEnabled(1)
        self.rad_external_source.setEnabled(1)
        self.rad_external_source.setChecked(False)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setEnabled(1)
        self.cmb_capture_src_grp.setCurrentIndex(0)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setEnabled(1)
        self.le_data_description.clear()
        self.cmb_capture_method.setEnabled(1)
        self.cmb_capture_method.setCurrentIndex(0)
        self.cmb_organisation.setEnabled(1)
        self.cmb_organisation.setCurrentIndex(0)
        self.btn_bl_ok.show()
        self.btn_bl_reset.show()

        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.grpb_edits.hide()

        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def display_not_published(self):
        """UI display when there is a dataset that hasn't been published
        """
        self.bulk_load.populate_bulk_comboboxes()
        self.bulk_load.load_current_fields()

        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_source.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.btn_bl_ok.hide()
        self.btn_bl_reset.hide()

        self.btn_compare_outlines.setDisabled(1)

        self.grpb_edits.show()
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.btn_edit_ok.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)

        self.btn_publish.setEnabled(1)

    def display_current_bl_not_compared(self):
        """UI Display when there is a dataset that hasn't been compared
        """
        self.bulk_load.populate_bulk_comboboxes()
        self.bulk_load.load_current_fields()

        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_source.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.btn_bl_ok.hide()
        self.btn_bl_reset.hide()

        self.grpb_edits.show()
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_ok.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)

        self.btn_compare_outlines.setEnabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def add_outlines(self):
        """Add bulk load outlines of current dataset to canvas
        """
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.layer_registry.remove_layer(self.bulk_load_layer)
        self.bulk_load_layer = None
        # add the bulk_load_outlines to the layer registry
        self.bulk_load_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.current_dataset))
        self.bulk_load_layer.loadNamedStyle(path + 'building_yellow.qml')
        iface.setActiveLayer(self.bulk_load_layer)

    def bulk_load_ok_clicked(self, commit_status):
        """ When bulk load outlines ok clicked
        """
        self.bulk_load.bulk_load(commit_status)
        # find if adding was sucessful
        sql = 'SELECT count(*) FROM buildings_bulk_load.supplied_datasets WHERE processed_date is NULL AND transfer_date is NULL;'
        result = self.db._execute(sql)
        result = result.fetchall()[0][0]
        # if bulk loading completed without errors
        if result == 1:
            self.add_outlines()
            self.display_current_bl_not_compared()

    def bulk_load_reset_clicked(self):
        """ When bulk Load reset clicked
        """
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_source.setChecked(False)

    def compare_outlines_clicked(self, commit_status):
        """ When compare outlines clicked
        """
        self.comparison.compare_outlines(commit_status)
        self.btn_publish.setEnabled(1)
        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setEnabled(1)

    def canvas_add_outline(self):
        """ When add outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        # set change instance to added class
        self.change_instance = bulk_load_changes.AddBulkLoad(self)
        # connect signals and slots
        self.btn_edit_ok.clicked.connect(partial(self.change_instance.edit_ok_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.change_instance.edit_cancel_clicked)
        self.bulk_load_layer.featureAdded.connect(self.change_instance.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(self.change_instance.creator_feature_deleted)
        # layer and UI setup
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
        # add territorial Authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_outlines(self):
        """ When edit outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        # set change instance to edit class
        self.change_instance = bulk_load_changes.EditBulkLoad(self)
        # set up signals and slots
        self.btn_edit_ok.clicked.connect(partial(self.change_instance.edit_ok_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.change_instance.edit_cancel_clicked)
        self.bulk_load_layer.selectionChanged.connect(self.change_instance.selection_changed)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.feature_changed)
        # layer and UI setup
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
        # add territorial authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def alter_relationships_clicked(self):
        """ When alter relationships button clicked
        """
        if self.change_instance is not None:
            self.change_instance.edit_cancel_clicked()
        self.db.close_connection()
        self.layer_registry.remove_all_layers()
        from buildings.gui.alter_building_relationships import AlterRelationships
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(self.layer_registry, self.current_dataset))

    def publish_clicked(self, commit_status):
        """ When publish button clicked
        """
        if self.change_instance is not None:
            self.change_instance.edit_cancel_clicked()
        self.db.open_cursor()
        sql = 'SELECT buildings_bulk_load.load_building_outlines(%s);'
        self.db.execute_no_commit(sql, (self.current_dataset,))
        sql = 'SELECT buildings_lds.populate_buildings_lds();'
        self.db.execute_no_commit(sql)
        if commit_status:
            self.db.commit_open_cursor()
        self.display_no_bulk_load()
        self.current_dataset = None
        self.lb_dataset_id.setText('None')
        self.layer_registry.remove_all_layers()

    def exit_clicked(self):
        """Called when bulk load frame exit button clicked,
           Return to start up frame
        """
        iface.actionCancelEdits().trigger()
        self.layer_registry.remove_all_layers()
        from buildings.gui.start_up import StartUpFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(StartUpFrame(self.layer_registry))
