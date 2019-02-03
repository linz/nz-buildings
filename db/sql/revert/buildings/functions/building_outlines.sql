-- Revert buildings:buildings/functions/building_outlines from pg

BEGIN;

DROP FUNCTION buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, integer, timestamp, geometry);

DROP FUNCTION buildings.building_outlines_insert_bulk(integer, integer);

DROP FUNCTION buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer);

DROP FUNCTION buildings.building_outlines_update_capture_method(integer, integer);

DROP FUNCTION buildings.building_outlines_update_end_lifespan(integer[]);

DROP FUNCTION buildings.building_outlines_update_shape(geometry, integer);

COMMIT;
