# -*- coding: utf-8 -*-
from qgis.utils import QGis

def check_data_format(lyr_name):
    
    def check_file_type(lyr):  
        """Check if the layer's storage type is ESRI Shapefile"""
        if lyr.dataProvider().storageType() != 'ESRI Shapefile':
            print("File Type is not ESRI Shapefile")
        else:
            print("File Type is ESRI Shapefile")

    def check_lyr_geom(lyr):
        """Check if the layer's wkb type is line string"""
        if lyr.wkbType() != QGis.WKBLineString:
            print("Layer Geometry is not WKB Linestring")
        else:
            print("Layer Geometry is WKB Linestring")

    def check_feat_geom(lyr):
        """Check if all features are Singlepart"""
        has_multi = False
        feats = []
        for feat in lyr.getFeatures():
            if feat.geometry().isMultipart():
                has_multi = True
                feats.append(feat)
        if has_multi:
            print("Layer contains %i multipart feature(s)" %len(feats))
        else:
            print("Layer do not contain multipart feature(s)")

    
    def check_lyr_crs(lyr):
        """Check if the layer has a correct crs"""
        if lyr.crs().authid() != "EPSG:2193":
            print("Layer crs is not EPSG:2193")
        else:
            print("Layer crs is EPSG:2193")

    '''lyr = iface.activeLayer()'''
    layers = iface.legendInterface().layers()
    
    for layer in layers:
        if layer.name() == lyr_name:
            check_file_type(layer)
            check_lyr_geom(layer)
            check_feat_geom(layer)
            check_lyr_crs(layer)






