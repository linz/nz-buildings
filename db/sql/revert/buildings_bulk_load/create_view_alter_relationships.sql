-- Revert nz-buildings:buildings_bulk_load/create_view_alter_relationships from pg

BEGIN;

DROP VIEW buildings_bulk_load.added_outlines;

DROP VIEW buildings_bulk_load.removed_outlines;

DROP VIEW buildings_bulk_load.matched_bulk_load_outlines;

DROP VIEW buildings_bulk_load.related_bulk_load_outlines;

DROP VIEW buildings_bulk_load.matched_existing_outlines;

DROP VIEW buildings_bulk_load.related_existing_outlines;

COMMIT;
