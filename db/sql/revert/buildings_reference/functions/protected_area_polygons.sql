-- Revert nz-buildings:buildings_reference/functions/protected_area_polygons from pg

BEGIN;

DROP FUNCTION buildings_reference.protected_areas_polygons_delete_by_external_id(integer);

DROP FUNCTION buildings_reference.protected_areas_polygons_insert(integer, varchar);

DROP FUNCTION buildings_reference.protected_areas_polygons_update_shape_by_external_id(integer, varchar);

COMMIT;
