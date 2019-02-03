-- Verify buildings:buildings/functions/buildings on pg

BEGIN;

SELECT has_function_privilege('buildings.buildings_insert()', 'execute');

SELECT has_function_privilege('buildings.buildings_update_end_lifespan(integer[])', 'execute');

ROLLBACK;
