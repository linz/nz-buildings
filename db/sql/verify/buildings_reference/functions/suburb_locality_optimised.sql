-- Verify nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings on pg

BEGIN;

SELECT has_function_privilege('buildings_reference.building_outlines_update_changed_and_deleted_suburb()', 'execute');

SELECT has_function_privilege('buildings_reference.building_outlines_update_added_suburb()', 'execute');

ROLLBACK;
