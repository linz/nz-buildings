-- Revert nz-buildings:buildings_common/functions/capture_method from pg

BEGIN;

DROP FUNCTION buildings_common.capture_method_insert(varchar(250));

COMMIT;
