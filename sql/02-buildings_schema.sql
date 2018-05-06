------------------------------------------------------------------------------
-- Create buildings schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings;

COMMENT ON SCHEMA buildings IS
'Schema that holds production buildings data.';

-- LOOKUP TABLES

-- Lifecycle Stage

CREATE TABLE IF NOT EXISTS buildings.lifecycle_stage (
      lifecycle_stage_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings.lifecycle_stage IS
'Lookup table that holds all of the lifecycle stages for a building.';

COMMENT ON COLUMN buildings.lifecycle_stage.lifecycle_stage_id IS
'Unique identifier for the lifecycle stage.';
COMMENT ON COLUMN buildings.lifecycle_stage.value IS
'The stage of a buildings lifecycle.';

-- Use

CREATE TABLE IF NOT EXISTS buildings.use (
      use_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings.use IS
'Lookup table that holds all of the uses for a building. These uses are '
'the same as those used in the Topo50 map series.';

COMMENT ON COLUMN buildings.use.use_id IS
'Unique identifier for the use.';
COMMENT ON COLUMN buildings.use.value IS
'The building use, maintained for the Topo50 map series.';

-- DATA TABLES

-- Building

CREATE TABLE IF NOT EXISTS buildings.buildings (
      building_id serial PRIMARY KEY
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , end_lifespan timestamptz
);

SELECT setval('buildings.buildings_building_id_seq', coalesce((SELECT max(building_id) + 1 FROM buildings.buildings), 1000000), false);

COMMENT ON TABLE buildings.buildings IS
'The building table maintains a unique identifier for a building. Over time, '
'a building can be represented by multiple building outlines aligned to '
'different imagery sources. These building outlines are linked via the '
'building_id.';

COMMENT ON COLUMN buildings.buildings.building_id IS
'Unique identifier for the building.';
COMMENT ON COLUMN buildings.buildings.begin_lifespan IS
'The date that the building was first captured in the system.';
COMMENT ON COLUMN buildings.buildings.end_lifespan IS
'The date that a building was either replaced or disused.';

-- Building Outlines

CREATE TABLE IF NOT EXISTS buildings.building_outlines (
      building_outline_id serial PRIMARY KEY
    , building_id integer NOT NULL REFERENCES buildings.buildings (building_id)
    , capture_method_id integer NOT NULL REFERENCES buildings_common.capture_method (capture_method_id)
    , capture_source_id integer NOT NULL REFERENCES buildings_common.capture_source (capture_source_id)
    , lifecycle_stage_id integer NOT NULL REFERENCES buildings.lifecycle_stage (lifecycle_stage_id)
    , suburb_locality_id integer NOT NULL
    , town_city_id integer
    , territorial_authority_id integer NOT NULL
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

COMMENT ON TABLE buildings.building_outlines IS
'The building_outline table holds a geometry, typically captured from an '
'aerial photograph. A new record is created for each new outline that '
'represents a building.';

COMMENT ON COLUMN buildings.building_outlines.building_outline_id IS
'Unique identifier for the building outline.';
COMMENT ON COLUMN buildings.building_outlines.building_id IS
'Foreign key to the buildings.building table. The building id is persistant for the '
'same building across all of the building outlines that represent it.';
COMMENT ON COLUMN buildings.building_outlines.capture_method_id IS
'Foreign key to the buildings_common.capture_method table. Holds the method by which the '
'geometry was captured.';
COMMENT ON COLUMN buildings.building_outlines.capture_source_id IS
'Foreign key to the buildings_common.capture_source table.';
COMMENT ON COLUMN buildings.building_outlines.lifecycle_stage_id IS
'Foreign key to the buildings.lifecycle_stage table.';
COMMENT ON COLUMN buildings.building_outlines.suburb_locality_id IS
'Holds an external id for suburbs / localities from the nz_locality dataset.';
COMMENT ON COLUMN buildings.building_outlines.town_city_id IS
'Holds an external id for the town / city from the nz_locality dataset.';
COMMENT ON COLUMN buildings.building_outlines.territorial_authority_id IS
'Holds an external id for the territorial authority from the '
'territorial_authority dataset.'
COMMENT ON COLUMN buildings.building_outlines.begin_lifespan IS
'The date that the building outline was added to the system.';
COMMENT ON COLUMN buildings.building_outlines.end_lifespan IS
'The date that the building outline was superceded, replaced or disused.';
COMMENT ON COLUMN buildings.building_outlines.shape IS
'The geometry of the building outline.';

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

COMMENT ON TABLE buildings.building_name IS
'The building_name table stores a name that is related to a building at a '
'point in time. Names have an lifespan independent from the building - the '
'name can change independent to any other changes to the building.';

COMMENT ON COLUMN buildings.building_name.building_name_id IS
'Unique identifier for a building name.';
COMMENT ON COLUMN buildings.building_name.building_id IS
'Foreign key to the buildings.building table.';
COMMENT ON COLUMN buildings.building_name.building_name IS
'The name of the building, where known.';
COMMENT ON COLUMN buildings.building_name.begin_lifespan IS
'The date that the building name was first captured in the system.';
COMMENT ON COLUMN buildings.building_name.end_lifespan IS
'The date that the building name was no longer attributed to a building in '
'the system, either because the name was no longer in use or because the '
'building was replaced or disused.';

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

COMMENT ON TABLE buildings.building_use IS
'The building_use table stores a use that is related to a building at a '
'point in time. Uses have an lifespan independent from the building - the '
'use can change independent to any other changes to the building.';

COMMENT ON COLUMN buildings.building_use.building_use_id IS
'Unique identifier for a building_use.';
COMMENT ON COLUMN buildings.building_use.building_id IS
'Foreign key to the buildings.building table.';
COMMENT ON COLUMN buildings.building_use.use_id IS
'Foreign key to the buildings.use table.';
COMMENT ON COLUMN buildings.building_use.begin_lifespan IS
'The date that the building use was first captured in the system.';
COMMENT ON COLUMN buildings.building_use.end_lifespan IS
'The date that the building use was no longer attributed to a building in '
'the system, either because the use was no longer in use or because the '
'building was replaced or disused.';

-- Lifecycle

CREATE TABLE IF NOT EXISTS buildings.lifecycle (
      lifecycle_id serial PRIMARY KEY
    , parent_building_id integer NOT NULL REFERENCES buildings.buildings (building_id)
    , building_id integer REFERENCES buildings.buildings (building_id)
);

SELECT setval('buildings.lifecycle_lifecycle_id_seq', coalesce((SELECT max(lifecycle_id) + 1 FROM buildings.lifecycle), 1000000), false);

DROP INDEX IF EXISTS idx_lifecycle_parent_building_id;
CREATE INDEX idx_lifecycle_parent_building_id
    ON buildings.lifecycle USING btree (parent_building_id);

DROP INDEX IF EXISTS idx_lifecycle_building_id;
CREATE INDEX idx_lifecycle_building_id
    ON buildings.lifecycle USING btree (building_id);

COMMENT ON TABLE buildings.lifecycle IS
'The lifecycle table stores the relationship between buildings when one '
'building is split into two buildings or two buildings are merged into one '
'building. This will generally occur when a building outline was erroneously '
'captured encompassing two buildings, which later becomes clear with '
'additional aerial imagery.';

COMMENT ON COLUMN buildings.lifecycle.lifecycle_id IS
'Unique identifier for a building_use.';
COMMENT ON COLUMN buildings.lifecycle.parent_building_id IS
'Foreign key to the buildings.building table. All records stored as parent '
'buildings will be end dated in the system.';
COMMENT ON COLUMN buildings.lifecycle.building_id IS
'Foreign key to the buildings.building table.';
