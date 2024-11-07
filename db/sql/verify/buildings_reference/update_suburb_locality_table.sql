-- Verify nz-buildings:buildings_reference/update_suburb_locality_name_column on pg

BEGIN;

SELECT suburb_locality, town_city
FROM buildings_reference.suburb_locality
WHERE FALSE;

ROLLBACK;
