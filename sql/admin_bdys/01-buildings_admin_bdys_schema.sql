------------------------------------------------------------------------------
-- Create buildings admin_bdys schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_admin_bdys;

-- Suburb / Locality

CREATE TABLE IF NOT EXISTS buildings_admin_bdys.suburb_locality (
      suburb_locality_id serial PRIMARY KEY
    , external_suburb_locality_id integer
    , suburb_4th character varying(60)
    , suburb_3rd character varying(60)
    , suburb_2nd character varying(60)
    , suburb_1st character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);

-- Town / City

CREATE TABLE IF NOT EXISTS buildings_admin_bdys.town_city (
      town_city_id serial PRIMARY KEY
    , external_city_id integer
    , name character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);

-- Territorial Authority

CREATE TABLE IF NOT EXISTS buildings_admin_bdys.territorial_authority (
      territorial_authority_id serial PRIMARY KEY
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);
