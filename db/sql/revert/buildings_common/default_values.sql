-- Revert buildings:buildings_common/default_values from pg

BEGIN;

TRUNCATE buildings_common.capture_method CASCADE;

TRUNCATE buildings_common.capture_source_group CASCADE;

COMMIT;
