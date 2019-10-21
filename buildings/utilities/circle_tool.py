from functools import partial
import math

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY
from qgis.gui import QgsRubberBand
from qgis.utils import iface

from buildings.utilities.point_tool import PointTool


def setup_circle(self):
    """
        called when draw circle button is clicked
    """
    self.points = []
    # set map tool to new point tool
    self.circle_tool = PointTool(iface.mapCanvas())
    iface.mapCanvas().setMapTool(self.circle_tool)
    # create polyline to track drawing on canvas
    self.polyline = QgsRubberBand(iface.mapCanvas(), False)
    self.polyline.setLineStyle(Qt.PenStyle(Qt.DotLine))
    self.polyline.setColor(QColor(255, 0, 0))
    self.polyline.setWidth(1)
    # signals for new map tool
    self.circle_tool.canvas_clicked.connect(partial(draw_circle, self))
    self.circle_tool.mouse_moved.connect(partial(update_line, self))


def draw_circle(self, point):
    """
        called when mapcanvas is clicked
    """
    self.points.append(point)
    self.polyline.addPoint(point, True)
    self.polyline.setToGeometry(QgsGeometry.fromPolylineXY(self.points), None)
    # if two points have been clicked (center and edge)
    if len(self.points) == 2:
        # calculate radius of circle
        radius = math.sqrt((self.points[1][0] - self.points[0][0]) ** 2 + (self.points[1][1] - self.points[0][1]) ** 2)
        # number of vertices of circle
        nodes = (round(math.pi / math.acos((radius - 0.001) / radius))) / 10
        # create point on center location
        point = QgsGeometry.fromPointXY(QgsPointXY(self.points[0]))
        # create buffer of specified distance around point
        buffer = point.buffer(radius, nodes)
        # add feature to bulk_load_outlines (triggering featureAdded)
        if self.__class__.__name__ == "BulkLoadFrame":
            self.feature = QgsFeature(self.bulk_load_layer.fields())
            self.feature.setGeometry(buffer)
            self.bulk_load_layer.addFeature(self.feature)
            self.bulk_load_layer.triggerRepaint()
        elif self.__class__.__name__ == "AlterRelationships":
            self.feature = QgsFeature(self.lyr_bulk_load.fields())
            self.feature.setGeometry(buffer)
            self.lyr_bulk_load.addFeature(self.feature)
            self.lyr_bulk_load.triggerRepaint()
        elif self.__class__.__name__ == "ProductionFrame":
            self.feature = QgsFeature(self.building_layer.fields())
            self.feature.setGeometry(buffer)
            self.building_layer.addFeature(self.feature)
            self.building_layer.triggerRepaint()
        # reset points list
        self.points = []


def update_line(self, point):
    """
        called when mouse moved on canvas
    """
    if len(self.points) == 1:
        # if the center has been clicked have a line follow the mouse movement
        line = [self.points[0], point]
        self.polyline.setToGeometry(QgsGeometry.fromPolylineXY(line), None)
