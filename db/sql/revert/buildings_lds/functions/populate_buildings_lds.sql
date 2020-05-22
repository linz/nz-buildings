-- Revert nz-buildings:buildings_lds/functions/populate_buildings_lds from pg

BEGIN;

DROP FUNCTION buildings_lds.populate_buildings_lds(integer);

COMMIT;
