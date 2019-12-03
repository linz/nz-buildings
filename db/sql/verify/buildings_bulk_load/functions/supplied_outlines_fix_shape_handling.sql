-- Verify nz-buildings:buildings_bulk_load/functions/supplied_outlines_fix_shape_handling on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.supplied_outlines_insert(integer, integer, geometry)', 'execute');

ROLLBACK;
