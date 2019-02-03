-- Revert buildings:buildings_common/functions/capture_source_group from pg

BEGIN;

DROP FUNCTION buildings_common.capture_source_group_insert(varchar(80), varchar(400));

COMMIT;
