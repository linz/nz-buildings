-- Verify buildings:buildings_bulk_load/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_bulk_load', 'usage');

SELECT
      organisation_id
    , value
FROM buildings_bulk_load.organisation
WHERE FALSE;

SELECT
      bulk_load_status_id
    , value
FROM buildings_bulk_load.bulk_load_status
WHERE FALSE;

SELECT
      qa_status_id
    , value
FROM buildings_bulk_load.qa_status
WHERE FALSE;

SELECT
      supplied_dataset_id
    , description
    , supplier_id
    , processed_date
    , transfer_date
FROM buildings_bulk_load.supplied_datasets
WHERE FALSE;

SELECT
      supplied_outline_id
    , supplied_dataset_id
    , external_outline_id
    , begin_lifespan
    , shape
FROM buildings_bulk_load.supplied_outlines
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , supplied_dataset_id
    , external_outline_id
    , bulk_load_status_id
    , capture_method_id
    , capture_source_id
    , suburb_locality_id
    , town_city_id
    , territorial_authority_id
    , begin_lifespan
    , shape
FROM buildings_bulk_load.bulk_load_outlines
WHERE FALSE;

SELECT
      building_outline_id
    , supplied_dataset_id
    , shape
FROM buildings_bulk_load.existing_subset_extracts
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , qa_status_id
FROM buildings_bulk_load.added
WHERE FALSE;

SELECT
      building_outline_id
    , qa_status_id
FROM buildings_bulk_load.removed
WHERE FALSE;

SELECT
      related_group_id
FROM buildings_bulk_load.related_groups
WHERE FALSE;

SELECT
      related_id
    , related_group_id
    , bulk_load_outline_id
    , building_outline_id
    , qa_status_id
FROM buildings_bulk_load.related
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , building_outline_id
    , qa_status_id
FROM buildings_bulk_load.matched
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , new_building_outline_id
FROM buildings_bulk_load.transferred
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , description
FROM buildings_bulk_load.deletion_description
WHERE FALSE;

ROLLBACK;
