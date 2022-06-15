-- Revert nz-buildings:buildings_bulk_load/functions/add_facilities_functions from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.load_facility_names();
DROP FUNCTION buildings_bulk_load.load_facility_use_id();
DROP FUNCTION buildings_bulk_load.load_matched_names();
DROP FUNCTION buildings_bulk_load.load_matched_use_id();
DROP FUNCTION buildings_bulk_load.load_related_names();
DROP FUNCTION buildings_bulk_load.load_related_use_id();

COMMIT;
