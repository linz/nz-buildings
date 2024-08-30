-- Revert nz-buildings:buildings/remove_building_outlines_town_city_id_column from pg

BEGIN;

ALTER TABLE buildings.building_outlines
ADD COLUMN town_city_id integer;

COMMIT;
