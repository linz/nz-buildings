------------------------------------------------------------------------------
-- Create buildings admin_bdys schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS admin_bdys;

-- nz_locality

CREATE TABLE IF NOT EXISTS admin_bdys.nz_locality (
    id integer NOT NULL,
    parent_id numeric(10,0),
    suburb_4th character varying(60),
    suburb_3rd character varying(60),
    suburb_2nd character varying(60),
    suburb_1st character varying(60),
    type_order numeric(10,0),
    type character varying(12),
    city_id numeric(10,0),
    city_name character varying(60),
    has_addres character varying(1),
    start_date date,
    end_date date,
    major_id numeric(10,0),
    major_name character varying(80),
    shape public.geometry(MultiPolygon,4167)
);

ALTER TABLE ONLY admin_bdys.nz_locality
    ADD CONSTRAINT nz_locality_pkey PRIMARY KEY (id);


-- territorial_authority

CREATE TABLE IF NOT EXISTS admin_bdys.territorial_authority (
    ogc_fid integer NOT NULL,
    shape public.geometry(MultiPolygon,4167),
    name character varying(100)
);

ALTER TABLE ONLY admin_bdys.territorial_authority
    ADD CONSTRAINT territorial_authority_pkey2 PRIMARY KEY (ogc_fid);