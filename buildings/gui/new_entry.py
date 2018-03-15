# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import qgis

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_entry.ui"))

db.connect()

class NewEntry(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()
    value = ''
    new_type = ''

    def __init__(self, parent=None):
        """Constructor."""
        super(NewEntry, self).__init__(parent)
        self.setupUi(self)

        # set up signals and slots
        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)
        self.le_description.setDisabled(1)
        self.cmb_new_type_selection.currentIndexChanged.connect(self.set_new_type)

    def get_comments(self):
        """
        Get comments from comment box, return default if empty
        """
        if self.le_new_entry.text() == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- EMPTY VALUE FIELD -------------------- \n\n Null values not allowed")
            self.error_dialog.show()
            return
        if len(self.le_new_entry.text()) >= 40:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- VALUE TOO LONG -------------------- \n\n Enter less than 40 characters")
            self.error_dialog.show()
            return
        return self.le_new_entry.text()

    def get_description(self):
        if self.new_type != "Capture Source Group":
            return
        else:
            if self.le_description.text() == '':
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- EMPTY DESCRIPTION FIELD -------------------- \n\n Null values not allowed")
                self.error_dialog.show()
                return
            if len(self.le_description.text()) >= 40:
                self.error_dialog = ErrorDialog()
                self.error_dialog.fill_report("\n -------------------- DESCRIPTION TOO LONG -------------------- \n\n Enter less than 40 characters")
                self.error_dialog.show()
                return
            return self.le_description.text()

    def get_combobox_value(self):
        """
        Get the type from the combo box
        """
        index = self.cmb_new_type_selection.currentIndex()
        return self.cmb_new_type_selection.itemText(index)

    def set_new_type(self):
        index = self.cmb_new_type_selection.currentIndex()
        self.new_type = self.cmb_new_type_selection.itemText(index)
        if self.new_type == 'Capture Source Group':
            self.le_description.setEnabled(1)
        else:
            self.le_description.setDisabled(1)

    def ok_clicked(self):
        # get value
        self.value = self.get_comments()
        # get type
        self.new_type = self.get_combobox_value()
        # call insert depending on type
        if self.value is not None:
            if self.new_type == 'Organisation':
                self.new_organisation(self.value)
            elif self.new_type == 'Lifecycle Stage':
                self.new_lifecycle_stage(self.value)
            elif self.new_type == 'Capture Method':
                self.new_capture_method(self.value)
            elif self.new_type == 'Capture Source Group':
                self.description = self.get_description()
                if self.description is not None:
                    self.new_capture_source_group(self.value, self.description)

    def cancel_clicked(self):
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame)

    def new_organisation(self, organisation):
        # =========================================================
        # New Organisation
        """
            update the organisation table.
            value output = organisation auto generate id
        """
        # check if organisation in buildings_bulk_load.organisation table
        sql = "SELECT * FROM buildings_bulk_load.organisation WHERE buildings_bulk_load.organisation.value = %s;"
        result = db._execute(sql, data=(organisation,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(" ")
            self.error_dialog.fill_report("\n -------------------- ORGANISATION EXISTS -------------------- \n\n Value entered exists in table")
            self.error_dialog.show()
            # TODO: return dialog box that organisation exists
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT organisation_id FROM buildings_bulk_load.organisation;"
            result = db._execute(sql)
            attributes = result.fetchall()
            length = len(attributes)
            if length == 0:
                id = 1
            else:
                id = attributes[length - 1][0] + 1  # id for new organisation
            # enter new organisation
            sql = "INSERT INTO buildings_bulk_load.organisation(organisation_id, value)VALUES(%s, %s);"
            db.execute(sql, (id, organisation))
            self.le_new_entry.clear()

    def new_lifecycle_stage(self, lifecycle_stage):
        # New Lifecycle Stage
        """
        update the lifecycle stage table
        value = lifecycle stage auto generate id
        """
        # check if lifecycle stage in buildings.lifecycle_stage table
        sql = "SELECT * FROM buildings.lifecycle_stage WHERE buildings.lifecycle_stage.value = %s;"
        result = db._execute(sql, data=(lifecycle_stage,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(" ")
            self.error_dialog.fill_report("\n -------------------- LIFECYCLE STAGE EXISTS -------------------- \n\n Value entered exists in table")
            self.error_dialog.show()
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT lifecycle_stage_id FROM buildings.lifecycle_stage;"
            result = db._execute(sql)
            attributes = result.fetchall()
            length = len(attributes)
            if length == 0:
                id = 1
            else:
                id = attributes[length - 1][0] + 1  # id for new lifecycle stage
            # enter new lifecycle stage
            sql = "INSERT INTO buildings.lifecycle_stage(lifecycle_stage_id, value)VALUES(%s, %s);"
            db.execute(sql, (id, lifecycle_stage))
            self.le_new_entry.clear()

    def new_capture_method(self, capture_method):
        # New Capture Method
        """
        update the capture method table
        value = capture method autogenerate id
        """

        # check if capture method in buildings_common.capture_method table
        sql = "SELECT * FROM buildings_common.capture_method WHERE buildings_common.capture_method.value = %s;"
        result = db._execute(sql, data=(capture_method,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(" ")
            self.error_dialog.fill_report("\n -------------------- CAPTURE METHOD EXISTS -------------------- \n\n Value entered exists in table")
            self.error_dialog.show()
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT capture_method_id FROM buildings_common.capture_method;"
            result = db._execute(sql)
            attributes = result.fetchall()
            length = len(attributes)
            if length == 0:
                id = 1
            else:
                id = attributes[length - 1][0] + 1  # id for new capture method
            # enter new capture method
            sql = "INSERT INTO buildings_common.capture_method(capture_method_id, value)VALUES(%s, %s);"
            db.execute(sql, data=(id, capture_method))
            self.le_new_entry.clear()

    def new_capture_source_group(self, capture_source_group, description):
        # New Capture Source Group
        """
        update the capture source group table
            value = capture source group autogenerate id
        """
        # Check if capture source group in buildings_common.capture_source_group table
        sql = "SELECT * FROM buildings_common.capture_source_group WHERE buildings_common.capture_source_group.value = %s;"
        result = db._execute(sql, data=(capture_source_group,))
        ls = result.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report(" ")
            self.error_dialog.fill_report("\n ---------------- CAPTURE SOURCE GROUP ---------------- \n\n Value entered exists in table")
            self.error_dialog.show()
            return

        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT capture_source_group_id FROM buildings_common.capture_source_group;"
            result = db._execute(sql)
            attributes = result.fetchall()
            length = len(attributes)
            if length == 0:
                id = 1
            else:
                id = attributes[length - 1][0] + 1  # id for new capture source group
            # enter new capture source group
            sql = "INSERT INTO buildings_common.capture_source_group(capture_source_group_id, value, description)VALUES(%s, %s, %s);"
            db.execute(sql, data=(id, capture_source_group, description))
            self.le_new_entry.clear()
            self.le_description.clear()
