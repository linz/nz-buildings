# relevant import
import csv

# fields of the existing potential match buildings we are interested in
columns_existing = ['id', 'Build_id', 'Overlap']
# dictionar of key: existing building id to values: list of existing building id to
# overlap, then id and overlap of all intersecting buildings
fields = {}

filtered_fields = []
# iterate through potential match existing layer
for feature in potential_match_existing.getFeatures():
    # list of attributes related to specified fields
    attrs = [feature[column] for column in columns_existing]
    temp_list = []
    temp_list.append(float(attrs[0]))
    if attrs[2] == NULL:
        temp_list.append(100)
    else:
        temp_list.append(attrs[2])
    fields[int(attrs[1])] = temp_list # add row to dictionary

# list relating to the incoming buildings that intersect multiple 
# existing buildings
multiple_intersections = []

# fields of the potential match incoming layer we are interested in
# TODO: make the number of e_Bid* vary according to the input layer
columns_incoming = ['id', 'e_Bid1', 'e_Bid2', 'e_Bid3', 'Overlap']
# iterate through the incoming potential match layer and find the attributes
# that intersect only one existing building
for features in potential_match_incoming.getFeatures():
    attrs = [features[column] for column in columns_incoming]
    if attrs[2] == NULL and attrs[3] == NULL:
        for key in fields:
            if key == attrs[1]:
                fields[key].append(attrs[0])
                if attrs[4] == NULL:
                    fields[key].append(100)
                else:
                    fields[key].append(attrs[4])
            if key == attrs[2]:
                fields[key].append(attrs[0])
                if attrs[4] == NULL:
                    fields[key].append(100)
                else:
                    fields[key].append(attrs[4])
            if key == attrs[3]:
                fields[key].append(attrs[0])
                if attrs[4] == NULL:
                    fields[key].append(100)
                else:
                    fields[key].append(attrs[4])
    # if intersect multiple add to this list
    else:
        multiple_intersections.append(attrs)

##################################################
# Extract building where incoming buildings intersect
# multiple existing buildings
incoming_id = []  # list of the incoming building ids that intersect 'id'
existing_build_id = []  # list if the existing buildng ids that intersect 'Build_id'
for mi in multiple_intersections:
    incoming_id.append(mi[0])  # filling the list
    count = 1
    total = 3
    while count <= total:
        if mi[count] != NULL:
            existing_build_id.append(mi[count])  # filling  the list
        count = count + 1

# creating string version of list for select by attributes
val = str(incoming_id)
st = ''
for c in val:
    if c != '[':
        if c != ']':
            if c != 'L':
                st = st + c
st = '(' + st + ')'
# find all the buildings in the potential match incoming layer that have the specified ids
query = '"id" IN' + st
selection = potential_match_incoming.getFeatures(QgsFeatureRequest().setFilterExpression(query))
potential_match_incoming.setSelectedFeatures([k.id() for k in selection])
# save to new shape file
name = 'Incoming_mulitple_matches'  # name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location
processing.runalg('qgis:saveselectedfeatures', potential_match_incoming, path)
multi_match_incoming = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 6-", "ogr")  # reading shapefile back into qgis

# creating string version of list for select by attributes
val = str(existing_build_id)
st = ''
for c in val:
    if c != '[':
        if c != ']':
            if c != 'L':
                st = st + c
st = '(' + st + ')'
# find all the buildings in potential match existing that have specified ids
query = '"Build_id" IN' + st
selection = potential_match_existing.getFeatures(QgsFeatureRequest().setFilterExpression(query))
potential_match_existing.setSelectedFeatures([k.id() for k in selection])
# save to new shape file
name = 'existing_mulitple_matches'  # name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location
processing.runalg('qgis:saveselectedfeatures', potential_match_existing, path)
multi_match_existing = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "Output 7-", "ogr")  # reading shapefile back into qgis

#########################################################################
# recalculate overlap
# needs to be done to calculate how much the existing building intersects with only the one incoming building
# Calculate Symmetrical Difference
name = 'SD recalculate'  # name of shapefile
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp'  # setting up save location

processing.runalg('qgis:symmetricaldifference', multi_match_existing, multi_match_incoming, path)
SD_rec = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "temp 3-", "ogr")  # reading shapefile back into qgis

