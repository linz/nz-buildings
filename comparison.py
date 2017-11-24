import csv
columns_existing = ['id', 'Build_id', 'Overlap']

filtered_fields = []
for feature in potential_match_existing.getFeatures():
    attrs = [feature[column] for column in columns_existing]
    filtered_fields.append(attrs)

    # have to add other fields to filtered_fields before writing to a file

output_file = "/home/linz_user/data/BuildingsProcessing/FinalDataPyQGIS/Comparison.csv"
with open(output_file, "w") as csv_file:
    writer = csv.writer(csv_file)
    header = ['id_ex', 'Build_id', 'Overlap_ex', 'id_in', 'Overlap_in', 'Difference']
    writer.writerow(header)
    for field in filtered_fields:
        writer.writerow(field)
