-- Revert nz-buildings:buildings_lds/functions/populate_buildings_lds from pg

BEGIN;

DROP FUNCTION buildings_lds.nz_building_outlines_insert();

DROP FUNCTION buildings_lds.nz_building_outlines_all_sources_insert();

DROP FUNCTION buildings_lds.nz_building_outlines_lifecycle_insert();

DROP FUNCTION buildings_lds.populate_buildings_lds();

COMMIT;
