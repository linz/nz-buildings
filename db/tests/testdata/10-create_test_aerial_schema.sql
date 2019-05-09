SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS aerial_lds;

COMMENT ON SCHEMA aerial_lds IS
'This schema contains datasets related to aerial imagery to be published '
'on the LINZ Data Service.';

-- Imagery Surveys

CREATE TABLE IF NOT EXISTS aerial_lds.nz_imagery_surveys (
      imagery_survey_id serial PRIMARY KEY
    , name character varying(100) NOT NULL
    , imagery_id integer
    , index_id integer
    , set_order integer
    , ground_sample_distance numeric(6,4)
    , accuracy character varying(100)
    , supplier character varying(80)
    , licensor character varying(250)
    , flown_from date CONSTRAINT after_first_flight CHECK (flown_from > '1903-12-17')
    , flown_to date CONSTRAINT survey_completed CHECK (flown_to < now())
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
    , CONSTRAINT valid_flight_dates CHECK (flown_from <= flown_to)
);

INSERT INTO aerial_lds.nz_imagery_surveys(imagery_survey_id , name, flown_from, flown_to, shape)
VALUES (1, 'Imagery One', '2016-01-01', '2016-02-01', '0106000020910800000100000001030000000100000005000000652E991C93A73C411D143F0A863155419BAA7B1333AA3C411D1A1C7F863155419BC2EFE634AA3C411A459E65DA30554165460DF094A73C411A4B7BDADA305541652E991C93A73C411D143F0A86315541'),
       (2, 'Imagery Two', '2017-01-01', '2017-02-01',  '010600002091080000010000000103000000010000000500000025FC5C6832AA3C41FCB6751C8631554125FC5C6832AA3C41E86F6C4BDA305541E3B2A05848AB3C41E86F6C4BDA305541E3B2A05848AB3C41E191179B8531554125FC5C6832AA3C41FCB6751C86315541');
