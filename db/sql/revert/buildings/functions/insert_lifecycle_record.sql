-- Revert nz-buildings:buildings/functions/insert_lifecycle_record from pg

BEGIN;

DROP FUNCTION buildings.lifecycle_insert_record(integer, integer);

COMMIT;
