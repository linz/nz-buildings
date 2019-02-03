-- Revert buildings:buildings/functions/buildings from pg

BEGIN;

DROP FUNCTION buildings.buildings_insert();

DROP FUNCTION buildings.buildings_update_end_lifespan(integer[]);

COMMIT;
