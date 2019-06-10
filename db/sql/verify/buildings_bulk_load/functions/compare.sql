-- Verify nz-buildings:buildings_bulk_load/functions/compare on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.find_added(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.find_removed(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.find_matched(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.find_related(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.reassign_related_ids(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.compare_building_outlines(integer)', 'execute');

ROLLBACK;
