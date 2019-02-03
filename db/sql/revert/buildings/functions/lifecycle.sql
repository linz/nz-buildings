-- Revert buildings:buildings/functions/lifecycle from pg

BEGIN;

DROP FUNCTION buildings.lifecycle_add_record(integer, integer);

COMMIT;
