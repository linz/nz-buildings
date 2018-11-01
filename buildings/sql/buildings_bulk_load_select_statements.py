"""
-------------------------------------------------------------------
Bulk Load Outlines Select Statements
-------------------------------------------------------------------
"""

# bulk load outlines

bulk_load_outlines_id_by_dataset_id = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s;
"""

bulk_load_removed_outlines_id_by_dataset_id = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s
  AND blo.bulk_load_status_id = 3;
"""

bulk_load_outline_shape_by_id = """
SELECT shape
FROM buildings_bulk_load.bulk_load_outlines
WHERE bulk_load_outline_id = %s;
"""

# deletion_description

deletion_description_value = """
SELECT DISTINCT description
FROM buildings_bulk_load.deletion_description
ORDER BY description;
"""

# Organisation

organisation_id_by_value = """
SELECT *
FROM buildings_bulk_load.organisation
WHERE value = %s;
"""

organisation_value = """
SELECT value
FROM buildings_bulk_load.organisation;
"""

organisation_value_by_dataset_id = """
SELECT value
FROM buildings_bulk_load.organisation o,
     buildings_bulk_load.bulk_load_outlines blo,
     buildings_bulk_load.supplied_datasets sd
WHERE blo.supplied_dataset_id = %s
AND blo.supplied_dataset_id = sd.supplied_dataset_id
AND sd.supplier_id = o.organisation_id;
"""

organisation_id_by_value = """
SELECT organisation_id
FROM buildings_bulk_load.organisation o
WHERE o.value = %s;
"""

# supplied dataset

supplied_dataset_description_by_dataset_id = """
SELECT description
FROM buildings_bulk_load.supplied_datasets sd
WHERE sd.supplied_dataset_id = %s;
"""

supplied_dataset_processed_date_by_dataset_id = """
SELECT processed_date
FROM buildings_bulk_load.supplied_datasets sd
WHERE sd.supplied_dataset_id = %s;
"""

supplied_dataset_count_processed_date_is_null = """
SELECT count(*)
FROM buildings_bulk_load.supplied_datasets
WHERE processed_date is NULL;
"""

supplied_dataset_processed_date_is_null = """
SELECT supplied_dataset_id
FROM buildings_bulk_load.supplied_datasets
WHERE processed_date is NULL;
"""

supplied_dataset_count_transfer_date_is_null = """
SELECT count(*)
FROM buildings_bulk_load.supplied_datasets
WHERE transfer_date is NULL;
"""

supplied_dataset_transfer_date_is_null = """
SELECT supplied_dataset_id
FROM buildings_bulk_load.supplied_datasets
WHERE transfer_date is NULL;
"""

supplied_dataset_count_both_dates_are_null = """
SELECT count(*)
FROM buildings_bulk_load.supplied_datasets
WHERE processed_date is NULL
AND transfer_date is NULL;
"""

# bulk_load_status

bulk_load_status_value = """
SELECT value
FROM buildings_bulk_load.bulk_load_status;
"""

bulk_load_status_value_by_outline_id = """
SELECT value
FROM buildings_bulk_load.bulk_load_status bls,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.bulk_load_status_id = bls.bulk_load_status_id
AND blo.bulk_load_outline_id = %s;
"""

bulk_load_status_id_by_value = """
SELECT bulk_load_status_id
FROM buildings_bulk_load.bulk_load_status bls
WHERE bls.value = %s;
"""

# existing subset extracts

existing_subset_extracts_by_building_outline_id = """
SELECT building_outline_id
FROM buildings_bulk_load.existing_subset_extracts
WHERE building_outline_id = %s;
"""

# added
added_outlines_by_dataset_id = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.added
WHERE bulk_load_outline_id IN (
      SELECT bulk_load_outline_id
      FROM buildings_bulk_load.bulk_load_outlines
      WHERE supplied_dataset_id = %s);
"""

# matched
matched_outlines_by_dataset_id = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.matched
WHERE bulk_load_outline_id IN(
      SELECT bulk_load_outline_id
      FROM buildings_bulk_load.bulk_load_outlines
      WHERE supplied_dataset_id = %s);
"""

# related
related_outlines_by_dataset_id = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.related
WHERE bulk_load_outline_id IN (
    SELECT bulk_load_outline_id
    FROM buildings_bulk_load.bulk_load_outlines
    WHERE supplied_dataset_id = %s);
"""

# alter-relationship

related_by_bulk_load_outlines = """
SELECT building_outline_id, bulk_load_outline_id
FROM buildings_bulk_load.related
WHERE related_group_id in (
  SELECT DISTINCT related_group_id
  FROM buildings_bulk_load.related
  JOIN buildings_bulk_load.bulk_load_outlines USING (bulk_load_outline_id)
  WHERE bulk_load_outline_id = %s AND supplied_dataset_id = %s);
"""

matched_by_bulk_load_outlines = """
SELECT building_outline_id
FROM buildings_bulk_load.matched
JOIN buildings_bulk_load.bulk_load_outlines USING (bulk_load_outline_id)
WHERE bulk_load_outline_id = %s AND supplied_dataset_id = %s;
"""

added_by_bulk_load_outlines = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.added
JOIN buildings_bulk_load.bulk_load_outlines USING (bulk_load_outline_id)
WHERE bulk_load_outline_id = %s AND supplied_dataset_id = %s;
"""

related_by_existing_outlines = """
SELECT building_outline_id, bulk_load_outline_id
FROM buildings_bulk_load.related
WHERE related_group_id in (
  SELECT DISTINCT related_group_id
  FROM buildings_bulk_load.related
  JOIN buildings_bulk_load.bulk_load_outlines USING (bulk_load_outline_id)
  WHERE building_outline_id = %s AND supplied_dataset_id = %s);
"""

matched_by_existing_outlines = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.matched
JOIN buildings_bulk_load.existing_subset_extracts USING (building_outline_id)
WHERE building_outline_id = %s AND supplied_dataset_id = %s;
"""
removed_by_existing_outlines = """
SELECT building_outline_id
FROM buildings_bulk_load.removed
JOIN buildings_bulk_load.existing_subset_extracts USING (building_outline_id)
WHERE building_outline_id = %s AND supplied_dataset_id = %s;
"""

related_by_dataset_id = """
SELECT r.related_group_id, r.building_outline_id, r.bulk_load_outline_id, q.value
FROM buildings_bulk_load.related r
JOIN buildings_bulk_load.qa_status q USING (qa_status_id)
JOIN buildings_bulk_load.bulk_load_outlines blo USING (bulk_load_outline_id)
WHERE blo.supplied_dataset_id = %s
ORDER BY r.related_group_id ASC;
"""

matched_by_dataset_id = """
SELECT m.building_outline_id, m.bulk_load_outline_id, q.value
FROM buildings_bulk_load.matched m
JOIN buildings_bulk_load.qa_status q USING (qa_status_id)
JOIN buildings_bulk_load.bulk_load_outlines blo USING (bulk_load_outline_id)
WHERE blo.supplied_dataset_id = %s
ORDER BY m.building_outline_id ASC;
"""

removed_by_dataset_id = """
SELECT r.building_outline_id, q.value
FROM buildings_bulk_load.removed r
JOIN buildings_bulk_load.qa_status q USING (qa_status_id)
JOIN buildings_bulk_load.existing_subset_extracts existing USING (building_outline_id)
WHERE existing.supplied_dataset_id = %s
ORDER BY r.building_outline_id ASC;
"""
