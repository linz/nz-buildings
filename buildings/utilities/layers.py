
from qgis.core import (
    QgsVectorLayer, QgsMapLayerRegistry, QgsProject
)
from qgis.utils import iface
import database as db

URI = db.set_uri()


class LayerRegistry(object):
    """
    Manages Layers for building tool
    """

    def __init__(self):
        self.uri = URI
        self.group = self.set_group()
        # self.base_layers = {}
        self.buildings = None
        self._layers = {}

        QgsMapLayerRegistry.instance().layersWillBeRemoved["QStringList"].connect(self.layer_removed)

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
        if root.findGroup("Builing Tool Layers"):
            return root.findGroup("building Tool Layers")
        else:
            root.insertGroup(0, "Building Tool Layers")
            return root.findGroup("Building Tool Layers")

    def add_postgres_layer(self, name, db_name, geomcolumn, schema, key, sql):
            """
            Adds postgres layer to registry and group

            @param name:            Name of Layer (in qgis)
            @type  name:            string
            @param db_name:        Name of table (in db)
            @type  db_name:        string
            @param geomcolumn:      Geometry column
            @type  geomcolumn:      string
            @param schema:          Schema name (db)
            @type  schema:          string
            @param key:             Key column
            @type  key:             string
            @param sql:             Subset String
            @type  sql:             string

            @return layer:     Layer instance
            @rtype  layer:     qgis.core.QgsVectorLayer
            """
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
        localities = self.add_postgres_layer(
            "nz_localities", "nz_locality",
            "shape", "admin_bdys", '', ''
        )
        # style_layer(localities, {1: ['204,204,102', '0.3', 'dash', '5;2']})

        self.group.addLayer(localities)
        self.group.addLayer(self.buildings)

    def update_layers(self):
        """Updates self._layers if layer is removed or added to self.group"""
        self._layers = {}
        if self.group:
            for layer in self.group.findLayers():
                self._layers[layer.layer().name()] = layer.layer()
