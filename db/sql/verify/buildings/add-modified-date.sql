-- Verify nz-buildings:buildings/add-modified-date on pg

BEGIN;

SELECT
      last_modified
FROM buildings.building_outlines
WHERE FALSE;

ROLLBACK;
