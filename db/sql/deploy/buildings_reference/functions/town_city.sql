-- Deploy nz-buildings:buildings_reference/functions/town_city to pg

BEGIN;

DROP FUNCTION IF EXISTS buildings_reference.town_city_intersect_polygon(geometry);
DROP FUNCTION IF EXISTS buildings_reference.town_city_delete_removed_areas();
DROP FUNCTION IF EXISTS buildings_reference.town_city_insert_new_areas();
DROP FUNCTION IF EXISTS buildings_reference.town_city_update_areas();

COMMIT;
