-- Deploy nz-buildings:buildings/remove_building_outlines_ta_not_null_constraint to pg

BEGIN;

ALTER TABLE buildings.building_outlines
ALTER COLUMN territorial_authority_id DROP NOT NULL;

COMMIT;
