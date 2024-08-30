-- Revert nz-buildings:buildings_reference/drop_town_city_table from pg

BEGIN;

CREATE TABLE IF NOT EXISTS buildings_reference.town_city (
      town_city_id serial PRIMARY KEY
    , external_city_id integer
    , name character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);

CREATE INDEX shx_town_city
    ON buildings_reference.town_city USING gist (shape);

COMMENT ON TABLE buildings_reference.town_city IS
'towns/cities of New Zealand';

COMMENT ON COLUMN buildings_reference.town_city.town_city_id IS
'Unique identifier for town_city.';
COMMENT ON COLUMN buildings_reference.town_city.external_city_id IS
'The id given by the external source.';
COMMENT ON COLUMN buildings_reference.town_city.name IS
'The name of the town/city.';

ALTER TABLE buildings_reference.reference_update_log
ADD COLUMN town_city boolean;

COMMIT;
