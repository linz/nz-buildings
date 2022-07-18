-- Verify nz-buildings:buildings/functions/add_names_and_uses_functions on pg

BEGIN;

SELECT has_function_privilege('buildings.building_name_added_insert_bulk(integer, integer)', 'execute');
SELECT has_function_privilege('buildings.building_name_matched_insert_bulk(integer)', 'execute');
SELECT has_function_privilege('buildings.building_name_related_insert_bulk(integer, integer)', 'execute');
SELECT has_function_privilege('buildings.building_name_removed_insert_bulk(integer)', 'execute');
SELECT has_function_privilege('buildings.building_use_added_insert_bulk(integer, integer)', 'execute');
SELECT has_function_privilege('buildings.building_use_matched_insert_bulk(integer)', 'execute');
SELECT has_function_privilege('buildings.building_use_related_insert_bulk(integer, integer)', 'execute');
SELECT has_function_privilege('buildings.building_use_removed_insert_bulk(integer)', 'execute');

ROLLBACK;
