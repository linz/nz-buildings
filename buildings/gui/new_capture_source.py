from builtins import str
from builtins import range

# -*- coding: utf-8 -*-

import os.path
from functools import partial

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot
from qgis.PyQt.QtWidgets import QFrame, QToolButton, QTableWidgetItem, QHeaderView, QAbstractItemView
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import QgsProject
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.gui.new_capture_source_area import NewCaptureSourceArea
from buildings.sql import (
    buildings_common_select_statements as common_select,
    buildings_reference_select_statements as reference_select,
)
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "new_capture_source.ui"))


class NewCaptureSource(QFrame, FORM_CLASS):

    le_external_source = None

    value = ""
    external_source = ""

    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(NewCaptureSource, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.populate_combobox()

        self.dockwidget = dockwidget
        self.layer_registry = LayerRegistry()
        self.error_dialog = None

        iface.mapCanvas().setSelectionColor(QColor("Yellow"))
        # add capture source area layer to canvas and set style
        self.add_capture_source_area_layer()

        # setup toolbar
        self.setup_toolbar()

        # initialise table
        self.init_table()
        # button
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.btn_filter_add.setIcon(QIcon(os.path.join(__location__, "..", "icons", "filter.png")))
        self.btn_filter_del.setIcon(QIcon(os.path.join(__location__, "..", "icons", "filter_del.png")))
        self.btn_new_geometry.setIcon(QIcon(os.path.join(__location__, "..", "icons", "plus.png")))
        # set up signals and slots
        self.capture_source_id = None
        self.btn_save.setDisabled(1)
        self.btn_save.clicked.connect(partial(self.save_clicked, commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.cmb_capture_source_group.currentIndexChanged.connect(self.cmb_capture_source_group_changed)
        self.btn_filter_add.clicked.connect(self.filter_add_clicked)
        self.btn_filter_del.clicked.connect(self.filter_del_clicked)
        self.capture_source_area.selectionChanged.connect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)
        self.btn_new_geometry.clicked.connect(self.add_new_geometry)

        QgsProject.instance().layerWillBeRemoved.connect(self.layers_removed)

    def populate_combobox(self):
        """
            Called on opening of frame populate combobox with capture source group
        """
        result = self.db._execute(common_select.capture_source_group_value_description)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + "- " + str(item[1])
            self.cmb_capture_source_group.addItem(text)

    def init_table(self):
        """
            Set up capture source area table
        """
        tbl = self.tbl_capture_source_area
        tbl.setRowCount(0)
        tbl.setColumnCount(2)
        tbl.setHorizontalHeaderItem(0, QTableWidgetItem("Id"))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem("Area Title"))
        tbl.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setShowGrid(True)
        sql_csa = reference_select.capture_source_area_id_and_name
        result = self.db._execute(sql_csa)
        for (polygon_id, area_title) in result.fetchall():
            row_tbl = tbl.rowCount()
            tbl.setRowCount(row_tbl + 1)
            tbl.setItem(row_tbl, 0, QTableWidgetItem("%s" % polygon_id))
            tbl.setItem(row_tbl, 1, QTableWidgetItem("%s" % area_title))
        tbl.sortItems(0)

    def add_capture_source_area_layer(self):
        """
            Called on opening of frame to add capture source area layer
        """
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles/")
        # add layer
        self.capture_source_area = self.layer_registry.add_postgres_layer(
            "capture_source_area", "capture_source_area", "shape", "buildings_reference", "", ""
        )
        # set style
        self.capture_source_area.loadNamedStyle(path + "capture_source.qml")
        # make capture source area the active layer
        iface.setActiveLayer(self.capture_source_area)

    def setup_toolbar(self):
        """
            Called on opening of from to set up the buildings toolbar for selection only
        """
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        # add selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == "Select Feature(s)":
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # display toolbar
        iface.building_toolbar.show()
        # set current action to select
        iface.actionSelect().trigger()

    def get_capture_source_group(self):
        """
            Returns capture source group from combobox
        """
        text = self.cmb_capture_source_group.currentText()
        if not text:
            return None
        text_ls = text.split("- ")
        return text_ls[0], text_ls[1]

    def get_external_source(self):
        """
            Returns external source from the table
        """
        selected_rows = [row.row() for row in self.tbl_capture_source_area.selectionModel().selectedRows()]
        if len(selected_rows) > 1 or len(selected_rows) == 0:
            return None
        external_source_id, _ = self.get_external_source_from_table(selected_rows[0])
        return external_source_id

    def get_external_source_from_table(self, row):
        """
            Returns external source id and value of the row
        """
        external_source_id = self.tbl_capture_source_area.item(row, 0).text()
        area_title = self.tbl_capture_source_area.item(row, 1).text()
        return external_source_id, area_title

    def update_UI(self):
        """
        Display the capture source info and enable/disable save botton
        """
        selected_rows = [row.row() for row in self.tbl_capture_source_area.selectionModel().selectedRows()]
        if len(selected_rows) == 1:
            self.btn_save.setEnabled(True)
            capt_src_grp_value, capt_src_grp_desc = self.get_capture_source_group()
            external_source_id, area_title = self.get_external_source_from_table(selected_rows[0])
            self.l_confirm.setText(
                "Click save to insert new Capture Source:\n{}\n{}\n({}: {})".format(
                    capt_src_grp_value, capt_src_grp_desc, external_source_id, area_title
                )
            )
        else:
            self.btn_save.setEnabled(False)
            self.l_confirm.clear()

    @pyqtSlot()
    def cmb_capture_source_group_changed(self):
        """
        Called when cmb_capture_source_group is changed
        """
        self.update_UI()

    @pyqtSlot(int)
    def add_new_geometry(self):
        QgsProject.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        self.layer_registry.remove_layer(self.capture_source_area)
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSourceArea(dw))

    @pyqtSlot(list, list, bool)
    def selection_changed(self, added, removed, cleared):
        """
            Called when feature selection is changed
        """
        # disconnect other signals
        self.tbl_capture_source_area.itemSelectionChanged.disconnect(self.tbl_item_changed)
        self.tbl_capture_source_area.clearSelection()
        # list of ids and titles selected
        ids_and_titles = [
            (str(feat["external_area_polygon_id"]), str(feat["area_title"]))
            for feat in self.capture_source_area.selectedFeatures()
        ]
        # if nothing is selected clear line edit and table
        if len(ids_and_titles) == 0:
            pass
        # if areas are selected
        elif len(ids_and_titles) > 0:
            # change table selection
            rows = self.tbl_capture_source_area.rowCount()
            self.tbl_capture_source_area.setSelectionMode(QAbstractItemView.MultiSelection)
            for (area_id, area_title) in ids_and_titles:
                index = 0
                while index < rows:
                    if self.tbl_capture_source_area.item(index, 0).text() == area_id:
                        if self.tbl_capture_source_area.item(index, 1).text() == area_title:
                            self.tbl_capture_source_area.selectRow(index)
                    index = index + 1
            self.tbl_capture_source_area.setSelectionMode(QAbstractItemView.SingleSelection)

        self.update_UI()

        # reconnect line edit signal
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)

    @pyqtSlot()
    def filter_add_clicked(self):
        """
            Called when btn_filter_add is clicked
        """
        # disconnect other signals
        self.capture_source_area.selectionChanged.disconnect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.disconnect(self.tbl_item_changed)

        self.capture_source_area.removeSelection()
        self.init_table()
        list_result = []
        text = self.le_filter.text()
        for row in range(self.tbl_capture_source_area.rowCount()):
            external_source_id = self.tbl_capture_source_area.item(row, 0).text()
            area_title = self.tbl_capture_source_area.item(row, 1).text()
            if text.lower() == external_source_id.lower() or text.lower() in area_title.lower():
                list_result.append((external_source_id, area_title))

        self.tbl_capture_source_area.setRowCount(0)
        for external_source_id, area_title in list_result:
            row_tbl = self.tbl_capture_source_area.rowCount()
            self.tbl_capture_source_area.setRowCount(row_tbl + 1)
            self.tbl_capture_source_area.setItem(row_tbl, 0, QTableWidgetItem("%s" % external_source_id))
            self.tbl_capture_source_area.setItem(row_tbl, 1, QTableWidgetItem("%s" % area_title))
        self.tbl_capture_source_area.sortItems(0)

        # reconnect other signals
        self.capture_source_area.selectionChanged.connect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)

    @pyqtSlot()
    def filter_del_clicked(self):
        """
        Called when btn_filter_del is clicked
        """
        self.tbl_capture_source_area.itemSelectionChanged.disconnect(self.tbl_item_changed)
        self.init_table()
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)
        self.capture_source_area.selectionChanged.emit([], [], False)

    @pyqtSlot()
    def tbl_item_changed(self):
        """
            called when item in table is changed
        """
        # disconnect other signals
        self.capture_source_area.selectionChanged.disconnect(self.selection_changed)
        # clear layer selection
        self.capture_source_area.removeSelection()
        selected_rows = self.tbl_capture_source_area.selectionModel().selectedRows()
        selection = ""
        for row in selected_rows:
            area_id = self.tbl_capture_source_area.item(row.row(), 0).text()
            area_title = self.tbl_capture_source_area.item(row.row(), 1).text()
            if selection == "":
                selection = "\"external_area_polygon_id\" = '{0}' and \"area_title\" = '{1}'".format(area_id, area_title)
            else:
                selection = selection + "or (\"external_area_polygon_id\" = '{0}' and \"area_title\" = '{1}')".format(
                    area_id, area_title
                )
        self.capture_source_area.selectByExpression(selection)

        self.update_UI()

        # reconnect other signals
        self.capture_source_area.selectionChanged.connect(self.selection_changed)

    @pyqtSlot(bool)
    def save_clicked(self, commit_status):
        """
            Called when ok button clicked
        """
        value, description = self.get_capture_source_group()
        if value is None:
            return
        external_source = self.get_external_source()
        if external_source is None:
            return

        # call insert function
        status = self.insert_capture_source(value, description, external_source, commit_status)
        self.btn_save.setDisabled(1)
        if status:
            iface.messageBar().pushMessage(
                "SUCCESS", "You've added a new capture source!", level=QgsMessageBar.SUCCESS, duration=3
            )
            self.capture_source_area.removeSelection()
            self.tbl_capture_source_area.clearSelection()

    @pyqtSlot()
    def exit_clicked(self):
        """
            Called when new capture source exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
            Clean up and remove the new capture source frame.
        """
        self.db.close_connection()
        QgsProject.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        # remove capture source layer
        self.layer_registry.remove_layer(self.capture_source_area)
        # reset and hide toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ["mActionPan"]:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()
        from buildings.gui.menu_frame import MenuFrame

        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        if "capture_source_area" in layerids:
            self.cmb_capture_source_group.setDisabled(1)
            self.btn_filter_add.setDisabled(1)
            self.btn_save.setDisabled(1)
            self.le_filter.setDisabled(1)
            self.tbl_capture_source_area.setDisabled(1)
            iface.messageBar().pushMessage(
                "ERROR",
                "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                level=QgsMessageBar.CRITICAL,
                duration=5,
            )
            return

    def insert_capture_source(self, value, description, external_source, commit_status):
        """
        add values to the capture_source table.
        capture_source_id is autogenerated
        """
        # find capture source group id based on capture source group value
        result = self.db._execute(common_select.capture_source_group_by_value_and_description, (value, description))
        capture_source_group_id = result.fetchall()[0][0]

        result = self.db._execute(
            common_select.capture_source_external_id_and_area_title_by_group_id, (capture_source_group_id,)
        )
        to_add = True
        for (external_source_id, area_title) in result.fetchall():
            if external_source_id == external_source:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    "\n --------------- CAPTURE SOURCE GROUP " "EXISTS --------------- \n\n Group already" " exists in table"
                )
                self.error_dialog.show()
                to_add = False
                break
        if to_add:
            self.db.open_cursor()
            sql = "SELECT buildings_common.capture_source_insert(%s, %s);"
            result = self.db.execute_no_commit(sql, (capture_source_group_id, external_source))
            self.capture_source_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
        return to_add
