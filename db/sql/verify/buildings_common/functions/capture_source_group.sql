-- Verify buildings:buildings_common/functions/capture_source_group on pg

BEGIN;

SELECT has_function_privilege('buildings_common.capture_source_group_insert(varchar(80), varchar(400))', 'execute');

ROLLBACK;
