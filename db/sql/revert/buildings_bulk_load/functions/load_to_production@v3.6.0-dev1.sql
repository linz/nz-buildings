-- Revert nz-buildings:buildings_bulk_load/functions/load_to_production from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.load_building_outlines(integer);

COMMIT;
