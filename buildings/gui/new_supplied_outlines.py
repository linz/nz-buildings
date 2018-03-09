# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal
import psycopg2
import qgis
from buildings.gui.error_dialog import ErrorDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "new_supplied_outlines.ui"))

# TODO: fix database connection process
conn = psycopg2.connect(database='building_outlines_test')
# create cursor
cur = conn.cursor()


class NewSuppliedOutlines(QFrame, FORM_CLASS):

    ok_task = pyqtSignal()
    cancelling_task = pyqtSignal()
    value = ''
    organistion = ''
    dataset_id = None
    layer = None

    def __init__(self, parent=None):
        """Constructor."""
        super(NewSuppliedOutlines, self).__init__(parent)
        self.setupUi(self)
        self.populate_combobox()

        self.btn_ok.clicked.connect(self.ok_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def populate_combobox(self):
        sql = "SELECT value FROM buildings_stage.organisation"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_organisation.addItem(item[0])

    def get_comments(self):
        # Get comments from comment box, fail if empty
        if self.le_supplied_data_description.text() == '':
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- EMPTY VALUE FIELD -------------------- \n\n Null values not allowed")
            self.error_dialog.show()
            return
        if len(self.le_supplied_data_description.text()) >= 40:
            self.error_dialog = ErrorDialog()
            self.error_dialog.fill_report("\n -------------------- VALUE TOO LONG -------------------- \n\n Enter less than 250 characters")
            self.error_dialog.show()
            return
        return self.le_supplied_data_description.text()
        # TODO if value is nothing fail

    def get_combobox_value(self):
        # Get the type from the combo box
        index = self.cmb_organisation.currentIndex()
        return self.cmb_organisation.itemText(index)

    def get_layer(self):
        return self.ml_supplied_outlines_layer.currentLayer()

    def ok_clicked(self):
        # get value
        self.value = self.get_comments()
        # get type
        self.organisation = self.get_combobox_value()
        # get layer
        self.layer = self.get_layer()
        # run sql
        if self.value is not None:
            self.insert_supplied_dataset(self.organisation, self.value)
            self.insert_supplied_outlines(self.dataset_id, self.layer)

        self.ok_task.emit()  # ?? what does this do

    def cancel_clicked(self):
        from buildings.gui.menu_frame import MenuFrame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(MenuFrame)

    def insert_supplied_dataset(self, organisation, description):
        # find organisation id value from buildings.organisation table
        sql = "SELECT organisation_id FROM buildings_stage.organisation WHERE buildings_stage.organisation.value = %s;"
        cur.execute(sql, (organisation,))
        supplier_id = cur.fetchall()[0][0]

        # generate supplied_outline_id
        sql = "SELECT supplied_dataset_id FROM buildings_stage.supplied_datasets;"
        cur.execute(sql)
        attributes = cur.fetchall()
        length = len(attributes)
        if length == 0:
            self.dataset_id = 1
        else:
            self.dataset_id = attributes[length - 1][0] + 1

        # insert new supplied dataset info into buildings_stage.supplied_datasets
        sql = "INSERT INTO buildings_stage.supplied_datasets(supplied_dataset_id, description, supplier_id) VALUES(%s, %s, %s)"
        cur.execute(sql, (self.dataset_id, description, supplier_id))
        conn.commit()

    def insert_supplied_outlines(self, dataset_id, layer):
        # iterate through outlines in map layer
        for outline in layer.getFeatures():
            attrs = outline.attributes()
            wkt = outline.geometry().exportToWkt()
            # convert to postgis shape and ensure outline geometry is a multipolygon
            sql = "SELECT ST_AsText(ST_Multi(ST_GeometryFromText(%s)));"
            cur.execute(sql, (wkt, ))
            geom = cur.fetchall()[0][0]
            # ensure outline SRID is 2193
            sql = "SELECT ST_SetSRID(ST_GeometryFromText(%s), 2193)"
            cur.execute(sql, (geom, ))
            geom = cur.fetchall()[0][0]
            # insert outline into buildings_stage.supplied_outline
            sql = "INSERT INTO buildings_stage.supplied_outlines(supplied_outline_id, supplied_dataset_id, shape)" + " VALUES(%s, %s, %s);"
            cur.execute(sql, (int(attrs[0]), dataset_id, geom))
        conn.commit()
        le_supplied_data_description.clear()
