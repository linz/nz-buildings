-- Verify nz-buildings:buildings_reference/functions/change_reference_name_col_insert on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.bivouac_points_insert(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.bivouac_points_update_by_external_id(integer, varchar, varchar)', 'execute');


SELECT has_function_privilege('buildings_reference.hut_points_insert(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.hut_points_update_by_external_id(integer, varchar, varchar)', 'execute');


SELECT has_function_privilege('buildings_reference.protected_areas_polygons_insert(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.protected_areas_polygons_update_by_external_id(integer, varchar, varchar)', 'execute');


SELECT has_function_privilege('buildings_reference.shelter_points_insert(integer, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.shelter_points_update_by_external_id(integer, varchar, varchar)', 'execute');


ROLLBACK;
