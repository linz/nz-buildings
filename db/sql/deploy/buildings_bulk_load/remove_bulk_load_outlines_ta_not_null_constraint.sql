-- Deploy nz-buildings:buildings_bulk_load/remove_bulk_load_outlines_ta_not_null_constraint to pg

BEGIN;

ALTER TABLE buildings_bulk_load.bulk_load_outlines
ALTER COLUMN territorial_authority_id DROP NOT NULL;

COMMIT;
