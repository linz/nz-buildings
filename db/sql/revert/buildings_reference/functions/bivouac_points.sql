-- Revert nz-buildings:buildings_reference/functions/bivouac_points from pg

BEGIN;

DROP FUNCTION buildings_reference.bivouac_points_delete_by_external_id(integer);

DROP FUNCTION buildings_reference.bivouac_points_insert(integer, varchar);

DROP FUNCTION buildings_reference.bivouac_points_update_shape_by_external_id(integer, varchar);

COMMIT;
