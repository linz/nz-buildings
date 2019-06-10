-- Revert nz-buildings:buildings_reference/functions/territorial_authority from pg

BEGIN;

DROP FUNCTION buildings_reference.territorial_authority_grid_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.territorial_authority_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.territorial_auth_delete_areas();

DROP FUNCTION buildings_reference.territorial_auth_insert_areas();

DROP FUNCTION buildings_reference.territorial_auth_update_areas();

COMMIT;
