-- Revert buildings:buildings_bulk_load/functions/deletion_description from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.delete_deleted_description(integer);

DROP FUNCTION buildings_bulk_load.deletion_description_insert(integer, varchar(250));

COMMIT;
