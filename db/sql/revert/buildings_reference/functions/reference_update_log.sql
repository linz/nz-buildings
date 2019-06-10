-- Revert nz-buildings:buildings_reference/functions/reference_update_log from pg

BEGIN;

DROP FUNCTION buildings_reference.reference_update_log_insert_log(varchar[]);

COMMIT;
