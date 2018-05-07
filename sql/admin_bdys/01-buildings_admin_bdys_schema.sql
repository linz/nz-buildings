------------------------------------------------------------------------------
-- Create buildings admin_bdys schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_admin_bdys;

-- NZ Locality

CREATE TABLE IF NOT EXISTS buildings_admin_bdys.nz_locality (
      id integer NOT NULL PRIMARY KEY
    , parent_id numeric(10,0)
    , suburb_4th character varying(60)
    , suburb_3rd character varying(60)
    , suburb_2nd character varying(60)
    , suburb_1st character varying(60)
    , type_order numeric(10,0)
    , type character varying(12)
    , city_id numeric(10,0)
    , city_name character varying(60)
    , has_addres character varying(1)
    , start_date date
    , end_date date
    , major_id numeric(10,0)
    , major_name character varying(80)
    , shape public.geometry(MultiPolygon,4167)
);

-- Territorial Authority

CREATE TABLE IF NOT EXISTS buildings_admin_bdys.territorial_authority (
      ogc_fid integer NOT NULL PRIMARY KEY
    , shape public.geometry(MultiPolygon,4167)
    , name character varying(100)
);
