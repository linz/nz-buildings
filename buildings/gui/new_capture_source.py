# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFrame, QIcon, QColor, QToolButton, QTableWidgetItem, QHeaderView, QAbstractItemView
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.gui.new_capture_source_area import NewCaptureSourceArea
from buildings.sql import (buildings_common_select_statements as common_select,
                           buildings_reference_select_statements as reference_select)
from buildings.utilities import database as db
from buildings.utilities.layers import LayerRegistry

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'new_capture_source.ui'))


class NewCaptureSource(QFrame, FORM_CLASS):

    le_external_source = None

    value = ''
    external_source = ''

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

        iface.mapCanvas().setSelectionColor(QColor('Yellow'))
        # add capture source area layer to canvas and set style
        self.add_capture_source_area_layer()

        # setup toolbar
        self.setup_toolbar()

        # initialise table
        self.init_table()
        # button
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.btn_validate.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'tick.png')))
        self.btn_new_geometry.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'plus.png')))
        # set up signals and slots
        self.capture_source_id = None
        self.btn_save.setDisabled(1)
        self.btn_save.clicked.connect(partial(
            self.save_clicked, commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.le_external_source_id.textChanged.connect(self.disable_save)
        self.btn_validate.clicked.connect(self.validate)
        self.capture_source_area.selectionChanged.connect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)
        self.btn_new_geometry.clicked.connect(self.add_new_geometry)

        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.layers_removed)

    def populate_combobox(self):
        """
            Called on opening of frame populate combobox with capture source group
        """
        result = self.db._execute(common_select.capture_source_group_value_description)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1])
            self.cmb_capture_source_group.addItem(text)

    def init_table(self):
        """
            Set up capture source area table
        """
        tbl = self.tbl_capture_source_area
        tbl.setRowCount(0)
        tbl.setColumnCount(2)
        tbl.setHorizontalHeaderItem(0, QTableWidgetItem('Id'))
        tbl.setHorizontalHeaderItem(1, QTableWidgetItem('Area Title'))
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
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'styles/')
        # add layer
        self.capture_source_area = self.layer_registry.add_postgres_layer(
            'capture_source_area', 'capture_source_area',
            'shape', 'buildings_reference', '', '')
        # set style
        self.capture_source_area.loadNamedStyle(path + 'capture_source.qml')
        # make capture source area the active layer
        iface.setActiveLayer(self.capture_source_area)

    def setup_toolbar(self):
        """
            Called on opening of from to set up the buildings toolbar for selection only
        """
        selecttools = iface.attributesToolBar().findChildren(QToolButton)
        # reset toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        # add selection actions
        iface.building_toolbar.addSeparator()
        for sel in selecttools:
            if sel.text() == 'Select Feature(s)':
                for a in sel.actions()[0:3]:
                    iface.building_toolbar.addAction(a)
        # display toolbar
        iface.building_toolbar.show()
        # set current action to select
        iface.actionSelect().trigger()

    def get_comments(self):
        """
        Returns comment from external source id line edit
        returns None if empty/disabled
        """
        return self.le_external_source_id.text()

    def get_combobox_value(self):
        """
            Returns capture source group from combobox
        """
        text = self.cmb_capture_source_group.currentText()
        text_ls = text.split('-')
        return text_ls[0]

    @pyqtSlot(int)
    def add_new_geometry(self):
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
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
        # if nothing is selected clear line edit and table
        if len(self.capture_source_area.selectedFeatures()) == 0:
            self.tbl_capture_source_area.clearSelection()
        # if areas are selected
        if len(self.capture_source_area.selectedFeatures()) > 0:
            # list of ids selected
            self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_source_area.selectedFeatures()]
            # change table selection
            self.tbl_capture_source_area.clearSelection()
            rows = self.tbl_capture_source_area.rowCount()
            selected_rows = [row.row() for row in self.tbl_capture_source_area.selectionModel().selectedRows()]
            self.tbl_capture_source_area.setSelectionMode(QAbstractItemView.MultiSelection)
            for item in self.ids:
                index = 0
                while index < rows:
                    if index not in selected_rows:
                        if self.tbl_capture_source_area.item(index, 0).text() == item:
                            self.tbl_capture_source_area.selectRow(index)
                    index = index + 1
            self.tbl_capture_source_area.setSelectionMode(QAbstractItemView.SingleSelection)
        # reconnect line edit signal
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)

    @pyqtSlot()
    def disable_save(self):
        """
            Called when line edit is changed
        """
        # disable save btn whenever line edit is changed
        self.btn_save.setDisabled(1)
        # disconnect other signals
        self.capture_source_area.selectionChanged.disconnect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.disconnect(self.tbl_item_changed)
        # clear selection and table
        self.capture_source_area.removeSelection()
        self.tbl_capture_source_area.clearSelection()
        # reconnect other signals
        self.capture_source_area.selectionChanged.connect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)

    @pyqtSlot()
    def validate(self):
        """
            Called when validate button is clicked
        """
        # disconnect other signals
        self.capture_source_area.selectionChanged.disconnect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.disconnect(self.tbl_item_changed)
        text = self.le_external_source_id.text()
        # remove selections
        self.capture_source_area.removeSelection()
        self.tbl_capture_source_area.clearSelection()
        # change table seletion
        for row in range(self.tbl_capture_source_area.rowCount()):
            if self.tbl_capture_source_area.item(row, 0).text() == text:
                self.tbl_capture_source_area.selectRow(row)
        if len([row.row() for row in self.tbl_capture_source_area.selectionModel().selectedRows()]) > 0:
            # select from layer
            selection = '"external_area_polygon_id" = {}'.format(text)
            self.capture_source_area.selectByExpression(selection)
            self.btn_save.setEnabled(1)
        else:
            self.btn_save.setDisabled(1)
        # reconnect other signals
        self.capture_source_area.selectionChanged.connect(self.selection_changed)
        self.tbl_capture_source_area.itemSelectionChanged.connect(self.tbl_item_changed)

    @ pyqtSlot()
    def tbl_item_changed(self):
        """
            called when item in table is changed
        """
        # disconnect other signals
        self.capture_source_area.selectionChanged.disconnect(self.selection_changed)
        # clear layer selection
        self.capture_source_area.removeSelection()
        selection = ''
        for row in self.tbl_capture_source_area.selectionModel().selectedRows():
            area_id = self.tbl_capture_source_area.item(row.row(), 0).text()
            if selection == '':
                selection = '"external_area_polygon_id" = {}'.format(area_id)
            else:
                selection = selection + 'or "external_area_polygon_id" = {}'.format(area_id)
        self.capture_source_area.selectByExpression(selection)
        # reconnect other signals
        self.capture_source_area.selectionChanged.connect(self.selection_changed)

    @pyqtSlot(bool)
    def save_clicked(self, commit_status):
        """
            Called when ok button clicked
        """
        # get external source id
        external_source = self.get_comments()
        # get type
        value = self.get_combobox_value()
        # call insert function
        status = self.insert_capture_source(value, external_source, commit_status)
        self.le_external_source_id.clear()
        self.capture_source_area.removeSelection()
        self.tbl_capture_source_area.clearSelection()
        self.btn_save.setDisabled(1)
        if status:
            iface.messageBar().pushMessage("SUCCESS",
                                           "You've added a new capture source!",
                                           level=QgsMessageBar.SUCCESS, duration=3)

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
        QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.layers_removed)
        # remove capture source layer
        self.layer_registry.remove_layer(self.capture_source_area)
        # reset and hide toolbar
        for action in iface.building_toolbar.actions():
            if action.objectName() not in ['mActionPan']:
                iface.building_toolbar.removeAction(action)
        iface.building_toolbar.hide()
        from buildings.gui.menu_frame import MenuFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot(str)
    def layers_removed(self, layerids):
        self.layer_registry.update_layers()
        if 'capture_source_area' in layerids:
            self.cmb_capture_source_group.setDisabled(1)
            self.btn_validate.setDisabled(1)
            self.btn_save.setDisabled(1)
            self.le_external_source_id.setDisabled(1)
            self.tbl_capture_source_area.setDisabled(1)
            iface.messageBar().pushMessage("ERROR",
                                           "Required layer Removed! Please reload the buildings plugin or the current frame before continuing",
                                           level=QgsMessageBar.CRITICAL, duration=5)
            return

    def insert_capture_source(self, value, external_source, commit_status):
        """
        add values to the capture_source table.
        capture_source_id is autogenerated
        """
        # find capture source group id based on capture source group value
        result = self.db._execute(common_select.capture_source_group_by_value, (value,))
        capture_source_group_id = result.fetchall()[0][0]

        result = self.db._execute(common_select.capture_source_by_group_id, (capture_source_group_id,))
        to_add = True
        for (external_source_id, ) in result.fetchall():
            if external_source_id == external_source:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n --------------- CAPTURE SOURCE GROUP '
                    'EXISTS --------------- \n\n Group already'
                    ' exists in table'
                )
                self.error_dialog.show()
                to_add = False
                break
        if to_add:
            self.db.open_cursor()
            sql = 'SELECT buildings_common.capture_source_insert(%s, %s);'
            result = self.db.execute_no_commit(
                sql, (capture_source_group_id, external_source))
            self.capture_source_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_external_source_id.clear()
        return to_add
