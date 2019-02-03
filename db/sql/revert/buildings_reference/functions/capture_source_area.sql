-- Revert buildings:buildings_reference/functions/capture_source_area from pg

BEGIN;

DROP FUNCTION buildings_reference.capture_source_area_insert(varchar(250), varchar(250), geometry);

COMMIT;
