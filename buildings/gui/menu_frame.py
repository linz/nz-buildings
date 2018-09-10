# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

from buildings.gui.bulk_load_frame import BulkLoadFrame
from buildings.gui.new_capture_source import NewCaptureSource
from buildings.gui.new_entry import NewEntry
from buildings.gui.production_frame import ProductionFrame
from buildings.utilities import database as db


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'menu_frame.ui'))


class MenuFrame(QFrame, FORM_CLASS):

    def __init__(self, dockwidget, layer_registry, parent=None):
        """Constructor."""
        super(MenuFrame, self).__init__(parent)
        self.setupUi(self)
        self.dockwidget = dockwidget
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
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadFrame(self.dockwidget, self.layer_registry))

    def production_clicked(self):
        """
        Called when production button is clicked
        """
        self.db.close_connection()
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(ProductionFrame(dw, self.layer_registry))

    def new_entry_clicked(self):
        """
        Called when new entry button is clicked
        """
        self.db.close_connection()
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewEntry(dw, self.layer_registry))

    def new_capture_source_clicked(self):
        """
        Called when new capture source button is clicked
        """
        self.db.close_connection()
        dw = self.dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSource(dw, self.layer_registry))
