"""
--------------------------------------------------------------------
Buildings
--------------------------------------------------------------------
"""

# building outlines

building_outlines = """
SELECT *
FROM buildings.building_outlines bo
WHERE ST_Intersects(bo.shape, %s)
AND bo.building_outline_id NOT IN ( SELECT building_outline_id FROM buildings_bulk_load.removed );
"""

building_outlines_end_lifespan_by_id = """
SELECT end_lifespan
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outline_shape_by_id = """
SELECT shape
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

# lifecycle stage

lifecycle_stage_by_value = """
SELECT *
FROM buildings.lifecycle_stage
WHERE value = %s;
"""

lifecycle_stage_value = """
SELECT value
FROM buildings.lifecycle_stage;
"""

lifecycle_stage_value_by_outlineID = """
SELECT ls.value
FROM buildings.lifecycle_stage ls,
     buildings.building_outlines bo
WHERE bo.building_outline_id = %s
AND bo.lifecycle_stage_id = ls.lifecycle_stage_id;
"""

lifecycle_stage_ID_by_value = """
SELECT lifecycle_stage_id
FROM buildings.lifecycle_stage
WHERE value = %s;
"""

"""
-------------------------------------------------------------------
Bulk Load Outlines
-------------------------------------------------------------------
"""

# bulk load outlines

bulk_load_outlines_ID_by_datasetID = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s;
"""

bulk_load_removed_outlines_ID_by_datasetID = """
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

reason_description_value = """
SELECT DISTINCT description
FROM buildings_bulk_load.deletion_description;
"""

deletion_description_by_id = """
SELECT description
FROM buildings_bulk_load.deletion_description
WHERE bulk_load_outline_id = %s;
"""

# Organisation

organisation_by_value = """
SELECT *
FROM buildings_bulk_load.organisation
WHERE value = %s;
"""

organisation_value = """
SELECT value
FROM buildings_bulk_load.organisation;
"""

organisation_value_by_datasetID = """
SELECT value
FROM buildings_bulk_load.organisation o,
     buildings_bulk_load.bulk_load_outlines blo,
     buildings_bulk_load.supplied_datasets sd
WHERE blo.supplied_dataset_id = %s
AND blo.supplied_dataset_id = sd.supplied_dataset_id
AND sd.supplier_id = o.organisation_id;
"""

organisation_ID_by_value = """
SELECT organisation_id
FROM buildings_bulk_load.organisation o
WHERE o.value = %s;
"""

# supplied dataset

dataset_description_by_datasetID = """
SELECT description
FROM buildings_bulk_load.supplied_datasets sd
WHERE sd.supplied_dataset_id = %s;
"""

dataset_processed_date_by_datasetID = """
SELECT processed_date
FROM buildings_bulk_load.supplied_datasets sd
WHERE sd.supplied_dataset_id = %s;
"""

dataset_count_processed_date_is_null = """
SELECT count(*)
FROM buildings_bulk_load.supplied_datasets
WHERE processed_date is NULL;
"""

dataset_processed_date_is_null = """
SELECT supplied_dataset_id
FROM buildings_bulk_load.supplied_datasets
WHERE processed_date is NULL;
"""

dataset_count_transfer_date_is_null = """
SELECT count(*)
FROM buildings_bulk_load.supplied_datasets
WHERE transfer_date is NULL;
"""

dataset_transfer_date_is_null = """
SELECT supplied_dataset_id
FROM buildings_bulk_load.supplied_datasets
WHERE transfer_date is NULL;
"""

dataset_count_both_dates_are_null = """
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

bulk_load_status_value_by_outlineID = """
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

existing_subset_extracts_by_building_outlineID = """
SELECT building_outline_id
FROM buildings_bulk_load.existing_subset_extracts
WHERE building_outline_id = %s;
"""

# added
current_added_outlines = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.added
WHERE bulk_load_outline_id IN (
      SELECT bulk_load_outline_id
      FROM buildings_bulk_load.bulk_load_outlines
      WHERE supplied_dataset_id = %s);
