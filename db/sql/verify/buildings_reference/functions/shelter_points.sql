-- Verify nz-buildings:buildings_reference/functions/shelter_points on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.shelter_points_delete_by_external_id(integer)', 'execute');

SELECT has_function_privilege('buildings_reference.shelter_points_insert(integer, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.shelter_points_update_shape_by_external_id(integer, varchar)', 'execute');

ROLLBACK;
