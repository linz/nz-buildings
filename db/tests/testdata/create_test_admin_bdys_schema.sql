SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS admin_bdys;

COMMENT ON SCHEMA admin_bdys IS
'Schema that holds test data similar to that used in production.';

-- Suburb_Locality & Town_City

CREATE TABLE IF NOT EXISTS admin_bdys.nz_locality (
    id integer NOT NULL PRIMARY KEY,
    parent_id integer,
    suburb_4th varchar(60),
    suburb_3rd varchar(60),
    suburb_2nd varchar(60),
    suburb_1st varchar(60),
    type_order integer,
    type varchar(12),
    city_id integer,
    city_name varchar(60),
    has_addressroad varchar(10),
    start_date timestamp,
    end_date timestamp,
    majorlocality_id integer,
    majorlocality_name varchar(80),
    shape public.geometry(MultiPolygon, 4167)
);

-- territorial_authority

CREATE TABLE IF NOT EXISTS admin_bdys.territorial_authority (
    ogc_fid integer NOT NULL PRIMARY KEY,
    name varchar(100),
    shape public.geometry(MultiPolygon, 4167)
);
