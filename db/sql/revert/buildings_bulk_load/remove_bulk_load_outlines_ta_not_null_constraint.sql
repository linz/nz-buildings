-- Revert nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_ta_not_null_constraint from pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
ALTER COLUMN territorial_authority_id SET NOT NULL;

COMMIT;
