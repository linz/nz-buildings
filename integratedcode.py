# integrated code


from qgis.utils import iface
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer
import processing

# function to read in the existing and input files
def read_in_files(existing, incoming):
    existingLayer = iface.addVectorLayer(existing, "1-", "ogr")
    if not existingLayer:
        print "existing layer not found"
    incomingLayer = iface.addVectorLayer(incoming, "2-", "ogr")
    if not incomingLayer:
        print "incoming layer not found"
    return [existingLayer, incomingLayer]


def removed_buildings(existing, incoming):
    # Finding removed buildings
    existing.selectAll()
    processing.runalg("qgis:selectbylocation", existing, incoming, ['intersects'], 0, 2)  # selecting the buildings
    # save selection to file
    name = 'Removed Buildings'  # name of shapefile
    path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location

    processing.runalg('qgis:saveselectedfeatures', existing, path)
    removed = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 1-", "ogr")  # reading shapefile back into qgis
    return removed


def new_buildings(existing, incoming):
    # Finding new buildings
    incoming.selectAll()
    processing.runalg("qgis:selectbylocation", incoming, existing, ['intersects'], 0, 2)  # selecting the buildings
    # save selection to file
    name = 'New Buildings'  # name of shapefile
    path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location

    processing.runalg('qgis:saveselectedfeatures', incoming, path)
    new = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 2-", "ogr")  # reading shapefile back into qgis
    return new


def potential_match(existing, incoming):
    # Finding potential Match in existing buildings
    processing.runalg("qgis:selectbylocation", existing, incoming, ['intersects'], 0, 0)  # selecting the buildings
    # save selection to file
    name1 = 'Potential Match Existing Layer'  # name of shapefile
    path1 = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name1 + '.shp'  # setting up save location

    PM_exists = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name1 + '.shp', "Output 3-", "ogr")  # reading shapefile back into qgis
    #existing.removeSelection()
    incoming.removeSelection()
    # Finding potential Match in incominging buildings
    processing.runalg("qgis:selectbylocation", incoming, existing, ['intersects'], 0, 0)  # selecting the buildings

    # save selection to file
    name = 'Potential Match IncomingLayer'  # name of shapefile
    path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location

    processing.runalg('qgis:saveselectedfeatures', incoming, path)
    PM_incoming = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 4-", "ogr")  # reading shapefile back into qgis

    return[PM_existing, PM_incoming]


def add_building_id(Potential_existing, Potential_incoming):
    # Adding Building id Field for Existing Potential Matches
    provider = Potential_existing.dataProvider()
    Build_id = [feat.id() for feat in Potential_existing.getFeatures()]
    field = QgsField("Build_id", QVariant.Double)
    provider.addAttributes([field])
    Potential_existing.updateFields()
    idx = Potential_existing.fieldNameIndex('Build_id')
    for bid in Build_id:
        new_values = {idx: bid}
        provider.changeAttributeValues({Build_id.index(bid): new_values})

    # Adding empty Building id field for Incoming Potential Matches
    providerI = Potential_incoming.dataProvider()
    fieldI = QgsField("Build_id", QVariant.Double)
    providerI.addAttributes([fieldI])
    Potential_incoming.updateFields()
    #idxI = Potential_incoming.fieldNameIndex('Build_id')


# main code

# take user input, needs fixing
# also get user input for file storage location


#qid = QInputDialog()
#title = "Enter Following Details"
#label = "Existing Data file location and name: "
#mode = QLineEdit.Normal
#default = "<enter here>"
#input_existing_text, ok = QInputDialog.getText(qid, title, label, mode, default)
#title2 = "Enter Following Details"
#label2 = "Incoming Data file location and name: "
#mode2 = QLineEdit.Normal
#default2 = "<enter here>"
#input_incoming_text, ok = QInputDialog.getText(qid, title2, label2, mode2, default2)

input_existing_text = "/home/linz_user/data/BuildingsProcessing/finalDataQGIS/existing_building_outlines_subset.shp"
input_incoming_text = "/home/linz_user/data/BuildingsProcessing/finalDataQGIS/incoming_building_outlines_subset.shp"
# call read in function
layers = read_in_files(input_existing_text, input_incoming_text)
existing_layer = layers[0]
incoming_layer = layers[1]

# find removed buildings
removed = removed_buildings(existing_layer, incoming_layer)

existing_layer.removeSelection()
incoming_layer.removeSelection()

# find new buildings
new = new_buildings(existing_layer, incoming_layer)

existing_layer.removeSelection()
incoming_layer.removeSelection()

# find potential matches
potential_matches = potential_match(existing_layer, incoming_layer)
potential_match_existing = potential_matches[0]
potential_match_incoming = potential_matches[1]

# add/prepare building IDs
#add_building_id(potential_match_existing, potential_match_incoming)
