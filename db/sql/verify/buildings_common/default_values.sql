-- Verify nz-buildings:buildings_common/default_values on pg

BEGIN;

SELECT 1/count(*)
FROM buildings_common.capture_method;

SELECT 1/count(*)
FROM buildings_common.capture_source_group;

ROLLBACK;
