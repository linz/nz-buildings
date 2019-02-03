-- Verify buildings:buildings_bulk_load/functions/supplied_outlines on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.supplied_outlines_insert(integer, integer, geometry)', 'execute');

ROLLBACK;
