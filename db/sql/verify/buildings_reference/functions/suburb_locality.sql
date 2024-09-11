-- Verify nz-buildings:buildings_reference/functions/suburb_locality on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.suburb_locality_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_delete_by_external_id(integer)', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_insert(integer, varchar, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_update_by_external_id(integer, varchar, varchar, varchar)', 'execute');

SELECT has_function_privilege('buildings_reference.suburb_locality_update_building_outlines(integer[], integer[])', 'execute');

ROLLBACK;
