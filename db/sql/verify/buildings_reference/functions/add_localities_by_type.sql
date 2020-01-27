-- Verify nz-buildings:buildings_reference/functions/add_localities_by_type on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.suburb_locality_insert_new_areas()', 'execute');

ROLLBACK;

