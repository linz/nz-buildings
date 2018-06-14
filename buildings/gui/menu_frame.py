# -*- coding: utf-8 -*-

import os.path

from PyQt4 import uic
from PyQt4.QtGui import QFrame

from buildings.gui.new_entry import NewEntry
from buildings.gui.new_capture_source import NewCaptureSource
from buildings.gui.bulk_load_outlines import BulkLoadOutlines
from buildings.gui.compare_outlines import CompareOutlines
from buildings.gui.bulk_new_outline import BulkNewOutline
from buildings.gui.production_new_outline import ProductionNewOutline
from buildings.gui.alter_building_relationships import AlterRelationships
from buildings.gui.alter_building_relationships import MultiLayerSelection
from buildings.utilities import database as db

import qgis
from qgis.utils import iface

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'menu.ui'))


class MenuFrame(QFrame, FORM_CLASS):

    def __init__(self, layer_registry, parent=None):
        """Constructor."""
        super(MenuFrame, self).__init__(parent)
        self.setupUi(self)
        self.layer_registry = layer_registry
        db.connect()
        self.cmb_add_outline.setCurrentIndex(0)

        # set up signals and slots
        self.btn_new_entry.clicked.connect(self.new_entry_clicked)
        self.btn_add_capture_source.clicked.connect(self.add_capture_source_clicked)
        self.btn_load_outlines.clicked.connect(self.load_outlines_clicked)
        self.btn_compare.clicked.connect(self.compare_outlines_clicked)
        self.cmb_add_outline.currentIndexChanged.connect(self.add_outline)

    def new_entry_clicked(self):
        """
        Called when new entry button is clicked
        """
        db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewEntry(self.layer_registry))

    def add_capture_source_clicked(self):
        """
        Called when add capture source button is clicked
        """
        db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(NewCaptureSource(self.layer_registry))

    def load_outlines_clicked(self):
        """
        Called when bulk load outlines is clicked
        """
        db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(BulkLoadOutlines(self.layer_registry))

    def compare_outlines_clicked(self):
        """
        Called when compare outlines is clicked
        """
        db.close_connection()
        dw = qgis.utils.plugins['roads'].dockwidget
        dw.stk_options.removeWidget(dw.stk_options.currentWidget())
        dw.new_widget(CompareOutlines(self.layer_registry))

    def add_outline(self):
        """
        Called when index of add outline combobox is changed
        """
        db.close_connection()
        text = self.cmb_add_outline.currentText()
        if text == 'Add New Outline to Bulk Load Dataset':
            dw = qgis.utils.plugins['roads'].dockwidget
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())
            dw.new_widget(BulkNewOutline(self.layer_registry))
        if text == 'Add New Outline to Production':
            dw = qgis.utils.plugins['roads'].dockwidget
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())
            dw.new_widget(ProductionNewOutline(self.layer_registry))
        if text == 'Alter Building Relationships':
            dw = qgis.utils.plugins['roads'].dockwidget
            dw.stk_options.removeWidget(dw.stk_options.currentWidget())
            dw.new_widget(AlterRelationships(self.layer_registry))
            canvas = iface.mapCanvas()
            self.tool = MultiLayerSelection(canvas)
            canvas.setMapTool(self.tool)
