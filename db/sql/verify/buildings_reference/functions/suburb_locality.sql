-- Verify buildings:buildings_reference/functions/suburb_locality on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.suburb_locality_intersect_polygon(geometry)', 'execute');

SELECT has_function_privilege('buildings_reference.bulk_load_outlines_update_suburb(integer)', 'execute');

ROLLBACK;
