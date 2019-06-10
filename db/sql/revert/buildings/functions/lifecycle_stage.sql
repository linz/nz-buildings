-- Revert nz-buildings:buildings/functions/lifecycle_stage from pg

BEGIN;

DROP FUNCTION buildings.lifecycle_stage_insert(varchar(40));

COMMIT;
