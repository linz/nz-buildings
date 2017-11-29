# final code
# 29/11/2017

#  relevant inputs
from qgis.utils import iface
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import processing
import csv


#############################################################################


def read_in_files(existing, incoming):
    '''
        function to read in the existing and input files
    '''
    existing_layer = iface.addVectorLayer(existing, "1-", "ogr")
    if not existing_layer:
        print "existing layer not found"
    incoming_layer = iface.addVectorLayer(incoming, "2-", "ogr")
    if not incoming_layer:
        print "incoming layer not found"
    return [existing_layer, incoming_layer]

##############################################################################


def removed_buildings(existing, incoming):
    '''
        Finding removed buildings
    '''
    existing.selectAll()
    # selecting the buildings
    processing.runalg("qgis:selectbylocation", existing, incoming,
                      ['intersects'], 0, 2)
    # save selection to file
    name = 'Removed Buildings'  # name of shapefile

    processing.runalg('qgis:saveselectedfeatures', existing, path)
    # reading shapefile back into qgis
    removed = iface.addVectorLayer(path + name + '.shp', "Output 1-", "ogr")
    return removed

##############################################################################


def new_buildings(existing, incoming):
    '''
        Finding new buildings
    '''
    incoming.selectAll()
    # selecting the buildings
    processing.runalg("qgis:selectbylocation", incoming, existing,
                      ['intersects'], 0, 2)
    # save selection to file
    name = 'New Buildings'  # name of shapefile

    processing.runalg('qgis:saveselectedfeatures', incoming, path)
    # reading shapefile back into qgis
    new = iface.addVectorLayer(path + name + '.shp', "Output 2-", "ogr")
    return new

#############################################################################


def potential_match(existing, incoming):
    '''
        Finding potential Match in existing buildings
    '''
    processing.runalg("qgis:selectbylocation", existing, incoming,
                      ['intersects'], 0, 0)  # selecting the buildings
    # save selection to file
    name_e = 'Potential Match Existing Layer'  # name of shapefile

    processing.runalg('qgis:saveselectedfeatures',
                      existing, path + name_e + '.shp')
    # reading shapefile back into qgis
    pm_existing = iface.addVectorLayer(path + name_e + '.shp',
                                       "Output 3-", "ogr")
    # existing.removeSelection()
    incoming.removeSelection()
    # Finding potential Match in incominging buildings
    processing.runalg("qgis:selectbylocation", incoming, existing,
                      ['intersects'], 0, 0)  # selecting the buildings

    # save selection to file
    name = 'Potential Match IncomingLayer'  # name of shapefile
    processing.runalg('qgis:saveselectedfeatures',
                      incoming, path + name + '.shp')
    # reading shapefile back into qgis
    pm_incoming = iface.addVectorLayer(path + name + '.shp',
                                       "Output 4-", "ogr")

    return[pm_existing, pm_incoming]

###############################################################################


def add_building_id(potential_existing, potential_incoming):
    '''
        Adding Building id Field for Existing Potential Matches
    '''
    provider = potential_existing.dataProvider()
    build_id = [feat.id() for feat in potential_existing.getFeatures()]
    field = QgsField("Build_id", QVariant.Double)
    provider.addAttributes([field])
    potential_existing.updateFields()
    idx = potential_existing.fieldNameIndex('Build_id')
    for bid in build_id:
        new_values = {idx: bid}
        provider.changeAttributeValues({build_id.index(bid): new_values})

    # Adding empty Building id field for Incoming Potential Matches
 #   providerI = potential_incoming.dataProvider()
#    fieldI = QgsField("Build_id", QVariant.Double)
 #   providerI.addAttributes([fieldI])
 #   Potential_incoming.updateFields()

#############################################################################


