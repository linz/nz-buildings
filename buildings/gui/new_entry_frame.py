# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import psycopg2
import qgis
# from roads.gui.error_dialog import ErrorDialog
# from buildings.gui.action_frame import ActionFrame

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_entry.ui"))
conn = psycopg2.connect(database='building_outlines_test')
# create cursor
cur = conn.cursor()


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

    def get_comments(self):
        """
        Get comments from comment box, return default if empty
        """
        return self.le_new_entry.text()
        # TODO if value is nothing fail

    def get_combobox_value(self):
        """
        Get the type from the combo box
        """
        index = self.cmb_new_type_selection.currentIndex()
        return self.cmb_new_type_selection.itemText(index)

    def ok_clicked(self):
        # get value
        self.value = self.get_comments()
        # get type
        self.new_type = self.get_combobox_value()
        # call insert depending on type
        if self.new_type == 'Organisation':
            self.new_organisation(self.value)
        elif self.new_type == 'Lifecycle Stage':
            self.new_lifecycle_stage(self.value)
        elif self.new_type == 'Capture Method':
            self.new_capture_method(self.value)
        elif self.new_type == 'Capture Source Group':
            self.new_capture_source_group(self.value)
        self.ok_task.emit()  # ?? what does this do

    def cancel_clicked(self):
        from buildings.gui.action_frame import ActionFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(ActionFrame)

    def new_organisation(self, organisation):
        # =========================================================
        # New Organisation
        """
            update the organisation table.
            value output = organisation auto generate id
        """
        # check if organisation in buildings.organisation table
        sql = "SELECT * FROM buildings_stage.organisation WHERE buildings_stage.organisation.value = %s;"
        cur.execute(sql, (organisation,))
        ls = cur.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            print "organisation exists in table"
            # self.error_dialog = ErrorDialog()
            # self.error_dialog.fill_report("organisation exists in table")
            # TODO: return dialog box that organisation exists
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT organisation_id FROM buildings_stage.organisation;"
            cur.execute(sql)
            attributes = cur.fetchall()
            length = len(attributes)
            id = attributes[length - 1][0] + 1  # id for new organisation
            # enter new organisation
            sql = "INSERT INTO buildings_stage.organisation(organisation_id, value)VALUES(%s, %s);"
            cur.execute(sql, (id, organisation))
            conn.commit()

    def new_lifecycle_stage(self, lifecycle_stage):
        # New Lifecycle Stage
        """
        update the lifecycle stage table
        value = lifecycle stage auto generate id
        """
        # check if lifecycle stage in buildings.lifecycle_stage table
        sql = "SELECT * FROM buildings.lifecycle_stage WHERE buildings.lifecycle_stage.value = %s;"
        cur.execute(sql, (lifecycle_stage,))
        ls = cur.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            print "lifecycle_stage exists in table"
            # TODO
            # return to tool that lifecycle_stage exists
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT lifecycle_stage_id FROM buildings.lifecycle_stage;"
            cur.execute(sql)
            attributes = cur.fetchall()
            length = len(attributes)
            id = attributes[length - 1][0] + 1  # id for new lifecycle stage
            # enter new lifecycle stage
            sql = "INSERT INTO buildings.lifecycle_stage(lifecycle_stage_id, value)VALUES(%s, %s);"
            cur.execute(sql, (id, lifecycle_stage))
            conn.commit()

    def new_capture_method(self, capture_method):
        # New Capture Method
        """
        update the capture method table
        value = capture method autogenerate id
        """

        # check if capture method in buildings.capture_method table
        sql = "SELECT * FROM buildings.capture_method WHERE buildings.capture_method.value = %s;"
        cur.execute(sql, (capture_method,))
        ls = cur.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            print "capture method value exists in table"
            # TODO
            # return to tool that capture method exists
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT capture_method_id FROM buildings.capture_method;"
            cur.execute(sql)
            attributes = cur.fetchall()
            length = len(attributes)
            id = attributes[length - 1][0] + 1  # id for new capture method
            # enter new capture method
            sql = "INSERT INTO buildings.capture_method(capture_method_id, value)VALUES(%s, %s);"
            cur.execute(sql, (id, capture_method))
            conn.commit()

    def new_capture_source_group(self, capture_source_group):
        # New Capture Source Group
        """
        update the capture source group table
            value = capture source group autogenerate id
        """

        # Check if capture source group in buildings.capture_source_group table
        sql = "SELECT * FROM buildings.capture_source_group WHERE buildings.capture_source_group.value = %s;"
        cur.execute(sql, (capture_source_group,))
        ls = cur.fetchall()
        # if it is in the table return dialog box and exit
        if len(ls) > 0:
            print "capture source group value exists in table"
            # TODO
            # return to tool that capture_source_group exists
            return
        # if it isn't in the table add to table
        elif len(ls) == 0:
            # find the last id value in table
            sql = "SELECT capture_source_group_id FROM buildings.capture_source_group;"
            cur.execute(sql)
            attributes = cur.fetchall()
            length = len(attributes)
            id = attributes[length - 1][0] + 1  # id for new organisation
            # enter new capture source group
            sql = "INSERT INTO buildings.capture_source_group(capture_source_group_id, value)VALUES(%s, %s);"
            cur.execute(sql, (id, capture_source_group))
