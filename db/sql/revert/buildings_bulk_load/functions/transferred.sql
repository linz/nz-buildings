-- Revert nz-buildings:buildings_bulk_load/functions/transferred from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.transferred_insert(integer, integer);

COMMIT;
