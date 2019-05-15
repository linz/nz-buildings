# -*- coding: utf-8 -*-

from functools import partial
import os

from PyQt4 import uic
from PyQt4.QtGui import QCompleter, QDialog
from PyQt4.QtCore import Qt, pyqtSlot

from qgis.utils import iface

from buildings.gui import bulk_load_changes
from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.utilities import layers

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'edit_dialog.ui'))


class EditDialog(QDialog, FORM_CLASS):

    def __init__(self, parent_frame, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.parent_frame = parent_frame
        self.layer_registry = self.parent_frame.layer_registry
        self.bulk_load_layer = self.parent_frame.bulk_load_layer
        self.current_dataset = self.parent_frame.current_dataset
        self.db = self.parent_frame.db
        self.territorial_auth = None

        self.init_dialog()

        # Bulk loadings & editing fields
        self.added_building_ids = []
        self.geom = None
        self.ids = []
        self.geoms = {}
        self.bulk_load_outline_id = None

        # processing class instances
        self.change_instance = None

        # initiate le_deletion_reason
        self.le_deletion_reason.setMaxLength(250)
        self.le_deletion_reason.setPlaceholderText('Reason for Deletion')
        self.completer_box()

        self.cmb_status.currentIndexChanged.connect(self.enable_le_deletion_reason)

    def init_dialog(self):
        self.layout_status.show()
        self.layout_capture_method.show()
        self.layout_general_info.show()
        self.cmb_status.setDisabled(1)
        self.le_deletion_reason.setDisabled(1)
        self.cmb_capture_method.setDisabled(1)
        self.cmb_capture_source.setDisabled(1)
        self.cmb_ta.setDisabled(1)
        self.cmb_town.setDisabled(1)
        self.cmb_suburb.setDisabled(1)
        self.btn_edit_save.setDisabled(1)
        self.btn_edit_reset.setDisabled(1)

    # connect dialog closed signal to exit editing
    def closeEvent(self, event):
        self.close_dialog()
        event.accept()

    def add_outline(self):
        self.setWindowTitle("Add Outline")
        self.added_building_ids = []
        self.geom = None
        self.tool = None
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
        self.layout_status.hide()
        self.layout_capture_method.show()
        self.layout_general_info.show()

        self.change_instance = bulk_load_changes.AddBulkLoad(self)
        # connect signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.bulk_load_layer.featureAdded.connect(self.change_instance.creator_feature_added)
        self.bulk_load_layer.featureDeleted.connect(self.change_instance.creator_feature_deleted)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.creator_geometry_changed)

        self.add_territorial_auth()

    def edit_attribute(self):
        """
            When edit outline radio button toggled
        """
        self.setWindowTitle("Edit Attribute")
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
        self.layout_status.show()
        self.layout_capture_method.show()
        self.layout_general_info.show()

        self.change_instance = bulk_load_changes.EditAttribute(self)
        # set up signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.bulk_load_layer.selectionChanged.connect(self.change_instance.selection_changed)

        self.add_territorial_auth()

    def edit_geometry(self):
        self.setWindowTitle("Edit Geometry")
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
        self.layout_status.hide()
        self.layout_capture_method.show()
        self.layout_general_info.hide()

        self.change_instance = bulk_load_changes.EditGeometry(self)
        # set up signals and slots
        self.btn_edit_save.clicked.connect(partial(self.change_instance.edit_save_clicked, True))
        self.btn_edit_reset.clicked.connect(self.change_instance.edit_reset_clicked)
        self.bulk_load_layer.geometryChanged.connect(self.change_instance.geometry_changed)

        self.add_territorial_auth()

    def close_dialog(self):
        """
            When 'x' is clicked
        """
        self.btn_edit_save.setEnabled(False)
        self.btn_edit_reset.setEnabled(False)

        self.change_instance = None
        self.added_building_ids = []
        self.geom = None
        self.ids = []
        self.building_outline_id = None
        self.geoms = {}

        self.parent_frame.edit_cancel_clicked()

    def add_territorial_auth(self):
        # add territorial Authority layer
        self.territorial_auth = self.layer_registry.add_postgres_layer(
            'territorial_authorities', 'territorial_authority',
            'shape', 'buildings_reference', '', ''
        )
        layers.style_layer(
            self.territorial_auth, {1: ['204,121,95', '0.3', 'dash', '5;2']})

    def remove_territorial_auth(self):
        if self.territorial_auth is not None:
            self.layer_registry.remove_layer(self.territorial_auth)

    def get_change_instance(self):
        return self.change_instance

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
