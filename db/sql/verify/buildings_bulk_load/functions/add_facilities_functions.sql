-- Verify nz-buildings:buildings_bulk_load/functions/add_facilities_functions on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.load_facility_names()', 'execute');
SELECT has_function_privilege('buildings_bulk_load.load_facility_use_id()', 'execute');
SELECT has_function_privilege('buildings_bulk_load.load_matched_names()', 'execute');
SELECT has_function_privilege('buildings_bulk_load.load_matched_use_id()', 'execute');
SELECT has_function_privilege('buildings_bulk_load.load_related_names()', 'execute');
SELECT has_function_privilege('buildings_bulk_load.load_related_use_id()', 'execute');

ROLLBACK;
