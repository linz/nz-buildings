-- Verify nz-buildings:buildings_reference/update_suburb_locality_name_column on pg

BEGIN;

SELECT name
FROM buildings_reference.suburb_locality
WHERE FALSE;

ROLLBACK;
