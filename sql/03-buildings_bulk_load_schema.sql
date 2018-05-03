------------------------------------------------------------------------------
-- Create buildings stage schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_bulk_load;

COMMENT ON SCHEMA buildings_bulk_load IS
'Schema that holds building outlines data while quality assurance is '
'conducted. Data is also prepared to be loaded into production.';

-- Organisation

CREATE TABLE IF NOT EXISTS buildings_bulk_load.organisation (
      organisation_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings_bulk_load.organisation IS
'This is a lookup table that holds names of organisations that are related to '
'buildings data. All suppliers of building outlines data must be recorded here.';

COMMENT ON COLUMN buildings_bulk_load.organisation.organisation_id IS
'Unique identifier for the organisation table.';
COMMENT ON COLUMN buildings_bulk_load.organisation.value IS
'The name of the organisation.';

-- Bulk Load Status

CREATE TABLE IF NOT EXISTS buildings_bulk_load.bulk_load_status (
      bulk_load_status_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings_bulk_load.bulk_load_status IS
'This is a lookup table that holds the status of building outlines through '
'the bulk load process.';

COMMENT ON COLUMN buildings_bulk_load.bulk_load_status.bulk_load_status_id IS
'Unique identifier for the bulk_load_status table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_status.value IS
'The bulk load status of the building outline. Options include: Supplied, '
'Added';

-- QA Status

CREATE TABLE IF NOT EXISTS buildings_bulk_load.qa_status (
      qa_status_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings_bulk_load.qa_status IS
'This is a lookup table that holds the status of building outlines during '
'.feet';

COMMENT ON COLUMN buildings_bulk_load.qa_status.qa_status_id IS
'Unique identifier for the qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.qa_status.value IS
'The QA status of the building outlines. ';

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

COMMENT ON TABLE buildings_bulk_load.supplied_datasets IS
'This table records information about datasets supplied to LINZ for bulk '
'load into the buildings system.';

COMMENT ON COLUMN buildings_bulk_load.supplied_datasets.supplied_dataset_id IS
'Unique identifier for the supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.supplied_datasets.description IS
'A general description of the supplied dataset.';
COMMENT ON COLUMN buildings_bulk_load.supplied_datasets.supplier_id IS
'Foreign key to the buildings.organisation table.';
COMMENT ON COLUMN buildings_bulk_load.supplied_datasets.processed_date IS
'The date that the supplied dataset was imported into the buildings_bulk_load '
'schema.';
COMMENT ON COLUMN buildings_bulk_load.supplied_datasets.transfer_date IS
'The date that the supplied dataset was transferred to production schema.';

-- Supplied Outlines

CREATE TABLE IF NOT EXISTS buildings_bulk_load.bulk_load_outlines (
      bulk_load_outline_id serial PRIMARY KEY
    , supplied_dataset_id integer NOT NULL REFERENCES buildings_bulk_load.supplied_datasets (supplied_dataset_id)
    , external_outline_id character varying(250)
    , bulk_load_status_id integer NOT NULL REFERENCES buildings_bulk_load.bulk_load_status (bulk_load_status_id)
    , capture_method_id integer NOT NULL REFERENCES buildings_common.capture_method (capture_method_id)
    , capture_source_id integer NOT NULL REFERENCES buildings_common.capture_source (capture_source_id)
    , suburb_locality_id integer NOT NULL
    , town_city_id integer
    , territorial_authority_id integer NOT NULL
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

COMMENT ON TABLE buildings_bulk_load.bulk_load_outlines IS
'This dataset contains all building outline geometries as they are received '
'from the supplier, in addition to any new building outlines added during '
'QA of that particular bulk load. A number of attributes are first '
'connected to the building outline in this table, which are later '
'loaded into the production buildings schema.';

COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.bulk_load_outline_id IS
'Unique identifier for the bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.external_outline_id IS
'External identifier, held in order to compare with future bulk loads from '
'the same external dataset.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.bulk_load_status_id IS
'Foreign key to the buildings_bulk_load.bulk_load_status table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.capture_method_id IS
'Foreign key to the buildings_common.capture_method table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.capture_source_id IS
'Foreign key to the buildings_common.capture_source table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.suburb_locality_id IS
'Foreign key to the buildings_common.suburb_locality table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.town_city_id IS
'Foreign key to the buildings_common.town_city table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.territorial_authority_id IS
'Foreign key to the buildings_common.territorial_authority table.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.begin_lifespan IS
'The date that the building was uploaded via bulk load tools.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.shape IS
'The geometry of the building outline as received from the supplier.';

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

COMMENT ON TABLE buildings_bulk_load.existing_subset_extracts IS
'This table contains extracts of production building outlines over the same '
'area covered by a new bulk load of building outlines data. Each set of '
'extracted building outlines is related to the new bulk load via the '
'supplied_dataset_id.';

COMMENT ON COLUMN buildings_bulk_load.existing_subset_extracts.building_outline_id IS
'Unique identifier for the existing_subset_extracts table and foreign key to the '
'buildings.building_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.existing_subset_extracts.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.existing_subset_extracts.shape IS
'The geometry of the building outline that exists in the production schema.';

-- Added

CREATE TABLE IF NOT EXISTS buildings_bulk_load.added (
      bulk_load_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
);

DROP INDEX IF EXISTS idx_added_qa_status_id;
CREATE INDEX idx_added_qa_status_id
    ON buildings_bulk_load.added USING btree (qa_status_id);

COMMENT ON TABLE buildings_bulk_load.added IS
'This table holds the building outlines that have been identified as new '
'buildings within the building outlines dataset.';

COMMENT ON COLUMN buildings_bulk_load.added.bulk_load_outline_id IS
'Unique identifier for the added table and foreign key to the '
'buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.added.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';

-- Removed

CREATE TABLE IF NOT EXISTS buildings_bulk_load.removed (
      building_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.existing_subset_extracts (building_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
);

DROP INDEX IF EXISTS idx_removed_qa_status_id;
CREATE INDEX idx_removed_qa_status_id
    ON buildings_bulk_load.removed USING btree (qa_status_id);

COMMENT ON TABLE buildings_bulk_load.removed IS
'This table holds the building outlines that have been identified as no '
'longer existing. These building outlines were within the area of '
'capture but were not found in a more recent capture process.';

COMMENT ON COLUMN buildings_bulk_load.removed.building_outline_id IS
'Unique identifier for the removed table and foreign key to the '
'buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.removed.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';

-- Related Candidates

CREATE TABLE IF NOT EXISTS buildings_bulk_load.related (
      related_id serial PRIMARY KEY
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

COMMENT ON TABLE buildings_bulk_load.related IS
'';

COMMENT ON COLUMN buildings_bulk_load.related.related_id IS
'Unique identifier for the related table.';
COMMENT ON COLUMN buildings_bulk_load.related.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outline_id table.';
COMMENT ON COLUMN buildings_bulk_load.related.building_outline_id IS
'Foreign key to the buildings_bulk_load.building_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.related.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.related.area_bulk_load IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.area_existing IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.area_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.percent_bulk_load_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.percent_existing_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.total_area_bulk_load_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.total_area_existing_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.total_percent_bulk_load_overlap IS
'';
COMMENT ON COLUMN buildings_bulk_load.related.total_percent_existing_overlap IS
'';

-- Matched

CREATE TABLE IF NOT EXISTS buildings_bulk_load.matched (
      matched_id serial PRIMARY KEY
    , bulk_load_outline_id integer NOT NULL REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , building_outline_id integer NOT NULL REFERENCES buildings_bulk_load.existing_subset_extracts (building_outline_id)
    , qa_status_id integer NOT NULL REFERENCES buildings_bulk_load.qa_status (qa_status_id)
);

DROP INDEX IF EXISTS idx_matched_building_outline_id;
CREATE INDEX idx_matched_building_outline_id
    ON buildings_bulk_load.matched USING btree (building_outline_id);

DROP INDEX IF EXISTS idx_matched_qa_status_id;
CREATE INDEX idx_matched_qa_status_id
    ON buildings_bulk_load.matched USING btree (qa_status_id);

COMMENT ON TABLE buildings_bulk_load.matched IS
'This table holds potential 1:1 matches between outlines that have been '
'loaded into the system in bulk and those that already exist.';

COMMENT ON COLUMN buildings_bulk_load.matched.matched_id IS
'Unique identifier for the matched table.';
COMMENT ON COLUMN buildings_bulk_load.matched.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outline_id table.';
COMMENT ON COLUMN buildings_bulk_load.matched.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.matched.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';


-- Transferred

CREATE TABLE IF NOT EXISTS buildings_bulk_load.transferred (
      bulk_load_outline_id integer PRIMARY KEY REFERENCES buildings_bulk_load.bulk_load_outlines (bulk_load_outline_id)
    , new_building_outline_id integer NOT NULL REFERENCES buildings.building_outlines (building_outline_id)
);

DROP INDEX IF EXISTS idx_transferred_new_building_outline_id;
CREATE INDEX idx_transferred_new_building_outline_id
    ON buildings_bulk_load.transferred USING btree (new_building_outline_id);

COMMENT ON TABLE buildings_bulk_load.transferred IS
'This table holds the building_outline_id ';

COMMENT ON COLUMN buildings_bulk_load.transferred.bulk_load_outline_id IS
'Unique identifier for the transferred table and foreign key to the '
'buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.transferred.new_building_outline_id IS
'Foreign key to the buildings.building_outlines table.';

-- VIEWS

-- Added Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.added_outlines AS
    SELECT
          added.bulk_load_outline_id
        , added.qa_status_id
        , supplied.supplied_dataset_id
        , supplied.shape
    FROM buildings_bulk_load.added
    JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id);

COMMENT ON VIEW buildings_bulk_load.added_outlines IS
'This table holds the building outlines that have been identified as new '
'buildings within the building outlines dataset.';

COMMENT ON COLUMN buildings_bulk_load.added_outlines.bulk_load_outline_id IS
'Unique identifier for the added table and foreign key to the '
'buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.added_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.added_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.added_outlines.shape IS
'The geometry of existing building outlines that are part of a 1:1 '
'relationship with bulk loaded outlines.';

-- Removed Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.removed_outlines AS
    SELECT
          removed.building_outline_id
        , removed.qa_status_id
        , current.supplied_dataset_id
        , current.shape
    FROM buildings_bulk_load.removed
    JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id);

COMMENT ON VIEW buildings_bulk_load.removed_outlines IS
'This table holds the building outlines that have been identified as removed '
'buildings within the building outlines dataset.';

COMMENT ON COLUMN buildings_bulk_load.removed_outlines.building_outline_id IS
'Unique identifier for the removed table and foreign key to the '
'buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.removed_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.removed_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.removed_outlines.shape IS
'The geometry of existing building outlines that are part of a 1:1 '
'relationship with bulk loaded outlines.';

-- Matched Existing Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.matched_existing_outlines AS
    SELECT
          matched.matched_id
        , matched.bulk_load_outline_id
        , matched.building_outline_id
        , matched.qa_status_id
        , current.supplied_dataset_id
        , current.shape
    FROM buildings_bulk_load.matched
    JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id);

COMMENT ON VIEW buildings_bulk_load.matched_existing_outlines IS
'The matched_existing_outlines view is used to visualise building '
'outlines that are current in the system and identified as part of an '
'1:1 relationship with bulk loaded outlines.';

COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.matched_id IS
'Unique identifier for the matched table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.shape IS
'The geometry of existing building outlines that are part of a 1:1 '
'relationship with bulk loaded outlines.';

-- Matched Bulk Load Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.matched_bulk_load_outlines AS
    SELECT
          matched.matched_id
        , matched.bulk_load_outline_id
        , matched.building_outline_id
        , matched.qa_status_id
        , supplied.supplied_dataset_id
        , supplied.shape
    FROM buildings_bulk_load.matched
    JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id);

COMMENT ON VIEW buildings_bulk_load.matched_bulk_load_outlines IS
'The matched_bulk_load_outlines view is used to visualise building '
'outlines that are current in the system and identified as part of an '
'1:1 relationship with existing outlines.';

COMMENT ON COLUMN buildings_bulk_load.matched_bulk_load_outlines.matched_id IS
'Unique identifier for the matched table.';
COMMENT ON COLUMN buildings_bulk_load.matched_bulk_load_outlines.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.matched_existing_outlines.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.matched_bulk_load_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.matched_bulk_load_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.matched_bulk_load_outlines.shape IS
'The geometry of bulk loaded building outlines that are part of an 1:1 '
'relationship with existing building outlines.';

-- Matched Details

CREATE OR REPLACE VIEW buildings_bulk_load.matched_details AS
    SELECT 
          matched.matched_id
        , matched.bulk_load_outline_id
        , matched.building_outline_id
        , matched.qa_status_id
        , supplied.supplied_dataset_id
        , round(ST_Area(supplied.shape)::numeric, 2) AS area_bulk_load
        , round(ST_Area(current.shape)::numeric, 2) As area_existing
        , round((@(ST_Area(current.shape) - ST_Area(supplied.shape)) / ST_Area(current.shape) * 100)::numeric, 2) AS percent_area_difference
        , round(ST_Area(ST_Intersection(supplied.shape, current.shape))::numeric, 2) AS area_overlap
        , round((ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) * 100)::numeric, 2) AS percent_bulk_load_overlap
        , round((ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) * 100)::numeric, 2) AS percent_existing_overlap
        , round(ST_HausdorffDistance(supplied.shape, current.shape)::numeric, 2) AS hausdorff_distance
    FROM buildings_bulk_load.matched
    JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id)
    JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id);

