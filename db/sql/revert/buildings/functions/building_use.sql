-- Revert nz-buildings:buildings/functions/building_use from pg

BEGIN;

DROP FUNCTION buildings.building_use_update_end_lifespan(integer[]);

COMMIT;
