-- Revert buildings:buildings_bulk_load/functions/organisation from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.organisation_insert(varchar(250));

COMMIT;