COMMENT ON VIEW buildings_bulk_load.matched_details IS
'The matched_details view includes area calculations that help determine '
'whether the match is likely to be valid or not.';

COMMENT ON COLUMN buildings_bulk_load.matched_details.matched_id IS
'Unique identifier for the matched table.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outline_id table.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.area_bulk_load IS
'The area of the building outline that is part of a bulk load.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.area_existing IS
'The area of the existing building outline that has been identified as a '
'match for the bulk load building outline.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.percent_area_difference IS
'The percentage of area difference between bulk load and existing.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.area_overlap IS
'The area of intersection between the two building outlines.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.percent_bulk_load_overlap IS
'The percentage of the bulk load building outline that is overlapped by the '
'existing building outline.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.percent_existing_overlap IS
'The percentage of the existing building outline that is overlapped by the '
'bulk load building outline.';
COMMENT ON COLUMN buildings_bulk_load.matched_details.hausdorff_distance IS
'Hausdorff Distance is an algorithm for determining if the shape of two '
'polygons is similar.';

-- Related Existing Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.related_existing_outlines AS
    SELECT DISTINCT
          related.related_id
        , related.bulk_load_outline_id
        , related.building_outline_id
        , related.qa_status_id
        , current.supplied_dataset_id
        , current.shape
    FROM buildings_bulk_load.related
    JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id);

