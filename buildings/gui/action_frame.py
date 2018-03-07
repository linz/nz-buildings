# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QFrame
from buildings.gui.new_entry_frame import NewEntry
from buildings.gui.new_capture_source_frame import NewCaptureSource
from buildings.gui.new_supplied_outlines import NewSuppliedOutlines
from buildings.gui.insert_buildings import InsertBuildings
import qgis
# import psycopg2


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "action.ui"))


class ActionFrame(QFrame, FORM_CLASS):

    new_entry = pyqtSignal()
    add_capture_source = pyqtSignal()
    new_supplied_outlines = pyqtSignal()
    insert_buildings = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        # self.dw = qgis.utils.plugins['roads'].dockwidget
        super(ActionFrame, self).__init__(parent)
        self.setupUi(self)

        # set up signals and slots
        self.btn_new_entry.clicked.connect(self.new_entry_clicked)
        self.btn_add_capture_source.clicked.connect(self.add_capture_source_clicked)
        self.btn_new_supplied_outlines.clicked.connect(self.new_supplied_outlines_clicked)
        self.btn_insert_builds.clicked.connect(self.insert_buildings_clicked)

    def new_entry_clicked(self):
        # open new entry frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewEntry)

    def add_capture_source_clicked(self):
        # open add capture source frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSource)

    def new_supplied_outlines_clicked(self):
        # open new supplied outlines frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewSuppliedOutlines)

    def insert_buildings_clicked(self):
        # open insert buildings frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(InsertBuildings)
