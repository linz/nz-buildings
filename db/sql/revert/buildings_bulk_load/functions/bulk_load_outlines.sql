-- Revert buildings:buildings_bulk_load/functions/bulk_load_outlines from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_insert(integer, integer, integer, integer, integer, integer, integer, integer, geometry);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_insert_supplied(integer, integer, integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_attributes(integer, integer, integer, integer, integer, integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_capture_method(integer, integer);

DROP FUNCTION buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer);

COMMIT;
