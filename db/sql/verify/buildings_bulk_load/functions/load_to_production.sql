-- Verify buildings:buildings_bulk_load/functions/load_to_production on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.load_building_outlines(integer)', 'execute');

ROLLBACK;
