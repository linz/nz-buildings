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
        self.mcmb_imagery_layer.currentIndexChanged.connect(self.populate_imagery_combobox)

    def populate_combobox(self):
        sql = "SELECT value FROM buildings_stage.organisation"
        cur.execute(sql)
        ls = cur.fetchall()
        for item in ls:
            self.cmb_organisation.addItem(item[0])

    def populate_imagery_combobox(self):
        index = self.mcmb_imagery_layer.currentIndex()
        if self.mcmb_imagery_layer.layer(index).name() == "imagery_surveys":
            for item in self.mcmb_imagery_layer.currentLayer().getFeatures():
                self.cmb_imagery.addItem(item[2])
        else:
            self.cmb_imagery.clear()

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

    def get_imagery_combobox_value(self):
        index = self.cmb_imagery.currentIndex()
        return self.cmb_imagery.itemText(index)

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
            # TODO: way to check not reading in duplicates?
            # find existing overlap
            tile = str(self.get_imagery_combobox_value())
            print "imagery = '{0}'".format(tile)
            # find imagery
            self.mcmb_imagery_layer.currentLayer().selectByExpression('imagery = %s'.format(tile), 0)
            # TODO:
            # intersect with building_outlines
            # if intersection returns no results
                # don't run feature overlap
                # all will be new?
                # check random subset
                # insert into building_outlines and buildings
            # else
                # run feature overlap code
                # sql = "SELECT (buildings_stage.compare_building_outlines(2));"
                # cur.execute(sql)
                # user checked data to buildings and building_outlines

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
            sql = "INSERT INTO buildings_stage.supplied_outlines(supplied_dataset_id, shape)" + " VALUES(%s, %s);"
            cur.execute(sql, (dataset_id, geom))
        conn.commit()
        self.le_supplied_data_description.clear()