def finding_intersecting_buildings(potential_exisitng, potential_incoming):
    '''
        function to iterate through the potential match buildings
        and find the incoming builds that intersect with more than
        one existing building.
    '''
    values = {}

    for building in potential_incoming.getFeatures():
        build = building.geometry()
        for polygon in potential_exisitng.getFeatures():
            poly = polygon.geometry()
            if poly.intersects(build):
                if building.id() in values:
                    values[building.id()].append(polygon.id())
                else:
                    temp = [polygon.id()]
                    values[building.id()] = temp

    max_intersect = -99999
    for key in values:
        temp = len(values[key])
        if temp > max_intersect:
            max_intersect = temp

    count = 1
    idx = []
    provider_intersect = potential_incoming.dataProvider()
    while count <= max_intersect:
        field_intersect = "e_Bid" + str(count)
        field_i = QgsField(field_intersect, QVariant.Double)
        provider_intersect.addAttributes([field_i])
        potential_match_incoming.updateFields()
        temp = potential_match_incoming.fieldNameIndex(field_intersect)
        idx.append(temp)
        count = count + 1
    count = 0
    while count < max_intersect:
        idx_value = idx[count]
        b = 0
        for building_id in values:
            b = b + 1
            temp_v = values[building_id]
            if len(temp_v) > count:
                new_values = {idx_value: temp_v[count]}
                provider_intersect.changeAttributeValues({building_id:
                                                         new_values})
        count = count + 1

##############################################################


def calculate_area(potential_existing, potential_incoming):
    '''
        Adding Area Fields to existing and incoming potential
        match files                                                     POSSIBILITY to improve and make a function to 
        .                                                               add area field to any shapefile        
    '''
    # Adding area field for existing potential matches
    provider = potential_existing.dataProvider()
    areas = [feat.geometry().area() for feat in
             potential_existing.getFeatures()]
    field = QgsField("area", QVariant.Double)
    provider.addAttributes([field])
    potential_existing.updateFields()
    idx = potential_existing.fieldNameIndex('area')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # Adding Area Field for Incoming Potential Matches
    provider = potential_incoming.dataProvider()
    areas = [feat.geometry().area() for feat in
             potential_incoming.getFeatures()]
    field = QgsField("area", QVariant.Double)
    provider.addAttributes([field])
    potential_incoming.updateFields()
    idx = potential_incoming.fieldNameIndex('area')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})


###########################################################


