-- Revert nz-buildings:buildings/remove_building_outlines_ta_not_null_constraint from pg

BEGIN;

ALTER TABLE buildings.building_outlines
ALTER COLUMN territorial_authority_id SET NOT NULL;

COMMIT;
