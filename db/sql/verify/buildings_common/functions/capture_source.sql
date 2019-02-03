-- Verify buildings:buildings_common/functions/capture_source on pg

BEGIN;

SELECT has_function_privilege('buildings_common.capture_source_insert(integer, varchar(250))', 'execute');

ROLLBACK;
