# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QFrame
from buildings.gui.new_entry import NewEntry
from buildings.gui.new_capture_source import NewCaptureSource
from buildings.gui.bulk_load_outlines import BulkLoadOutlines
from buildings.gui.new_outline import NewOutline
from buildings.utilities import database as db

import qgis

db.connect()

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "menu.ui"))


class MenuFrame(QFrame, FORM_CLASS):

    new_entry = pyqtSignal()
    add_capture_source = pyqtSignal()
    new_supplied_outlines = pyqtSignal()
    insert_buildings = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(MenuFrame, self).__init__(parent)
        self.setupUi(self)

        # set up signals and slots
        self.btn_new_entry.clicked.connect(self.new_entry_clicked)
        self.btn_add_capture_source.clicked.connect(self.add_capture_source_clicked)
        self.btn_load_outlines.clicked.connect(self.load_outlines_clicked)
        self.btn_new_outline.clicked.connect(self.new_outline_clicked)

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

    def load_outlines_clicked(self):
        # open new supplied outlines frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadOutlines)

    def new_outline_clicked(self):
        # open new outlines frame
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewOutline)
