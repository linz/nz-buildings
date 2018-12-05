# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt4.QtGui import QAction, QApplication, QColor, QCompleter, QFrame, QMenu, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui import bulk_load, bulk_load_changes, comparisons
from buildings.gui.alter_building_relationships import AlterRelationships
from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_bulk_load_select_statements as bulk_load_select,
                           buildings_reference_select_statements as reference_select)
from buildings.utilities import database as db, layers
from buildings.utilities.layers import LayerRegistry

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bulk_load.ui'))


class BulkLoadFrame(QFrame, FORM_CLASS):
    """Bulk Load outlines frame class"""

    closed = pyqtSignal()

    def __init__(self, dockwidget, parent=None):
        """Constructor."""

        super(BulkLoadFrame, self).__init__(parent)
        self.setupUi(self)
        # Frame fields
        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.bulk_load_layer = QgsVectorLayer()
        self.territorial_auth = QgsVectorLayer()
        # layer set up
        self.historic_layer = None
        self.bulk_load_layer = None
        self.territorial_auth = None
        self.error_dialog = None
        # Bulk loadings & editing fields
        self.added_building_ids = []
        self.geom = None
        self.ids = []
        self.geoms = {}
        self.bulk_load_outline_id = None
        self.edit_status = None
        # processing class instances
        self.change_instance = None
        # database setup
        self.db = db
        db.connect()
        # selection colour
        iface.mapCanvas().setSelectionColor(QColor('Yellow'))
        # set up confirmation message box
        self.msgbox_bulk_load = self.confirmation_dialog_box('bulk load')
        self.msgbox_compare = self.confirmation_dialog_box('compare')
        self.msgbox_publish = self.confirmation_dialog_box('publish')
        self.cb_bulk_load.hide()

        # Find current supplied dataset
        result = self.db._execute(bulk_load_select.supplied_dataset_count_processed_date_is_null)
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
            p_result = self.db._execute(bulk_load_select.supplied_dataset_processed_date_is_null)
            self.current_dataset = p_result.fetchall()[0][0]
            self.lb_dataset_id.setText(str(self.current_dataset))
            self.add_outlines()
            self.display_current_bl_not_compared()
            self.cb_bulk_load.show()
            self.cb_bulk_load.setChecked(True)

        # if all datasets are processed
        else:
            result2 = self.db._execute(bulk_load_select.supplied_dataset_count_transfer_date_is_null)
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
                t_result = self.db._execute(bulk_load_select.supplied_dataset_transfer_date_is_null)
                self.current_dataset = t_result.fetchall()[0][0]
                self.lb_dataset_id.setText(str(self.current_dataset))
                self.add_outlines()
                self.display_not_published()
                self.cb_bulk_load.show()
                self.cb_bulk_load.setChecked(True)

            # No current dataset is being worked on
            else:
                self.current_dataset = None
                self.lb_dataset_id.setText('None')
                self.display_no_bulk_load()

        # initiate le_deletion_reason
        self.le_deletion_reason.setMaxLength(250)
        self.le_deletion_reason.setPlaceholderText('Reason for Deletion')
        self.completer_box()

        # initiate le_data_description
        self.le_data_description.setMaxLength(250)
        self.le_data_description.setPlaceholderText('Data Description')

        self.menu = QMenu()
        self.action_add_outline = QAction('Add Outline', self.menu)
        self.action_edit_attribute = QAction('Edit Attribute', self.menu)
        self.action_edit_geometry = QAction('Edit Geometry', self.menu)
        self.menu.addAction(self.action_add_outline)
        self.menu.addSeparator()
        self.menu.addAction(self.action_edit_attribute)
        self.menu.addAction(self.action_edit_geometry)
        self.menu.setFixedWidth(300)
        self.tbtn_edits.setMenu(self.menu)
        self.layout_status.hide()
        self.layout_capture_method.hide()
        self.layout_general_info.hide()

        self.tbtn_edits.triggered.connect(self.tbtn_edits_triggered)
        self.tbtn_edits.clicked.connect(self.tbtn_edits_clicked)

        # set up signals and slots
        self.rad_external_id.toggled.connect(
            partial(bulk_load.enable_external_bulk, self))
        self.ml_outlines_layer.currentIndexChanged.connect(
            partial(bulk_load.populate_external_fcb, self))
        self.btn_bl_save.clicked.connect(
            partial(self.bulk_load_save_clicked, True))
        self.btn_bl_reset.clicked.connect(self.bulk_load_reset_clicked)

        self.btn_compare_outlines.clicked.connect(
            partial(self.compare_outlines_clicked, True))

        self.cmb_status.currentIndexChanged.connect(
            self.enable_le_deletion_reason)

        self.btn_alter_rel.clicked.connect(self.alter_relationships_clicked)
        self.btn_publish.clicked.connect(partial(self.publish_clicked, True))
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.cb_bulk_load.clicked.connect(self.cb_bulk_load_clicked)

        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.dontremovefunc)

    def confirmation_dialog_box(self, button_text):
        return QMessageBox(QMessageBox.Question, button_text.upper(),
                           'Are you sure you want to %s outlines?' % button_text, buttons=QMessageBox.No | QMessageBox.Yes)

    def confirm(self, msgbox):
        reply = msgbox.exec_()
        if reply == QMessageBox.Yes:
            return True
        return False

    def display_dataset_error(self):
        """UI Display when there are multiple supplied datasets."""

        self.current_dataset = None
        self.lb_dataset_id.setText('None')

        self.grpb_bulk_load.hide()
        self.grpb_edits.hide()

        self.btn_compare_outlines.setDisabled(1)
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def display_no_bulk_load(self):
        """UI Display When there is no Current dataset."""

        self.grpb_bulk_load.show()
        bulk_load.populate_bulk_comboboxes(self)
        self.ml_outlines_layer.setEnabled(1)
        self.rad_external_id.setEnabled(1)
        self.rad_external_id.setChecked(False)
        self.fcb_external_id.setDisabled(1)
        self.cmb_capture_src_grp.setEnabled(1)
        self.cmb_capture_src_grp.setCurrentIndex(0)
        self.cmb_external_id.setEnabled(1)
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
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

        self.add_historic_outlines()

        self.l_cs_area_title.setText('')

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
        self.rad_external_id.setDisabled(1)
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
        self.le_deletion_reason.setDisabled(1)
        self.cmb_capture_method_2.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_save.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)
        self.btn_edit_cancel.setDisabled(1)

        sql = reference_select.capture_source_area_name_by_supplied_dataset
        area_id = self.db._execute(sql, (self.current_dataset,))
        area_id = area_id.fetchall()
        if area_id is not None:
            self.l_cs_area_title.setText(area_id[0][0])
        else:
            self.l_cs_area_title.setText('')

    def display_not_published(self):
        """
            UI display when there is a dataset that hasn't been published.
        """
        self.display_data_exists()
        self.btn_compare_outlines.setDisabled(1)
        self.btn_publish.setEnabled(1)

    def display_current_bl_not_compared(self):
        """
            UI Display when there is a dataset that hasn't been compared.
        """

        self.display_data_exists()
        self.btn_compare_outlines.setEnabled(1)
        sql = reference_select.capture_source_area_name_by_supplied_dataset
        area_id = self.db._execute(sql, (self.current_dataset,))
        if area_id is not None:
            self.area_id = area_id.fetchall()
        if len(self.area_id) > 0:
            self.area_id = self.area_id[0][0]
            self.l_cs_area_title.setText(self.area_id)
        else:
            self.area_id = None
            self.l_cs_area_title.setText('')
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n ---------------------- NO CAPTURE SOURCE AREA ---------'
                '----------------- \n\nThere is no area id, please fix in database'
            )
            self.error_dialog.show()
            self.display_dataset_error()
            self.btn_compare_outlines.setDisabled(1)
            return
        self.btn_alter_rel.setDisabled(1)
        self.btn_publish.setDisabled(1)

    def add_outlines(self):
        """
            Add bulk load outlines of current dataset to canvas.
        """

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        # add the bulk_load_outlines to the layer registry
        self.bulk_load_layer = self.layer_registry.add_postgres_layer(
            'bulk_load_outlines', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '',
            'supplied_dataset_id = {0}'.format(self.current_dataset))
        self.bulk_load_layer.loadNamedStyle(path + 'building_editing.qml')
        iface.setActiveLayer(self.bulk_load_layer)

    def add_historic_outlines(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        self.historic_layer = self.layer_registry.add_postgres_layer(
            'loaded_datasets', 'bulk_load_outlines',
            'shape', 'buildings_bulk_load', '', '')
        self.historic_layer.loadNamedStyle(path + 'building_historic.qml')

    @pyqtSlot(bool)
    def cb_bulk_load_clicked(self, checked):
        group = QgsProject.instance().layerTreeRoot().findGroup('Building Tool Layers')
        if checked:
            group.setVisible(Qt.Checked)
        else:
            group.setVisible(Qt.Unchecked)

    @pyqtSlot(bool)
    def bulk_load_save_clicked(self, commit_status):
        """
            When bulk load outlines save clicked
        """
        if self.confirm(self.msgbox_bulk_load):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            bulk_load.bulk_load(self, commit_status)
            # find if adding was sucessful
            result = self.db._execute(bulk_load_select.supplied_dataset_count_both_dates_are_null)
            result = result.fetchall()[0][0]
            # if bulk loading completed without errors
            if result == 1:
                QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.dontremovefunc)
                self.layer_registry.remove_layer(self.historic_layer)
                QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.dontremovefunc)
                self.add_outlines()
                self.display_current_bl_not_compared()
            QApplication.restoreOverrideCursor()
            self.cb_bulk_load.show()

    @pyqtSlot()
    def bulk_load_reset_clicked(self):
        """
            When bulk Load reset clicked
        """
        self.cmb_capture_method.setCurrentIndex(0)
        self.ml_outlines_layer.setCurrentIndex(0)
        self.cmb_organisation.setCurrentIndex(0)
        self.le_data_description.clear()
        self.rad_external_id.setChecked(False)

    @pyqtSlot(bool)
    def compare_outlines_clicked(self, commit_status):
        """
            When compare outlines clicked
        """
        if self.confirm(self.msgbox_compare):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            comparisons.compare_outlines(self, commit_status)
            self.btn_publish.setEnabled(1)
            self.btn_compare_outlines.setDisabled(1)
            self.btn_alter_rel.setEnabled(1)
            QApplication.restoreOverrideCursor()

    @pyqtSlot(QAction)
    def tbtn_edits_triggered(self, action):
        """
            When edit tool button triggered
        """
        self.tbtn_edits.setDefaultAction(action)
        text = action.text()
        self.enter_edit_mode(text)

    @pyqtSlot()
    def tbtn_edits_clicked(self):
        """
            When edit tool button clicked
        """
        text = self.tbtn_edits.text()
        if text != 'Choose Edit Mode':
            self.enter_edit_mode(text)
        else:
            self.tbtn_edits.showMenu()

    def enter_edit_mode(self, text):

        self.btn_edit_reset.setEnabled(True)
        self.btn_edit_cancel.setEnabled(True)
        self.tbtn_edits.setEnabled(False)
        self.tbtn_edits.setStyleSheet('QToolButton {color: green;}')
        if text == 'Add Outline':
            self.canvas_add_outline()
        elif text == 'Edit Attribute':
            self.canvas_edit_attribute()
        elif text == 'Edit Geometry':
            self.canvas_edit_geometry()

    def canvas_add_outline(self):
        """
            When add outline radio button toggled
        """
        self.added_building_ids = []
        self.geom = None
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        # set change instance to added class
        try:
            self.btn_edit_save.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_reset.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_cancel.clicked.disconnect()
        except TypeError:
            pass
        self.layout_status.hide()
        self.layout_capture_method.show()
        self.layout_general_info.show()

        self.change_instance = bulk_load_changes.AddBulkLoad(self)
        # connect signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.edit_cancel_clicked)
        self.bulk_load_layer.featureAdded.connect(self.change_instance.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(self.change_instance.creator_feature_deleted)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.creator_geometry_changed)

        # add territorial Authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(
            self.territorial_auth, {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_attribute(self):
        """
            When edit outline radio button toggled
        """
        self.ids = []
        self.building_outline_id = None
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        try:
            self.btn_edit_save.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_reset.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_cancel.clicked.disconnect()
        except TypeError:
            pass
        self.layout_status.show()
        self.layout_capture_method.show()
        self.layout_general_info.show()

        self.change_instance = bulk_load_changes.EditAttribute(self)
        # set up signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.edit_cancel_clicked)
        self.bulk_load_layer.selectionChanged.connect(self.change_instance.selection_changed)

        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def canvas_edit_geometry(self):
        self.geoms = {}
        iface.actionCancelEdits().trigger()
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        try:
            self.btn_edit_save.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_reset.clicked.disconnect()
        except TypeError:
            pass
        try:
            self.btn_edit_cancel.clicked.disconnect()
        except TypeError:
            pass
        self.layout_status.hide()
        self.layout_capture_method.show()
        self.layout_general_info.hide()

        self.change_instance = bulk_load_changes.EditGeometry(self)
        # set up signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.btn_edit_cancel.clicked.connect(self.edit_cancel_clicked)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.geometry_changed)
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(self.territorial_auth,
                           {1: ['204,121,95', '0.3', 'dash', '5;2']})

    @pyqtSlot()
    def edit_cancel_clicked(self):
        """
            When cancel clicked
        """
        if len(QgsMapLayerRegistry.instance().mapLayersByName('bulk_load_outlines')) > 0:
            if isinstance(self.change_instance, bulk_load_changes.EditAttribute):
                try:
                    self.bulk_load_layer.selectionChanged.disconnect(self.change_instance.selection_changed)
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.EditGeometry):
                try:
                    self.bulk_load_layer.geometryChanged.disconnect()
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.AddBulkLoad):
                try:
                    self.bulk_load_layer.featureAdded.disconnect()
                except TypeError:
                    pass
                try:
                    self.bulk_load_layer.featureDeleted.disconnect()
                except TypeError:
                    pass
                try:
                    self.bulk_load_layer.geometryChanged.disconnect()
                except TypeError:
                    pass

        self.btn_edit_save.setEnabled(False)
        self.btn_edit_reset.setEnabled(False)
        self.btn_edit_cancel.setEnabled(False)
        self.tbtn_edits.setEnabled(True)
        self.tbtn_edits.setStyleSheet('QToolButton {color: black;}')

        iface.actionCancelEdits().trigger()
        # reload layers
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.dontremovefunc)
        self.layer_registry.remove_layer(self.territorial_auth)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.dontremovefunc)
        # hide comboboxes
        self.layout_status.hide()
        self.layout_capture_method.hide()
        self.layout_general_info.hide()
        # reset adding outlines
        self.added_building_ids = []
        self.geom = None
        # reset editing attribute
        self.ids = []
        self.building_outline_id = None
        # reset editing geomtry
        self.geoms = {}
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

    def completer_box(self):
        """
            Box automatic completion
        """

        reasons = self.db._execute(bulk_load_select.deletion_description_value)
        reason_list = [row[0] for row in reasons.fetchall()]
        # Fill the search box
        self.completer = QCompleter(reason_list)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.le_deletion_reason.setCompleter(self.completer)

    @pyqtSlot()
    def enable_le_deletion_reason(self):
        if self.cmb_status.currentText() == 'Deleted During QA':
            self.le_deletion_reason.setEnabled(1)
            self.le_deletion_reason.setFocus()
            self.le_deletion_reason.selectAll()
        else:
            self.le_deletion_reason.setDisabled(1)
            self.le_deletion_reason.clear()

    @pyqtSlot()
    def alter_relationships_clicked(self):
        """
            When alter relationships button clicked
            open alter relationships frame
        """
        if self.change_instance is not None:
            self.edit_cancel_clicked()
        self.db.close_connection()
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.dontremovefunc)
        self.layer_registry.remove_layer(self.bulk_load_layer)
        if self.territorial_auth is not None:
            self.layer_registry.remove_layer(self.territorial_auth)
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(AlterRelationships(
            dw, self.current_dataset))

    @pyqtSlot(bool)
    def publish_clicked(self, commit_status):
        """
            When publish button clicked
        """

        if self.confirm(self.msgbox_publish):
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if self.change_instance is not None:
                self.edit_cancel_clicked()
            self.db.open_cursor()
            sql = 'SELECT buildings_bulk_load.load_building_outlines(%s);'
            self.db.execute_no_commit(sql, (self.current_dataset,))
            if commit_status:
                self.db.commit_open_cursor()
            self.display_no_bulk_load()
            self.current_dataset = None
            self.lb_dataset_id.setText('None')
            QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.dontremovefunc)
            self.layer_registry.remove_layer(self.bulk_load_layer)
            self.add_historic_outlines()
            QApplication.restoreOverrideCursor()
            self.cb_bulk_load.hide()
            QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.dontremovefunc)

    @pyqtSlot()
    def exit_clicked(self):
        """
            Called when bulk load frame exit button clicked.
        """
        self.edit_cancel_clicked()
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
            Clean up and remove the bulk load frame.
        """
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.dontremovefunc)
        iface.actionCancelEdits().trigger()
        if self.historic_layer is not None:
            self.layer_registry.remove_layer(self.historic_layer)
        if self.bulk_load_layer is not None:
            self.layer_registry.remove_layer(self.bulk_load_layer)
        if self.territorial_auth is not None:
            self.layer_registry.remove_layer(self.territorial_auth)
        from buildings.gui.menu_frame import MenuFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot(str)
    def dontremovefunc(self, layerids):
        self.layer_registry.update_layers()
        if 'bulk_load_outlines' in layerids or 'territorial_authorities' in layerids:
            self.btn_edit_save.setDisabled(1)
            self.btn_edit_reset.setDisabled(1)
            self.btn_edit_cancel.setDisabled(1)
            self.tbtn_edits.setDisabled(1)
            self.btn_compare_outlines.setDisabled(1)
            self.btn_alter_rel.setDisabled(1)
            self.btn_publish.setDisabled(1)
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            return

        if 'loaded_datasets' in layerids:
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            # disable bulk loading buttons
            self.btn_bl_save.setDisabled(1)
            self.btn_bl_reset.setDisabled(1)
            return
