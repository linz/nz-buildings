-- Verify nz-buildings:buildings_bulk_load/add_name_and_use_columns on pg

BEGIN;

SELECT bulk_load_use_id,
bulk_load_name
FROM buildings_bulk_load.bulk_load_outlines

WHERE FALSE;

ROLLBACK;
