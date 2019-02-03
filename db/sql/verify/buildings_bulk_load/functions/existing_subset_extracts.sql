-- Verify buildings:buildings_bulk_load/functions/existing_subset_extracts on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.existing_subset_extracts_insert(integer, integer, geometry)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.existing_subset_extracts_update_supplied_dataset(integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.existing_subset_extracts_remove_by_building_outline_id(integer[])', 'execute');

ROLLBACK;
