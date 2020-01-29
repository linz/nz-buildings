-- Revert nz-buildings:buildings_reference/functions/suburb_locality from pg

BEGIN;

DROP FUNCTION buildings_reference.suburb_locality_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.suburb_locality_delete_removed_areas();

DROP FUNCTION buildings_reference.suburb_locality_insert_new_areas();

DROP FUNCTION buildings_reference.suburb_locality_update_suburb_locality();

COMMIT;
