-- Deploy nz-buildings:buildings_reference/functions/update_suburb_locality_changed_deleted_buildings to pg

BEGIN;

DROP FUNCTION IF EXISTS buildings_reference.building_outlines_update_changed_and_deleted_suburb();
DROP FUNCTION IF EXISTS buildings_reference.building_outlines_update_added_suburb();

COMMIT;
