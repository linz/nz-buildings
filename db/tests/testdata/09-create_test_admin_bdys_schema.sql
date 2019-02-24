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

-- Insert Data

INSERT INTO admin_bdys.nz_locality(id, parent_id, suburb_4th, suburb_3rd, suburb_2nd, suburb_1st, type_order, type, city_id, city_name, has_addressroad, start_date, end_date, majorlocality_id, majorlocality_name, shape)
VALUES (101, 0, 'Kelburn North', NULL, NULL, NULL, 0, 'SUBURB', 1001, 'Wellington', 'Y', now(), NULL, 1001, 'Wellington', '0106000020471000000100000001030000000100000005000000F8667C865B0866405737D808350D44C00CC875098D0866404D1F72CA2E0D44C06223B9B28E086640E47221909C0D44C08A9CA5145D086640B565D732A00D44C0F8667C865B0866405737D808350D44C0'),
       (102, 0, 'Aro Valley', NULL, NULL, NULL, 0, 'SUBURB', 1001, 'Wellington', 'Y', now(), NULL, 1001, 'Wellington', '01060000204710000001000000010300000001000000050000008A9CA5145D086640B565D732A00D44C087B846FD70086640CB1EB8BD9E0D44C0D6888AC17108664030276043DA0D44C0930247F25D086640912DC3D7DB0D44C08A9CA5145D086640B565D732A00D44C0'),
       (103, 0, 'Newtown', NULL, NULL, NULL, 0, 'SUBURB', 1001, 'Wellington', 'Y', now(), NULL, 1001, 'Wellington', '010600002047100000010000000103000000010000000500000087B846FD70086640CB1EB8BD9E0D44C06223B9B28E086640E47221909C0D44C0EBBE8C988F08664030056FE1D70D44C0D6888AC17108664030276043DA0D44C087B846FD70086640CB1EB8BD9E0D44C0'),
       (105, 0, 'Napier Airport', NULL, NULL, NULL, 0, 'SUBURB', 1003, 'Napier', 'Y', now(), NULL, 1003, 'Napier', '0106000020471000000100000001030000000100000005000000930247F25D086640912DC3D7DB0D44C0EBBE8C988F08664030056FE1D70D44C0C9B675D28F086640A81D6808EB0D44C0B5A8841D5E0866406B4D92A4F00D44C0930247F25D086640912DC3D7DB0D44C0');