def calculate_overlap(potential_existing, potential_incoming):
    '''
        
        Method to calculate the overlap between single intersecting
        existing and incoming buildings

    '''
    # Calculate Symmetrical Difference
    name = 'Symmetric Difference'  # name of shapefile

    processing.runalg('qgis:symmetricaldifference', potential_existing,
                      potential_incoming, path)
    # reading shapefile back into qgis
    s_diff = iface.addVectorLayer(path + name + '.shp', "Output 5-",
                                 "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(s_diff, False)

    # Split Symmetric Difference Layer by existing field
    processing.runalg('qgis:selectbyattribute', s_diff, 'id',
                      0, "id is not NULL")
    name = "sdiff_existing"
    processing.runalg('qgis:saveselectedfeatures', s_diff, path + name)
    s_diff_existing = iface.addVectorLayer(path + name + '.shp',
                                          "temp 1-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(s_diff_existing, False)

    # Adding Area Field for Existing Potential Matches
    provider = s_diff_existing.dataProvider()
    areas = []
    for feat in s_diff_existing.getFeatures():
        if feat.geometry() is None:
            areas.append(float(0))

        else:
            areas.append(feat.geometry().area())

    # Adding area field to existing symmetrical difference layer
    provider = s_diff_existing.dataProvider()
    field1 = QgsField("areaDiff", QVariant.Double)
    provider.addAttributes([field1])
    s_diff_existing.updateFields()
    idx = s_diff_existing.fieldNameIndex('areaDiff')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # joing the existing symmetric difference area to the existing
    # potential match attributes table
    match_layer = potential_existing
    diff_table = s_diff_existing
    match_id = 'id'
    diff_id = 'id'
    joinObject = QgsVectorJoinInfo()
    joinObject.joinLayerId = diff_table.id()
    joinObject.joinFieldName = diff_id
    joinObject.targetFieldName = match_id
    joinObject.memoryCache = True
    # specifying to only copy the areaDiff field
    joinObject.setJoinFieldNamesSubset(['areaDiff'])
    match_layer.addJoin(joinObject)

    # Creating new Field Overlap
    # existing
    provider = potential_existing.dataProvider()
    field = QgsField("Overlap", QVariant.Double)
    provider.addAttributes([field])
    potential_existing.updateFields()
    idx = potential_existing.fieldNameIndex('Overlap')

    # caclulating overlap existing
    provider = s_diff_existing.dataProvider()
    potential_existing.startEditing()
    expression = QgsExpression('100-(("temp 1- sdiff_existing Polygon_areaDiff"/"area")*100)')
    expression.prepare(potential_existing.pendingFields())

    for f in potential_existing.getFeatures():
        f[idx] = expression.evaluate(f)
        potential_existing.updateFeature(f)

    potential_existing.commitChanges()

    # Split Symmetric Difference Layer by incoming field
    processing.runalg('qgis:selectbyattribute', s_diff, 'id_2',
                      0, "id_2 is not NULL")
    name = "sdiff_incoming"
    processing.runalg('qgis:saveselectedfeatures', s_diff, path + name)
    s_diff_incoming = iface.addVectorLayer(path + name + '.shp',
                                          "temp 2-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(s_diff_incoming, False)

    # Adding Area Field for Incoming Potential Matches
    provider = s_diff_incoming.dataProvider()
    areas = []
    for feat in s_diff_incoming.getFeatures():
        if feat.geometry() is None:
            areas.append(float(0))

        else:
            areas.append(feat.geometry().area())

    # Adding area field to incoming symmetrical difference layer
    provider = s_diff_incoming.dataProvider()
    field1 = QgsField("areaDiff", QVariant.Double)
    provider.addAttributes([field1])
    s_diff_incoming.updateFields()
    idx = s_diff_incoming.fieldNameIndex('areaDiff')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # joing the incoming symmetric difference area to
    # the incoming potential match attributes table
    match_layer = potential_incoming
    diff_table = s_diff_incoming
    match_id = 'id'
    diff_id = 'id_2'
    joinObject = QgsVectorJoinInfo()
    joinObject.joinLayerId = diff_table.id()
    joinObject.joinFieldName = diff_id
    joinObject.targetFieldName = match_id
    joinObject.memoryCache = True
    # specifying to only copy the areaDiff field
    joinObject.setJoinFieldNamesSubset(['areaDiff'])
    match_layer.addJoin(joinObject)

    # Incoming
    provider = potential_incoming.dataProvider()
    field = QgsField("Overlap", QVariant.Double)
    provider.addAttributes([field])
    potential_incoming.updateFields()
    idx = potential_incoming.fieldNameIndex('Overlap')

    # caclulating overlap incoming
    provider = s_diff_incoming.dataProvider()
    potential_incoming.startEditing()
    expression = QgsExpression('100-(("temp 2- sdiff_incoming Polygon_areaDiff"/"area")*100)')
    expression.prepare(potential_incoming.pendingFields())

    for f in potential_incoming.getFeatures():
        f[idx] = expression.evaluate(f)
        potential_incoming.updateFeature(f)

    potential_incoming.commitChanges()


#####################################################################
def comparisons(potential_existing, potential_incoming, path, csv_file):
    '''
        generates the comparisons (area and overlap) between incoming and existing
        shape files
        also produces a csv file detailing the comparison information
    '''

    # fields of the existing potential match buildings we are interested in
    columns_existing = ['id', 'Build_id', 'area',
                        'Overlap', 'temp 1- sdiff_existing Polygon_areaDiff']
    # dictionary of key: existing building id to values:
    # list of existing building id to
    # overlap, then id and overlap of all intersecting buildings
    fields = {}
    # iterate through potential match existing layer
    for feature in potential_existing.getFeatures():
        # list of attributes related to specified fields
        attrs = [feature[column] for column in columns_existing]
        temp_list = []
        temp_list.append(float(attrs[0]))
        if attrs[4] == NULL:
            temp_list.append(attrs[2])
        else:
            temp_list.append(attrs[2] - attrs[4])
        if attrs[3] == NULL:
            temp_list.append(100)
        else:
            temp_list.append(attrs[3])

        fields[int(attrs[1])] = temp_list  # add row to dictionary

    # list relating to the incoming buildings that intersect multiple
    # existing buildings
    multiple_intersections = []

    # fields of the potential match incoming layer we are interested in
    columns_incoming = ['id', 'e_Bid1', 'e_Bid2', 'e_Bid3',                 # SPECIFIC TO SUBSET, Other datasets may have polygons with 
                        'area', 'temp 2- sdiff_incoming Polygon_areaDiff',  # more than three intersecting buildings 
                        'Overlap']                                          #     |
    # iterate through the incoming potential match layer                    #     |    
    # and find the attributes that intersect only one existing building     #     |
    for features in potential_incoming.getFeatures():                       #     |
        attrs = [features[column] for column in columns_incoming]           #     |
        if attrs[2] == NULL and attrs[3] == NULL:                           #     |
            for key in fields:                                              #     |
                if key == attrs[1]:                                         #     |
                    fields[key].append(attrs[0])                            #     |
                    if attrs[5] == NULL:                                    #     |
                        fields[key].append(attrs[4])                        #     |
                    else:                                                   #     |
                        fields[key].append(attrs[4] - attrs[5])             #     |
                    if attrs[6] == NULL:                                    #     |
                        fields[key].append(100)                             #     |
                    else:                                                   #     |
                        fields[key].append(attrs[6])                        #     V
        # if intersect multiple add to this list
        else:
            multiple_intersections.append(attrs)

    ##################################################
    # Extract building where incoming buildings intersect
    # multiple existing buildings
    # list of the incoming building ids that intersect 'id'
    incoming_id = []
    # list if the existing buildng ids that intersect 'Build_id'
    existing_build_id = []
    for mi in multiple_intersections:
        incoming_id.append(mi[0])  # filling the list
        count = 1
        total = 3  # make variable
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
    # find all the buildings in the potential match
    # incoming layer that have the specified ids
    query = '"id" IN' + st
    selection = potential_incoming.getFeatures(QgsFeatureRequest().setFilterExpression(query))
    potential_incoming.setSelectedFeatures([k.id() for k in selection])
    # save to new shape file
    name = 'Incoming_mulitple_matches'  # name of shapefile
    processing.runalg('qgis:saveselectedfeatures', potential_incoming, path)
    multi_match_incoming = iface.addVectorLayer(path + name + '.shp',
                                                "Output 6-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(multi_match_incoming, False)
    # creating string version of list for select by attributes
    val = str(existing_build_id)
    st = ''
    for c in val:
        if c != '[':
            if c != ']':
                if c != 'L':
                    st = st + c
    st = '(' + st + ')'

    # find all the buildings in potential match
    # existing that have specified ids
    query = '"Build_id" IN' + st
    selection = potential_existing.getFeatures(QgsFeatureRequest().setFilterExpression(query))
    potential_existing.setSelectedFeatures([k.id() for k in selection])
    # save to new shape file
    name = 'existing_mulitple_matches'  # name of shapefile
    processing.runalg('qgis:saveselectedfeatures', potential_existing, path)
    multi_match_existing = iface.addVectorLayer(path + name + '.shp',
                                                "Output 7-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(multi_match_existing, False)

    #########################################################################
    # recalculate overlap
    # needs to be done to calculate how much the existing building
    # intersects with only the one incoming building
    # Calculate Symmetrical Difference
    name = 'SD recalculate'  # name of shapefile

    processing.runalg('qgis:symmetricaldifference',
                      multi_match_existing, multi_match_incoming, path)
    SD_rec = iface.addVectorLayer(path + name + '.shp', "temp 3-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(SD_rec, False)
    # Split Symmetric Difference Layer by existing field
    processing.runalg('qgis:selectbyattribute', SD_rec, 'id', 0,
                      "id is not NULL")
    path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/"
    name = "SD_rec_existing"
    processing.runalg('qgis:saveselectedfeatures', SD_rec, path + name)
    SD_rec_existing = iface.addVectorLayer(path + name + '.shp',
                                           "temp 4-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(SD_rec_existing, False)

    processing.runalg('qgis:selectbyattribute', SD_rec, 'id_2', 0,
                      "id_2 is not NULL")
    path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/"
    name = "SD_rec_incoming"
    processing.runalg('qgis:saveselectedfeatures', SD_rec, path + name)
    SD_rec_incoming = iface.addVectorLayer(path + name + '.shp',
                                           "temp 5-", "ogr")
    legend = iface.legendInterface()
    legend.setLayerVisible(SD_rec_incoming, False)

    # Adding Area Field for Existing Multiple Matches
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
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # joing the existing symmetric difference area to the
    # existing potential match attributes
    # table
    match_layer = multi_match_existing
    diff_table = SD_rec_existing
    match_id = 'id'
    diff_id = 'id'
    joinObject = QgsVectorJoinInfo()
    joinObject.joinLayerId = diff_table.id()
    joinObject.joinFieldName = diff_id
    joinObject.targetFieldName = match_id
    joinObject.memoryCache = True
    # specifying to only copy the areaDiff field
    joinObject.setJoinFieldNamesSubset(['areaDiff'])
    match_layer.addJoin(joinObject)

    # Creating new Field Overlap
    # existing
    provider = multi_match_existing.dataProvider()
    field = QgsField("Overlap_re", QVariant.Double)
    provider.addAttributes([field])
    multi_match_existing.updateFields()
    idx_1 = multi_match_existing.fieldNameIndex("Overlap_re")

    # caclulating overlap existing
    provider = SD_rec_existing.dataProvider()
    multi_match_existing.startEditing()
    expression = QgsExpression('100-(("temp 4- SD_rec_existing Polygon_areaDiff"/"area")*100)')

    expression.prepare(multi_match_existing.pendingFields())

    for f in multi_match_existing.getFeatures():
        f[idx_1] = expression.evaluate(f)
        multi_match_existing.updateFeature(f)

    multi_match_existing.commitChanges()

    # Adding Area Field for Incoming Multiple Matches
    provider = SD_rec_incoming.dataProvider()
    areas = []
    for feat in SD_rec_incoming.getFeatures():
        if feat.geometry() is None:
            areas.append(float(0))
        else:
            areas.append(feat.geometry().area())

    # Adding area field to incoming symmetrical difference layer
    provider = SD_rec_incoming.dataProvider()
    field1 = QgsField("areaDiff", QVariant.Double)
    provider.addAttributes([field1])
    SD_rec_incoming.updateFields()
    idx = SD_rec_incoming.fieldNameIndex('areaDiff')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # joing the existing symmetric difference area to the
    # existing potential match attributes
    # table
    match_layer = multi_match_incoming
    diff_table = SD_rec_incoming
    match_id = 'id'
    diff_id = 'id_2'
    joinObject = QgsVectorJoinInfo()
    joinObject.joinLayerId = diff_table.id()
    joinObject.joinFieldName = diff_id
    joinObject.targetFieldName = match_id
    joinObject.memoryCache = True
    # specifying to only copy the areaDiff field
    joinObject.setJoinFieldNamesSubset(['areaDiff'])
    match_layer.addJoin(joinObject)
    #########################################################
    # new dictionary of incoming building id to existing intersecting buildings
    mult_e_intersect_i = {}
    temp_dict = {}  # to get map of ids across incoming and existing
    columns = ['id', 'Overlap', 'area', 'e_Bid1', 'e_Bid2', 'e_Bid3',          # SPECIFIC TO SUBSET
               'temp 5- SD_rec_incoming Polygon_areaDiff']                     #     |
    for building in multi_match_incoming.getFeatures():                        #     |
        attrs = [building[column] for column in columns]                       #     |
        area = attrs[2] - attrs[6]                                             #     |
        mult_e_intersect_i[int(attrs[0])] = [int(attrs[0]), area, attrs[1]]    #     |
        if attrs[2] != NULL:                                                   #     |
            temp_dict[attrs[2]] = attrs[0]                                     #     |
        if attrs[3] != NULL:                                                   #     |
            temp_dict[attrs[3]] = attrs[0]                                     #     |
        if attrs[4] != NULL:                                                   #     |
            temp_dict[attrs[4]] = attrs[0]                                     #     V

    columns = ['id', 'Build_id', 'area', 'Overlap_re',
               'temp 4- SD_rec_existing Polygon_areaDiff']
    for building in multi_match_existing.getFeatures():
        attrs = [building[column] for column in columns]
        building_id = attrs[1]
        if building_id in temp_dict.keys():
            overlap = attrs[3]
            area = attrs[2] - attrs[4]
            if temp_dict[building_id] in mult_e_intersect_i:
                income_id = temp_dict[building_id]
                mult_e_intersect_i[income_id].append(building_id)
                mult_e_intersect_i[income_id].append(area)
                mult_e_intersect_i[income_id].append(overlap)
    
    # remove from fields dictionary existing buildings
    # that overlap with multiple incoming buildings (and therefore)
    # don't have 'pairs'
    temp_list = []
    for key in fields:
        if len(fields[key]) == 3:
            temp_list.append(key)
    map(fields.pop, temp_list)

    # separate out buildings with only one intersection
    one_overlap = {}
    temp_list = []

    # calculate the differences
    for key in fields:
        if len(fields[key]) == 6:
            one_overlap[key] = fields[key]
            overlap_existing = fields[key][2]
            overlap_incoming = fields[key][5]
            area_existing = fields[key][1]
            area_incoming = fields[key][4]
            difference_overlap = overlap_existing - overlap_incoming
            difference_area = area_existing - area_incoming
            one_overlap[key].append(difference_area)
            one_overlap[key].append(difference_overlap)
            temp_list.append(key)
    map(fields.pop, temp_list)

    # remove from fields (dictionary containing all existing buildings with multiple intersecting)
    # incoming buildings) the intersectoins with less than X% overlap
    for key in fields:
        temp_list = fields[key]
        l = range(len(temp_list))
        l = l[5::3]
        for value in temp_list:
            to_remove = []
            if temp_list.index(value) in l:
                if value <= 5:  # threshold value: can be changed
                    id_num = temp_list[temp_list.index(value) - 2]
                    overlap_percent = value
                    area_overlap = temp_list[temp_list.index(value) - 1]
                    to_remove.append(temp_list.index(id_num))
                    to_remove.append(temp_list.index(overlap_percent))
                    to_remove.append(temp_list.index(area_overlap))
                    if key not in one_overlap:
                        one_overlap[key] = [temp_list[0], temp_list[1],
                                            temp_list[2], id_num,
                                            area_overlap, overlap_percent]
        count = 0
        for val in to_remove:
            temp_list.pop(val - count)
            count = count + 1
        fields[key] = temp_list

    # remove from one overlap where the intersection between 
    # existing and incoming buildings is insignificant
        for key in one_overlap:
            temp_list = one_overlap[key]
            l = range(len(temp_list))
            l = l[5]
            for value in temp_list:
                to_remove = []
                if temp_list.index(value) == l:
                    if value <= 5: # threshold value: can be changed
                        to_remove = temp_list

        count = 0
        for val in to_remove:
            temp_list.pop(val - count)
            count = count + 1
        one_overlap[key] = temp_list

    # remove buildings with minimal overlap from multiple existing and one incoming building
    for key in mult_e_intersect_i:
        temp_list = mult_e_intersect_i[key]
        l = range(len(temp_list))
        l = l[5::3]
        to_remove = []
        for value in temp_list:
            if temp_list.index(value) in l:
                if value <= 5:   # threshold value: can be changed
                    id_num = temp_list[temp_list.index(value) - 2]
                    overlap_area = temp_list[temp_list.index(value) - 1]
                    overlap_percent = value
                    to_remove.append(temp_list.index(id_num))
                    to_remove.append(temp_list.index(overlap_percent))
                    to_remove.append(temp_list.index(overlap_area))
                    if id_num not in one_overlap:
                        one_overlap[id_num] = ['', overlap_area,
                                               overlap_percent, key,
                                               temp_list[1], temp_list[2]]
        count = 0
        for val in to_remove:
            temp_list.pop(val - count)
            count = count + 1
        mult_e_intersect_i[key] = temp_list

    # iterate through dictionaries again and remove
    # and add those which now meet the spec

    # of one_overlap
    for key in mult_e_intersect_i:
        if len(mult_e_intersect_i[key]) == 6:
            if mult_e_intersect_i[key][3] not in one_overlap:
                one_overlap[mult_e_intersect_i[key][3]] = [' ',
                            mult_e_intersect_i[key][4], mult_e_intersect_i[key][5],
                            mult_e_intersect_i[key][0], mult_e_intersect_i[key][1],
                            mult_e_intersect_i[key][2]]
            mult_e_intersect_i[key] = []

    for key in fields:
        if len(fields[key]) == 6:
            if fields[key][3] not in one_overlap:
                one_overlap[fields[key]] = [fields[key][0], fields[key][1],
                                            fields[key][2], fields[key][3],
                                            fields[key][4], fields[key][5]]
            mult_e_intersect_i[key] = []

    # write results to csv file
    with open(csv_file, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        header = ['Single Building Intersection', ' ', ' ']
        writer.writerow(header)
        text = ['Existing Building ID', 'Existing Buiding Fid', 'EB Area',
                'EB_Overlap', 'Incoming Building Fid', 'IB Area', 'IC Overlap',
                'Area Difference', 'Overlap Difference']
        writer.writerow(text)
        for key in one_overlap:
            temp = []
            temp.append(key)
            for v in one_overlap[key]:
                temp.append(v)
            writer.writerow(temp)
        writer.writerow(' ')
        header = ['Multiple Incoming Buildings Intersecting Single',
                  'Existing Building', ' ', ' ']
        writer.writerow(header)
        text = ['Existing Building ID', 'Existing Buiding Fid', 'EB Area',
                'EB_Overlap', 'Incoming Building Fid', 'IB Area', 'IB Overlap',
                'Incoming Building Fid', 'IB Area', 'IB Overlap', '...']
        writer.writerow(text)
        for key, value in fields.items():
            if len(fields[key]) > 0:
                temp = []
                temp.append(key)
                for v in value:
                    temp.append(v)
                writer.writerow(temp)
        writer.writerow(' ')
        header = ['Multiple Existing Buildings Intersecting Single',
                  'Incoming Building', ' ', ' ']
        writer.writerow(header)
        text = ['Incoming Building Fid', 'IB Area', 'IB_Overlap',
                'Existing Building ID', 'EB Area', 'EB Overlap',
                'Existing Building ID', 'EB Area', 'EB Overlap', '...']
        writer.writerow(text)
        for key, value in mult_e_intersect_i.items():
            if len(mult_e_intersect_i[key]) > 0:
                temp = []
                for v in value:
                    temp.append(v)
                writer.writerow(temp)
    csv_file.close()

#####################################################################


def update_csv(new, removed, csv_file):
    '''
    add new and removed data to the csv file
    '''
    # new buildings
    # calculate and add area field
    provider = new.dataProvider()
    areas = [feat.geometry().area() for feat in
             new.getFeatures()]
    field = QgsField("area", QVariant.Double)
    provider.addAttributes([field])
    new.updateFields()
    idx = new.fieldNameIndex('area')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # add values to dictionary
    new_builds = {}
    columns = ['id', 'area']
    for building in new.getFeatures():
        attrs = [building[column] for column in columns]
        new_builds[attrs[0]] = attrs[1]

    with open(csv_file, 'a') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(' ')
        li = ['New Buildings (incoming)', '', '']
        writer.writerow(li)
        li = ['Building Fid', 'Area']
        writer.writerow(li)
        for key in new_builds:
            temp_list = [key, new_builds[key]]
            writer.writerow(temp_list)
        csv_f.close()

    # Removed Buildings
    # calculate and add area field
    provider = removed.dataProvider()
    areas = [feat.geometry().area() for feat in
             removed.getFeatures()]
    field = QgsField("area", QVariant.Double)
    provider.addAttributes([field])
    new.updateFields()
    idx = removed.fieldNameIndex('area')
    for area in areas:
        new_values = {idx: float(area)}
        provider.changeAttributeValues({areas.index(area): new_values})

    # add values to dictionary
    removed_builds = {}
    columns = ['id', 'area']
    for building in removed.getFeatures():
        attrs = [building[column] for column in columns]
        removed_builds[attrs[0]] = attrs[1]

    with open(csv_file, 'a') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(' ')
        li = ['Removed Buildings (existing)', '', '']
        writer.writerow(li)
        li = ['Building Fid', 'Area']
        writer.writerow(li)
        for key in removed_builds:
            temp_list = [key, removed_builds[key]]
            writer.writerow(temp_list)


####################################################################
# Main Code:

# EDIT HERE TO CHANGE FILE LOCATIONS:
input_existing_text = '/home/linz_user/data/BuildingsProcessing/finalDataQGIS/existing_building_outlines_subset.shp'
input_incoming_text = '/home/linz_user/data/BuildingsProcessing/finalDataQGIS/incoming_building_outlines_subset.shp'
path = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/"
csv_file = path + 'output.csv'


# call read in function
layers = read_in_files(input_existing_text, input_incoming_text)
existing_layer = layers[0]
incoming_layer = layers[1]

# find removed buildings
removed = removed_buildings(existing_layer, incoming_layer)
legend = iface.legendInterface()
legend.setLayerVisible(removed, False)

existing_layer.removeSelection()
incoming_layer.removeSelection()

# find new buildings
new = new_buildings(existing_layer, incoming_layer)
legend.setLayerVisible(new, False)

existing_layer.removeSelection()
incoming_layer.removeSelection()

# find potential matches
potential_matches = potential_match(existing_layer, incoming_layer)
potential_match_existing = potential_matches[0]
potential_match_incoming = potential_matches[1]
legend.setLayerVisible(potential_match_existing, False)
legend.setLayerVisible(potential_match_incoming, False)

# add/prepare building IDs
add_building_id(potential_match_existing, potential_match_incoming)

# Find the existing building ids of the incoming intersecting buildings
# this adds new fields to the attribute tables of the incoming layer
finding_intersecting_buildings(potential_match_existing,
                               potential_match_incoming)

# calculates the area of each polygon and adds it to area fields in the
# potential match attributes tables
calculate_area(potential_match_existing, potential_match_incoming)

calculate_overlap(potential_match_existing, potential_match_incoming)

# generates comparisons of overlapping buildings, output as csv file
output_file = comparisons(potential_match_existing,
                          potential_match_incoming, path, csv_file)

# add new and removed buildings to csv file
update_csv(new, removed, csv_file)

# final output shape file:
    # always used incoming data as most recent data
pm = path + 'Potential Match IncomingLayer.shp'
n = path + 'New Buildings.shp'
processing.runalg("qgis:mergevectorlayers", pm + ';' + n,
                  path + "best_candidates.shp")
best_candidates = iface.addVectorLayer(path + 'best_candidates.shp',
                                       "Output 8-", "ogr")  # output shapefile

# deselecting everything
for a in iface.attributesToolBar().actions(): 
  if a.objectName() == 'mActionDeselectAll':
    a.trigger()
    break
