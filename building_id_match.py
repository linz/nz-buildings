# comment
values = {}

for building in potential_match_incoming.getFeatures():
    build = building.geometry()
    for polygon in potential_match_existing.getFeatures():
        poly = polygon.geometry()
        if poly.intersects(build):
            if building.id() in values:
                values[building.id()].append(polygon.id())
            else:
                temp = [polygon.id()]
                values[building.id()] = temp
print values

max_intersect = -99999
for key in values:
    temp = len(values[key])
    if temp > max_intersect:
        max_intersect = temp
print max_intersect  # 3

count = 1
idx = []
provider_intersect = potential_match_incoming.dataProvider()
while count<=max_intersect:
    field_intersect = "e_Bid "+str(count)
    fieldI = QgsField(field_intersect, QVariant.Double)
    provider_intersect.addAttributes([fieldI])
    potential_match_incoming.updateFields()
    temp = potential_match_incoming.fieldNameIndex(field_intersect)
    idx.append(temp)
    count = count + 1
    
count = 0
while count < max_intersect:
    idx_value = idx[count]
    b = 0
    for building_id in values:
        b = b+1
        temp_v = values[building_id]
        if len(temp_v) > count:
            new_values = {idx_value : temp_v[count]}
            provider_intersect.changeAttributeValues({building_id:new_values})
    count = count + 1

