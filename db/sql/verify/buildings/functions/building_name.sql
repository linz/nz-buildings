-- Verify buildings:buildings/functions/building_name on pg

BEGIN;

SELECT has_function_privilege('buildings.building_name_update_end_lifespan(integer[])', 'execute');

ROLLBACK;
