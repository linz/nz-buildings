-- Deploy nz-buildings:buildings_reference/update_suburb_locality_name_column to pg

BEGIN;

ALTER TABLE buildings_reference.suburb_locality
ADD COLUMN suburb_locality varchar(100),
ADD COLUMN town_city varchar(100);

-- update data for new column suburb_locality
UPDATE buildings_reference.suburb_locality
SET suburb_locality = COALESCE(suburb_4th, suburb_3rd, suburb_2nd, suburb_1st);

ALTER TABLE buildings_reference.suburb_locality
ALTER COLUMN suburb_locality SET NOT NULL;

-- update data for new column town_city
UPDATE buildings_reference.suburb_locality
SET town_city = town_city.name
FROM buildings_reference.town_city
WHERE ST_Within(suburb_locality.shape, ST_Buffer(town_city.shape, 1));

COMMIT;
