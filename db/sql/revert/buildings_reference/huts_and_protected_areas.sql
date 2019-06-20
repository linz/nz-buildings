-- Revert nz-buildings:buildings_reference/huts_and_protected_areas from pg

BEGIN;

-- Drop columns from building_reference_log.

ALTER TABLE buildings_reference.reference_update_log DROP protected_areas;
ALTER TABLE buildings_reference.reference_update_log DROP bivouacs;
ALTER TABLE buildings_reference.reference_update_log DROP shelters;
ALTER TABLE buildings_reference.reference_update_log DROP huts;

-- Drop huts, shelters, bivouacs and protected areas tables

DROP TABLE buildings_reference.protected_areas CASCADE;
DROP TABLE buildings_reference.bivouac_points CASCADE;
DROP TABLE buildings_reference.shelter_points CASCADE;
DROP TABLE buildings_reference.hut_points CASCADE;

COMMIT;
