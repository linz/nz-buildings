-- Verify nz-buildings:buildings_lds/functions/populate_buildings_lds on pg

BEGIN;

SELECT has_function_privilege('buildings_lds.nz_building_outlines_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.nz_building_outlines_all_sources_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.nz_building_outlines_lifecycle_insert()', 'execute');

SELECT has_function_privilege('buildings_lds.populate_buildings_lds()', 'execute');

ROLLBACK;
