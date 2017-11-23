import processing 

## Finding removed buildings
existingLayer.selectAll()
processing.runalg("qgis:selectbylocation",existingLayer,incomingLayer,['intersects'],0,2) # selecting the buildings

# save selection to file
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
name = 'Removed Buildings' #name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

processing.runalg('qgis:saveselectedfeatures', existingLayer, path)
removed = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 1-", "ogr") # reading shapefile back into qgis 


