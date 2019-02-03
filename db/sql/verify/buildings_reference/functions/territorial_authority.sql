-- Verify buildings:buildings_reference/functions/territorial_authority on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.territorial_authority_grid_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.territorial_authority_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.bulk_load_outlines_update_territorial_authority(integer)', 'execute');

ROLLBACK;
