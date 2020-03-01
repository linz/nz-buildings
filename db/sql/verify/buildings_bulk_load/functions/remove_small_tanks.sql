-- Verify nz-buildings:buildings_bulk_load/functions/remove_small_tanks on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_remove_small_tanks(integer)', 'execute');

ROLLBACK;
