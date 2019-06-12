-- Revert nz-buildings:buildings/functions/building_outlines from pg

BEGIN;

DROP FUNCTION buildings.building_outlines_insert(integer, integer, integer, integer, integer, integer, integer, geometry);

DROP FUNCTION buildings.building_outlines_insert_bulk(integer, integer);

DROP FUNCTION buildings.building_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer);

DROP FUNCTION buildings.building_outlines_update_capture_method(integer, integer);

DROP FUNCTION buildings.building_outlines_update_end_lifespan(integer[]);

DROP FUNCTION buildings.building_outlines_update_shape(geometry, integer);

DROP FUNCTION buildings.building_outlines_update_suburb(integer[]);

DROP FUNCTION buildings.building_outlines_update_territorial_authority(integer[]);

DROP FUNCTION buildings.building_outlines_update_town_city(integer[]);

COMMIT;
