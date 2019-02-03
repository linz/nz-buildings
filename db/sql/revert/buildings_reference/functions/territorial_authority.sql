-- Revert buildings:buildings_reference/functions/territorial_authority from pg

BEGIN;

DROP FUNCTION buildings_reference.territorial_authority_grid_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.territorial_authority_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.bulk_load_outlines_update_territorial_authority(integer);

COMMIT;
