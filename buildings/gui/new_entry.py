# -*- coding: utf-8 -*-

import os.path
from functools import partial

from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QFrame
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from buildings.gui.error_dialog import ErrorDialog
from buildings.sql import (buildings_bulk_load_select_statements as bulk_load_select,
                           buildings_common_select_statements as common_select,
                           buildings_select_statements as buildings_select)
from buildings.utilities import database as db


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'new_entry.ui'))


class NewEntry(QFrame, FORM_CLASS):

    value = ''
    new_type = ''

    def __init__(self, dockwidget, parent=None):
        """Constructor."""
        super(NewEntry, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
        self.db = db
        self.db.connect()

        # set up signals and slots
        self.organisation_id = None
        self.lifecycle_stage_id = None
        self.capture_method_id = None
        self.capture_source_group_id = None
        self.btn_ok.clicked.connect(
            partial(self.ok_clicked, commit_status=True))
        self.btn_exit.clicked.connect(self.exit_clicked)
        self.le_description.setDisabled(1)
        self.cmb_new_type_selection.currentIndexChanged.connect(self.set_new_type)

    def close_cursor(self):
        db.close_cursor()

    def connect(self):
        db.connect()

    def get_comments(self):
        """
        Get comments from comment box, return default if empty
        """
        if self.le_new_entry.text() == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n -------------------- EMPTY VALUE FIELD ------'
                '-------------- \n\n Null values not allowed'
            )
            self.error_dialog.show()
            return
        if len(self.le_new_entry.text()) >= 40:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(
                '\n -------------------- VALUE TOO LONG ---------'
                '----------- \n\n Enter less than 40 characters'
            )
            self.error_dialog.show()
            return
        return self.le_new_entry.text()

    def get_description(self):
        """
        Returns description input
        This is only required if the type to add is
        capture source group
        """
        if self.new_type != 'Capture Source Group':
            return
        else:
            if self.le_description.text() == '':
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- EMPTY DESCRIPTION FIELD '
                    '-------------------- \n\n Null values not allowed'
                )
                self.error_dialog.show()
                return
            if len(self.le_description.text()) >= 40:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report(
                    '\n -------------------- DESCRIPTION TOO LONG ---'
                    '----------------- \n\n Enter less than 40 characters'
                )
                self.error_dialog.show()
                return
            return self.le_description.text()

    def get_combobox_value(self):
        """
        Get the type to add from the combo box
        """
        return self.cmb_new_type_selection.currentText()

    @pyqtSlot()
    def set_new_type(self):
        """
        Called when type to add combobox index is chaged
        """
        self.new_type = self.cmb_new_type_selection.currentText()
        if self.new_type == 'Capture Source Group':
            self.le_description.setEnabled(1)
        else:
            self.le_description.setDisabled(1)

    @pyqtSlot(bool)
    def ok_clicked(self, commit_status):
        # get value
        self.value = self.get_comments()
        # get type
        self.new_type = self.get_combobox_value()
        self.status = False
        # call insert depending on type
        if self.value is not None:
            if self.new_type == 'Organisation':
                self.status = self.new_organisation(self.value, commit_status)

            elif self.new_type == 'Lifecycle Stage':
                self.status = self.new_lifecycle_stage(self.value, commit_status)

            elif self.new_type == 'Capture Method':
                self.status = self.new_capture_method(self.value, commit_status)

            elif self.new_type == 'Capture Source Group':
                self.description = self.get_description()
                if self.description is not None:
                    self. status = self.new_capture_source_group(
                        self.value, self.description, commit_status)
        if self.status:
            iface.messageBar().pushMessage("SUCCESS",
                                           "You've added a new {}!".format(self.new_type),
                                           level=QgsMessageBar.SUCCESS, duration=3)

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

    def new_organisation(self, organisation, commit_status):
        """
            update the organisation table.
            value output = organisation auto generate id
        """
        # check if organisation in buildings_bulk_load.organisation table
        result = self.db._execute(
            bulk_load_select.organisation_by_value, (organisation,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(' ')
            self.error_dialog.fill_report(
                '\n -------------------- ORGANISATION EXISTS ----'
                '---------------- \n\n Value entered exists in table')
            self.error_dialog.show()
            return False
        # if it isn't in the table add to table
        elif len(ls) == 0:
                # enter but don't commit
            self.db.open_cursor()
            sql = 'SELECT buildings_bulk_load.organisation_insert(%s);'
            result = self.db.execute_no_commit(sql, (organisation,))
            self.organisation_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_new_entry.clear()
            return True

    def new_lifecycle_stage(self, lifecycle_stage, commit_status):
        """
        update the lifecycle stage table
        value = lifecycle stage auto generate id
        """
        # check if lifecycle stage in buildings.lifecycle_stage table
        result = self.db._execute(
            buildings_select.lifecycle_stage_by_value, (lifecycle_stage,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(' ')
            self.error_dialog.fill_report(
                '\n -------------------- LIFECYCLE STAGE EXISTS -'
                '------------------- \n\n Value entered exists in table'
            )
            self.error_dialog.show()
            return False
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # enter but don't commit
            self.db.open_cursor()
            sql = 'SELECT buildings.lifecycle_stage_insert(%s);'
            result = self.db.execute_no_commit(sql, (lifecycle_stage,))
            self.lifecycle_stage_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_new_entry.clear()
            return True

    def new_capture_method(self, capture_method, commit_status):
        """
        update the capture method table
        value = capture method autogenerate id
        """

        # check if capture method in buildings_common.capture_method table
        result = self.db._execute(
            common_select.capture_method_by_value, (capture_method,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(' ')
            self.error_dialog.fill_report(
                '\n -------------------- CAPTURE METHOD EXISTS --'
                '------------------ \n\n Value entered exists in table'
            )
            self.error_dialog.show()
            return False
        # if it isn't in the table add to table
        elif len(ls) == 0:
                # enter but don't commit
            self.db.open_cursor()
            sql = 'SELECT buildings_common.capture_method_insert(%s);'
            result = self.db.execute_no_commit(sql, (capture_method,))
            self.capture_method_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_new_entry.clear()
            return True

    def new_capture_source_group(self, capture_source_group, description,
                                 commit_status):
        """
        update the capture source group table
        value = capture source group autogenerate id
        """
        # Check if capture source group in buildings
        # _common.capture_source_group table
        result = self.db._execute(common_select.capture_source_group_by_value_and_description, (capture_source_group, description))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(' ')
            self.error_dialog.fill_report(
                '\n ---------------- CAPTURE SOURCE GROUP '
                '---------------- \n\n Value entered exists in table'
            )
            self.error_dialog.show()
            return False
        elif len(ls) == 0:
            # enter but don't commit
            self.db.open_cursor()
            sql = 'SELECT buildings_common.capture_source_group_insert(%s, %s);'
            result = self.db.execute_no_commit(
                sql, (capture_source_group, description))
            self.capture_source_group_id = result.fetchall()[0][0]
            if commit_status:
                self.db.commit_open_cursor()
            self.le_new_entry.clear()
            self.le_description.clear()
            return True
