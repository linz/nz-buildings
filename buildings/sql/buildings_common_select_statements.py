"""
----------------------------------------------------------------
Buildings Common Select Statements:

- Capture Method
  - capture_method_by_value (value)
  - capture_method_id_by_value (value)
  - capture_method_value
  - capture_method_value_by_building_outline_id (building_outline_id)
  - capture_method_value_by_bulk_outline_id (bulk_load_outline_id)
  - capture_method_value_by_dataset_id (supplied_dataset_id)

- Capture Source Group
  - capture_source_group_by_value (value)
  - capture_source_group_by_value_and_description (value, description)
  - capture_source_group_id_by_dataset_id (supplied_dataset_id)
  - capture_source_group_id_by_value (value)
  - capture_source_group_value_description
  - capture_source_group_value_external
  - capture_source_group_value_external_by_building_outline_id (building_outline_id)
  - capture_source_group_value_external_by_bulk_outline_id (bulk_load_outline_id)
  - capture_source_group_value_external_by_dataset_id (current_dataset_id)

- Capture Source
  - capture_source_external_id_and_area_title_by_group_id (capture_source_group_id)
  - capture_source_external_source_id
  - capture_source_external_source_id_by_dataset_id (dataset_id)
  - capture_source_id_by_capture_source_group_id_and_external_source_id (capture_source_group_id, external_source_id)
  - capture_source_id_by_capture_source_group_id_is_null
  - capture_source_value_description

----------------------------------------------------------------
"""

# capture method

capture_method_by_value = """
SELECT *
FROM buildings_common.capture_method
WHERE buildings_common.capture_method.value = %s;
"""

capture_method_id_by_value = """
SELECT capture_method_id
FROM buildings_common.capture_method cm
WHERE cm.value = %s;
"""

capture_method_value = """
SELECT value
FROM buildings_common.capture_method;
"""

capture_method_value_by_building_outline_id = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings.building_outlines bo
WHERE bo.capture_method_id = cm.capture_method_id
AND bo.building_outline_id = '%s';
"""

capture_method_value_by_bulk_outline_id = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.capture_method_id = cm.capture_method_id
AND blo.bulk_load_outline_id = %s;
"""

capture_method_value_by_dataset_id = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.capture_method_id = cm.capture_method_id
AND blo.supplied_dataset_id = %s;
"""

# capture source group

capture_source_group_by_value = """
SELECT *
FROM buildings_common.capture_source_group
WHERE buildings_common.capture_source_group.value = %s;
"""

capture_source_group_by_value_and_description = """
SELECT capture_source_group_id
FROM buildings_common.capture_source_group csg
WHERE csg.value = %s
AND csg.description = %s;
"""

capture_source_group_id_by_dataset_id = """
SELECT cs.capture_source_group_id
FROM buildings_common.capture_source_group csg,
     buildings_common.capture_source cs,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s
AND blo.capture_source_id = cs.capture_source_id
AND cs.capture_source_group_id = csg.capture_source_group_id;
"""

capture_source_group_id_by_value = """
SELECT csg.capture_source_group_id
FROM buildings_common.capture_source_group csg
JOIN buildings_common.capture_source cs USING (capture_source_group_id)
WHERE csg.value = %s;
"""

capture_source_group_value_description = """
SELECT value, description
FROM buildings_common.capture_source_group;
"""

capture_source_group_id_value_description = """
SELECT capture_source_group_id, value, description
FROM buildings_common.capture_source_group;
"""

capture_source_group_value_external_by_building_outline_id = """
SELECT cs.external_source_id,
       csa.area_title,
       csg.value
FROM buildings_common.capture_source_group csg
JOIN buildings_common.capture_source cs USING (capture_source_group_id)
JOIN buildings_reference.capture_source_area csa ON cs.external_source_id = csa.external_area_polygon_id
JOIN buildings.building_outlines bo USING (capture_source_id)
WHERE bo.building_outline_id = %s;
"""

capture_source_group_value_external_by_bulk_outline_id = """
SELECT cs.external_source_id,
       csa.area_title,
       csg.value
FROM buildings_common.capture_source_group csg
JOIN buildings_common.capture_source cs USING (capture_source_group_id)
JOIN buildings_reference.capture_source_area csa ON cs.external_source_id = csa.external_area_polygon_id
JOIN buildings_bulk_load.bulk_load_outlines blo USING (capture_source_id)
WHERE blo.bulk_load_outline_id = %s;
"""

capture_source_group_value_external = """
SELECT cs.external_source_id,
       csa.area_title,
       csg.value
FROM buildings_common.capture_source_group csg
JOIN buildings_common.capture_source cs USING (capture_source_group_id)
JOIN buildings_reference.capture_source_area csa ON cs.external_source_id = csa.external_area_polygon_id;
"""

capture_source_group_value_external_by_dataset_id = """
SELECT cs.external_source_id,
       csa.area_title,
       csg.value
FROM buildings_common.capture_source_group csg
JOIN buildings_common.capture_source cs USING (capture_source_group_id)
JOIN buildings_reference.capture_source_area csa ON cs.external_source_id = csa.external_area_polygon_id
JOIN buildings_bulk_load.bulk_load_outlines blo USING (capture_source_id)
WHERE blo.supplied_dataset_id = %s
LIMIT 1;
"""

# capture source

capture_source_external_id_and_area_title_by_group_id = """
SELECT cs.external_source_id, csa.area_title
FROM buildings_common.capture_source cs
JOIN buildings_reference.capture_source_area csa ON cs.external_source_id = csa.external_area_polygon_id
WHERE cs.capture_source_group_id = %s;
"""

capture_source_external_source_id_by_dataset_id = """
SELECT cs.external_source_id
FROM buildings_common.capture_source cs,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s
AND blo.capture_source_id = cs.capture_source_id;
"""

capture_source_external_source_id = """
SELECT external_source_id
FROM buildings_common.capture_source;
"""

capture_source_id_by_capture_source_group_id_and_external_source_id = """
SELECT cs.capture_source_id
FROM buildings_common.capture_source cs
WHERE cs.capture_source_group_id = %s
AND cs.external_source_id = %s;
"""

capture_source_id_by_capture_source_group_id_is_null = """
SELECT cs.capture_source_id
FROM buildings_common.capture_source cs
WHERE cs.capture_source_group_id = %s
AND cs.external_source_id is NULL;
"""

capture_source_value_description = """
SELECT value,
       description
FROM buildings_common.capture_source_group;
"""