COMMENT ON VIEW buildings_bulk_load.related_existing_outlines IS
'The related_existing_outlines view is used to visualise building '
'outlines that are current in the system and identified as part of an '
'm:n relationship with bulk loaded outlines.';

COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.related_id IS
'Unique identifier for the related table.';
COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outline_id table.';
COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.related_existing_outlines.shape IS
'The geometry of existing building outlines that are part of an m:n '
'relationship with bulk loaded outlines.';

-- Related Bulk Load Outlines

CREATE OR REPLACE VIEW buildings_bulk_load.related_bulk_load_outlines AS
    SELECT DISTINCT
          related.related_id
        , related.bulk_load_outline_id
        , related.building_outline_id
        , related.qa_status_id
        , supplied.supplied_dataset_id
        , supplied.shape
    FROM buildings_bulk_load.related
    JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id);

COMMENT ON VIEW buildings_bulk_load.related_bulk_load_outlines IS
'The related_bulk_load_outlines view is used to visualise building '
'outlines that have been bulk loaded and identified as part of an '
'm:n relationship.';

COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.related_id IS
'Unique identifier for the related table.';
COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outline_id table.';
COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';
COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.supplied_dataset_id IS
'Foreign key to the buildings_bulk_load.supplied_datasets table.';
COMMENT ON COLUMN buildings_bulk_load.related_bulk_load_outlines.shape IS
'The geometry of existing building outlines that are part of an m:n '
'relationship with bulk loaded outlines.';
