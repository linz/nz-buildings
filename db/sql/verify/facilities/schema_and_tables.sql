-- Verify nz-buildings:facilities/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('facilities', 'usage');

SELECT
      facility_id,
      source_facility_id,
      name,
      source_name,
      use,
      use_type,
      use_subtype,
      estimated_occupancy,
      last_modified,
      internal,
      internal_comments,
      shape
FROM facilities.facilities
WHERE FALSE;

ROLLBACK;
