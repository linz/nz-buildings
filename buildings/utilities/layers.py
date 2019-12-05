from __future__ import absolute_import
from builtins import object
from qgis.core import QgsApplication, QgsVectorLayer, QgsProject, QgsSymbol, QgsSingleSymbolRenderer
from qgis.utils import iface
from . import database as db

URI = db.set_uri()


def check_layer_in_registry(layername):
    """Checks if layer in QgsProject using layer name

    @param layername:       Name of layer
    @type  layername:       String
    @return:                True if layer registry contains named layer
    @rtype:                 boolean
    """

    try:
        QgsProject.instance().mapLayersByName(layername)
        return True
    except IndexError:
        return False


def style_layer(layer, attr_dict):
    """
    Style input layer with attributes from dictionary

    @param layer:          Layer to style
    @type  layer:          qgis.core.QgsVectorLayer
    @param attr_dict:       Dictionary of style attributes
    @type  attr_dict:       dict
    """
    registry = QgsApplication.symbolLayerRegistry()
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    symbol.deleteSymbolLayer(0)
    if layer.geometryType() == 2:
        for key, attr in attr_dict.items():
            lineMeta = registry.symbolLayerMetadata("SimpleLine")
            # Line layer
            lineLayer = lineMeta.createSymbolLayer(
                {"color": attr[0], "width": attr[1], "penstyle": attr[2], "use_custom_dash": "1", "customdash": attr[3]}
            )
            symbol.appendSymbolLayer(lineLayer)
    else:
        for key, attributes in attr_dict.items():
            if key == 1:
                for attr in attributes:
                    create_line_layer(registry, symbol, attr[0], attr[1])  # color  # width
            else:
                for attr in attributes:
                    create_marker_layer(
                        registry,
                        symbol,
                        attr[0],  # markertype
                        attr[1],  # colour
                        attr[2],  # outlinecolour
                        attr[3],  # size
                        attr[4],  # frequency
                        attr[5],
                    )
    # Replace the renderer of the current layer
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def create_line_layer(registry, symbol, color, width):
    """Set up line layer style

    @param registry:     Registry for layer
    @type  registry:     qgis.core.QgsProject
    @param symbol:       Symbol for styling
    @type  symbol:       qgis.core.QgsSymbol
    @param color:    Colour of line (RGB values in a string)
    @type  color:    string
    @param width:        Width of line
    @type  width:        string
    """
    line_meta = registry.symbolLayerMetadata("SimpleLine")
    line_layer = line_meta.createSymbolLayer({"width": width, "color": color, "penstyle": "solid"})
    symbol.appendSymbolLayer(line_layer)


def create_marker_layer(registry, symbol, marker, color, outline_color, size, ptype, owidth):
    """Set up marker layer style

    @param registry:     Registry for layer
    @type  registry:     qgis.core.QgsProject
    @param symbol:       Symbol for styling
    @type  symbol:       qgis.core.QgsSymbol
    @param marker:       Type of marker
    @type  marker:       string
    @param color:        Colour of marker (RGB values in a string)
    @type  color:        string
    @param outline_color: Border colour of marker (RGB values in a string)
    @type  outline_color: string
    @param size:         Size of marker
    @type  size:         string
    @param ptype:        Placement Type
    @type  ptype:        string
    @param owidth:       Width of outline border
    @type  owidth:       string
    """
    marker_meta = registry.symbolLayerMetadata("MarkerLine")
    marker_layer = marker_meta.createSymbolLayer({"color": color, "interval": "3", "placement": ptype})
    # Replace the default layer with our own SimpleMarker
    marker_layer.subSymbol().deleteSymbolLayer(0)
    amarker = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer(
        {"name": marker, "color": color, "color_border": outline_color, "size": size, "outline_width": owidth}
    )
    marker_layer.subSymbol().appendSymbolLayer(amarker)
    symbol.appendSymbolLayer(marker_layer)


class LayerRegistry(object):
    """
    Manages Layers for building tool
    """

    def __init__(self):
        self.uri = URI
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup("Building Tool Layers")
        if group is not None:
            self.group = group
        else:
            self.group = self.set_group()
        self.base_layers = {}
        self._layers = {}

    @property
    def layers(self):
        return self._layers

    def clear_layer_selection(self):
        """Clear selection on the list of layers"""
        for layer in list(self.layers.values()):
            layer.removeSelection()

        iface.mapCanvas().refresh()

    def remove_all_layers(self):
        """Remove all layers except base_layers"""
        for layer in list(self.layers.values()):
            if layer not in list(self.base_layers.values()):
                QgsProject.instance().removeMapLayer(layer.id())
                self.update_layers()

    def remove_layer(self, layer):
        """
        Rollback and remove specified layer

        @param layer:     Layer instance
        @type  layer:     qgis.core.QgsVectorLayer
        """
        if layer in list(self.layers.values()):
            layer.rollBack()
            QgsProject.instance().removeMapLayer(layer.id())
            self.update_layers()

    def set_group(self):
        """ Sets up the QgsLayerTreeGroup for Layer Registry

        @return:    Root Group
        @rtype:     qgis.core.QgsLayerTreeGroup
        """
        root = QgsProject.instance().layerTreeRoot()
        if root.findGroup("Building Tool Layers"):
            return root.findGroup("building Tool Layers")
        else:
            root.insertGroup(0, "Building Tool Layers")
            return root.findGroup("Building Tool Layers")

    def add_postgres_layer(self, name, db_name, geomcolumn, schema, key, sql):
        self.group = QgsProject.instance().layerTreeRoot().findGroup("Building Tool Layers")
        try:
            layer = QgsProject.instance().mapLayersByName(name)[-1]
        except IndexError:
            URI.setDataSource(schema, db_name, geomcolumn, sql, key)
            layer = QgsVectorLayer(URI.uri(), name, "postgres")
            QgsProject.instance().addMapLayer(layer, False)
            self.group.insertLayer(0, layer)
        self.update_layers()
        return layer

    def set_up_base_layers(self):
        territorial = self.add_postgres_layer(
            "territorial_authority", "territorial_authority", "shape", "buildings_reference", "", ""
        )
        style_layer(territorial, {1: ["204,204,102", "0.3", "dash", "5;2"]})
        temp_bool = False
        for layers in self.group.findLayers():
            if layers.name() == territorial.name():
                temp_bool = True
        if not temp_bool:
            self.group.addLayer(territorial)
            self.base_layers = {"territorial": territorial}

    def update_layers(self):
        """Updates self._layers if layer is removed or added to self.group"""
        root = QgsProject.instance().layerTreeRoot()
        if root.findGroup("Building Tool Layers") is not None:
            self._layers = {}
            if self.group is not None:
                for layer in self.group.findLayers():
                    self._layers[layer.layer().name()] = layer.layer()
        else:
            self._layers = {}
