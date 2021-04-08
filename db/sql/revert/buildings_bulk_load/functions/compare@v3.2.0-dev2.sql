-- Revert nz-buildings:buildings_bulk_load/functions/compare from pg

BEGIN;

DROP FUNCTION buildings_bulk_load.find_added(integer);

DROP FUNCTION buildings_bulk_load.find_removed(integer);

DROP FUNCTION buildings_bulk_load.find_matched(integer);

DROP FUNCTION buildings_bulk_load.find_related(integer);

DROP FUNCTION buildings_bulk_load.reassign_related_ids(integer);

DROP FUNCTION buildings_bulk_load.compare_building_outlines(integer);

COMMIT;
