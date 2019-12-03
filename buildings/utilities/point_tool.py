from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsPointXY
from qgis.gui import QgsMapToolEmitPoint


class PointTool(QgsMapToolEmitPoint):
    # qgis maptool for drawing circle interactions
    canvas_clicked = pyqtSignal(["QgsPointXY"])
    mouse_moved = pyqtSignal(["QgsPointXY"])

    def __init__(self, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas

    def flags(self):
        from qgis.gui import QgsMapTool

        return QgsMapTool.Transient

    def canvasPressEvent(self, event):
        # Get the click
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.canvas_clicked.emit(QgsPointXY(point[0], point[1]))

    def canvasMoveEvent(self, event):
        # get the point where the mouse is
        x = event.pos().x()
        y = event.pos().y()

        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.mouse_moved.emit(QgsPointXY(point[0], point[1]))
