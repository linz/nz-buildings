# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QCursor, QPixmap
from qgis.core import QgsRectangle, QgsProject, QgsPointXY, QgsWkbTypes, QgsVectorLayer
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from qgis.utils import Qgis


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# The QgsVectorLayer.SelectBehavior enum was introduced in QGIS 3.22. Prior to
# this the second arg to QgsVectorLayer.selectByRect() took an int, but this
# now raises a type error. In earlier versions without the enum, trying to
# access it will raise an AttributeError, which we can catch to set fallback
# values for these older versions
try:
    ADD_TO_SELECTION = QgsVectorLayer.SelectBehavior.AddToSelection
    SET_SELECTION = QgsVectorLayer.SelectBehavior.SetSelection
except AttributeError:
    ADD_TO_SELECTION = 1
    SET_SELECTION = 0


class MultiLayerSelection(QgsMapToolEmitPoint):

    multi_selection_changed = pyqtSignal()

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.start_point = None
        self.end_point = None
        self.is_emitting_point = False

        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)

        self.cursor = QCursor(QPixmap(os.path.join(__location__, "..", "icons", "cursor.png")))

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def flags(self):
        from qgis.gui import QgsMapTool

        return QgsMapTool.Transient

    def canvasPressEvent(self, event):
        self.start_point = self.toMapCoordinates(event.pos())
        self.end_point = self.start_point
        self.is_emitting_point = True
        self.show_rectangle()

    def canvasMoveEvent(self, event):
        """Overridden mouse move event from QgsMapTool"""
        if not self.is_emitting_point:
            # Don't do anything unless press event has occurred.
            return
        self.end_point = self.toMapCoordinates(event.pos())
        # Click + drag rectangle updated while cursor is moving.
        self.show_rectangle()

    def canvasReleaseEvent(self, event):
        """Overridden mouse release event from QgsMapTool"""
        self.is_emitting_point = False
        self.end_point = self.toMapCoordinates(event.pos())

        layer_bulk = QgsProject.instance().mapLayersByName("bulk_load_outlines")
        layer_existing = QgsProject.instance().mapLayersByName("existing_subset_extracts")
        layers = [layer for layer in layer_bulk] + [layer for layer in layer_existing]

        if self.rectangle() is not None:
            for layer in layers:
                layer_rect = self.canvas.mapSettings().mapToLayerCoordinates(layer, self.rectangle())
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    layer.selectByRect(layer_rect, ADD_TO_SELECTION)
                else:
                    layer.selectByRect(layer_rect, SET_SELECTION)
        else:
            w = self.canvas.mapUnitsPerPixel() * 3
            p = self.toMapCoordinates(event.pos())
            rect = QgsRectangle(p.x() - w, p.y() - w, p.x() + w, p.y() + w)
            for layer in layers:
                layer_rect = self.canvas.mapSettings().mapToLayerCoordinates(layer, rect)
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    layer.selectByRect(layer_rect, ADD_TO_SELECTION)
                else:
                    layer.selectByRect(layer_rect, SET_SELECTION)
        self.rubber_band.hide()
        # Signal emits every time canvas release event occurs and selection
        # could potentially have changed.
        self.multi_selection_changed.emit()

    def rectangle(self):
        """Create the rectangle formed via click and drag"""
        if self.start_point is None or self.end_point is None:
            return None
        elif self.start_point.x() == self.end_point.x() or self.start_point.y() == self.end_point.y():
            return None
        return QgsRectangle(self.start_point, self.end_point)

    def show_rectangle(self):
        """
        Handles the click + drag selection rectangle shown on the map canvas.
        """
        if self.start_point.x() == self.end_point.x() or self.start_point.y() == self.end_point.y():
            # Prevent creation of invalid rectangle.
            return
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        point1 = QgsPointXY(self.start_point.x(), self.start_point.y())
        point2 = QgsPointXY(self.start_point.x(), self.end_point.y())
        point3 = QgsPointXY(self.end_point.x(), self.end_point.y())
        point4 = QgsPointXY(self.end_point.x(), self.start_point.y())
        self.rubber_band.addPoint(point1, False)
        self.rubber_band.addPoint(point2, False)
        self.rubber_band.addPoint(point3, False)
        self.rubber_band.addPoint(point4, True)  # True = update canvas.
        self.rubber_band.show()

    def setCursor(self, cursor):
        self.cursor = QCursor(cursor)
