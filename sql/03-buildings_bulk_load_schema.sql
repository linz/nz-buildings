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
'QA of the bulk load process.';

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
'Foreign key to the buildings_bulk_load.organisation table.';
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
'Holds an external id for suburbs / localities from the nz_locality dataset.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.town_city_id IS
'Holds an external id for the town / city from the nz_locality dataset.';
COMMENT ON COLUMN buildings_bulk_load.bulk_load_outlines.territorial_authority_id IS
'Holds an external id for the territorial authority from the '
'territorial_authority dataset.';
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

-- Related

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
'This table holds potential m:n matches between outlines that have been '
'loaded into the system in bulk and those that already exist.';

COMMENT ON COLUMN buildings_bulk_load.related.related_id IS
'Unique identifier for the related table.';
COMMENT ON COLUMN buildings_bulk_load.related.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outlines table.';
COMMENT ON COLUMN buildings_bulk_load.related.building_outline_id IS
'Foreign key to the buildings_bulk_load.existing_subset_extracts table.';
COMMENT ON COLUMN buildings_bulk_load.related.qa_status_id IS
'Foreign key to the buildings_bulk_load.qa_status table.';

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

COMMENT ON TABLE buildings_bulk_load.matched IS
'This table holds potential 1:1 matches between outlines that have been '
'loaded into the system in bulk and those that already exist.';

COMMENT ON COLUMN buildings_bulk_load.matched.bulk_load_outline_id IS
'Foreign key to the buildings_bulk_load.bulk_load_outlines table.';
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
