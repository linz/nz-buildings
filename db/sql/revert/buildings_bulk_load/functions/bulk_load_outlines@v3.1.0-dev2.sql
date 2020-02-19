-- Revert nz-buildings:buildings_bulk_load/functions/bulk_load_outlines from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_insert(integer, integer, integer, integer, integer, integer, integer, integer, geometry);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_insert_supplied(integer, integer, integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_capture_method(integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_suburb(integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_suburbs(integer[]);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_territorial_authority(integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_territorial_authorities(integer[]);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_town_city(integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_all_town_cities(integer[]);

COMMIT;
