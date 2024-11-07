-- Revert nz-buildings:buildings_reference/functions/town_city from pg

BEGIN;

DROP FUNCTION buildings_reference.town_city_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.town_city_delete_removed_areas();

DROP FUNCTION buildings_reference.town_city_insert_new_areas();

DROP FUNCTION buildings_reference.town_city_update_areas();

COMMIT;
