# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QFrame, QIcon, QLineEdit, QMessageBox, QApplication, QCheckBox

from buildings.gui.error_dialog import ErrorDialog
from buildings.reference_data import topo50
from buildings.sql import buildings_bulk_load_select_statements as bulk_load_select
from buildings.utilities import database as db

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'reference_data.ui'))


class UpdateReferenceData(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(UpdateReferenceData, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.db = db
        self.db.connect()
        self.error_dialog = None
        self.message = ''
        self.btn_view_key.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'view_password.png')))

        # disable all check boxes if a curret dataset exists
        sql = bulk_load_select.supplied_dataset_latest_id_and_dates
        result = self.db.execute_return(sql)
        if result is None:
            self.enable_checkboxes()
        else:
            result = result.fetchone()
            process = result[1]
            transfer = result[2]
            if process is not None and transfer is not None:
                self.enable_checkboxes()
            else:
                self.disable_checkboxes()

        # set up signals and slots
        self.btn_view_key.pressed.connect(self.view_key)
        self.btn_view_key.released.connect(self.hide_key)
        self.le_key.editingFinished.connect(self.hide_key)
        self.grbx_topo.toggled.connect(self.check_all_topo)
        self.grbx_admin.toggled.connect(self.check_all_admin)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_ok.clicked.connect(self.ok_clicked)

    def close_cursor(self):
        self.db.close_cursor()

    def connect(self):
        self.db.connect()

    def enable_checkboxes(self):
        """Enable frame"""
        self.le_key.setEnabled(1)
        self.grbx_topo.setEnabled(1)
        self.grbx_admin.setEnabled(1)
        self.chbx_canals.setEnabled(1)
        self.chbx_coastline_and_islands.setEnabled(1)
        self.chbx_lagoons.setEnabled(1)
        self.chbx_lakes.setEnabled(1)
        self.chbx_ponds.setEnabled(1)
        self.chbx_rivers.setEnabled(1)
        self.chbx_swamps.setEnabled(1)
        self.chbx_suburbs.setEnabled(1)
        self.chbx_town.setEnabled(1)
        self.chbx_ta.setEnabled(1)
        self.chbx_ta_grid.setEnabled(1)
        self.btn_ok.setEnabled(1)
        # clear message
        self.lb_message.setText('')

    def disable_checkboxes(self):
        """Disable frame (when outlines dataset in progress)"""
        self.le_key.setDisabled(1)
        self.grbx_topo.setDisabled(1)
        self.grbx_admin.setDisabled(1)
        self.chbx_canals.setDisabled(1)
        self.chbx_coastline_and_islands.setDisabled(1)
        self.chbx_lagoons.setDisabled(1)
        self.chbx_lakes.setDisabled(1)
        self.chbx_ponds.setDisabled(1)
        self.chbx_rivers.setDisabled(1)
        self.chbx_swamps.setDisabled(1)
        self.chbx_suburbs.setDisabled(1)
        self.chbx_town.setDisabled(1)
        self.chbx_ta.setDisabled(1)
        self.chbx_ta_grid.setDisabled(1)
        self.btn_ok.setDisabled(1)
        # add message
        self.lb_message.setText('\nNOTE: You can\'t update reference data with\n             a dataset in progress \n')

    @pyqtSlot()
    def view_key(self):
        """Called when view key button pressed"""
        self.le_key.setEchoMode(QLineEdit.Normal)

    @pyqtSlot()
    def hide_key(self):
        """Called when view key button released/editing of text finished"""
        self.le_key.setEchoMode(QLineEdit.Password)

    @pyqtSlot()
    def ok_clicked(self):
        """Called when ok btn clicked"""
        # set cursor to busy
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.message = ''
        api_key = self.le_key.text()
        if api_key == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n------------- NO API KEY -------------'
                '\n\nPlease enter a koordinates api key to'
                ' update the reference data.'
            )
            QApplication.restoreOverrideCursor()
            self.error_dialog.show()
            return
        updates = []
        # canals
        if self.chbx_canals.isChecked():
            status = topo50.update_topo50(api_key, 'canal')
            self.update_message(status, 'canal_polygons')
            if status != 'error':
                updates.append('canal')
        # lagoon
        if self.chbx_lagoons.isChecked():
            status = topo50.update_topo50(api_key, 'lagoon')
            self.update_message(status, 'lagoon_polygons')
            if status != 'error':
                updates.append('lagoon')
        # lake
        if self.chbx_lakes.isChecked():
            status = topo50.update_topo50(api_key, 'lake')
            self.update_message(status, 'lake_polygons')
            if status != 'error':
                updates.append('lake')
        # pond
        if self.chbx_ponds.isChecked():
            status = topo50.update_topo50(api_key, 'pond')
            self.update_message(status, 'pond_polygons')
            if status != 'error':
                updates.append('pond')
        # rivers
        if self.chbx_rivers.isChecked():
            status = topo50.update_topo50(api_key, 'river')
            self.update_message(status, 'river_polygons')
            if status != 'error':
                updates.append('river')
        # swamp
        if self.chbx_swamps.isChecked():
            status = topo50.update_topo50(api_key, 'swamp')
            self.update_message(status, 'swamp_polygons')
            if status != 'error':
                updates.append('swamp')

        sql = 'SELECT buildings_reference.reference_update_log_insert_log(%s);'
        self.db.execute_return(sql, (updates,))
        # restore cursor
        QApplication.restoreOverrideCursor()
        # final message box
        if self.message == '':
            self.message = 'No layers were updated.'
        self.message_box()
        self.msgbox.exec_()

    @pyqtSlot()
    def exit_clicked(self):
        """
        Called when new entry exit button clicked.
        """
        self.close_frame()
        self.dockwidget.lst_sub_menu.clearSelection()

    def close_frame(self):
        """
        Clean up and remove the new entry frame.
        """
        self.db.close_connection()
        from buildings.gui.menu_frame import MenuFrame
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame(dw))

    @pyqtSlot()
    def check_all_topo(self):
        """ Called when combobox to check all topo layers is toggled"""
        if self.grbx_topo.isChecked():
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(True)
                box.setEnabled(1)
        else:
            for box in self.grbx_topo.findChildren(QCheckBox):
                box.setChecked(False)
                box.setEnabled(1)

    @pyqtSlot()
    def check_all_admin(self):
        """ Called when combobox to check all admin layers is toggled"""
        if self.grbx_admin.isChecked():
            for box in self.grbx_admin.findChildren(QCheckBox):
                box.setChecked(True)
                box.setEnabled(1)
        else:
            for box in self.grbx_admin.findChildren(QCheckBox):
                box.setChecked(False)
                box.setEnabled(1)

    def message_box(self):
        self.msgbox = QMessageBox(QMessageBox.Information, 'Note', self.message,
                                  buttons=QMessageBox.Ok)

    def request_error(self):
        """Called when failure to request a changeset"""
        self.error_dialog = ErrorDialog()
        self.error_dialog.fill_report(
            '\n ---------------------- REQUEST ERROR ---------'
            '----------------- \n\nSomething appears to have gone'
            ' wrong with requesting the changeset, first please'
            ' check you entered the correct api key if this is correct'
            ' then please inform a developer.'
        )
        self.error_dialog.show()
        QApplication.restoreOverrideCursor()

    def update_message(self, status, name):
        """add to message for display at end of processing"""
        if status == 'current':
            self.message += 'The {} table was up to date\n'.format(name)
        if status == 'updated':
            self.message += 'The {} table has been updated\n'.format(name)
        if status == 'error':
            self.message += 'The request errored on the {} table\n'.format(name)
            self.request_error()
            return
