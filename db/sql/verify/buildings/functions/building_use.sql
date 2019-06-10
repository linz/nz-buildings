-- Verify nz-buildings:buildings/functions/building_use on pg

BEGIN;

SELECT has_function_privilege('buildings.building_use_update_end_lifespan(integer[])', 'execute');

ROLLBACK;
