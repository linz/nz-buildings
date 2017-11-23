import processing 

## Finding potential Match in existing buildings
processing.runalg("qgis:selectbylocation",existingLayer,incomingLayer,['intersects'],0,0) # selecting the buildings

# save selection to file
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
name = 'Potential Match ExistingLayer' #name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

processing.runalg('qgis:saveselectedfeatures', existingLayer, path)
PM_existing = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 3-", "ogr") # reading shapefile back into qgis 

##########################
## Finding potential Match in incominging buildings
processing.runalg("qgis:selectbylocation",incomingLayer,existingLayer,['intersects'],0,0) # selecting the buildings

# save selection to file
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
name = 'Potential Match IncomingLayer' #name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

processing.runalg('qgis:saveselectedfeatures', incomingLayer, path)
PM_incoming = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 4-", "ogr") # reading shapefile back into qgis 

