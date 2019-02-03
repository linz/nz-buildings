-- Revert buildings:buildings_common/functions/capture_source from pg

BEGIN;

DROP FUNCTION buildings_common.capture_source_insert(integer, varchar(250));

COMMIT;
