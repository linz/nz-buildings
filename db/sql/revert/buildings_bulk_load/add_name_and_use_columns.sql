-- Revert nz-buildings:buildings_bulk_load/add_name_and_use_columns from pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
DROP COLUMN IF EXISTS bulk_load_use_id CASCADE;
ALTER TABLE buildings_bulk_load.bulk_load_outlines
DROP COLUMN IF EXISTS bulk_load_name CASCADE;

COMMIT;
