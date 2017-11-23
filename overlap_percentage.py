## Relevant Imports
import processing
from PyQt4.QtCore import *

  #################################################################
# Adding Area Field for Existing Potential Matches
provider = PM_existing.dataProvider()

areas = [ feat.geometry().area() 
          for feat in PM_existing.getFeatures() ]
          
field = QgsField("area_poly", QVariant.Double)
provider.addAttributes([field])
PM_existing.updateFields()

idx = PM_existing.fieldNameIndex('area_poly')

for area in areas:
    new_values = {idx : float(area)}
    provider.changeAttributeValues({areas.index(area):new_values})
    
  ##################################################################  
# Adding Area Field for Incoming Potential Matches
providerI = PM_incoming.dataProvider()

areasI = [ feat.geometry().area() 
          for feat in PM_incoming.getFeatures() ]
          
fieldI = QgsField("area_poly", QVariant.Double)
providerI.addAttributes([fieldI])
PM_incoming.updateFields()

idxI = PM_incoming.fieldNameIndex('area_poly')

for areaI in areasI:
    new_valuesI = {idxI : float(areaI)}
    providerI.changeAttributeValues({areasI.index(areaI):new_valuesI})
    
######################################################################
# Calculate Symmetrical Difference

name = 'Symmetric Difference' #name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

processing.runalg('qgis:symmetricaldifference', PM_existing, PM_incoming, path)
SDiff = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 5-", "ogr") # reading shapefile back into qgis 

#######################################################################
# Split Symmetric Difference Layer by field

processing.runalg('qgis:selectbyattribute', SDiff, 'id', 0, "id is not NULL")