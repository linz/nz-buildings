------------------------------------------------------------------------------
-- Create buildings schema and tables
------------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS buildings;

-- LOOKUP TABLES

-- Capture Method

CREATE TABLE IF NOT EXISTS buildings.capture_method (
      capture_method_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Capture Source Group

CREATE TABLE IF NOT EXISTS buildings.capture_source_group (
      capture_source_group_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Lifecycle Stage

CREATE TABLE IF NOT EXISTS buildings.lifecycle_stage (
      lifecycle_stage_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Use

CREATE TABLE IF NOT EXISTS buildings.use (
      use_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- DATA TABLES

-- Capture Source

CREATE TABLE IF NOT EXISTS buildings.capture_source (
      capture_source_id serial PRIMARY KEY
    , capture_source_group_id integer NOT NULL REFERENCES buildings.capture_source_group (capture_source_group_id)
    , external_source_id character varying(250)
);

DROP INDEX IF EXISTS idx_capture_source_capture_source_group_id;
CREATE INDEX idx_capture_source_capture_source_group_id
    ON buildings.capture_source USING btree (capture_source_group_id);

-- Building

CREATE TABLE IF NOT EXISTS buildings.buildings (
      building_id serial PRIMARY KEY
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , end_lifespan timestamptz
);

SELECT setval('buildings.buildings_building_id_seq', coalesce((SELECT max(building_id) + 1 FROM buildings.buildings), 1000000), false);

-- Building Outlines

CREATE TABLE IF NOT EXISTS buildings.building_outlines (
      building_outline_id serial PRIMARY KEY
    , building_id integer NOT NULL REFERENCES buildings.buildings (building_id)
    , capture_method_id integer NOT NULL REFERENCES buildings.capture_method (capture_method_id)
    , capture_source_id integer NOT NULL REFERENCES buildings.capture_source (capture_source_id)
    , lifecycle_stage_id integer NOT NULL REFERENCES buildings.lifecycle_stage (lifecycle_stage_id)
    , suburb_locality character varying(80) NOT NULL DEFAULT ''
    , town_city character varying(80) NOT NULL DEFAULT ''
    , territorial_authority character varying(80) NOT NULL DEFAULT ''
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , end_lifespan timestamptz
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

SELECT setval('buildings.building_outlines_building_outline_id_seq', coalesce((SELECT max(building_outline_id) + 1 FROM buildings.building_outlines), 1000000), false);

DROP INDEX IF EXISTS idx_building_outlines_building_id;
CREATE INDEX idx_building_outlines_building_id
    ON buildings.building_outlines USING btree (building_id);

DROP INDEX IF EXISTS idx_building_outlines_capture_method_id;
CREATE INDEX idx_building_outlines_capture_method_id
    ON buildings.building_outlines USING btree (capture_method_id);

DROP INDEX IF EXISTS idx_building_outlines_capture_source_id;
CREATE INDEX idx_building_outlines_capture_source_id
    ON buildings.building_outlines USING btree (capture_source_id);

DROP INDEX IF EXISTS idx_building_outlines_lifecycle_stage_id;
CREATE INDEX idx_building_outlines_lifecycle_stage_id
    ON buildings.building_outlines USING btree (lifecycle_stage_id);

DROP INDEX IF EXISTS shx_building_outlines;
CREATE INDEX shx_building_outlines
    ON buildings.building_outlines USING gist (shape);

-- Building Name

CREATE TABLE IF NOT EXISTS buildings.building_name (
      building_name_id serial PRIMARY KEY
    , building_id integer NOT NULL REFERENCES buildings.buildings (building_id)
    , building_name character varying(250) NOT NULL DEFAULT ''
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , end_lifespan timestamptz
);

SELECT setval('buildings.building_name_building_name_id_seq', coalesce((SELECT max(building_name_id) + 1 FROM buildings.building_name), 1000000), false);

DROP INDEX IF EXISTS idx_building_name_building_id;
CREATE INDEX idx_building_name_building_id
    ON buildings.building_name USING btree (building_id);

-- Building Use

CREATE TABLE IF NOT EXISTS buildings.building_use (
      building_use_id serial PRIMARY KEY
    , building_id integer NOT NULL REFERENCES buildings.buildings (building_id)
    , use_id integer NOT NULL REFERENCES buildings.use (use_id)
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , end_lifespan timestamptz
);

SELECT setval('buildings.building_use_building_use_id_seq', coalesce((SELECT max(building_use_id) + 1 FROM buildings.building_use), 1000000), false);

DROP INDEX IF EXISTS idx_building_use_building_id;
CREATE INDEX idx_building_use_building_id
    ON buildings.building_use USING btree (building_id);

DROP INDEX IF EXISTS idx_building_use_use_id;
CREATE INDEX idx_building_use_use_id
    ON buildings.building_use USING btree (use_id);

-- Lifecycle

CREATE TABLE IF NOT EXISTS buildings.lifecycle (
      lifecycle_id serial PRIMARY KEY
    , parent_building_outline_id integer NOT NULL REFERENCES buildings.building_outlines (building_outline_id)
    , building_outline_id integer REFERENCES buildings.building_outlines (building_outline_id)
);

SELECT setval('buildings.lifecycle_lifecycle_id_seq', coalesce((SELECT max(lifecycle_id) + 1 FROM buildings.lifecycle), 1000000), false);

DROP INDEX IF EXISTS idx_lifecycle_parent_building_outline_id;
CREATE INDEX idx_lifecycle_parent_building_outline_id
    ON buildings.lifecycle USING btree (parent_building_outline_id);

DROP INDEX IF EXISTS idx_lifecycle_building_outline_id;
CREATE INDEX idx_lifecycle_building_outline_id
    ON buildings.lifecycle USING btree (building_outline_id);
