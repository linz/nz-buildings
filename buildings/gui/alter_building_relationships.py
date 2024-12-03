# -*- coding: utf-8 -*-

import os.path
from ast import literal_eval
from functools import partial

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QAction,
    QFrame,
    QHeaderView,
    QListWidgetItem,
    QMessageBox,
    QTableWidgetItem,
)
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtCore import QSize, Qt
from qgis.core import QgsProject
from qgis.gui import QgsMessageBar
from qgis.utils import Qgis, iface

from buildings.gui import bulk_load_changes
from buildings.gui.error_dialog import ErrorDialog
from buildings.gui.edit_dialog import EditDialog
from buildings.gui.deletion_reason_dialog import DeletionReason
from buildings.utilities import database as db
from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.sql import buildings_select_statements as buildings_select
from buildings.sql import general_select_statements as general_select
from buildings.utilities import circle_tool
from buildings.utilities.layers import LayerRegistry
from buildings.utilities.multi_layer_selection import MultiLayerSelection
from buildings.utilities.point_tool import PointTool

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "alter_building_relationship.ui")
)


class AlterRelationships(QFrame, FORM_CLASS):
    def __init__(self, dockwidget, current_dataset, parent=None):
        """Constructor."""

        # Attributes set in subsequent methods
        self.message_bar_edit = None
        self.message_bar_qa = None
        self.add_action = None
        self.edit_geom_action = None
        self.edit_attrs_action = None
        self.lyr_related_existing = None
        self.lyr_related_bulk_load = None
        self.lyr_matched_existing = None
        self.lyr_matched_bulk_load = None
        self.lyr_removed_existing = None
        self.lyr_added_bulk_load = None
        self.lyr_related_bulk_load_in_edit = None
        self.lyr_related_existing_in_edit = None
        self.lyr_matched_bulk_load_in_edit = None
        self.lyr_matched_existing_in_edit = None
        self.lyr_removed_existing_in_edit = None
        self.lyr_added_bulk_load_in_edit = None
        self.lyr_existing = None
        self.lyr_bulk_load = None
        self.lyr_facilities = None
        self.msgbox = None
        self.tool = None
        self.reason_text = None
        self.circle_tool = None
        self.polyline = None
        self.circle_action = None

        super(AlterRelationships, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.valid_building_uses = {
            None: "None",
            **{
                use_id: use
                for use_id, use in self.db.execute_return(
                    "SELECT * FROM buildings.use;"
                ).fetchall()
            },
        }

        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.current_dataset = current_dataset
        self.error_dialog = None
        self.autosave = False
        self.delete = False
        self.deletion_reason = None
        self.zoom = True
        self.attributes_changed = False

        self.frame_setup()
        self.layers_setup()
        self.edit_dialog = EditDialog(self)
        self.change_instance = None
        self.toolbar_setup()
        self.connect_signals()

    def frame_setup(self):

        self.message_bar_edit = QgsMessageBar()
        self.layout_msg_bar_edit.addWidget(self.message_bar_edit)
        self.message_bar_qa = QgsMessageBar()
        self.layout_msg_bar_qa.addWidget(self.message_bar_qa)

        self.btn_qa_not_removed.setIcon(
            QIcon(os.path.join(__location__, "..", "icons", "match.png"))
        )
        self.btn_next.setIcon(
            QIcon(os.path.join(__location__, "..", "icons", "next.png"))
        )
        self.btn_maptool.setIcon(
            QIcon(
                os.path.join(
                    __location__, "..", "icons", "multi_layer_selection_tool.png"
                )
            )
        )

        self.cbox_use.insertItems(0, self.valid_building_uses.values())

        self.maptool_clicked()
        self.reset_buttons()
        self.btn_next.setEnabled(False)
        self.qa_button_set_enable(False)
        self.btn_qa_not_removed.setEnabled(False)
        self.populate_cmb_relationship()
        self.setup_message_box()

    def layers_setup(self):
        self.add_building_lyrs()
        self.repaint_view()
        self.clear_layer_filter()
        iface.setActiveLayer(self.lyr_bulk_load)

    def toolbar_setup(self):

        if "Add Outline" not in (
            action.text() for action in iface.building_toolbar.actions()
        ):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "plus.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.add_action = QAction(icon, "Add Outline", iface.building_toolbar)
            iface.registerMainWindowAction(self.add_action, "Ctrl+1")
            self.add_action.triggered.connect(self.canvas_add_outline)
            iface.building_toolbar.addAction(self.add_action)

        if "Edit Geometry" not in (
            action.text() for action in iface.building_toolbar.actions()
        ):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "edit_geometry.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_geom_action = QAction(
                icon, "Edit Geometry", iface.building_toolbar
            )
            iface.registerMainWindowAction(self.edit_geom_action, "Ctrl+2")
            self.edit_geom_action.triggered.connect(self.canvas_edit_geometry)
            iface.building_toolbar.addAction(self.edit_geom_action)

        if "Edit Attributes" not in (
            action.text() for action in iface.building_toolbar.actions()
        ):
            image_dir = os.path.join(__location__, "..", "icons")
            icon_path = os.path.join(image_dir, "edit_attributes.png")
            icon = QIcon()
            icon.addFile(icon_path, QSize(8, 8))
            self.edit_attrs_action = QAction(
                icon, "Edit Attributes", iface.building_toolbar
            )
            iface.registerMainWindowAction(self.edit_attrs_action, "Ctrl+3")
            self.edit_attrs_action.triggered.connect(self.canvas_edit_attribute)
            iface.building_toolbar.addAction(self.edit_attrs_action)

            iface.building_toolbar.show()

    def connect_signals(self):

        self.dockwidget.closed.connect(self.on_dockwidget_closed)

        self.btn_qa_okay.clicked.connect(
            partial(self.btn_qa_status_clicked, "Okay", commit_status=True)
        )
        self.btn_qa_pending.clicked.connect(
            partial(self.btn_qa_status_clicked, "Pending", commit_status=True)
        )
        self.btn_qa_refer2supplier.clicked.connect(
            partial(self.btn_qa_status_clicked, "Refer to Supplier", commit_status=True)
        )
        self.btn_qa_not_checked.clicked.connect(
            partial(self.btn_qa_status_clicked, "Not Checked", commit_status=True)
        )
        self.btn_qa_not_removed.clicked.connect(
            partial(self.btn_qa_status_clicked, "Not Removed", commit_status=True)
        )
        self.btn_next.clicked.connect(self.zoom_to_next)
        self.btn_maptool.clicked.connect(self.maptool_clicked)
        self.btn_unlink.clicked.connect(
            partial(self.unlink_clicked, commit_status=True)
        )
        self.btn_matched.clicked.connect(
            partial(self.matched_clicked, commit_status=True)
        )
        self.btn_related.clicked.connect(
            partial(self.related_clicked, commit_status=True)
        )
        self.btn_delete.clicked.connect(
            partial(self.delete_clicked, commit_status=True)
        )
        self.btn_copy_from_existing.clicked.connect(
            self.on_click_btn_copy_from_existing
        )
        self.btn_set_attributes.clicked.connect(self.on_click_btn_set_attributes)
        self.btn_delete_attributes.clicked.connect(self.on_click_btn_delete_attributes)
        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.cmb_relationship.currentIndexChanged.connect(
            self.cmb_relationship_current_index_changed
        )
        self.tbl_relationship.itemSelectionChanged.connect(
            self.tbl_relationship_item_selection_changed
        )

        self.cb_lyr_bulk_load.stateChanged.connect(self.cb_lyr_bulk_load_state_changed)
        self.cb_lyr_existing.stateChanged.connect(self.cb_lyr_existing_state_changed)

        self.cb_autosave.stateChanged.connect(self.cb_autosave_state_changed)

        QgsProject.instance().layerWillBeRemoved.connect(self.layers_removed)

    def add_building_lyrs(self):
        """Add building layers"""

        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles/")

        self.lyr_facilities = self.layer_registry.add_postgres_layer(
            "facilities",
            "facilities",
            "shape",
            "facilities",
            "",
            "",
        )
        self.lyr_facilities.loadNamedStyle(path + "facilities.qml")

        self.lyr_related_existing = self.layer_registry.add_postgres_layer(
            "related_existing_outlines",
            "related_existing_outlines",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_related_existing.loadNamedStyle(path + "building_purple_existing.qml")

        self.lyr_related_bulk_load = self.layer_registry.add_postgres_layer(
            "related_bulk_load_outlines",
            "related_bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_related_bulk_load.loadNamedStyle(path + "building_purple.qml")

        self.lyr_matched_existing = self.layer_registry.add_postgres_layer(
            "matched_existing_outlines",
            "matched_existing_outlines",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_matched_existing.loadNamedStyle(path + "building_blue_existing.qml")

        self.lyr_matched_bulk_load = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_outlines",
            "matched_bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_matched_bulk_load.loadNamedStyle(path + "building_blue.qml")

        self.lyr_removed_existing = self.layer_registry.add_postgres_layer(
            "removed_outlines",
            "removed_outlines",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_removed_existing.loadNamedStyle(path + "building_red_existing.qml")

        self.lyr_added_bulk_load = self.layer_registry.add_postgres_layer(
            "added_outlines",
            "added_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_added_bulk_load.loadNamedStyle(path + "building_green.qml")

        self.lyr_related_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "related_bulk_load_in_edit",
            "bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_related_bulk_load_in_edit.loadNamedStyle(path + "building_purple.qml")

        self.lyr_related_existing_in_edit = self.layer_registry.add_postgres_layer(
            "related_existing_in_edit",
            "existing_subset_extracts",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_related_existing_in_edit.loadNamedStyle(path + "building_purple.qml")

        self.lyr_matched_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "matched_bulk_load_in_edit",
            "bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_matched_bulk_load_in_edit.loadNamedStyle(path + "building_blue.qml")

        self.lyr_matched_existing_in_edit = self.layer_registry.add_postgres_layer(
            "matched_existing_in_edit",
            "existing_subset_extracts",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_matched_existing_in_edit.loadNamedStyle(path + "building_blue.qml")

        self.lyr_removed_existing_in_edit = self.layer_registry.add_postgres_layer(
            "removed_existing_in_edit",
            "existing_subset_extracts",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "",
        )
        self.lyr_removed_existing_in_edit.loadNamedStyle(path + "building_red.qml")

        self.lyr_added_bulk_load_in_edit = self.layer_registry.add_postgres_layer(
            "added_bulk_load_in_edit",
            "bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "",
        )
        self.lyr_added_bulk_load_in_edit.loadNamedStyle(path + "building_green.qml")

        self.lyr_existing = self.layer_registry.add_postgres_layer(
            "existing_subset_extracts",
            "existing_subset_extracts",
            "shape",
            "buildings_bulk_load",
            "building_outline_id",
            "supplied_dataset_id = {0}".format(self.current_dataset),
        )
        self.lyr_existing.loadNamedStyle(path + "building_transparent.qml")

        self.lyr_bulk_load = self.layer_registry.add_postgres_layer(
            "bulk_load_outlines",
            "bulk_load_outlines",
            "shape",
            "buildings_bulk_load",
            "bulk_load_outline_id",
            "supplied_dataset_id = {0}".format(self.current_dataset),
        )
        self.lyr_bulk_load.loadNamedStyle(path + "buildings_bulk_load_alter_rel.qml")

    def repaint_view(self):
        """Repaint views to update changes in result"""
        self.lyr_added_bulk_load.triggerRepaint()
        self.lyr_removed_existing.triggerRepaint()
        self.lyr_matched_bulk_load.triggerRepaint()
        self.lyr_matched_existing.triggerRepaint()
        self.lyr_related_bulk_load.triggerRepaint()
        self.lyr_related_existing.triggerRepaint()

    def clear_layer_filter(self):
        """Returns 'null' filter for layers"""
        self.lyr_added_bulk_load_in_edit.setSubsetString("null")
        self.lyr_removed_existing_in_edit.setSubsetString("null")
        self.lyr_matched_existing_in_edit.setSubsetString("null")
        self.lyr_matched_bulk_load_in_edit.setSubsetString("null")
        self.lyr_related_existing_in_edit.setSubsetString("null")
        self.lyr_related_bulk_load_in_edit.setSubsetString("null")

        self.lyr_added_bulk_load.setSubsetString("")
        self.lyr_removed_existing.setSubsetString("")
        self.lyr_matched_existing.setSubsetString("")
        self.lyr_matched_bulk_load.setSubsetString("")
        self.lyr_related_existing.setSubsetString("")
        self.lyr_related_bulk_load.setSubsetString("")

    def setup_message_box(self):
        self.msgbox = QMessageBox(
            QMessageBox.Question,
            "Auto-save",
            "Are you sure you want to turn on auto-save?",
            buttons=QMessageBox.No | QMessageBox.Yes,
        )

    def on_dockwidget_closed(self):
        """Remove highlight when the dockwideget closes"""
        pass

    def maptool_clicked(self):
        canvas = iface.mapCanvas()
        self.tool = MultiLayerSelection(canvas)
        canvas.setMapTool(self.tool)
        # set up signal and slot
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)

    def multi_selection_changed(self):

        self.tbl_relationship.itemSelectionChanged.disconnect(
            self.tbl_relationship_item_selection_changed
        )
        self.tbl_relationship.clearSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        self.reset_buttons()

        selected_bulk = [feat.id() for feat in self.lyr_bulk_load.selectedFeatures()]
        selected_existing = [feat.id() for feat in self.lyr_existing.selectedFeatures()]

        has_multi_set = False
        has_added, has_removed, has_matched, has_related = False, False, False, False
        existing_to_lst, bulk_to_list = [], []
        bulk_attr_to_list = []

        for feat_id in selected_bulk:
            if feat_id in bulk_to_list:
                continue
            id_added = self.find_added_outlines(feat_id)
            id_matched = self.find_matched_existing_outlines(feat_id)
            ids_existing, ids_bulk = self.find_related_existing_outlines(feat_id)
            if id_added:
                if has_matched or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                bulk_to_list.append(feat_id)
                bulk_attr_to_list.append(id_added)
                has_added = True
            elif id_matched:
                if has_added or has_removed or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                if has_matched:
                    has_multi_set = True
                existing_to_lst = [id_matched[0]]
                bulk_to_list = [feat_id]
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                if has_related:
                    has_multi_set = True
                existing_to_lst = ids_existing
                bulk_to_list = ids_bulk
                has_related = True

        for feat_id in selected_existing:
            if feat_id in existing_to_lst:
                continue
            id_removed = self.find_removed_outlines(feat_id)
            id_matched = self.find_matched_bulk_load_outlines(feat_id)
            ids_existing, ids_bulk = self.find_related_bulk_load_outlines(feat_id)
            if id_removed:
                if has_matched or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                existing_to_lst.append(feat_id)
                has_removed = True
            elif id_matched:
                if has_added or has_removed or has_related:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                if has_matched:
                    has_multi_set = True
                existing_to_lst = [feat_id]
                bulk_to_list = [id_matched[1]]
                has_matched = True
            elif ids_existing and ids_bulk:
                if has_added or has_removed or has_matched:
                    self.multi_relationship_selected_error_msg()
                    self.tbl_relationship.itemSelectionChanged.connect(
                        self.tbl_relationship_item_selection_changed
                    )
                    return
                if has_related:
                    has_multi_set = True
                existing_to_lst = ids_existing
                bulk_to_list = ids_bulk
                has_related = True
        self.insert_into_list(self.lst_existing, existing_to_lst)
        self.insert_into_list(self.lst_bulk, bulk_to_list)
        self.disable_listwidget(self.lst_existing)
        self.disable_listwidget(self.lst_bulk)
        self.lyr_existing.selectByIds(existing_to_lst)
        self.lyr_bulk_load.selectByIds(bulk_to_list)

        # error msg when more than one set of matched or related set are selected
        if has_multi_set:
            self.message_bar_edit.pushMessage(
                "Multiple matched or related sets selected, can only unlink one at a time."
            )
        # switch button
        if has_matched or has_related:
            self.btn_unlink.setEnabled(True)
            self.btn_copy_from_existing.setEnabled(True)
            self.btn_set_attributes.setEnabled(True)
            self.btn_delete_attributes.setEnabled(True)
            self.ledit_name.setEnabled(True)
            self.cbox_use.setEnabled(True)
            self.switch_btn_match_and_related()
        elif has_added and has_removed:
            self.switch_btn_match_and_related()
        elif has_added and not has_removed:
            self.btn_delete.setEnabled(True)
            self.btn_set_attributes.setEnabled(True)
            self.btn_delete_attributes.setEnabled(True)
            self.ledit_name.setEnabled(True)
            self.cbox_use.setEnabled(True)
        # select rows in tbl_relationship
        self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        if has_removed:
            for id_existing in existing_to_lst:
                self.select_row_in_tbl_removed(id_existing)
        elif has_added:
            for id_bulk in bulk_to_list:
                self.select_row_in_tbl_added(id_bulk)
        elif has_matched:
            self.select_row_in_tbl_matched(existing_to_lst[0], bulk_to_list[0])
        elif has_related:
            for id_existing in existing_to_lst:
                for id_bulk in bulk_to_list:
                    self.select_row_in_tbl_related(id_existing, id_bulk)
        self.tbl_relationship.setSelectionMode(QAbstractItemView.SingleSelection)

        # Add attributes to list for displaying
        if has_removed:
            for id_ in existing_to_lst:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        existing_use = self.tbl_relationship.item(row, 2).text()
                        existing_name = self.tbl_relationship.item(row, 3).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
                        break
            # if removed and added selected, then alternative extraction of attributes required due to different tables
            if has_added:
                attr_dict = {}
                for item in bulk_attr_to_list:
                    added_id = int(
                        item[0].replace("(", "").replace(")", "").split(",")[0]
                    )
                    added_use = item[1]
                    added_name = item[2]
                    attr_dict[added_id] = [added_use, added_name]
                for id_ in bulk_to_list:
                    bulk_use = attr_dict[id_][0]
                    bulk_name = attr_dict[id_][1]
                    self.insert_into_list(
                        self.lst_bulk_attrs, [[id_, bulk_use, bulk_name]]
                    )
            self.update_attr_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))
        elif has_added:
            for id_ in bulk_to_list:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        bulk_use = self.tbl_relationship.item(row, 1).text()
                        bulk_name = self.tbl_relationship.item(row, 2).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_use, bulk_name]]
                        )
                        break
            self.update_attr_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))
        elif has_matched:
            for id_ in existing_to_lst:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        existing_use = self.tbl_relationship.item(row, 3).text()
                        existing_name = self.tbl_relationship.item(row, 4).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
                        break
            for id_ in bulk_to_list:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 1).text()):
                        bulk_load_use = self.tbl_relationship.item(row, 5).text()
                        bulk_load_name = self.tbl_relationship.item(row, 6).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_load_use, bulk_load_name]]
                        )
                        break
            self.update_attr_list_item_color(QColor("#00b4d4"), QColor("#00b4d4"))
        elif has_related:
            for id_ in existing_to_lst:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 1).text()):
                        existing_use = self.tbl_relationship.item(row, 4).text()
                        existing_name = self.tbl_relationship.item(row, 5).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
                        break
            for id_ in bulk_to_list:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 2).text()):
                        bulk_load_use = self.tbl_relationship.item(row, 6).text()
                        bulk_load_name = self.tbl_relationship.item(row, 7).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_load_use, bulk_load_name]]
                        )
                        break
            self.update_attr_list_item_color(QColor("#e601ff"), QColor("#e601ff"))

        # Change item color in the list
        if has_removed or has_added:
            self.update_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))
        elif has_matched:
            self.update_list_item_color(QColor("#00b4d4"), QColor("#00b4d4"))
        elif has_related:
            self.update_list_item_color(QColor("#e601ff"), QColor("#e601ff"))

        self.tbl_relationship.itemSelectionChanged.connect(
            self.tbl_relationship_item_selection_changed
        )

    def unfinished_error_msg(self):
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            "\n------------- UNFINISHED PROCESS -------------"
            "\n\nPlease click Save or Cancel to finish before continuing."
        )
        self.error_dialog.show()

    def unlink_clicked(self, commit_status=True):
        """
        Unlink the buildings in the table
        Called when unlink_all button is clicked
        """
        self.btn_unlink.setEnabled(False)
        self.btn_maptool.setEnabled(False)
        self.qa_button_set_enable(False)

        ids_existing = self.get_ids_from_lst(self.lst_existing)
        ids_bulk = self.get_ids_from_lst(self.lst_bulk)
        self.insert_into_lyr_removed_in_edit(ids_existing)
        self.insert_into_lyr_added_in_edit(ids_bulk)

        self.connect_to_error_msg()

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

        if self.autosave:
            self.save_clicked(commit_status)
        else:
            self.btn_save.setEnabled(True)

    def matched_clicked(self, commit_status=True):
        """
        Match the buildings in the list
        Called when matched button is clicked
        """
        if self.lst_existing.count() == 1 and self.lst_bulk.count() == 1:
            self.btn_matched.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_maptool.setEnabled(False)
            self.qa_button_set_enable(False)

            id_existing = int(self.lst_existing.item(0).text())
            id_bulk = int(self.lst_bulk.item(0).text())

            self.insert_into_lyr_matched_existing_in_edit(id_existing)
            self.insert_into_lyr_matched_bulk_load_in_edit(id_bulk)

            self.delete_original_relationship_in_existing(id_existing)
            self.delete_original_relationship_in_bulk_load(id_bulk)

            self.connect_to_error_msg()

            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()

            if self.autosave:
                self.save_clicked(commit_status)
            else:
                self.btn_save.setEnabled(True)

    def related_clicked(self, commit_status=True):
        """
        Relate the buildings in the list
        Called when related button is clicked
        """
        if self.lst_existing.count() == 0 or self.lst_bulk.count() == 0:
            pass
        elif self.lst_existing.count() == 1 and self.lst_bulk.count() == 1:
            pass
        else:
            self.btn_related.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_maptool.setEnabled(False)
            self.qa_button_set_enable(False)

            for row in range(self.lst_existing.count()):
                id_existing = int(self.lst_existing.item(row).text())

                self.insert_into_lyr_related_existing_in_edit(id_existing)
                self.delete_original_relationship_in_existing(id_existing)

            for row in range(self.lst_bulk.count()):
                id_bulk = int(self.lst_bulk.item(row).text())

                self.insert_into_lyr_related_bulk_load_in_edit(id_bulk)
                self.delete_original_relationship_in_bulk_load(id_bulk)

            self.connect_to_error_msg()

            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()

            if self.autosave:
                self.save_clicked(commit_status)
            else:
                self.btn_save.setEnabled(True)

    def delete_clicked(self, commit_status=True):
        self.deletion_reason = DeletionReason(self.lst_bulk.count())
        self.deletion_reason.show()
        self.deletion_reason.btn_ok.clicked.connect(
            partial(self.reason_given, commit_status)
        )
        self.deletion_reason.btn_cancel.clicked.connect(self.reason_cancel)

    def reason_given(self, commit_status):
        self.deletion_reason.close()
        if self.deletion_reason.le_reason.text() != "":
            self.btn_matched.setEnabled(False)
            self.btn_related.setEnabled(False)
            self.delete = True
            self.reason_text = self.deletion_reason.le_reason.text()
            self.connect_to_error_msg()
            self.btn_delete.setEnabled(False)
            if self.autosave:
                self.save_clicked(commit_status)
            else:
                self.btn_save.setEnabled(True)
        else:
            iface.messageBar().pushMessage(
                "ERROR",
                "Please ensure that you enter a reason for deletion, you cannot delete a building otherwise.",
                level=Qgis.Info,
                duration=5,
            )

    def reason_cancel(self):
        self.deletion_reason.close()

    def on_click_btn_copy_from_existing(self):
        selected_existing_outlines = self.get_lst_content(self.lst_existing_attrs)
        existing_uses = [row[1][1] for row in selected_existing_outlines]
        existing_names = [row[1][2] for row in selected_existing_outlines]
        non_null_pairs = [
            pair
            for pair in zip(existing_uses, existing_names)
            if pair != ("None", "None")
        ]
        if non_null_pairs:
            existing_use = non_null_pairs[0][0]
            use_id = self.valid_building_use_ids[existing_use]
            self.cbox_use.setCurrentIndex(use_id)
            existing_name = non_null_pairs[0][1]
            self.ledit_name.setText(existing_name)
        else:
            self.cbox_use.setCurrentIndex(0)
            self.ledit_name.setText("")

    def on_click_btn_set_attributes(self, commit_status=True):
        use = self.cbox_use.currentText()
        name = self.ledit_name.text()
        name = "None" if name == "" else name
        if use == "None" and name != "None":
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                "An outline cannot have a name without a use. Please select a value for use."
            )
            self.error_dialog.show()
            return
        for row_id, row_content in self.get_lst_content(self.lst_bulk_attrs):
            updated_row_content = [row_content[0], use, name]
            self.lst_bulk_attrs.item(row_id).setText(str(updated_row_content))
        self.connect_to_error_msg()
        self.attributes_changed = True
        if self.autosave:
            self.save_clicked(commit_status)
        else:
            self.btn_save.setEnabled(True)

    def on_click_btn_delete_attributes(self, commit_status=True):
        for row_id, row_content in self.get_lst_content(self.lst_bulk_attrs):
            updated_row_content = [row_content[0], "None", "None"]
            self.lst_bulk_attrs.item(row_id).setText(str(updated_row_content))
        self.connect_to_error_msg()
        self.attributes_changed = True
        if self.autosave:
            self.save_clicked(commit_status)
        else:
            self.btn_save.setEnabled(True)

    def save_clicked(self, commit_status=True):
        """
        Save result and change database
        Called when save button is clicked
        """
        self.db.open_cursor()

        if self.delete:
            for row in range(self.lst_bulk.count()):
                feat_id = int(self.lst_bulk.item(row).text())
                # remove outline from added table
                sql = "SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);"
                self.db.execute_no_commit(sql, (feat_id,))
                # change status id
                sql = "SELECT buildings_bulk_load.bulk_load_outlines_update_bulk_load_status(%s, %s);"
                self.db.execute_no_commit(sql, (feat_id, 3))
                # insert reason for deletion
                sql = "SELECT buildings_bulk_load.deletion_description_insert(%s, %s);"
                self.db.execute_no_commit(sql, (feat_id, self.reason_text))
            self.reason_text = ""
            self.delete = False
        elif self.attributes_changed:
            self.update_bulkload_attributes()
            self.attributes_changed = False
        else:
            self.delete_original_relationships()
            self.insert_new_added_outlines()
            self.insert_new_removed_outlines()
            self.insert_new_matched_outlines()
            self.insert_new_related_outlines()

        if commit_status:
            self.db.commit_open_cursor()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        self.reset_buttons()
        self.qa_button_set_enable(True)

        self.disconnect_to_error_msg()

        self.repaint_view()
        self.clear_layer_filter()
        iface.mapCanvas().refreshAllLayers()

        self.refresh_tbl_relationship()

    def cancel_clicked(self):
        self.reset_buttons()
        self.qa_button_set_enable(True)
        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        try:
            self.disconnect_to_error_msg()
        except TypeError:
            pass

        self.repaint_view()
        self.clear_layer_filter()
        iface.mapCanvas().refreshAllLayers()

    def exit_clicked(self):
        """
        Called when alter building relationships exit button clicked.
        """
        self.close_frame()

    def close_frame(self):
        """
        Clean up and remove the alter building relationships frame.
        """
        self.reset_buttons()
        self.qa_button_set_enable(True)
        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        if self.change_instance is not None:
            self.edit_dialog.close()

        QgsProject.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        for val in [
            str(layer.id())
            for layer in QgsProject.instance().layerTreeRoot().layerOrder()
        ]:
            if "existing_subset_extracts" in val:
                self.lyr_existing.removeSelection()
            if "bulk_load_outlines" in val:
                self.lyr_bulk_load.removeSelection()
        try:
            self.disconnect_to_error_msg()
        except TypeError:
            pass

        self.layer_registry.remove_layer(self.lyr_existing)
        self.layer_registry.remove_layer(self.lyr_bulk_load)
        self.layer_registry.remove_layer(self.lyr_added_bulk_load)
        self.layer_registry.remove_layer(self.lyr_removed_existing)
        self.layer_registry.remove_layer(self.lyr_matched_existing)
        self.layer_registry.remove_layer(self.lyr_matched_bulk_load)
        self.layer_registry.remove_layer(self.lyr_related_bulk_load)
        self.layer_registry.remove_layer(self.lyr_related_existing)
        self.layer_registry.remove_layer(self.lyr_added_bulk_load_in_edit)
        self.layer_registry.remove_layer(self.lyr_removed_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_matched_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_matched_bulk_load_in_edit)
        self.layer_registry.remove_layer(self.lyr_related_existing_in_edit)
        self.layer_registry.remove_layer(self.lyr_related_bulk_load_in_edit)
        self.layer_registry.remove_layer(self.lyr_facilities)

        for action in iface.building_toolbar.actions():
            if action.text() not in ["Pan Map"]:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()

        from buildings.gui.bulk_load_frame import BulkLoadFrame

        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadFrame(dw))
        iface.actionPan().trigger()

    def cmb_relationship_current_index_changed(self):
        current_text = self.cmb_relationship.currentText()
        if current_text == "Related Outlines":
            self.init_tbl_relationship(
                [
                    "Group",
                    "Exist ID",
                    "Bulk ID",
                    "QA Status",
                    "Exist Use",
                    "Exist Name",
                    "Bulk Use",
                    "Bulk Name",
                ]
            )
            self.populate_tbl_related()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(False)
            if self.is_empty_tbl_relationship("Related Outlines"):
                self.qa_button_set_enable(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Matched Outlines":
            self.init_tbl_relationship(
                [
                    "Exist ID",
                    "Bulk ID",
                    "QA Status",
                    "Exist Use",
                    "Exist Name",
                    "Bulk Use",
                    "Bulk Name",
                ]
            )
            self.populate_tbl_matched()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(False)
            if self.is_empty_tbl_relationship("Matched Outlines"):
                self.qa_button_set_enable(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Removed Outlines":
            self.init_tbl_relationship(
                ["Exist ID", "QA Status", "Exist Use", "Exist Name"]
            )
            self.populate_tbl_removed()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(True)
            if self.is_empty_tbl_relationship("Removed Outlines"):
                self.qa_button_set_enable(False)
                self.btn_qa_not_removed.setEnabled(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Added Outlines":
            self.init_tbl_relationship(["Bulk ID", "Bulk Use", "Bulk Name"])
            self.populate_tbl_added()
            self.btn_qa_not_removed.setEnabled(False)
            self.qa_button_set_enable(False)
            self.btn_next.setEnabled(False)
        elif current_text == "Related Outlines - name sort":
            self.init_tbl_relationship(
                [
                    "Group",
                    "Exist ID",
                    "Bulk ID",
                    "QA Status",
                    "Exist Use",
                    "Exist Name",
                    "Bulk Use",
                    "Bulk Name",
                ]
            )
            self.populate_tbl_related_name_sort()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(False)
            if self.is_empty_tbl_relationship("Related Outlines"):
                self.qa_button_set_enable(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Matched Outlines - name sort":
            self.init_tbl_relationship(
                [
                    "Exist ID",
                    "Bulk ID",
                    "QA Status",
                    "Exist Use",
                    "Exist Name",
                    "Bulk Use",
                    "Bulk Name",
                ]
            )
            self.populate_tbl_matched_name_sort()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(False)
            if self.is_empty_tbl_relationship("Matched Outlines"):
                self.qa_button_set_enable(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Removed Outlines - name sort":
            self.init_tbl_relationship(
                ["Exist ID", "QA Status", "Exist Use", "Exist Name"]
            )
            self.populate_tbl_removed_name_sort()
            self.btn_next.setEnabled(True)
            self.btn_qa_not_removed.setEnabled(True)
            if self.is_empty_tbl_relationship("Removed Outlines"):
                self.qa_button_set_enable(False)
                self.btn_qa_not_removed.setEnabled(False)
            else:
                self.qa_button_set_enable(True)
        elif current_text == "Added Outlines - name sort":
            self.init_tbl_relationship(["Bulk ID", "Bulk Use", "Bulk Name"])
            self.populate_tbl_added_name_sort()
            self.btn_qa_not_removed.setEnabled(False)
            self.qa_button_set_enable(False)
            self.btn_next.setEnabled(False)

        elif current_text == "":
            self.tbl_relationship.setRowCount(0)
            self.tbl_relationship.setColumnCount(0)
            self.qa_button_set_enable(False)
            self.btn_qa_not_removed.setEnabled(False)
            self.btn_next.setEnabled(False)

        self.disable_tbl_editing(self.tbl_relationship)

    def tbl_relationship_item_selection_changed(self):

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        if self.has_no_selection_in_table(self.tbl_relationship):
            self.lyr_existing.removeSelection()
            self.lyr_bulk_load.removeSelection()
            return

        row = self.tbl_relationship.selectionModel().selectedRows()[0].row()
        current_text = self.cmb_relationship.currentText()
        # Treat " - name sort" text as Related/Matched/Removed/Added Outlines
        current_text = current_text.split()[0] + " " + current_text.split()[1]

        if current_text == "Related Outlines":
            id_existing = int(self.tbl_relationship.item(row, 1).text())
            id_bulk = int(self.tbl_relationship.item(row, 2).text())
            ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
            self.insert_into_list(self.lst_existing, ids_existing)
            self.insert_into_list(self.lst_bulk, ids_bulk)
            self.update_list_item_color(QColor("#e601ff"), QColor("#e601ff"))
            self.lyr_existing.selectByIds(ids_existing)
            self.lyr_bulk_load.selectByIds(ids_bulk)
            self.btn_unlink.setEnabled(True)

            # Add related attributes to list for displaying
            for id_ in ids_existing:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 1).text()):
                        existing_use = self.tbl_relationship.item(row, 4).text()
                        existing_name = self.tbl_relationship.item(row, 5).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
                        break
            for id_ in ids_bulk:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 2).text()):
                        bulk_load_use = self.tbl_relationship.item(row, 6).text()
                        bulk_load_name = self.tbl_relationship.item(row, 7).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_load_use, bulk_load_name]]
                        )
                        break
            self.update_attr_list_item_color(QColor("#e601ff"), QColor("#e601ff"))

        elif current_text == "Matched Outlines":
            row = self.tbl_relationship.selectionModel().selectedRows()[0].row()
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            id_bulk = int(self.tbl_relationship.item(row, 1).text())

            ids_existing = [id_existing]
            ids_bulk = [id_bulk]

            self.insert_into_list(self.lst_existing, ids_existing)
            self.insert_into_list(self.lst_bulk, ids_bulk)
            self.update_list_item_color(QColor("#00b4d4"), QColor("#00b4d4"))
            self.lyr_existing.selectByIds(ids_existing)
            self.lyr_bulk_load.selectByIds(ids_bulk)
            self.btn_unlink.setEnabled(True)

            # Add matched attributes to list for displaying
            for id_ in ids_existing:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        existing_use = self.tbl_relationship.item(row, 3).text()
                        existing_name = self.tbl_relationship.item(row, 4).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
                        break
            for id_ in ids_bulk:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 1).text()):
                        bulk_load_use = self.tbl_relationship.item(row, 5).text()
                        bulk_load_name = self.tbl_relationship.item(row, 6).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_load_use, bulk_load_name]]
                        )
                        break
            self.update_attr_list_item_color(QColor("#00b4d4"), QColor("#00b4d4"))

        elif current_text == "Removed Outlines":
            id_existing = int(self.tbl_relationship.item(row, 0).text())
            self.insert_into_list(self.lst_existing, [id_existing])
            self.update_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))
            self.lyr_existing.selectByIds([id_existing])
            self.lyr_bulk_load.selectByIds([])

            # Add removed attributes to list for displaying
            for id_ in [id_existing]:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        existing_use = self.tbl_relationship.item(row, 2).text()
                        existing_name = self.tbl_relationship.item(row, 3).text()
                        self.insert_into_list(
                            self.lst_existing_attrs,
                            [[id_, existing_use, existing_name]],
                        )
            self.update_attr_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))

        elif current_text == "Added Outlines":
            id_bulk = int(self.tbl_relationship.item(row, 0).text())
            self.insert_into_list(self.lst_bulk, [id_bulk])
            self.update_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))
            self.lyr_bulk_load.selectByIds([id_bulk])
            self.btn_delete.setEnabled(True)

            # Add added attributes to list for displaying
            for id_ in [id_bulk]:
                for row in range(self.tbl_relationship.rowCount()):
                    if id_ == int(self.tbl_relationship.item(row, 0).text()):
                        bulk_use = self.tbl_relationship.item(row, 1).text()
                        bulk_name = self.tbl_relationship.item(row, 2).text()
                        self.insert_into_list(
                            self.lst_bulk_attrs, [[id_, bulk_use, bulk_name]]
                        )
            self.update_attr_list_item_color(QColor("#ff2b01"), QColor("#3f9800"))

        if self.zoom:
            self.zoom_to_feature()

    def btn_qa_status_clicked(self, qa_status, commit_status=True):

        selected_rows = [
            index.row()
            for index in self.tbl_relationship.selectionModel().selectedRows()
        ]
        if not selected_rows:
            return
        self.tbl_relationship.itemSelectionChanged.disconnect(
            self.tbl_relationship_item_selection_changed
        )
        self.db.open_cursor()

        qa_status_id = self.get_qa_status_id(qa_status)
        current_text = self.cmb_relationship.currentText()
        # Treat " - name sort" text as Related/Matched/Removed/Added Outlines
        current_text = current_text.split()[0] + " " + current_text.split()[1]

        ids_existing, ids_bulk = [], []
        existing_use, existing_name = [], []

        if current_text == "Related Outlines":
            if qa_status_id == 5:
                return
            qa_column = 3
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 1).text())
                id_bulk = int(self.tbl_relationship.item(row, 2).text())
                self.update_qa_status_in_related(id_existing, id_bulk, qa_status_id)
                ids_existing, ids_bulk = self.find_related_existing_outlines(id_bulk)
        elif current_text == "Matched Outlines":
            if qa_status_id == 5:
                return
            qa_column = 2
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 0).text())
                id_bulk = int(self.tbl_relationship.item(row, 1).text())
                self.update_qa_status_in_matched(id_existing, id_bulk, qa_status_id)
                ids_existing.append(id_existing)
                ids_bulk.append(id_bulk)
        elif current_text == "Removed Outlines":
            qa_column = 1
            selected_ids = []
            for row in selected_rows:
                id_existing = int(self.tbl_relationship.item(row, 0).text())
                selected_ids.append(id_existing)
                self.update_qa_status_in_removed(id_existing, qa_status_id)
                ids_existing.append(id_existing)
            if qa_status_id == 5:
                self.copy_and_match_removed_building()
                self.cmb_relationship.setCurrentIndex(
                    self.cmb_relationship.findText("Matched Outlines")
                )

        if commit_status:
            self.db.commit_open_cursor()

        self.refresh_tbl_relationship()
        self.reset_buttons()
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()
        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        self.tbl_relationship.itemSelectionChanged.connect(
            self.tbl_relationship_item_selection_changed
        )

        # Move to the next 'not checked'
        if qa_status_id != 5:
            for row in range(max(selected_rows) + 1, self.tbl_relationship.rowCount()):
                if self.scroll_to_next(row, qa_column, selected_rows):
                    break
                if not self.tbl_relationship.selectionModel().selectedRows():
                    self.tbl_relationship.selectRow(max(selected_rows))
                    item = self.tbl_relationship.item(max(selected_rows), qa_column)
                    self.tbl_relationship.scrollToItem(item)
        elif qa_status_id == 5:
            for row in range(self.tbl_relationship.rowCount()):
                id_existing = int(self.tbl_relationship.item(row, 0).text())
                if id_existing in selected_ids:
                    self.zoom = False
                    self.tbl_relationship.selectRow(row)
                    self.tbl_relationship.scrollToItem(
                        self.tbl_relationship.item(row, qa_column)
                    )
                    self.zoom = True
                    break
            if len(selected_ids) > 1:
                self.message_bar_edit.pushMessage(
                    "You cannot have multiple selected matched relationships. "
                    "The first (ordered numerically) has been selected"
                )

    def zoom_to_next(self):
        found = False
        selected_rows = [
            index.row()
            for index in self.tbl_relationship.selectionModel().selectedRows()
        ]
        if not selected_rows:
            selected_rows = [-1]
        current_text = self.cmb_relationship.currentText()
        # Treat " - name sort" text as Related/Matched/Removed/Added Outlines
        current_text = current_text.split()[0] + " " + current_text.split()[1]
        if current_text == "Related Outlines":
            qa_column = 3
        elif current_text == "Matched Outlines":
            qa_column = 2
        elif current_text == "Removed Outlines":
            qa_column = 1
        for row in range(max(selected_rows) + 1, self.tbl_relationship.rowCount()):
            if self.scroll_to_next(row, qa_column, selected_rows):
                found = True
                break
        if not found:
            selected_rows = [0]
            for row in range(self.tbl_relationship.rowCount()):
                if self.scroll_to_next(row, qa_column, selected_rows):
                    break

    def cb_lyr_bulk_load_state_changed(self):
        legend = QgsProject.instance().layerTreeRoot()
        if self.cb_lyr_bulk_load.isChecked():
            legend.findLayer(
                self.lyr_added_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(
                self.lyr_matched_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(
                self.lyr_related_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(self.lyr_added_bulk_load.id()).setItemVisibilityChecked(
                True
            )
            legend.findLayer(self.lyr_matched_bulk_load.id()).setItemVisibilityChecked(
                True
            )
            legend.findLayer(self.lyr_related_bulk_load.id()).setItemVisibilityChecked(
                True
            )
        else:
            legend.findLayer(
                self.lyr_added_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(
                self.lyr_matched_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(
                self.lyr_related_bulk_load_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(self.lyr_added_bulk_load.id()).setItemVisibilityChecked(
                False
            )
            legend.findLayer(self.lyr_matched_bulk_load.id()).setItemVisibilityChecked(
                False
            )
            legend.findLayer(self.lyr_related_bulk_load.id()).setItemVisibilityChecked(
                False
            )

    def cb_lyr_existing_state_changed(self):
        legend = QgsProject.instance().layerTreeRoot()
        if self.cb_lyr_existing.isChecked():
            legend.findLayer(
                self.lyr_removed_existing_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(
                self.lyr_matched_existing_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(
                self.lyr_related_existing_in_edit.id()
            ).setItemVisibilityChecked(True)
            legend.findLayer(self.lyr_removed_existing.id()).setItemVisibilityChecked(
                True
            )
            legend.findLayer(self.lyr_matched_existing.id()).setItemVisibilityChecked(
                True
            )
            legend.findLayer(self.lyr_related_existing.id()).setItemVisibilityChecked(
                True
            )
        else:
            legend.findLayer(
                self.lyr_removed_existing_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(
                self.lyr_matched_existing_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(
                self.lyr_related_existing_in_edit.id()
            ).setItemVisibilityChecked(False)
            legend.findLayer(self.lyr_removed_existing.id()).setItemVisibilityChecked(
                False
            )
            legend.findLayer(self.lyr_matched_existing.id()).setItemVisibilityChecked(
                False
            )
            legend.findLayer(self.lyr_related_existing.id()).setItemVisibilityChecked(
                False
            )

    def cb_autosave_state_changed(self):
        if self.btn_save.isEnabled():
            self.unfinished_error_msg()
            self.cb_autosave.setCheckState(0)
            self.autosave = False
            self.btn_save.setVisible(True)
            return
        if self.cb_autosave.isChecked():
            if self.confirm_to_autosave():
                self.autosave = True
                self.btn_save.setVisible(False)
            else:
                self.cb_autosave.setCheckState(0)
                self.autosave = False
                self.btn_save.setVisible(True)
        else:
            self.autosave = False
            self.btn_save.setVisible(True)

    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        layers = [
            "added_bulk_load_in_edit",
            "removed_existing_in_edit",
            "matched_existing_in_edit",
            "matched_bulk_load_in_edit",
            "related_existing_in_edit",
            "related_bulk_load_in_edit",
            "added_outlines",
            "removed_outlines",
            "matched_existing_outlines",
            "matched_bulk_load_outlines",
            "related_existing_outlines",
            "related_bulk_load_outlines",
            "bulk_load_outlines",
            "existing_subset_extracts",
        ]
        for layer in layers:
            if layer in layerids:
                self.cmb_relationship.setDisabled(1)
                self.btn_qa_not_checked.setDisabled(1)
                self.btn_qa_refer2supplier.setDisabled(1)
                self.btn_qa_pending.setDisabled(1)
                self.btn_qa_okay.setDisabled(1)
                self.btn_qa_not_removed.setDisabled(1)
                self.btn_maptool.setDisabled(1)
                self.btn_unlink.setDisabled(1)
                self.btn_matched.setDisabled(1)
                self.btn_related.setDisabled(1)
                self.btn_delete.setDisabled(1)
                self.btn_cancel.setDisabled(1)
                self.btn_save.setDisabled(1)
                self.cb_autosave.setDisabled(1)
                self.cb_lyr_bulk_load.setDisabled(1)
                self.cb_lyr_existing.setDisabled(1)
                iface.messageBar().pushMessage(
                    "ERROR",
                    "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                    level=Qgis.Critical,
                    duration=5,
                )
                return

    def copy_and_match_removed_building(self):
        # iterate through all the selected removed buildings
        for feature in self.lyr_existing.selectedFeatures():
            # get geometry
            geometry = self.db.execute_no_commit(
                general_select.convert_geometry, (feature.geometry().asWkt(),)
            )
            geometry = geometry.fetchall()[0][0]
            sql = (
                buildings_select.building_outlines_capture_method_id_by_building_outline_id
            )
            building_outline_id = feature.attributes()[0]
            # get capture method of existing outline
            capture_method = self.db.execute_no_commit(sql, (building_outline_id,))
            capture_method = capture_method.fetchall()[0][0]
            sql = (
                bulk_load_select.bulk_load_outlines_capture_source_by_supplied_dataset_id
            )
            # get capture source of current dataset
            capture_source = self.db.execute_no_commit(sql, (self.current_dataset,))
            capture_source = capture_source.fetchall()[0][0]
            # get suburb, town_city and territorial authority of existing outline
            sql = (
                buildings_select.building_outlines_suburb_locality_id_by_building_outline_id
            )
            suburb = self.db.execute_no_commit(sql, (building_outline_id,))
            suburb = suburb.fetchall()[0][0]
            sql = buildings_select.building_outlines_town_city_id_by_building_outline_id
            # town_city = self.db.execute_no_commit(sql, (building_outline_id,))
            # town_city = town_city.fetchall()[0][0]
            sql = (
                buildings_select.building_outlines_territorial_authority_id_by_building_outline
            )
            territorial_auth = self.db.execute_no_commit(sql, (building_outline_id,))
            territorial_auth = territorial_auth.fetchall()[0][0]
            # insert outline into building_bulk_load.bulk_load_outlines
            sql = "SELECT buildings_bulk_load.bulk_load_outlines_insert(%s, %s, %s, %s, %s, %s, %s, %s)"
            bulk_load_id = self.db.execute_no_commit(
                sql,
                (
                    self.current_dataset,
                    None,
                    2,
                    capture_method,
                    capture_source,
                    suburb,
                    territorial_auth,
                    geometry,
                ),
            )
            bulk_load_id = bulk_load_id.fetchall()[0][0]
            # remove existing building from removed table
            sql = "SELECT buildings_bulk_load.removed_delete_existing_outline(%s);"
            self.db.execute_no_commit(sql, (building_outline_id,))
            # add existing and new building to matched table
            sql = "SELECT buildings_bulk_load.matched_insert_building_outlines(%s, %s);"
            self.db.execute_no_commit(sql, (bulk_load_id, building_outline_id))
            # change to not checked
            sql = "SELECT buildings_bulk_load.matched_update_qa_status_id(%s, %s, %s);"
            self.db.execute_no_commit(sql, (1, building_outline_id, bulk_load_id))
        # refresh to get new outlines
        iface.mapCanvas().refreshAllLayers()

    def confirm_to_autosave(self):
        reply = self.msgbox.exec_()
        if reply == QMessageBox.Yes:
            return True
        return False

    def switch_btn_match_and_related(self):
        if self.lst_bulk.count() == 0 or self.lst_existing.count() == 0:
            pass
        elif self.lst_bulk.count() == 1 and self.lst_existing.count() == 1:
            self.btn_matched.setEnabled(True)
            self.btn_related.setEnabled(False)
            self.btn_delete.setEnabled(True)
        else:
            self.btn_related.setEnabled(True)
            self.btn_matched.setEnabled(False)
            self.btn_delete.setEnabled(True)

    def multi_relationship_selected_error_msg(self):
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            "\n------------- MULTIPLE RELATIONSHIP SELECTED -------------"
            "\n\nThere are multiple relationships selected. Please unlink "
            "matched or related outlines before altering relationships."
        )
        self.error_dialog.show()

    def find_added_outlines(self, id_bulk):
        result = self.db.execute_return(
            bulk_load_select.added_by_bulk_load_outline_id_dataset_id,
            (id_bulk, self.current_dataset),
        )
        return result.fetchone()

    def find_removed_outlines(self, id_existing):
        result = self.db.execute_return(
            bulk_load_select.removed_by_existing_outline_id_dataset_id,
            (id_existing, self.current_dataset),
        )
        return result.fetchone()

    def find_matched_existing_outlines(self, id_bulk):
        result = self.db.execute_return(
            bulk_load_select.matched_by_bulk_load_outline_id_dataset_id,
            (id_bulk, self.current_dataset),
        )
        return result.fetchone()

    def find_matched_bulk_load_outlines(self, id_existing):
        ids_existing, ids_bulk = [], []
        existing_use, existing_name = [], []

        result = self.db.execute_return(
            bulk_load_select.matched_by_existing_outline_id_dataset_id,
            (id_existing, self.current_dataset),
        )
        return result.fetchone()

    def find_related_existing_outlines(self, id_bulk):
        ids_existing, ids_bulk = [], []
        existing_use, existing_name = [], []
        bulk_load_use, bulk_load_name = [], []

        result = self.db.execute_return(
            bulk_load_select.related_by_bulk_load_outline_id_dataset_id,
            (id_bulk, self.current_dataset),
        )
        for (
            id_existing,
            id_bulk,
            existing_use,
            existing_name,
            bulk_load_use,
            bulk_load_name,
        ) in result.fetchall():
            ids_existing.append(id_existing)
            ids_bulk.append(id_bulk)
        return list(set(ids_existing)), list(set(ids_bulk))

    def find_related_bulk_load_outlines(self, id_existing):
        ids_existing, ids_bulk = [], []
        existing_use, existing_name = [], []

        result = self.db.execute_return(
            bulk_load_select.related_by_existing_outline_id_dataset_id,
            (id_existing, self.current_dataset),
        )
        for (id_existing, id_bulk) in result.fetchall():
            ids_existing.append(id_existing)
            ids_bulk.append(id_bulk)
        return list(set(ids_existing)), list(set(ids_bulk))

    def insert_into_table(self, tbl, ids):
        rows = []
        for (id_existing, id_bulk) in ids:
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            if id_existing:
                tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            if id_bulk:
                tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            rows.append(row_tbl)
        return rows

    def connect_to_error_msg(self):
        self.tool.multi_selection_changed.disconnect(self.multi_selection_changed)
        self.tool.multi_selection_changed.connect(self.unfinished_error_msg)
        self.tbl_relationship.itemSelectionChanged.disconnect(
            self.tbl_relationship_item_selection_changed
        )
        self.tbl_relationship.itemSelectionChanged.connect(self.unfinished_error_msg)
        self.reset_buttons()
        self.btn_maptool.setEnabled(False)

    def disconnect_to_error_msg(self):
        self.tool.multi_selection_changed.disconnect(self.unfinished_error_msg)
        self.tool.multi_selection_changed.connect(self.multi_selection_changed)
        self.tbl_relationship.itemSelectionChanged.disconnect(self.unfinished_error_msg)
        self.tbl_relationship.itemSelectionChanged.connect(
            self.tbl_relationship_item_selection_changed
        )
        self.reset_buttons()
        self.btn_maptool.setEnabled(True)

    def has_no_selection_in_table(self, tbl):
        if not tbl.selectionModel().selectedRows():
            return True
        return False

    def insert_into_lyr_removed_in_edit(self, ids_existing):
        for id_existing in ids_existing:
            filter_ = self.lyr_removed_existing_in_edit.subsetString()
            self.lyr_removed_existing_in_edit.setSubsetString(
                filter_ + " or building_outline_id = %s" % id_existing
            )

    def insert_into_lyr_added_in_edit(self, ids_bulk):
        for id_bulk in ids_bulk:
            filter_ = self.lyr_added_bulk_load_in_edit.subsetString()
            self.lyr_added_bulk_load_in_edit.setSubsetString(
                filter_ + " or bulk_load_outline_id = %s" % id_bulk
            )

    def delete_original_relationship_in_existing(self, id_existing):
        """
        Remove features in the view layer
        """
        if not self.lyr_removed_existing.subsetString():
            self.lyr_removed_existing.setSubsetString(
                '"building_outline_id" != %s' % id_existing
            )
        else:
            self.lyr_removed_existing.setSubsetString(
                self.lyr_removed_existing.subsetString()
                + ' and "building_outline_id" != %s' % id_existing
            )

        if not self.lyr_matched_existing.subsetString():
            self.lyr_matched_existing.setSubsetString(
                '"building_outline_id" != %s' % id_existing
            )
        else:
            self.lyr_matched_existing.setSubsetString(
                self.lyr_matched_existing.subsetString()
                + ' and "building_outline_id" != %s' % id_existing
            )

        if not self.lyr_related_existing.subsetString():
            self.lyr_related_existing.setSubsetString(
                '"building_outline_id" != %s' % id_existing
            )
        else:
            self.lyr_related_existing.setSubsetString(
                self.lyr_related_existing.subsetString()
                + ' and "building_outline_id" != %s' % id_existing
            )

    def delete_original_relationship_in_bulk_load(self, id_bulk):
        """
        Remove features in the view layer
        """
        if not self.lyr_added_bulk_load.subsetString():
            self.lyr_added_bulk_load.setSubsetString(
                '"bulk_load_outline_id" != %s' % id_bulk
            )
        else:
            self.lyr_added_bulk_load.setSubsetString(
                self.lyr_added_bulk_load.subsetString()
                + ' and "bulk_load_outline_id" != %s' % id_bulk
            )

        if not self.lyr_matched_bulk_load.subsetString():
            self.lyr_matched_bulk_load.setSubsetString(
                '"bulk_load_outline_id" != %s' % id_bulk
            )
        else:
            self.lyr_matched_bulk_load.setSubsetString(
                self.lyr_matched_bulk_load.subsetString()
                + ' and "bulk_load_outline_id" != %s' % id_bulk
            )

        if not self.lyr_related_bulk_load.subsetString():
            self.lyr_related_bulk_load.setSubsetString(
                '"bulk_load_outline_id" != %s' % id_bulk
            )
        else:
            self.lyr_related_bulk_load.setSubsetString(
                self.lyr_related_bulk_load.subsetString()
                + ' and "bulk_load_outline_id" != %s' % id_bulk
            )

    def reset_buttons(self):
        self.btn_unlink.setEnabled(False)
        self.btn_matched.setEnabled(False)
        self.btn_related.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_maptool.setEnabled(True)
        self.btn_copy_from_existing.setEnabled(False)
        self.btn_set_attributes.setEnabled(False)
        self.btn_delete_attributes.setEnabled(False)
        self.cbox_use.setEnabled(False)
        self.ledit_name.setEnabled(False)

    def qa_button_set_enable(self, boolean):
        self.btn_qa_okay.setEnabled(boolean)
        self.btn_qa_pending.setEnabled(boolean)
        self.btn_qa_refer2supplier.setEnabled(boolean)
        self.btn_qa_not_checked.setEnabled(boolean)

    def insert_into_list(self, lst, ids):
        for fid in ids:
            lst.addItem(QListWidgetItem("%s" % fid))

    def get_ids_from_lst(self, lst):
        feat_ids = []
        for row in range(lst.count()):
            feat_ids.append(int(lst.item(row).text()))
        return feat_ids

    @staticmethod
    def get_lst_content(lst):
        """
        Returns a list of tuples of the row_id and the row content evaluated using `literal_eval`.
        """
        return [(n, literal_eval(lst.item(n).text())) for n in range(lst.count())]

    def disable_listwidget(self, lst):
        for row in range(lst.count()):
            item = lst.item(row)
            item.setFlags(Qt.ItemIsEnabled)

    def update_list_item_color(self, existing_color, bulk_color):
        for i in range(self.lst_existing.count()):
            self.lst_existing.item(i).setForeground(QColor(existing_color))
        for i in range(self.lst_bulk.count()):
            self.lst_bulk.item(i).setForeground(QColor(bulk_color))

    def update_attr_list_item_color(self, existing_color, bulk_color):
        for i in range(self.lst_existing_attrs.count()):
            self.lst_existing_attrs.item(i).setForeground(QColor(existing_color))
        for i in range(self.lst_bulk_attrs.count()):
            self.lst_bulk_attrs.item(i).setForeground(QColor(bulk_color))

    def delete_from_lyr_removed_in_edit(self, id_existing):
        filter_ = self.lyr_removed_existing_in_edit.subsetString()
        self.lyr_removed_existing_in_edit.setSubsetString(
            "(" + filter_ + ') and "building_outline_id" != %s' % id_existing
        )

    def delete_from_lyr_added_in_edit(self, id_bulk):
        filter_ = self.lyr_added_bulk_load_in_edit.subsetString()
        self.lyr_added_bulk_load_in_edit.setSubsetString(
            "(" + filter_ + ') and "bulk_load_outline_id" != %s' % id_bulk
        )

    def insert_into_lyr_matched_existing_in_edit(self, id_existing):
        self.lyr_matched_existing_in_edit.setSubsetString(
            '"building_outline_id" = %s' % id_existing
        )

    def insert_into_lyr_matched_bulk_load_in_edit(self, id_bulk):
        self.lyr_matched_bulk_load_in_edit.setSubsetString(
            '"bulk_load_outline_id" = %s' % id_bulk
        )

    def insert_into_lyr_related_existing_in_edit(self, id_existing):
        filter_ = self.lyr_related_existing_in_edit.subsetString()
        self.lyr_related_existing_in_edit.setSubsetString(
            filter_ + ' or "building_outline_id" = %s' % id_existing
        )

    def insert_into_lyr_related_bulk_load_in_edit(self, id_bulk):
        filter_ = self.lyr_related_bulk_load_in_edit.subsetString()
        self.lyr_related_bulk_load_in_edit.setSubsetString(
            filter_ + ' or "bulk_load_outline_id" = %s' % id_bulk
        )

    def delete_original_relationships(self):
        sql_delete_related_existing = (
            "SELECT buildings_bulk_load.related_delete_existing_outlines(%s);"
        )
        sql_delete_matched_existing = (
            "SELECT buildings_bulk_load.matched_delete_existing_outlines(%s);"
        )
        sql_delete_removed = (
            "SELECT buildings_bulk_load.removed_delete_existing_outline(%s);"
        )
        sql_delete_added = (
            "SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);"
        )

        for row in range(self.lst_existing.count()):
            item = self.lst_existing.item(row)
            id_existing = int(item.text())
            self.db.execute_no_commit(sql_delete_removed, (id_existing,))
            self.db.execute_no_commit(sql_delete_matched_existing, (id_existing,))
            self.db.execute_no_commit(sql_delete_related_existing, (id_existing,))

        for row in range(self.lst_bulk.count()):
            item = self.lst_bulk.item(row)
            id_bulk = int(item.text())

            self.db.execute_no_commit(sql_delete_added, (id_bulk,))

    def insert_new_added_outlines(self):
        # added
        sql_insert_added = (
            "SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s, %s);"
        )
        for feat in self.lyr_added_bulk_load_in_edit.getFeatures():
            id_bulk = feat["bulk_load_outline_id"]
            self.db.execute_no_commit(sql_insert_added, (id_bulk, 2))

    def insert_new_removed_outlines(self):
        # removed
        sql_insert_removed = (
            "SELECT buildings_bulk_load.removed_insert_building_outlines(%s);"
        )
        for feat in self.lyr_removed_existing_in_edit.getFeatures():
            id_existing = feat["building_outline_id"]
            self.db.execute_no_commit(sql_insert_removed, (id_existing,))

    def insert_new_matched_outlines(self):
        # matched
        sql_insert_matched = (
            "SELECT buildings_bulk_load.matched_insert_building_outlines(%s, %s);"
        )
        for feat1 in self.lyr_matched_bulk_load_in_edit.getFeatures():
            id_bulk = feat1["bulk_load_outline_id"]
            for feat2 in self.lyr_matched_existing_in_edit.getFeatures():
                id_existing = feat2["building_outline_id"]
                self.db.execute_no_commit(sql_insert_matched, (id_bulk, id_existing))

    def insert_new_related_outlines(self):
        # related
        related_outlines = [
            feat for feat in self.lyr_related_bulk_load_in_edit.getFeatures()
        ]
        if related_outlines:
            sql_insert_related_group = (
                "SELECT buildings_bulk_load.related_group_insert();"
            )
            result = self.db.execute_no_commit(sql_insert_related_group)
            new_group_id = result.fetchone()[0]
        sql_insert_related = (
            "SELECT buildings_bulk_load.related_insert_building_outlines(%s, %s, %s);"
        )
        for feat1 in self.lyr_related_bulk_load_in_edit.getFeatures():
            id_bulk = feat1["bulk_load_outline_id"]
            for feat2 in self.lyr_related_existing_in_edit.getFeatures():
                id_existing = feat2["building_outline_id"]
                self.db.execute_no_commit(
                    sql_insert_related, (new_group_id, id_bulk, id_existing)
                )

    def update_bulkload_attributes(self):
        sql_update_attrs = """
            UPDATE buildings_bulk_load.bulk_load_outlines
            SET bulk_load_use_id = %s, bulk_load_name = %s
            WHERE bulk_load_outline_id = %s;
            """
        for row_id, (id_, use, name) in self.get_lst_content(self.lst_bulk_attrs):
            use_id = self.valid_building_use_ids[use]
            if name in {"", "None"}:
                name = None
            self.db.execute_no_commit(sql_update_attrs, (use_id, name, id_))

    def disable_tbl_editing(self, tbl):
        """Disable editing so item cannot be changed in the table"""
        for row in range(tbl.rowCount()):
            tbl.showRow(row)
            for col in range(tbl.columnCount()):
                if tbl.item(row, col):
                    tbl.item(row, col).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def refresh_tbl_relationship(self):
        """Refresh tbl_relationship by switching cmb_relationship"""
        index = self.cmb_relationship.currentIndex()
        self.cmb_relationship.setCurrentIndex(0)
        self.cmb_relationship.setCurrentIndex(index)

    def populate_cmb_relationship(self):
        """Populates cmb_relationship"""
        self.cmb_relationship.clear()
        item_list = [
            "Removed Outlines",
            "Matched Outlines",
            "Related Outlines",
            "Added Outlines",
            "Removed Outlines - name sort",
            "Matched Outlines - name sort",
            "Related Outlines - name sort",
            "Added Outlines - name sort",
        ]
        self.cmb_relationship.addItems([""] + item_list)

    def init_tbl_relationship(self, header_items):
        """Initiates tbl_relationship"""
        tbl = self.tbl_relationship
        tbl.setRowCount(0)
        tbl.setColumnCount(len(header_items))

        for i, header_item in enumerate(header_items):
            tbl.setHorizontalHeaderItem(i, QTableWidgetItem(header_item))

        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.verticalHeader().setVisible(False)

        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)

        tbl.setShowGrid(True)

    def populate_tbl_related(self):
        """Populates tbl_relationship when cmb_relationship switches to related"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.related_by_dataset_id, (self.current_dataset,)
        )
        for (
            id_group,
            id_existing,
            id_bulk,
            qa_status,
            exist_use,
            exist_name,
            bulk_use,
            bulk_name,
        ) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_group))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 4, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 5, QTableWidgetItem("%s" % exist_name))
            tbl.setItem(row_tbl, 6, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 7, QTableWidgetItem("%s" % bulk_name))

    def populate_tbl_matched(self):
        """Populates tbl_relationship when cmb_relationship switches to matched"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.matched_by_dataset_id, (self.current_dataset,)
        )
        for (
            id_existing,
            id_bulk,
            qa_status,
            exist_use,
            exist_name,
            bulk_use,
            bulk_name,
        ) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 4, QTableWidgetItem("%s" % exist_name))
            tbl.setItem(row_tbl, 5, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 6, QTableWidgetItem("%s" % bulk_name))

    def populate_tbl_removed(self):
        """Populates tbl_relationship when cmb_relationship switches to removed"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.removed_by_dataset_id, (self.current_dataset,)
        )
        for (id_existing, qa_status, exist_use, exist_name) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % exist_name))

    def populate_tbl_added(self):
        """Populates tbl_relationship when cmb_relationship switches to added"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.added_by_dataset_id, (self.current_dataset,)
        )
        for (id_bulk_load, bulk_use, bulk_name) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_bulk_load))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % bulk_name))

    def populate_tbl_related_name_sort(self):
        """Populates tbl_relationship when cmb_relationship switches to related - name sort"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.related_by_dataset_id_name_sort, (self.current_dataset,)
        )
        for (
            id_group,
            id_existing,
            id_bulk,
            qa_status,
            exist_use,
            exist_name,
            bulk_use,
            bulk_name,
        ) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_group))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 4, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 5, QTableWidgetItem("%s" % exist_name))
            tbl.setItem(row_tbl, 6, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 7, QTableWidgetItem("%s" % bulk_name))

    def populate_tbl_matched_name_sort(self):
        """Populates tbl_relationship when cmb_relationship switches to matched - name sort"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.matched_by_dataset_id_name_sort, (self.current_dataset,)
        )
        for (
            id_existing,
            id_bulk,
            qa_status,
            exist_use,
            exist_name,
            bulk_use,
            bulk_name,
        ) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % id_bulk))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 4, QTableWidgetItem("%s" % exist_name))
            tbl.setItem(row_tbl, 5, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 6, QTableWidgetItem("%s" % bulk_name))

    def populate_tbl_removed_name_sort(self):
        """Populates tbl_relationship when cmb_relationship switches to removed - name sort"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.removed_by_dataset_id_name_sort, (self.current_dataset,)
        )
        for (id_existing, qa_status, exist_use, exist_name) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_existing))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % qa_status))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % exist_use))
            tbl.setItem(row_tbl, 3, QTableWidgetItem("%s" % exist_name))

    def populate_tbl_added_name_sort(self):
        """Populates tbl_relationship when cmb_relationship switches to added - name sort"""
        tbl = self.tbl_relationship
        result = self.db.execute_return(
            bulk_load_select.added_by_dataset_id_name_sort, (self.current_dataset,)
        )
        for (id_bulk_load, bulk_use, bulk_name) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % id_bulk_load))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % bulk_use))
            tbl.setItem(row_tbl, 2, QTableWidgetItem("%s" % bulk_name))

    def is_empty_tbl_relationship(self, relationship):
        if self.tbl_relationship.rowCount() == 0:
            self.message_bar_qa.pushMessage(
                "%s are not available in the current dataset." % relationship
            )
            return True
        return False

    def get_qa_status_id(self, qa_status):
        """Returns qa_status_id according to the sender button"""
        if qa_status == "Okay":
            qa_status_id = 2
        elif qa_status == "Pending":
            qa_status_id = 3
        elif qa_status == "Refer to Supplier":
            qa_status_id = 4
        elif qa_status == "Not Checked":
            qa_status_id = 1
        elif qa_status == "Not Removed":
            qa_status_id = 5
        else:
            qa_status_id = None
        return qa_status_id

    def zoom_to_feature(self):

        extent = None
        for lyr in [self.lyr_existing, self.lyr_bulk_load]:
            selected_feat = [feat for feat in lyr.selectedFeatures()]
            if selected_feat:
                if not extent:
                    extent = lyr.boundingBoxOfSelected()
                else:
                    extent.combineExtentWith(lyr.boundingBoxOfSelected())
        if extent:
            iface.mapCanvas().setExtent(extent)
            iface.mapCanvas().zoomScale(300.0)

    def scroll_to_next(self, row, qa_column, selected_rows):
        item = self.tbl_relationship.item(row, qa_column)
        if item.text() == "Not Checked":
            self.tbl_relationship.selectRow(row)
            self.tbl_relationship.scrollToItem(item)
            return True
        return False

    def update_qa_status_in_related(self, id_existing, id_bulk, qa_status_id):
        """Updates qa_status_id in related table"""
        sql_update_related = (
            "SELECT buildings_bulk_load.related_update_qa_status_id(%s, %s, %s);"
        )
        self.db.execute_no_commit(
            sql_update_related, (qa_status_id, id_existing, id_bulk)
        )

    def update_qa_status_in_matched(self, id_existing, id_bulk, qa_status_id):
        """Updates qa_status_id in matched table"""
        sql_update_matched = (
            "SELECT buildings_bulk_load.matched_update_qa_status_id(%s, %s, %s);"
        )
        self.db.execute_no_commit(
            sql_update_matched, (qa_status_id, id_existing, id_bulk)
        )

    def update_qa_status_in_removed(self, id_existing, qa_status_id):
        """Updates qa_status_id in removed table"""
        sql_update_removed = (
            "SELECT buildings_bulk_load.removed_update_qa_status_id(%s, %s);"
        )
        self.db.execute_no_commit(sql_update_removed, (qa_status_id, id_existing))

    def select_row_in_tbl_matched(self, id_existing, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText("Matched Outlines")
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
        for row in range(self.tbl_relationship.rowCount()):
            if (
                int(tbl.item(row, 0).text()) == id_existing
                and int(tbl.item(row, 1).text()) == id_bulk
            ):
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_related(self, id_existing, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText("Related Outlines")
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
            self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        for row in range(self.tbl_relationship.rowCount()):
            if (
                int(tbl.item(row, 1).text()) == id_existing
                and int(tbl.item(row, 2).text()) == id_bulk
            ):
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_removed(self, id_existing):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText("Removed Outlines")
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
            self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_existing:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def select_row_in_tbl_added(self, id_bulk):
        tbl = self.tbl_relationship
        index = self.cmb_relationship.findText("Added Outlines")
        if self.cmb_relationship.currentIndex() != index:
            self.cmb_relationship.setCurrentIndex(index)
            self.tbl_relationship.setSelectionMode(QAbstractItemView.MultiSelection)
        for row in range(self.tbl_relationship.rowCount()):
            if int(tbl.item(row, 0).text()) == id_bulk:
                tbl.selectRow(row)
                tbl.scrollToItem(tbl.item(row, 0))

    def canvas_add_outline(self):
        self.lyr_existing.removeSelection()
        self.lyr_bulk_load.removeSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.lst_existing_attrs.clear()
        self.lst_bulk_attrs.clear()

        self.tbl_relationship.clearSelection()

        self.edit_dialog.add_outline()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

        self.circle_tool = None
        self.polyline = None

        # setup circle button
        image_dir = os.path.join(__location__, "..", "icons")
        icon_path = os.path.join(image_dir, "circle.png")
        icon = QIcon()
        icon.addFile(icon_path, QSize(8, 8))
        self.circle_action = QAction(icon, "Draw Circle", iface.building_toolbar)
        iface.registerMainWindowAction(self.circle_action, "Ctrl+0")
        self.circle_action.triggered.connect(self.circle_tool_clicked)
        self.circle_action.setCheckable(True)
        iface.building_toolbar.addAction(self.circle_action)

    def canvas_edit_geometry(self):
        """
        When edit geometry radio button toggled
        """
        self.lyr_existing.removeSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.edit_dialog.edit_geometry()
        self.edit_dialog.show()
        self.change_instance = self.edit_dialog.get_change_instance()

    def canvas_edit_attribute(self):
        """
        When edit outline radio button toggled
        """
        self.lyr_existing.removeSelection()

        self.lst_existing.clear()
        self.lst_bulk.clear()

        self.edit_dialog.show()
        self.edit_dialog.edit_attribute()
        self.change_instance = self.edit_dialog.get_change_instance()

    def circle_tool_clicked(self):
        circle_tool.setup_circle(self)

    def edit_cancel_clicked(self):
        if len(QgsProject.instance().mapLayersByName("bulk_load_outlines")) > 0:
            if isinstance(self.change_instance, bulk_load_changes.EditAttribute):
                try:
                    self.lyr_bulk_load.selectionChanged.disconnect(
                        self.change_instance.selection_changed
                    )
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.EditGeometry):
                try:
                    self.lyr_bulk_load.geometryChanged.disconnect(
                        self.change_instance.geometry_changed
                    )
                except TypeError:
                    pass
            elif isinstance(self.change_instance, bulk_load_changes.AddBulkLoad):
                try:
                    self.lyr_bulk_load.featureAdded.disconnect()
                except TypeError:
                    pass
                try:
                    self.lyr_bulk_load.featureDeleted.disconnect()
                except TypeError:
                    pass
                try:
                    self.lyr_bulk_load.geometryChanged.disconnect()
                except TypeError:
                    pass
                if self.polyline:
                    self.polyline.reset()
                if isinstance(self.circle_tool, PointTool):
                    self.circle_tool.canvas_clicked.disconnect()
                    self.circle_tool.mouse_moved.disconnect()
                    self.circle_tool.deactivate()
                iface.actionPan().trigger()

        iface.actionCancelEdits().trigger()

        QgsProject.instance().layerWillBeRemoved.disconnect(self.layers_removed)

        QgsProject.instance().layerWillBeRemoved.connect(self.layers_removed)

        self.toolbar_setup()

        for val in [
            str(layer.id())
            for layer in QgsProject.instance().layerTreeRoot().layerOrder()
        ]:
            if "existing_subset_extracts" in val:
                self.lyr_existing.removeSelection()
            if "bulk_load_outlines" in val:
                self.lyr_bulk_load.removeSelection()

        self.tbl_relationship.clearSelection()

        self.btn_maptool.click()

        self.change_instance = None

    def reload_bulk_load_layer(self):
        """To ensure QGIS has most up to date ID for the newly split feature see #349"""
        layer_tree_layer = QgsProject.instance().layerTreeRoot().findLayer(self.lyr_bulk_load.id())
        layer_tree_model = iface.layerTreeView().layerTreeModel()
        legend_nodes = layer_tree_model.layerLegendNodes(layer_tree_layer)
        legend_node_null = [ln for ln in legend_nodes if not ln.data(Qt.DisplayRole)]
        legend_node_null[0].setData(Qt.Unchecked, Qt.CheckStateRole)
        legend_node_null[0].setData(Qt.Checked, Qt.CheckStateRole)
        legend_node_added = [
            ln for ln in legend_nodes if ln.data(Qt.DisplayRole) == "Added In Edit"
        ]
        legend_node_added[0].setData(Qt.Unchecked, Qt.CheckStateRole)
        legend_node_added[0].setData(Qt.Checked, Qt.CheckStateRole)

    @property
    def valid_building_use_ids(self):
        """self.valid_building_uses flipped to map use strings to use_id ints"""
        return {use: use_id for use_id, use in self.valid_building_uses.items()}
