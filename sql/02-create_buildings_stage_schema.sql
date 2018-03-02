------------------------------------------------------------------------------
-- Create buildings stage schema and tables
------------------------------------------------------------------------------


CREATE SCHEMA IF NOT EXISTS buildings_stage;

-- Organisation

CREATE TABLE IF NOT EXISTS buildings_stage.organisation (
      organisation_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- QA Status

CREATE TABLE IF NOT EXISTS buildings_stage.qa_status (
      qa_status_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Supplied Datasets

CREATE TABLE IF NOT EXISTS buildings_stage.supplied_datasets (
      supplied_dataset_id serial PRIMARY KEY
    , description character varying(250) NOT NULL
    , supplier_id integer NOT NULL REFERENCES buildings_stage.organisation (organisation_id)
    , processed_date timestamptz NOT NULL DEFAULT now()
    , transfer_date timestamptz
);

DROP INDEX IF EXISTS idx_supplied_datasets_supplier_id;
CREATE INDEX idx_supplied_datasets_supplier_id
    ON buildings_stage.supplied_datasets USING btree (supplier_id);

-- Supplied Outlines

CREATE TABLE IF NOT EXISTS buildings_stage.supplied_outlines (
      supplied_outline_id serial PRIMARY KEY
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

SELECT setval('buildings_stage.supplied_outlines_supplied_outline_id_seq', coalesce((SELECT max(supplied_outline_id) + 1 FROM buildings_stage.supplied_outlines), 1000000), false);

DROP INDEX IF EXISTS idx_supplied_outlines_supplied_dataset_id;
CREATE INDEX idx_supplied_outlines_supplied_dataset_id
    ON buildings_stage.supplied_outlines USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS shx_supplied_outlines;
CREATE INDEX shx_supplied_outlines
    ON buildings_stage.supplied_outlines USING gist (shape);

-- Existing Subset Extracts

CREATE TABLE IF NOT EXISTS buildings_stage.existing_subset_extracts (
      building_outline_id integer PRIMARY KEY REFERENCES buildings.building_outlines (building_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_existing_subset_extracts_supplied_dataset_id;
CREATE INDEX idx_existing_subset_extracts_supplied_dataset_id
    ON buildings_stage.existing_subset_extracts USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS shx_existing_subset_extracts;
CREATE INDEX shx_existing_subset_extracts
    ON buildings_stage.existing_subset_extracts USING gist (shape);

-- New

CREATE TABLE IF NOT EXISTS buildings_stage.new (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_new_supplied_dataset_id;
CREATE INDEX idx_new_supplied_dataset_id
    ON buildings_stage.new USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS shx_new;
CREATE INDEX shx_new
    ON buildings_stage.new USING gist (shape);

-- Removed

CREATE TABLE IF NOT EXISTS buildings_stage.removed (
      building_outline_id integer PRIMARY KEY REFERENCES buildings_stage.existing_subset_extracts (building_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_removed_supplied_dataset_id;
CREATE INDEX idx_removed_supplied_dataset_id
    ON buildings_stage.removed USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_removed_qa_status_id;
CREATE INDEX idx_removed_qa_status_id
    ON buildings_stage.removed USING btree (qa_status_id);

DROP INDEX IF EXISTS shx_removed;
CREATE INDEX shx_removed
    ON buildings_stage.removed USING gist (shape);

-- Merged

CREATE TABLE IF NOT EXISTS buildings_stage.merged (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , area_covering numeric(10, 2) NOT NULL
    , percent_covering numeric(5, 2) NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_merged_supplied_dataset_id;
CREATE INDEX idx_merged_supplied_dataset_id
    ON buildings_stage.merged USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_merged_qa_status_id;
CREATE INDEX idx_merged_qa_status_id
    ON buildings_stage.merged USING btree (qa_status_id);

DROP INDEX IF EXISTS shx_merged;
CREATE INDEX shx_merged
    ON buildings_stage.merged USING gist (shape);

-- Merge Candidates

CREATE TABLE IF NOT EXISTS buildings_stage.merge_candidates (
      building_outline_id integer PRIMARY KEY REFERENCES buildings_stage.existing_subset_extracts (building_outline_id)
    , supplied_outline_id integer NOT NULL REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , area_covered numeric(10, 2) NOT NULL
    , percent_covered numeric(5, 2) NOT NULL
);

DROP INDEX IF EXISTS idx_merge_candidates_supplied_outline_id;
CREATE INDEX idx_merge_candidates_supplied_outline_id
    ON buildings_stage.merge_candidates USING btree (supplied_outline_id);

DROP INDEX IF EXISTS idx_merge_candidates_supplied_dataset_id;
CREATE INDEX idx_merge_candidates_supplied_dataset_id
    ON buildings_stage.merge_candidates USING btree (supplied_dataset_id);

-- Split

CREATE TABLE IF NOT EXISTS buildings_stage.split (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , area_covered numeric(10, 2) NOT NULL
    , percent_covered numeric(5, 2) NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_split_supplied_dataset_id;
CREATE INDEX idx_split_supplied_dataset_id
    ON buildings_stage.split USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_split_qa_status_id;
CREATE INDEX idx_split_qa_status_id
    ON buildings_stage.split USING btree (qa_status_id);

DROP INDEX IF EXISTS shx_split;
CREATE INDEX shx_split
    ON buildings_stage.split USING gist (shape);

-- Split Candidates

CREATE TABLE IF NOT EXISTS buildings_stage.split_candidates (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_stage.existing_subset_extracts (building_outline_id)
    , area_covering numeric(10, 2) NOT NULL
    , percent_covering numeric(5, 2) NOT NULL
);

DROP INDEX IF EXISTS idx_split_candidates_supplied_outline_id;
CREATE INDEX idx_split_candidates_supplied_outline_id
    ON buildings_stage.split_candidates USING btree (supplied_outline_id);

DROP INDEX IF EXISTS idx_split_candidates_supplied_dataset_id;
CREATE INDEX idx_split_candidates_supplied_dataset_id
    ON buildings_stage.split_candidates USING btree (supplied_dataset_id);

-- Best Candidates

CREATE TABLE IF NOT EXISTS buildings_stage.best_candidates (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_stage.existing_subset_extracts (building_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , area_difference numeric(10, 2) NOT NULL
    , percent_difference numeric(5, 2) NOT NULL
    , hausdorff_distance numeric(6, 4) NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_best_candidates_building_outline_id;
CREATE INDEX idx_best_candidates_building_outline_id
    ON buildings_stage.best_candidates USING btree (building_outline_id);

DROP INDEX IF EXISTS idx_best_candidates_supplied_dataset_id;
CREATE INDEX idx_best_candidates_supplied_dataset_id
    ON buildings_stage.best_candidates USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_best_candidates_qa_status_id;
CREATE INDEX idx_best_candidates_qa_status_id
    ON buildings_stage.best_candidates USING btree (qa_status_id);

DROP INDEX IF EXISTS shx_best_candidates;
CREATE INDEX shx_best_candidates
    ON buildings_stage.best_candidates USING gist (shape);

-- Check Candidates

CREATE TABLE IF NOT EXISTS buildings_stage.check_candidates (
      supplied_outline_id integer PRIMARY KEY REFERENCES buildings_stage.supplied_outlines (supplied_outline_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_stage.existing_subset_extracts (building_outline_id)
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_stage.supplied_datasets (supplied_dataset_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_stage.qa_status (qa_status_id)
    , area_difference numeric(10, 2) NOT NULL
    , percent_difference numeric(5, 2) NOT NULL
    , hausdorff_distance numeric(6, 4) NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

DROP INDEX IF EXISTS idx_check_candidates_building_outline_id;
CREATE INDEX idx_check_candidates_building_outline_id
    ON buildings_stage.check_candidates USING btree (building_outline_id);

DROP INDEX IF EXISTS idx_check_candidates_supplied_dataset_id;
CREATE INDEX idx_check_candidates_supplied_dataset_id
    ON buildings_stage.check_candidates USING btree (supplied_dataset_id);

DROP INDEX IF EXISTS idx_check_candidates_qa_status_id;
CREATE INDEX idx_check_candidates_qa_status_id
    ON buildings_stage.check_candidates USING btree (qa_status_id);

DROP INDEX IF EXISTS shx_check_candidates;
CREATE INDEX shx_check_candidates
    ON buildings_stage.check_candidates USING gist (shape);
