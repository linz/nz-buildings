-- Revert nz-buildings:buildings_bulk_load/functions/remove_small_tanks from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_tanks(integer);

COMMIT;
