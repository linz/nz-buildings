
from qgis.core import (
    QgsVectorLayer, QgsMapLayerRegistry, QgsProject,
    QgsSymbolLayerV2Registry, QgsSymbolV2, QgsSingleSymbolRendererV2
)
from qgis.utils import iface
import database as db

URI = db.set_uri()


def check_layer_in_registry(layername):
    """Checks if layer in QgsMapLayerRegistry using layer name

    @param layername:       Name of layer
    @type  layername:       String
    @return:                True if layer registry contains named layer
    @rtype:                 boolean
    """

    try:
        QgsMapLayerRegistry.instance().mapLayersByName(layername)
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
    registry = QgsSymbolLayerV2Registry.instance()
    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
    symbol.deleteSymbolLayer(0)
    if layer.geometryType() == 2:
        for key, attr in attr_dict.iteritems():
            lineMeta = registry.symbolLayerMetadata("SimpleLine")
            # Line layer
            lineLayer = lineMeta.createSymbolLayer({
                'color': attr[0],
                'width': attr[1],
                'penstyle': attr[2],
                'use_custom_dash': '1',
                'customdash': attr[3]})
            symbol.appendSymbolLayer(lineLayer)
    else:
        for key, attributes in attr_dict.iteritems():
            if key == 1:
                for attr in attributes:
                    create_line_layer(
                        registry, symbol,
                        attr[0],  # color
                        attr[1]  # width
                    )
            else:
                for attr in attributes:
                    create_marker_layer(
                        registry, symbol,
                        attr[0],  # markertype
                        attr[1],  # colour
                        attr[2],  # outlinecolour
                        attr[3],  # size
                        attr[4],  # frequency
                        attr[5])
    # Replace the renderer of the current layer
    renderer = QgsSingleSymbolRendererV2(symbol)
    layer.setRendererV2(renderer)
    layer.triggerRepaint()


def create_line_layer(registry, symbol, color, width):
    """Set up line layer style

    @param registry:     Registry for layer
    @type  registry:     qgis.core.QgsMapLayerRegistry
    @param symbol:       Symbol for styling
    @type  symbol:       qgis.core.QgsSymbolV2
    @param color:    Colour of line (RGB values in a string)
    @type  color:    string
    @param width:        Width of line
    @type  width:        string
    """
    line_meta = registry.symbolLayerMetadata("SimpleLine")
    line_layer = line_meta.createSymbolLayer(
        {'width': width, 'color': color, 'penstyle': 'solid'}
    )
    symbol.appendSymbolLayer(line_layer)


def create_marker_layer(
        registry, symbol, marker, color,
        outline_color, size, ptype, owidth):
    """Set up marker layer style

    @param registry:     Registry for layer
    @type  registry:     qgis.core.QgsMapLayerRegistry
    @param symbol:       Symbol for styling
    @type  symbol:       qgis.core.QgsSymbolV2
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
    marker_layer = marker_meta.createSymbolLayer({
        'color': color, 'interval': '3', 'placement': ptype})
    # Replace the default layer with our own SimpleMarker
    marker_layer.subSymbol().deleteSymbolLayer(0)
    amarker = registry.symbolLayerMetadata("SimpleMarker").createSymbolLayer(
        {'name': marker, 'color': color,
         'color_border': outline_color,
         'size': size, 'outline_width': owidth})
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
        self.buildings = None
        self._layers = {}

        QgsMapLayerRegistry.instance().layersWillBeRemoved["QStringList"].connect(self.layer_removed)

    @property
    def layers(self):
        return self._layers

    def clear_layer_selection(self):
        """Clear selection on the list of layers"""
        for layer in self.layers.values():
            layer.removeSelection()

        iface.mapCanvas().refresh()

    def disconnect_layer_removed(self):
        """
        Disconnects the signal when a layer is removed which
        is used to update self._layers
        """
        QgsMapLayerRegistry.instance().layersWillBeRemoved["QStringList"].disconnect(
            self.layer_removed
        )

    def layer_removed(self, layers_removed):
        """Signal when layer is removed from registry"""
        for layer_id in layers_removed:
            if self.buildings:
                if layer_id == self.buildings.id():
                    self.buildings = None
                else:
                    self.update_layers()
            else:
                self.update_layers()

    def remove_all_layers(self):
        """Remove all layers except base_layers"""
        for layer in self.layers.values():
            if layer not in self.base_layers.values():
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def remove_layer(self, layer):
        """
        Rollback and remove specified layer

        @param layer:     Layer instance
        @type  layer:     qgis.core.QgsVectorLayer
        """

        if layer in self.layers.values():
            layer.rollBack()
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
            if layer == self.buildings:
                self.buildings = None

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
        try:
            layer = QgsMapLayerRegistry.instance().mapLayersByName(name)[-1]
        except IndexError:
            URI.setDataSource(schema, db_name, geomcolumn, sql, key)
            layer = QgsVectorLayer(URI.uri(), name, "postgres", False)
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            self.group.insertLayer(0, layer)
        self.update_layers()
        return layer

    def set_up_base_layers(self):
        territorial = self.add_postgres_layer(
            "territorial_authority", "territorial_authority",
            "shape", "buildings_admin_bdys", '', ''
        )
        style_layer(territorial, {1: ['204,204,102', '0.3', 'dash', '5;2']})
        temp_bool = False
        for layers in self.group.findLayers():
            if layers.name() == territorial.name():
                temp_bool = True
        if not temp_bool:
            self.group.addLayer(territorial)
            self.base_layers = {"territorial": territorial}

    def update_layers(self):
        """Updates self._layers if layer is removed or added to self.group"""
        self._layers = {}
        if self.group is not None:
            for layer in self.group.findLayers():
                self._layers[layer.layer().name()] = layer.layer()
