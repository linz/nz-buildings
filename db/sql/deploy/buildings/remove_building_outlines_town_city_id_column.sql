-- Deploy nz-buildings:buildings/remove_building_outlines_town_city_id_column to pg

BEGIN;

ALTER TABLE buildings.building_outlines
DROP COLUMN town_city_id;

COMMIT;
