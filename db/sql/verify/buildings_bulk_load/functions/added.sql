-- Verify buildings:buildings_bulk_load/functions/added on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.added_delete_bulk_load_outlines(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.added_insert_all_bulk_loaded_outlines(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.added_insert_bulk_load_outlines(integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.added_select_by_dataset(integer)', 'execute');

ROLLBACK;
