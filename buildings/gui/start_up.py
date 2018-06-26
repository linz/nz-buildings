# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

from buildings.gui.bulk_load_frame import BulkLoadFrame
from buildings.gui.new_entry import NewEntry
from buildings.gui.new_capture_source import NewCaptureSource
from buildings.utilities import database as db

import qgis

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'start_up.ui'))


class StartUpFrame(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(StartUpFrame, self).__init__(parent)
        self.setupUi(self)
        self.layer_registry = layer_registry
        self.db = db
        self.db.connect()

        # set up signals and slots
        self.btn_bulk_load.clicked.connect(self.bulk_load_clicked)
        self.btn_production.clicked.connect(self.production_clicked)
        self.btn_new_entry.clicked.connect(self.new_entry_clicked)
        self.btn_new_capture_source.clicked.connect(self.new_capture_source_clicked)

    def bulk_load_clicked(self):
        """
        Called when bulk loaded button is clicked
        """
        self.db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadFrame(self.layer_registry))

    def production_clicked(self):
        """
        Called when add capture source button is clicked
        """
        pass

    def new_entry_clicked(self):
        """
        Called when new entry button is clicked
        """
        self.db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewEntry(self.layer_registry))

    def new_capture_source_clicked(self):
        """
        Called when new capture source button is clicked
        """
        self.db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSource(self.layer_registry))
