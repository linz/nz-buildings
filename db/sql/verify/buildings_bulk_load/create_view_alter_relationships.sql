-- Verify nz-buildings:buildings_bulk_load/create_view_alter_relationships on pg

BEGIN;

SELECT
      bulk_load_outline_id
    , shape
FROM buildings_bulk_load.added_outlines
WHERE FALSE;

SELECT
      building_outline_id
    , shape
FROM buildings_bulk_load.removed_outlines
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , shape
FROM buildings_bulk_load.matched_bulk_load_outlines
WHERE FALSE;

SELECT
      bulk_load_outline_id
    , shape
FROM buildings_bulk_load.related_bulk_load_outlines
WHERE FALSE;

SELECT
      building_outline_id
    , shape
FROM buildings_bulk_load.matched_existing_outlines
WHERE FALSE;

SELECT
      building_outline_id
    , shape
FROM buildings_bulk_load.related_existing_outlines
WHERE FALSE;

ROLLBACK;