"""

# matched
current_matched_outlines = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.matched
WHERE bulk_load_outline_id IN(
      SELECT bulk_load_outline_id
      FROM buildings_bulk_load.bulk_load_outlines
      WHERE supplied_dataset_id = %s);
"""

# related
current_related_outlines = """
SELECT bulk_load_outline_id
FROM buildings_bulk_load.related
WHERE bulk_load_outline_id IN (
    SELECT bulk_load_outline_id
    FROM buildings_bulk_load.bulk_load_outlines
    WHERE supplied_dataset_id = %s);
"""

"""
----------------------------------------------------------------
Buildings Common
----------------------------------------------------------------
"""

# capture method

capture_method_value = """
SELECT value
FROM buildings_common.capture_method;
"""

capture_method_value_by_datasetID = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.capture_method_id = cm.capture_method_id
AND blo.supplied_dataset_id = %s;
"""

capture_method_ID_by_value = """
SELECT capture_method_id
FROM buildings_common.capture_method cm
WHERE cm.value = %s;
"""

capture_method_value_by_bulk_outlineID = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.capture_method_id = cm.capture_method_id
AND blo.bulk_load_outline_id = %s;
"""

capture_method_value_by_building_outlineID = """
SELECT value
FROM buildings_common.capture_method cm,
     buildings.building_outlines bo
WHERE bo.capture_method_id = cm.capture_method_id
AND bo.building_outline_id = %s;
"""

capture_method_by_value = """
SELECT *
FROM buildings_common.capture_method
WHERE buildings_common.capture_method.value = %s;
"""

# capture source group

capture_srcgrp_value_description = """
SELECT value, description
FROM buildings_common.capture_source_group;
"""

capture_srcgrp_by_value = """
SELECT *
FROM buildings_common.capture_source_group
WHERE buildings_common.capture_source_group.value = %s;
"""

capture_srcgrp_capture_srcgrpID_by_datasetID = """
SELECT cs.capture_source_group_id
FROM buildings_common.capture_source_group csg,
     buildings_common.capture_source cs,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s
AND blo.capture_source_id = cs.capture_source_id
AND cs.capture_source_group_id = csg.capture_source_group_id;
"""

capture_source_group_srcrpID_by_value = """
SELECT capture_source_group_id
FROM buildings_common.capture_source_group
WHERE value = %s;
"""

capture_srcgrp_by_value_and_description = """
SELECT capture_source_group_id
FROM buildings_common.capture_source_group csg
WHERE csg.value = %s
AND csg.description = %s;
"""

capture_source_group_value_desc_external = """
SELECT csg.value,
       csg.description,
       cs.external_source_id
FROM buildings_common.capture_source_group csg,
     buildings_common.capture_source cs
WHERE cs.capture_source_group_id = csg.capture_source_group_id;
"""

capture_source_group_value_desc_external_by_bulk_outlineID = """
SELECT csg.value,
       csg.description,
       cs.external_source_id
FROM buildings_common.capture_source_group csg,
     buildings_common.capture_source cs,
     buildings_bulk_load.bulk_load_outlines blo
WHERE csg.capture_source_group_id = cs.capture_source_group_id
AND blo.capture_source_id = cs.capture_source_id
AND blo.bulk_load_outline_id = %s;
"""

capture_source_group_value_desc_external_by_building_outlineID = """
SELECT csg.value,
       csg.description,
       cs.external_source_id
FROM buildings_common.capture_source_group csg,
     buildings_common.capture_source cs,
     buildings.building_outlines bo
WHERE csg.capture_source_group_id = cs.capture_source_group_id
AND bo.capture_source_id = cs.capture_source_id
AND bo.building_outline_id = %s;
"""

# capture source

capture_src_extsrcID_by_datasetID = """
SELECT cs.external_source_id
FROM buildings_common.capture_source cs,
     buildings_bulk_load.bulk_load_outlines blo
WHERE blo.supplied_dataset_id = %s
AND blo.capture_source_id = cs.capture_source_id;
"""

