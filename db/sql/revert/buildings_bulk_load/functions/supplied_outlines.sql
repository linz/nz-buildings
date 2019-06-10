-- Revert nz-buildings:buildings_bulk_load/functions/supplied_outlines from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.supplied_outlines_insert(integer, integer, geometry);

COMMIT;
