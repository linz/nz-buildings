-- Verify nz-buildings:facilities_lds/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('facilities_lds', 'usage');

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
      shape
FROM facilities_lds.nz_facilities
WHERE FALSE;

ROLLBACK;

