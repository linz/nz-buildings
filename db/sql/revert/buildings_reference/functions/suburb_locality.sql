-- Revert buildings:buildings_reference/functions/suburb_locality from pg

BEGIN;

DROP FUNCTION buildings_reference.suburb_locality_intersect_polygon(geometry);

DROP FUNCTION buildings_reference.bulk_load_outlines_update_suburb(integer);

COMMIT;
