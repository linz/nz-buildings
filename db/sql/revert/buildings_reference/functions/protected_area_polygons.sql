-- Revert nz-buildings:buildings_reference/functions/protected_area_polygons from pg

BEGIN;

DROP FUNCTION buildings_reference.protected_areas_delete_by_external_id(integer);

DROP FUNCTION buildings_reference.protected_areas_insert(integer, varchar);

DROP FUNCTION buildings_reference.protected_areas_update_shape_by_external_id(integer, varchar);

COMMIT;
