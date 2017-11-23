import processing

# Finding new buildings
incomingLayer.selectAll()
processing.runalg("qgis:selectbylocation",incomingLayer,existingLayer,['intersects'],0,2) # selecting the buildings

# save selection to file
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
name = 'New Buildings' #name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

processing.runalg('qgis:saveselectedfeatures', incomingLayer, path)
removed = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 2-", "ogr") # reading shapefile back into qgis 