# Split Symmetric Difference Layer by existing field
processing.runalg('qgis:selectbyattribute', SD_rec, 'id', 0, "id is not NULL")
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/"
name = "SD_rec_existing"
processing.runalg('qgis:saveselectedfeatures', SD_rec, path + name)
SD_rec_existing = iface.addVectorLayer("/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/" + name + '.shp', "temp 4-", "ogr")

# Adding Area Field for Existing Potential Matches
provider = SD_rec_existing.dataProvider()
areas = []
for feat in SD_rec_existing.getFeatures():
    if feat.geometry() is None:
        areas.append(float(0))

    else:
        areas.append(feat.geometry().area())

# Adding area field to existing symmetrical difference layer
provider = SD_rec_existing.dataProvider()
field1 = QgsField("areaDiff", QVariant.Double)
provider.addAttributes([field1])
SD_rec_existing.updateFields()
idx = SD_rec_existing.fieldNameIndex('areaDiff')
# print idx
# print idx # debugging
for area in areas:
    new_values = {idx: float(area)}
    # print new_values
    # print areas.index(area)
    provider.changeAttributeValues({areas.index(area): new_values})

# joing the existing symmetric difference area to the existing potential match attributes
# table
match_layer = multi_match_existing
diff_table = SD_rec_existing
MATCH_ID = 'id'
DIFF_ID = 'id'
joinObject = QgsVectorJoinInfo()
joinObject.joinLayerId = diff_table.id()
joinObject.joinFieldName = DIFF_ID
joinObject.targetFieldName = MATCH_ID
joinObject.memoryCache = True
joinObject.setJoinFieldNamesSubset(['areaDiff'])  # specifying to only copy the areaDiff field
match_layer.addJoin(joinObject)

# Creating new Field Overlap
# existing
provider = multi_match_existing.dataProvider()
field = QgsField("Overlap_re", QVariant.Double)
provider.addAttributes([field])
multi_match_existing.updateFields()
idx_1 = multi_match_existing.fieldNameIndex("Overlap_re")
print idx_1

# caclulating overlap existing
provider = SD_rec_existing.dataProvider()
multi_match_existing.startEditing()
expression = QgsExpression('100-(("temp 4- SD_rec_existing Polygon_areaDiff"/"area")*100)')
# print expression
expression.prepare(multi_match_existing.pendingFields())

for f in multi_match_existing.getFeatures():
    f[idx_1] = expression.evaluate(f)
    multi_match_existing.updateFeature(f)

multi_match_existing.commitChanges()
#########################################################

# new dictionary of incoming building id to existing intersecting buildings
mult_e_intersect_i = {}
temp_dict = {}  # to get map of ids across incoming and existing
columns = ['id', 'Overlap', 'e_Bid1', 'e_Bid2', 'e_Bid3']
for building in multi_match_incoming.getFeatures():
    attrs = [building[column] for column in columns]
    mult_e_intersect_i[int(attrs[0])] = [int(attrs[0]), attrs[1]]
    if attrs[2] != NULL:
        temp_dict[attrs[2]] = attrs[0]
    if attrs[3] != NULL:
        temp_dict[attrs[3]] = attrs[0]
    if attrs[4] != NULL:
        temp_dict[attrs[4]] = attrs[0]

columns = ['id', 'Build_id', 'Overlap_re']
for building in multi_match_existing.getFeatures():
    attrs = [building[column] for column in columns]
    building_id = attrs[1]
    if building_id in temp_dict.keys():
        overlap = attrs[2]
        if temp_dict[building_id] in mult_e_intersect_i:
            income_id = temp_dict[building_id]
            mult_e_intersect_i[income_id].append(building_id)
            mult_e_intersect_i[income_id].append(overlap)


# TODO:
# calculate differences before writing to csv file
# tidy up csv file
# figure out which buildings to include and which to exclude


# write results to csv file
with open('/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/dict.csv', 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in fields.items():
        temp = []
        temp.append(key)
        for v in value:
            temp.append(v)
        writer.writerow(temp)
    writer.writerow(' ')
    for key, value in mult_e_intersect_i.items():
        temp = []
        for v in value:
            temp.append(v)
        writer.writerow(temp)
