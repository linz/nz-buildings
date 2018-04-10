# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame
from PyQt4.QtCore import pyqtSignal

import qgis

import processing

from buildings.gui.error_dialog import ErrorDialog
from buildings.utilities import database as db

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "alter_building_relationship.ui"))

db.connect()


class AlterRelationships(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(AlterRelationships, self).__init__(parent)
        self.setupUi(self)

        # signals and slots

        # signal for selection and insert into list
        self.btn_unlink_selected.clicked.connect(self.unlink_selected_clicked)
        self.btn_unlink_all.clicked.connect(self.unlink_all_clicked)
        self.btn_link.clicked.connect(self.link_clicked)
        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_cancel.clicked.connect(self.cancel_clicked)

    def unlink_selected_clicked(self):
        selected_existing_id = (1, 2)
        selected_bulk_load_id = (1, 2)
        sql_delete = '''DELETE FROM buildings_bulk_load.related
                        WHERE building_outline_id IN %s AND bulk_load_outline_id IN %s;
                        '''
        db._execute(sql_delete, (selected_existing_id, selected_bulk_load_id))

    def unlink_all_clicked(self):
        all_existing_id = (1, 2)
        all_bulk_load_id = (1, 2)
        sql_delete = '''DELETE FROM .related
                        WHERE building_outline_id IN %s AND bulk_load_outline_id IN %s;
                        '''
        db._execute(sql_delete, (all_existing_id, all_bulk_load_id))

    def link_clicked(self):
        existing_id = 1
        bulk_load_id = 1
        # need to insert other field as well
        sql_insert = '''INSERT INTO buildings_bulk_load.matched (bulk_load_outline_id, building_outline_id)
                        VALUES (%s,%s)
                        '''
        sql_delete_added = 'DELETE FROM buildings_bulk_load.added WHERE bulk_load_outline_id = %s;'
        sql_delete_removed = 'DELETE FROM buildings_bulk_load.removed WHERE building_outline_id = %s;'

        db._execute(sql_insert, (existing_id, bulk_load_id))
        db._execute(sql_delete_added, bulk_load_id)
        db._execute(sql_delete_removed, existing_id)

    def save_clicked(self):

