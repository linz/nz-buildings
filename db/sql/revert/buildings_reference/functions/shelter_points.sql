-- Revert nz-buildings:buildings_reference/functions/shelter_points from pg

BEGIN;

DROP FUNCTION buildings_reference.shelter_points_delete_by_external_id(integer);

DROP FUNCTION buildings_reference.shelter_points_insert(integer, varchar);

DROP FUNCTION buildings_reference.shelter_points_update_shape_by_external_id(integer, varchar);

COMMIT;
