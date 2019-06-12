-- Verify nz-buildings:buildings/functions/building_outlines on pg

BEGIN;

SELECT has_function_privilege('buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, integer, geometry)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_insert_bulk(integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_capture_method(integer, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_end_lifespan(integer[])', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_shape(geometry, integer)', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_suburb(integer[])', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_territorial_authority(integer[])', 'execute');

SELECT has_function_privilege('buildings.building_outlines_update_town_city(integer[])', 'execute');

ROLLBACK;
