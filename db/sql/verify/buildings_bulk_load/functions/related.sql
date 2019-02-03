-- Verify buildings:buildings_bulk_load/functions/related on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.building_outlines_related_select_by_dataset(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.buildings_related_select_by_dataset(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.related_delete_existing_outlines(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.related_insert_building_outlines(integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.related_group_insert()', 'execute');

SELECT has_function_privilege('buildings_bulk_load.related_select_by_dataset(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.related_update_qa_status_id(integer, integer, integer)', 'execute');

ROLLBACK;
