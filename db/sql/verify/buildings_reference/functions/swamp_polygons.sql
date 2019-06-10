-- Verify nz-buildings:buildings_reference/functions/swamp_polygons on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.swamp_polygons_delete_by_external_id(integer)', 'execute');

SELECT has_function_privilege('buildings_reference.swamp_polygons_insert(integer, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.swamp_polygons_update_shape_by_external_id(integer, varchar)', 'execute');

ROLLBACK;
