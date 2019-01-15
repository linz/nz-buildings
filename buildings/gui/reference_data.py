# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, Qt
from PyQt4.QtGui import QFrame, QIcon, QLineEdit, QMessageBox, QApplication

from buildings.gui.error_dialog import ErrorDialog
from buildings.reference_data import canal_polygons_update, lagoon_polygons_update, lake_polygons_update, pond_polygons_update, river_polygons_update
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

        # disable all check boxes if a curret dataset exists
        sql = bulk_load_select.supplied_dataset_latest_id_and_dates
        result = self.db._execute(sql)
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

        # disable unused check boxes (temporary measure)
        self.chbx_suburbs.setDisabled(1)
        self.chbx_town.setDisabled(1)
        self.chbx_ta.setDisabled(1)
        self.chbx_ta_grid.setDisabled(1)
        self.chbx_capture_source_area.setDisabled(1)
        self.btn_view_key.setIcon(QIcon(os.path.join(__location__, '..', 'icons', 'view_password.png')))

        # set up signals and slots
        self.btn_view_key.pressed.connect(self.view_key)
        self.btn_view_key.released.connect(self.hide_key)
        self.le_key.editingFinished.connect(self.hide_key)
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.btn_ok.clicked.connect(self.ok_clicked)

    def close_cursor(self):
        self.db.close_cursor()

    def connect(self):
        self.db.connect()

    def enable_checkboxes(self):
        self.le_key.setEnabled(1)
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
        self.chbx_capture_source_area.setEnabled(1)
        # clear message
        self.lb_message.setText('')

    def disable_checkboxes(self):
        self.le_key.setDisabled(1)
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
        self.chbx_capture_source_area.setDisabled(1)
        # add message
        self.lb_message.setText('\nNOTE: You can\'t update reference data with\n             a dataset in progress \n')

    @pyqtSlot()
    def view_key(self):
        self.le_key.setEchoMode(QLineEdit.Normal)

    @pyqtSlot()
    def hide_key(self):
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
        # create update log
        sql = 'SELECT buildings_reference.reference_update_log_insert();'
        update_id = self.db._execute(sql)
        update_id = update_id.fetchone()
        # canals
        if self.chbx_canals.isChecked():
            status = canal_polygons_update.update_canals(api_key)
            if status == 'current':
                self.message += 'The canal_polygons table was up to date\n'
            if status == 'updated':
                self.message += 'The canal_polygons table has been updated\n'
            if status == 'error':
                self.request_error()
                return
            if status != 'error':
                sql = 'SELECT buildings_reference.reference_update_log_update_canal_boolean(%s);'
                sql = self.db._execute(sql, (update_id[0],))
        # lagoon
        if self.chbx_lagoons.isChecked():
            status = lagoon_polygons_update.update_lagoons(api_key)
            if status == 'current':
                self.message += 'The lagoon_polygons table was up to date\n'
            if status == 'updated':
                self.message += 'The lagoon_polygons table has been updated\n'
            if status == 'error':
                self.request_error()
                return
            if status != 'error':
                sql = 'SELECT buildings_reference.reference_update_log_update_lagoon_boolean(%s);'
                sql = self.db._execute(sql, (update_id[0],))
        # lake
        if self.chbx_lakes.isChecked():
            status = lake_polygons_update.update_lakes(api_key)
            if status == 'current':
                self.message += 'The lake_polygons table was up to date\n'
            if status == 'updated':
                self.message += 'The lake_polygons table has been updated\n'
            if status == 'error':
                self.request_error()
                return
            if status != 'error':
                sql = 'SELECT buildings_reference.reference_update_log_update_lake_boolean(%s);'
                sql = self.db._execute(sql, (update_id[0],))
        # pond
        if self.chbx_ponds.isChecked():
            status = pond_polygons_update.update_ponds(api_key)
            if status == 'current':
                self.message += 'The pond_polygons table was up to date\n'
            if status == 'updated':
                self.message += 'The pond_polygons table has been updated\n'
            if status == 'error':
                self.request_error()
                return
            if status != 'error':
                sql = 'SELECT buildings_reference.reference_update_log_update_pond_boolean(%s);'
                sql = self.db._execute(sql, (update_id[0],))
        # rivers
        if self.chbx_rivers.isChecked():
            status = river_polygons_update.update_rivers(api_key)
            if status == 'current':
                self.message += 'The river_polygons table was up to date\n'
            if status == 'updated':
                self.message += 'The river_polygons table has been updated\n'
            if status == 'error':
                self.request_error()
                return
            if status != 'error':
                sql = 'SELECT buildings_reference.reference_update_log_update_river_boolean(%s);'
                sql = self.db._execute(sql, (update_id[0],))

        # restore cursor
        QApplication.restoreOverrideCursor()
        # final message box
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

    def message_box(self):
        self.msgbox = QMessageBox(QMessageBox.Question, 'Note', self.message,
                                  buttons=QMessageBox.Ok)

    def request_error(self):
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
