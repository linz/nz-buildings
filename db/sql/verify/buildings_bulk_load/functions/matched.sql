-- Verify nz-buildings:buildings_bulk_load/functions/matched on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.building_outlines_matched_select_by_dataset(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.matched_delete_existing_outlines(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.matched_find_building_id(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.matched_insert_building_outlines(integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.matched_select_by_dataset(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.matched_update_qa_status_id(integer, integer, integer)', 'execute');

ROLLBACK;
