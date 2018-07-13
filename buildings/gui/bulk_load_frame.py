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
from buildings.gui import bulk_load
from buildings.gui import comparisons
from buildings.gui import bulk_load_changes
from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import select_statements as select

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load.ui'))


class BulkLoadFrame(QFrame, FORM_CLASS):
    """
        Bulk Load outlines frame class
    """

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(BulkLoadFrame, self).__init__(parent)
        self.setupUi(self)
        # Frame fields
        self.layer_registry = layer_registry
        self.bulk_load_layer = QgsVectorLayer()
        self.territorial_auth = QgsVectorLayer()
        self.error_dialog = None
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
        # database setup
        self.db = db
        db.connect()
        # selection colour
        iface.mapCanvas().setSelectionColor(QColor("Yellow"))

        # Find current supplied dataset
        result = self.db._execute(select.dataset_count_processed_date_is_null)
        result = result.fetchall()[0][0]
        # if there is an unprocessed dataset
        if result > 1:
            # error
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n ---------------------- DATASET ERROR ---------'
                '----------------- \n\nThere are multiple not processed'
                ' datasets. Please fix database tables before continuing'
            )
            self.error_dialog.show()
            self.display_dataset_error()

        elif result == 1:
            p_result = self.db._execute(select.dataset_processed_date_is_null)
            self.current_dataset = p_result.fetchall()[0][0]
            self.lb_dataset_id.setText(str(self.current_dataset))
            self.add_outlines()
            self.display_current_bl_not_compared()

        # if all datasets are processed
        else:
            result2 = self.db._execute(select.dataset_count_transfer_date_is_null)
            result2 = result2.fetchall()[0][0]

            # if there is a processed but not transferred dataset
            if result > 1:
                # error
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n ---------------------- DATASET ERROR ---------'
                    '----------------- \n\nThere are multiple not transferred'
                    ' datasets. Please fix database tables before continuing'
                )
                self.error_dialog.show()
                self.display_dataset_error()

            elif result2 == 1:
                t_result = self.db._execute(select.dataset_transfer_date_is_null)
                self.current_dataset = t_result.fetchall()[0][0]
                self.lb_dataset_id.setText(str(self.current_dataset))
                self.add_outlines()
                self.display_not_published()

            # No current dataset is being worked on
            else:
                self.current_dataset = None
                self.lb_dataset_id.setText('None')
                self.display_no_bulk_load()

        # populate imagery cmb
        sql = 'SELECT area_title FROM buildings_reference.capture_source_area;'
        results = self.db._execute(sql)
        results = results.fetchall()
        for thing in results:
            self.cmb_capture_source_area.addItem(thing[0])
        # set up signals and slots
        self.rad_external_source.toggled.connect(
            partial(bulk_load.enable_external_bulk, self))
        self.ml_outlines_layer.currentIndexChanged.connect(
            partial(bulk_load.populate_external_fcb, self))
        self.btn_bl_save.clicked.connect(
            partial(self.bulk_load_save_clicked, True))
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)

        self.btn_compare_outlines.clicked.connect(
            partial(self.compare_outlines_clicked, True))

        self.rad_add.toggled.connect(self.canvas_add_outline)
        self.rad_edit.toggled.connect(self.canvas_edit_outlines)

        self.btn_alter_rel.clicked.connect(self.alter_relationships_clicked)

        self.btn_publish.clicked.connect(partial(self.publish_clicked, True))

        self.btn_exit.clicked.connect(self.exit_clicked)

    def display_dataset_error(self):
        """
            UI Display when there are multiple supplied datasets
        """
        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.grpb_bulk_load.hide()
        self.grpb_edits.hide()

        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def display_no_bulk_load(self):
        """
            UI Display When there is no Current dataset
        """
        self.grpb_bulk_load.show()
        bulk_load.populate_bulk_comboboxes(self)
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
        self.btn_bl_save.show()
        self.btn_bl_reset.show()

        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.grpb_edits.hide()

        self.btn_compare_outlines.setDisabled(1)
        self.cmb_capture_source_area.setDisabled(1)
        self.cmb_capture_source_area.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def display_data_exists(self):
        """
            Display setup when data has been bulk loaded
            - subfunction of: display_not_published &
              display_current_bl_not_compared
        """
        bulk_load.populate_bulk_comboboxes(self)
        bulk_load.load_current_fields(self)

        self.grpb_bulk_load.show()
        self.ml_outlines_layer.setDisabled(1)
        self.rad_external_source.setDisabled(1)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setDisabled(1)
        self.cmb_external_id.setDisabled(1)
        self.le_data_description.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_organisation.setDisabled(1)
        self.btn_bl_save.hide()
        self.btn_bl_reset.hide()

        self.grpb_edits.show()
        self.cmb_status.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_save.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)

    def display_not_published(self):
        """
            UI display when there is a dataset that hasn't been published
        """
        self.display_data_exists()
        self.btn_compare_outlines.setDisabled(1)
        self.cmb_capture_source_area.setDisabled(1)
        self.btn_publish.setEnabled(1)

    def display_current_bl_not_compared(self):
        """
            UI Display when there is a dataset that hasn't been compared
        """
        self.display_data_exists()
        self.btn_compare_outlines.setEnabled(1)
        self.cmb_capture_source_area.setEnabled(1)
        self.cmb_capture_source_area.setEnabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def add_outlines(self):
        """
            Add bulk load outlines of current dataset to canvas
        """
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.layer_registry.remove_layer(self.bulk_load_layer)
        self.bulk_load_layer = None
        # add the bulk_load_outlines to the layer registry
        self.bulk_load_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0} AND bulk_load_status_id != 3'.format(self.current_dataset))
        self.bulk_load_layer.loadNamedStyle(path + 'building_yellow.qml')
        iface.setActiveLayer(self.bulk_load_layer)
        self.bulk_load_removed = self.layer_registry.add_postgres_layer(
            'removed_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0} AND bulk_load_status_id = 3'.format(self.current_dataset))
        self.bulk_load_removed.loadNamedStyle(path + 'building_orange.qml')
        self.bulk_load_added = self.layer_registry.add_postgres_layer(
            'added_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0} AND bulk_load_status_id = 2'.format(self.current_dataset))
        self.bulk_load_added.loadNamedStyle(path + 'building_green.qml')

    def bulk_load_save_clicked(self, commit_status):
        """
            When bulk load outlines save clicked
        """
        bulk_load.bulk_load(self, commit_status)
        # find if adding was sucessful
        result = self.db._execute(select.dataset_count_both_dates_are_null)
        result = result.fetchall()[0][0]
        # if bulk loading completed without errors
        if result == 1:
            self.add_outlines()
            self.display_current_bl_not_compared()

    def bulk_load_reset_clicked(self):
        """
            When bulk Load reset clicked
        """
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_source.setChecked(False)

    def compare_outlines_clicked(self, commit_status):
        """
            When compare outlines clicked
        """
        comparisons.compare_outlines(self, commit_status)
        self.btn_publish.setEnabled(1)
        self.btn_compare_outlines.setDisabled(1)
        self.cmb_capture_source_area.setDisabled(1)
        self.btn_alter_rel.setEnabled(1)

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        # set change instance to added class
        try:
            self.btn_edit_save.clicked.disconnect()
        except Exception:
            pass
        try:
            self.btn_edit_reset.clicked.disconnect()
        except Exception:
            pass
        self.change_instance = bulk_load_changes.AddBulkLoad(self)
        # connect signals and slots
        self.btn_edit_save.clicked.connect(
            partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(
            self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(
            self.change_instance.edit_cancel_clicked)
        self.bulk_load_layer.featureAdded.connect(
            self.change_instance.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(
            self.change_instance.creator_feature_deleted)
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
        self.btn_edit_save.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        # add territorial Authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_outlines(self):
        """
            When edit outline radio button toggled
        """
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        # set change instance to edit class
        try:
            self.btn_edit_save.clicked.disconnect()
        except Exception:
            pass
        try:
            self.btn_edit_reset.clicked.disconnect()
        except Exception:
            pass
        self.change_instance = bulk_load_changes.EditBulkLoad(self)
        # set up signals and slots
        self.btn_edit_save.clicked.connect(
            partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(
            self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(
            self.change_instance.edit_cancel_clicked)
        self.bulk_load_layer.selectionChanged.connect(
            self.change_instance.selection_changed)
        self.bulk_load_layer.geometryChanged.connect(
            self.change_instance.feature_changed)
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
        self.btn_edit_save.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        # add territorial authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def alter_relationships_clicked(self):
        """
            When alter relationships button clicked
            open alter relationships frame
        """
        if self.change_instance is not None:
            self.change_instance.edit_cancel_clicked()
        self.db.close_connection()
        self.layer_registry.remove_all_layers()
        from buildings.gui.alter_building_relationships import AlterRelationships
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(
            self.layer_registry, self.current_dataset))
        from buildings.gui.alter_building_relationships import MultiLayerSelection
        canvas = iface.mapCanvas()
        self.tool = MultiLayerSelection(canvas)
        canvas.setMapTool(self.tool)

    def publish_clicked(self, commit_status):
        """
            When publish button clicked
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
        """
            Called when bulk load frame exit button clicked,
            Return to start up frame
        """
        iface.actionCancelEdits().trigger()
        self.layer_registry.remove_all_layers()
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(self.layer_registry))