capture_source_external_sourceID = """
SELECT external_source_id
FROM buildings_common.capture_source;
"""

capture_source_ID_by_capsrcgrpID_and_externalSrcID = """
SELECT capture_source_id
FROM buildings_common.capture_source cs,
WHERE cs.capture_source_group_id = %s
AND cs.external_source_id = %s;
"""

capture_source_ID_by_capsrcgrdID_is_null = """
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

capture_source_by_external_or_group_id = """
SELECT * FROM buildings_common.capture_source
WHERE buildings_common.capture_source.external_source_id = %s
OR buildings_common.capture_source.capture_source_group_id = %s;
"""

capture_source_by_group_id_external_is_null = """
SELECT * FROM buildings_common.capture_source
WHERE buildings_common.capture_source.external_source_id = NULL
OR buildings_common.capture_source.capture_source_group_id = %s;
"""


"""
--------------------------------------------------------------------
buildings reference
--------------------------------------------------------------------
"""

# suburb locality

suburb_locality_suburb_4th = """
SELECT DISTINCT suburb_4th
FROM buildings_reference.suburb_locality;
"""

suburb_locality_suburb_4th_by_bulk_outlineID = """
SELECT suburb_4th
FROM buildings_reference.suburb_locality sl,
     buildings_bulk_load.bulk_load_outlines blo
WHERE sl.suburb_locality_id = blo.suburb_locality_id
AND blo.bulk_load_outline_id = %s;
"""

suburb_locality_suburb_4th_by_building_outlineID = """
SELECT suburb_4th
FROM buildings_reference.suburb_locality sl,
     buildings.building_outlines bo
WHERE sl.suburb_locality_id = bo.suburb_locality_id
AND bo.building_outline_id = %s;
"""

suburb_locality_suburb_4th_by_id = """
SELECT suburb_4th
FROM buildings_reference.suburb_locality
WHERE suburb_locality_id = %s;
"""

suburb_locality_id_by_suburb_4th = """
SELECT suburb_locality_id
FROM buildings_reference.suburb_locality
WHERE buildings_reference.suburb_locality.suburb_4th = %s;
"""

# town city

town_city_name = """
SELECT DISTINCT name
FROM buildings_reference.town_city;
"""

town_city_name_by_bulk_outlineID = """
SELECT name
FROM buildings_reference.town_city tc,
     buildings_bulk_load.bulk_load_outlines blo
WHERE tc.town_city_id = blo.town_city_id
AND blo.bulk_load_outline_id = %s;
"""

town_city_name_by_building_outlineID = """
SELECT name
FROM buildings_reference.town_city tc,
     buildings.building_outlines bo
WHERE tc.town_city_id = bo.town_city_id
AND bo.building_outline_id = %s;
"""

town_city_name_by_id = """
SELECT name
FROM buildings_reference.town_city
WHERE town_city_id = %s;
"""

town_city_ID_by_name = """
SELECT town_city_id
FROM buildings_reference.town_city
WHERE buildings_reference.town_city.name = %s;
"""

# territorial Authority

territorial_authority_name = """
SELECT DISTINCT name
FROM buildings_reference.territorial_authority;
"""

territorial_authority_name_by_bulk_outline_id = """
SELECT name
FROM buildings_reference.territorial_authority ta,
     buildings_bulk_load.bulk_load_outlines blo
WHERE ta.territorial_authority_id = blo.territorial_authority_id
AND blo.bulk_load_outline_id = %s;
"""

territorial_authority_name_by_building_outline_id = """
SELECT name
FROM buildings_reference.territorial_authority ta,
     buildings.building_outlines bo
WHERE ta.territorial_authority_id = bo.territorial_authority_id
AND bo.building_outline_id = %s;
"""

territorial_authority_name_by_id = """
SELECT name
FROM buildings_reference.territorial_authority
WHERE territorial_authority_id = %s;
"""

territorial_authority_ID_by_name = """
SELECT territorial_authority_id
FROM buildings_reference.territorial_authority
WHERE buildings_reference.territorial_authority.name = %s;
"""
