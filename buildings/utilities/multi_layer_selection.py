# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QApplication, QCursor, QPixmap
from qgis.core import QgsRectangle, QgsMapLayerRegistry, QgsPoint
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand
from qgis.utils import QGis


class MultiLayerSelection(QgsMapToolEmitPoint):

    multi_selection_changed = pyqtSignal()

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubber_band = QgsRubberBand(self.canvas, QGis.Polygon)
        self.start_point = None
        self.end_point = None
        self.is_emitting_point = False

        self.rubber_band.reset(QGis.Polygon)

        self.cursor = QCursor(QPixmap([
            '16 16 3 1',
            '# c None',
            'a c #000000',
            '. c #ffffff',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            'aaaaaaaaaaaaaaaaa',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########',
            '########a########'
        ]))

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def flags(self):
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
        self.show_rectangle()

        self.rubber_band.reset(QGis.Polygon)
        layer_bulk = QgsMapLayerRegistry.instance().mapLayersByName(
            'bulk_load_outlines')
        layer_existing = QgsMapLayerRegistry.instance().mapLayersByName(
            'existing_subset_extracts')
        layers = [layer for layer in layer_bulk] \
            + [layer for layer in layer_existing]

        if self.rectangle() is not None:
            for layer in layers:
                layer_rect = self.canvas.mapSettings().mapToLayerCoordinates(
                    layer, self.rectangle())
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    layer.select(layer_rect, True)
                else:
                    layer.select(layer_rect, False)
        else:
            w = self.canvas.mapUnitsPerPixel() * 3
            p = self.toMapCoordinates(event.pos())
            rect = QgsRectangle(p.x() - w, p.y() - w, p.x() + w, p.y() + w)
            for layer in layers:
                layer_rect = self.canvas.mapSettings().mapToLayerCoordinates(
                    layer, rect)
                if QApplication.keyboardModifiers() == Qt.ShiftModifier:
                    layer.select(layer_rect, True)
                else:
                    layer.select(layer_rect, False)

        # Signal emits every time canvas release event occurs and selection
        # could potentially have changed.
        self.multi_selection_changed.emit()

    def rectangle(self):
        """Create the rectangle formed via click and drag"""
        if self.start_point is None or self.end_point is None:
            return None
        elif self.start_point.x() == self.end_point.x() or \
                self.start_point.y() == self.end_point.y():
            return None
        return QgsRectangle(self.start_point, self.end_point)

    def show_rectangle(self):
        """
        Handles the click + drag selection rectangle shown on the map canvas.
        """
        if self.start_point.x() == self.end_point.x() or \
                self.start_point.y() == self.end_point.y():
            # Prevent creation of invalid rectangle.
            return
        self.rubber_band.reset(QGis.Polygon)
        point1 = QgsPoint(self.start_point.x(), self.start_point.y())
        point2 = QgsPoint(self.start_point.x(), self.end_point.y())
        point3 = QgsPoint(self.end_point.x(), self.end_point.y())
        point4 = QgsPoint(self.end_point.x(), self.start_point.y())
        self.rubber_band.addPoint(point1, False)
        self.rubber_band.addPoint(point2, False)
        self.rubber_band.addPoint(point3, False)
        self.rubber_band.addPoint(point4, True)  # True = update canvas.
        self.rubber_band.show()

    def setCursor(self, cursor):
        self.cursor = QCursor(cursor)
