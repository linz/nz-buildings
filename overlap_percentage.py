## Relevant Imports
import processing
from PyQt4.QtCore import *

######################################################################
# Calculate Symmetrical Difference

#name = 'Symmetric Difference' #name of shapefile
#path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp' # setting up save location

#processing.runalg('qgis:symmetricaldifference', potential_match_existing, potential_match_incoming, path)
#SDiff = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 5-", "ogr") # reading shapefile back into qgis 

#######################################################################
# Split Symmetric Difference Layer by field

#processing.runalg('qgis:selectbyattribute', SDiff, 'id', 0, "id is not NULL")
#path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/"
#name = "sdiff_existing"
#processing.runalg('qgis:saveselectedfeatures', SDiff, path+name)
#SDiff_existing = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 6-", "ogr")

    # Adding Area Field for Existing Potential Matches
#provider = SDiff_existing.dataProvider()
#areas = []
#for feat in SDiff_existing.getFeatures():
#    if feat.geometry() == None:
#        areas.append(float(0))

#    else:
#        areas.append(feat.geometry().area())

#field1 = QgsField("areaDiff", QVariant.Double)
#provider.addAttributes([field1])
#SDiff_existing.updateFields()
#idx = SDiff_existing.fieldNameIndex('areaDiff')
#print idx
    # print idx # debugging
#for area in areas:
#    new_values = {idx: float(area)}
#    print new_values
#    print areas.index(area)
#    provider.changeAttributeValues({areas.index(area): new_values})

#point_layer= potential_match_existing #None

#text_table= SDiff_existing #None

#POINT_ID='id'
#TEXT_ID='id'
#joinObject = QgsVectorJoinInfo()
#joinObject.joinLayerId = text_table.id()
#QgsVectorLayer.removeJoin(point_layer, text_table.id())
#joinObject.joinFieldName = TEXT_ID
#joinObject.targetFieldName = POINT_ID
#joinObject.memoryCache = True
#joinObject.setJoinFieldNamesSubset(['areaDiff'])
#point_layer.addJoin(joinObject)

#provider = potential_match_existing.dataProvider()
#field = QgsField("Overlap", QVariant.Double)
#provider.addAttributes([field])
#potential_match_existing.updateFields()
#idx = potential_match_existing.fieldNameIndex('Overlap')
#print idx # debugging

#string = "output ", str(6), "-sdiff_existing Polygon_areaDiff"
 #potential_match_existing.string)
# This allows field lookup
potential_match_existing.startEditing()

expression = QgsExpression('1 + 3')
expression.prepare(potential_match_existing.pendingFields())
idx = 5

for f in potential_match_existing.getFeatures():
    f[idx] = expression.evaluate( f )
    potential_match_existing.updateFeature( f )

potential_match_existing.commitChanges()

