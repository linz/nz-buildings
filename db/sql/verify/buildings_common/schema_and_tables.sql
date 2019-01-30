-- Verify buildings:buildings_common/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_common', 'usage');

SELECT
      capture_method_id
    , value
FROM buildings_common.capture_method
WHERE FALSE;

SELECT
      capture_source_group_id
    , value
    , description
FROM buildings_common.capture_source_group
WHERE FALSE;

SELECT
      capture_source_id
    , capture_source_group_id
    , external_source_id
FROM buildings_common.capture_source
WHERE FALSE;

ROLLBACK;
