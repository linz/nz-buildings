# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFrame, QColor, QToolButton
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import select_statements as select
from buildings.utilities import database as db


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'new_capture_source.ui'))


class NewCaptureSource(QFrame, FORM_CLASS):

    le_external_source = None

    value = ''
    external_source = ''

    def __init__(self, dockwidget, layer_registry, parent=None):
        """Constructor."""
        super(NewCaptureSource, self).__init__(parent)
        self.setupUi(self)

        self.db = db
        self.db.connect()

        self.populate_combobox()
        self.le_external_source_id.setDisabled(1)

        self.dockwidget = dockwidget
        self.layer_registry = layer_registry
        self.error_dialog = None

        iface.mapCanvas().setSelectionColor(QColor('Yellow'))
        # add capture source area layer to canvas and set style
        self.add_capture_source_area_layer()

        # setup toolbar
        self.setup_toolbar()

        # set up signals and slots
        self.capture_source_id = None
        self.btn_ok.clicked.connect(partial(
            self.ok_clicked, commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)

        self.rad_external_source.toggled.connect(self.enable_external_source)
        self.capture_source_area.selectionChanged.connect(self.selection_changed)

    def populate_combobox(self):
        """Called on opening of frame populate combobox with capture source group
        """
        result = self.db._execute(select.capture_srcgrp_value_description)
        ls = result.fetchall()
        for item in ls:
            text = str(item[0]) + '- ' + str(item[1])
            self.cmb_capture_source_group.addItem(text)

    def add_capture_source_area_layer(self):
        """Called on opening of frame to add capture source area layer
        # """
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
        """Called on opening of from to set up the buildings toolbar for selection only
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
        if not self.rad_external_source.isChecked():
            return None
        else:
            return self.le_external_source_id.text()

    def get_combobox_value(self):
        """Returns capture source group from combobox
        """
        text = self.cmb_capture_source_group.currentText()
        text_ls = text.split('-')
        return text_ls[0]

    @pyqtSlot(bool)
    def enable_external_source(self, boolVal):
        """Called when external source radiobutton is toggled
        """
        if self.rad_external_source.isChecked():
            self.le_external_source_id.setEnabled(1)
            if len(self.capture_source_area.selectedFeatures()) > 0:
                self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_source_area.selectedFeatures()]
                self.le_external_source_id.setText(', '.join(self.ids))
        if not self.rad_external_source.isChecked():
            self.le_external_source_id.clear()
            self.le_external_source_id.setDisabled(1)

    @pyqtSlot(list, list, bool)
    def selection_changed(self, added, removed, cleared):
        """Called when feature selection is changed
        """
        if len(self.capture_source_area.selectedFeatures()) == 0:
            if self.rad_external_source.isChecked():
                self.rad_external_source.toggle()
            self.le_external_source_id.setDisabled(1)
        else:
            if not self.rad_external_source.isChecked():
                self.rad_external_source.toggle()
            self.le_external_source_id.setEnabled(1)
            self.ids = [str(feat["external_area_polygon_id"]) for feat in self.capture_source_area.selectedFeatures()]
            self.le_external_source_id.setText(', '.join(self.ids))

    @pyqtSlot(bool)
    def ok_clicked(self, commit_status):
        """Called when ok button clicked
        """
        # get external source id
        self.external_source = self.get_comments()
        # if no external source is entered and radio button selected open error
        if self.rad_external_source.isChecked():
            if self.external_source == '':
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- EMPTY VALUE FIELD ------'
                    '-------------- \n\n If no external source id deselect '
                    'external source radio button'
                )
                self.error_dialog.show()
                return
            if len(self.external_source) > 250:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- VALUE TOO LONG ---------'
                    '----------- \n\n Enter less than 250 characters'
                )
                self.error_dialog.show()
                return
        # get type
        self.value = self.get_combobox_value()
        # call insert function
        self.capture_source_id = self.insert_capture_source(
            self.value, self.external_source, commit_status)
        self.le_external_source_id.clear()

    @pyqtSlot()
    def exit_clicked(self):
        """Called when new capture source exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """Clean up and remove the new capture source frame.
        """
        self.db.close_connection()
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
        dw.new_widget(MenuFrame(dw, self.layer_registry))

    def insert_capture_source(self, value, external_source, commit_status):
        """
        add values to the capture_source table.
        capture_source_id is autogenerated
        """
        # find capture source group id based on capture source group value
        result = self.db._execute(select.capture_srcgrp_by_value, (value,))
        capture_source_group_id = result.fetchall()[0][0]

        # check if capture source exists in table
        if external_source is None:
            result = self.db._execute(
                select.capture_source_by_group_id_external_is_null, (
                    capture_source_group_id,
                ))
        else:
            result = self.db._execute(
                select.capture_source_by_external_or_group_id, (
                    external_source, capture_source_group_id,
                ))
        ls = result.fetchall()
        if len(ls) > 0:
            to_add = True
            for item in ls:
                # if capture source with same CSG and ES exists
                if item[1] == capture_source_group_id:
                    if item[2] == external_source:
                        self.error_dialog = ErrorDialog()
                        self.error_dialog.fill_report(
                            '\n --------------- CAPTURE SOURCE GROUP '
                            'EXISTS --------------- \n\n Group already'
                            ' exists in table'
                        )
                        self.error_dialog.show()
                        to_add = False
            if to_add:
                # enter but don't commit
                self.db.open_cursor()
                sql = 'SELECT buildings_common.capture_source_insert(%s, %s);'
                result = self.db.execute_no_commit(
                    sql, (capture_source_group_id, external_source))
                self.capture_source_id = result.fetchall()[0][0]
                if commit_status:
                    self.db.commit_open_cursor()
                self.le_external_source_id.clear()
        # if sql querry returns nothing add to table
        elif len(ls) == 0:
            # enter but don't commit
            self.db.open_cursor()
            sql = 'SELECT buildings_common.capture_source_insert(%s, %s);'
            result = self.db.execute_no_commit(
                sql, (capture_source_group_id, external_source))
            self.capture_source_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_external_source_id.clear()
