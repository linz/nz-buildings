-- Verify buildings:buildings_bulk_load/functions/bulk_load_outlines on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_insert(integer, integer, integer, integer, integer, integer, integer, integer, geometry)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_insert_supplied(integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_capture_method(integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer)', 'execute');

ROLLBACK;
