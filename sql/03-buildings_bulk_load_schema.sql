------------------------------------------------------------------------------
-- Create buildings stage schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_bulk_load;

-- Organisation

CREATE TABLE IF NOT EXISTS buildings_bulk_load.organisation (
      organisation_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Bulk Load Status

CREATE TABLE IF NOT EXISTS buildings_bulk_load.bulk_load_status (
      bulk_load_status_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- QA Status

CREATE TABLE IF NOT EXISTS buildings_bulk_load.qa_status (
      qa_status_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Supplied Datasets

CREATE TABLE IF NOT EXISTS buildings_bulk_load.supplied_datasets (
      supplied_dataset_id serial PRIMARY KEY
    , description character varying(250) NOT NULL
    , supplier_id integer NOT NULL REFERENCES buildings_bulk_load.organisation (organisation_id)
    , processed_date timestamptz
    , transfer_date timestamptz
);

DROP INDEX IF EXISTS idx_supplied_datasets_supplier_id;
CREATE INDEX idx_supplied_datasets_supplier_id
    ON buildings_bulk_load.supplied_datasets USING btree (supplier_id);

-- Supplied Outlines

CREATE TABLE IF NOT EXISTS buildings_bulk_load.bulk_load_outlines (
      bulk_load_outline_id serial PRIMARY KEY
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_bulk_load.supplied_datasets (supplied_dataset_id)
    , external_outline_id character varying(250)
    , bulk_load_status_id integer NOT NULL REFERENCES buildings_bulk_load.bulk_load_status (bulk_load_status_id)
    , capture_method_id integer NOT NULL REFERENCES buildings_common.capture_method (capture_method_id)
    , capture_source_id integer NOT NULL REFERENCES buildings_common.capture_source (capture_source_id)
    , suburb_locality_id integer
    , town_city_id integer
    , territorial_authority_id integer
    , begin_lifespan timestamptz NOT NULL DEFAULT now()
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

SELECT setval('buildings_bulk_load.bulk_load_outlines_bulk_load_outline_id_seq', coalesce((SELECT max(bulk_load_outline_id) + 1 FROM buildings_bulk_load.bulk_load_outlines), 1000000), false);

DROP INDEX IF EXISTS idx_bulk_load_outlines_supplied_dataset_id;
CREATE INDEX idx_bulk_load_outlines_supplied_dataset_id
    ON buildings_bulk_load.bulk_load_outlines USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_bulk_load_outlines_bulk_load_status_id;
CREATE INDEX idx_bulk_load_outlines_bulk_load_status_id
    ON buildings_bulk_load.bulk_load_outlines USING btree (bulk_load_status_id);

DROP INDEX IF EXISTS idx_bulk_load_outlines_capture_method_id;
CREATE INDEX idx_bulk_load_outlines_capture_method_id
    ON buildings_bulk_load.bulk_load_outlines USING btree (capture_method_id);

DROP INDEX IF EXISTS idx_bulk_load_outlines_capture_source_id;
CREATE INDEX idx_bulk_load_outlines_capture_source_id
    ON buildings_bulk_load.bulk_load_outlines USING btree (capture_source_id);

DROP INDEX IF EXISTS shx_bulk_load_outlines;
CREATE INDEX shx_bulk_load_outlines
    ON buildings_bulk_load.bulk_load_outlines USING gist (shape);

-- Existing Subset Extracts

CREATE TABLE IF NOT EXISTS buildings_bulk_load.existing_subset_extracts (
      building_outline_id integer PRIMARY KEY REFERENCES buildings.building_outlines (building_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_bulk_load.supplied_datasets (supplied_dataset_id)
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_existing_subset_extracts_supplied_dataset_id;
CREATE INDEX idx_existing_subset_extracts_supplied_dataset_id
    ON buildings_bulk_load.existing_subset_extracts USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS shx_existing_subset_extracts;
CREATE INDEX shx_existing_subset_extracts
    ON buildings_bulk_load.existing_subset_extracts USING gist (shape);

-- Added

CREATE TABLE IF NOT EXISTS buildings_bulk_load.added (
      bulk_load_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
);

DROP INDEX IF EXISTS idx_added_qa_status_id;
CREATE INDEX idx_added_qa_status_id
    ON buildings_bulk_load.added USING btree (qa_status_id);

-- Removed

CREATE TABLE IF NOT EXISTS buildings_bulk_load.removed (
      building_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.existing_subset_extracts (building_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
);

DROP INDEX IF EXISTS idx_removed_qa_status_id;
CREATE INDEX idx_removed_qa_status_id
    ON buildings_bulk_load.removed USING btree (qa_status_id);

-- Related Candidates

CREATE TABLE IF NOT EXISTS buildings_bulk_load.related (
      related_candidate_id serial PRIMARY KEY
    , bulk_load_outline_id integer NOT NULL REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_bulk_load.existing_subset_extracts (building_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
    , area_bulk_load numeric(10, 2) NOT NULL
    , area_existing numeric(10, 2) NOT NULL
    , area_overlap numeric(10, 2) NOT NULL
    , percent_bulk_load_overlap numeric(5, 2) NOT NULL
    , percent_existing_overlap numeric(5, 2) NOT NULL
    , total_area_bulk_load_overlap numeric(10, 2) NOT NULL
    , total_area_existing_overlap numeric(10, 2) NOT NULL
    , total_percent_bulk_load_overlap numeric(5, 2) NOT NULL
    , total_percent_existing_overlap numeric(5, 2) NOT NULL
);

DROP INDEX IF EXISTS idx_related_bulk_load_outline_id;
CREATE INDEX idx_related_bulk_load_outline_id
    ON buildings_bulk_load.related USING btree (bulk_load_outline_id);

DROP INDEX IF EXISTS idx_related_building_outline_id;
CREATE INDEX idx_related_building_outline_id
    ON buildings_bulk_load.related USING btree (building_outline_id);

DROP INDEX IF EXISTS idx_related_qa_status_id;
CREATE INDEX idx_related_qa_status_id
    ON buildings_bulk_load.related USING btree (qa_status_id);

-- Matched

CREATE TABLE IF NOT EXISTS buildings_bulk_load.matched (
      bulk_load_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_bulk_load.existing_subset_extracts (building_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
    , area_bulk_load numeric(10, 2) NOT NULL
    , area_existing numeric(10, 2) NOT NULL
    , percent_area_difference numeric(5, 2) NOT NULL
    , area_overlap numeric(10, 2) NOT NULL
    , percent_bulk_load_overlap numeric(5, 2) NOT NULL
    , percent_existing_overlap numeric(5, 2) NOT NULL
    , hausdorff_distance numeric(6, 4) NOT NULL
);

DROP INDEX IF EXISTS idx_matched_building_outline_id;
CREATE INDEX idx_matched_building_outline_id
    ON buildings_bulk_load.matched USING btree (building_outline_id);

DROP INDEX IF EXISTS idx_matched_qa_status_id;
CREATE INDEX idx_matched_qa_status_id
    ON buildings_bulk_load.matched USING btree (qa_status_id);

-- Transferred

CREATE TABLE IF NOT EXISTS buildings_bulk_load.transferred (
      bulk_load_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , new_building_outline_id integer NOT NULL REFERENCES buildings.building_outlines (building_outline_id)
);

DROP INDEX IF EXISTS idx_transferred_new_building_outline_id;
CREATE INDEX idx_transferred_new_building_outline_id
    ON buildings_bulk_load.transferred USING btree (new_building_outline_id);
