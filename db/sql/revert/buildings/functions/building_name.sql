-- Revert buildings:buildings/functions/building_name from pg

BEGIN;

DROP FUNCTION buildings.building_name_update_end_lifespan(integer[]);

COMMIT;
