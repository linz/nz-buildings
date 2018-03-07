# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import psycopg2
import qgis

conn = psycopg2.connect(database='building_outlines_test')
# create cursor
cur = conn.cursor()

# from buildings.core.lookup import (
#     CAPTURE_METHODS, CAPTURE_SOURCES, LIFECYCLE_STAGES, USES,
#     SUBURB_LOCALITIES, TOWN_CITIES, TERRITORIAL_AUTHORITIES
# )


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_capture_source.ui"))


class NewCaptureSource(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()
    value = ''
    external_source = ''

    def __init__(self, parent=None):
        """Constructor."""
        super(NewCaptureSource, self).__init__(parent)
        self.setupUi(self)
        self.populate_combobox()

        # set up signals and slots
        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_combobox(self):
        sql = "SELECT value FROM buildings.capture_source_group"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_capture_source_group.addItem(item[0])

    def get_comments(self):
        # Get comments from comment box, return default if empty
        return self.le_external_source_id.text()
        # TODO if value is nothing fail

    def get_combobox_value(self):
        # Get the type from the combo box
        index = self.cmb_capture_source_group.currentIndex()
        return self.cmb_capture_source_group.itemText(index)

    def ok_clicked(self):
        # get value
        self.external_source = self.get_comments()
        # get type
        self.value = self.get_combobox_value()
        # call insert
        self.insert_capture_source(self.value, self.external_source)
        self.ok_task.emit()  # ?? what does this do

    def cancel_clicked(self):
        from buildings.gui.action_frame import ActionFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(ActionFrame)

    def insert_capture_source(self, value, external_source):
        # New Capture Source
        """
            add values to the capture_source table.
            capture_source_id = autogenerated
        """
        # find capture source group id based on capture source group value
        sql = "SELECT capture_source_group_id FROM buildings.capture_source_group WHERE buildings.capture_source_group.value = %s;"
        cur.execute(sql, (value,))
        capture_source_group_id = cur.fetchall()[0][0]

        # check if capture source exists in table
        sql = "SELECT * FROM buildings.capture_source WHERE buildings.capture_source.external_source_id = %s OR buildings.capture_source.capture_source_group_id = %s;"
        cur.execute(sql, (external_source, capture_source_group_id))
        ls = cur.fetchall()
        if len(ls) > 0:
            to_add = True
            for item in ls:
                # if capture source with same CSG and ES exists
                if item[1] == capture_source_group_id:
                    if item[2] == external_source:
                        print "capture source exists in table"
                        to_add = False
                        # TODO: send update message to user that external source exists
            # if no entry with external source and capture source group add to table
            if to_add:
                sql = "SELECT capture_source_id FROM buildings.capture_source;"
                cur.execute(sql)
                length = len(cur.fetchall())
                id = length + 1
                sql = "INSERT INTO buildings.capture_source(capture_source_id, capture_source_group_id, external_source_id)VALUES(%s, %s, %s)"
                cur.execute(sql, (id, capture_source_group_id, external_source))

        # if sql querry returns nothing add to table
        elif len(ls) == 0:
            sql = "SELECT capture_source_id FROM buildings.capture_source;"
            cur.execute(sql)
            length = len(cur.fetchall())
            id = length + 1
            sql = "INSERT INTO buildings.capture_source(capture_source_id, capture_source_group_id, external_source_id)VALUES(%s, %s, %s)"
            cur.execute(sql, (id, capture_source_group_id, external_source))

        conn.commit()
