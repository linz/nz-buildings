------------------------------------------------------------------------------
-- Create buildings LDS schema and tables

-- Tables:
-- nz_building_outlines
-- nz_building_outlines_all_sources
-- nz_building_outlines_lifecycle

------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_lds;

COMMENT ON SCHEMA buildings_lds IS
'Schema that holds tables published via the LINZ Data Service.';

-- NZ Building Outlines
-- NZ Building Outlines contains the current depiction of building outlines.
CREATE TABLE IF NOT EXISTS buildings_lds.nz_building_outlines (
      building_id integer PRIMARY KEY
    , name character varying(250) NOT NULL
    , use character varying(40) NOT NULL
    , suburb_locality character varying(80) NOT NULL
    , town_city character varying(80) NOT NULL
    , territorial_authority character varying(100) NOT NULL
    , capture_method character varying(40) NOT NULL
    , capture_source_group character varying(80) NOT NULL
    , capture_source_id integer NOT NULL
    , capture_source_name character varying(100) NOT NULL
    , capture_source_from date NOT NULL
    , capture_source_to date NOT NULL
    , last_modified date
    , shape public.geometry(Polygon, 2193) NOT NULL
);

COMMENT ON TABLE buildings_lds.nz_building_outlines IS
'NZ Building Outlines contains the most recent representation of each '
'building as a building outline.';

COMMENT ON COLUMN buildings_lds.nz_building_outlines.building_id IS
'Unique identifier for a building. The building id is persistant for the same '
'building across all of the building outlines that represent it.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.name IS
'The name of the building, where known. If no known name this will be '
'an empty string.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.use IS
'The building use, maintained for the Topo50 map series. If no known use '
'this will default to Unknown.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.suburb_locality IS
'The suburb / locality that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.town_city IS
'The town / city that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.territorial_authority IS
'The territorial authority that the majority of the building outline is '
'within. Sourced from Stats NZ.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_method IS
'The method by which the geometry was captured e.g. Feature Extraction.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_group IS
'The source from which the geometry was captured e.g. NZ Aerial Imagery.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_id IS
'The id of the capture source area - currently all ids are a foreign key to '
'the NZ Imagery Surveys dataset.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_name IS
'The title/name of the specific capture source area.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_from IS
'The earliest date on which aerial photographs were taken as part of the related '
'imagery survey.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_to IS
'The latest date on which aerial photographs were taken as part of the related '
'imagery survey.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.last_modified IS
'The most recent date on which any attribute or geometry that is part of '
'the building outline was modified.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.shape IS
'The geometry of the building outline, represented as a Polygon using '
'NZTM2000 / EPSG 2193. Internal rings are possible, multiple external rings '
'are not.';

-- NZ Building Outlines: All Sources
-- NZ Building Outlines: All Sources contains all of the procured building
-- outlines.
CREATE TABLE IF NOT EXISTS buildings_lds.nz_building_outlines_all_sources (
      building_outline_id integer PRIMARY KEY
    , building_id integer NOT NULL
    , name character varying(250) NOT NULL
    , use character varying(40) NOT NULL
    , suburb_locality character varying(80) NOT NULL
    , town_city character varying(80) NOT NULL
    , territorial_authority character varying(100) NOT NULL
    , capture_method character varying(40) NOT NULL
    , capture_source_group character varying(80) NOT NULL
    , capture_source_id integer NOT NULL
    , capture_source_name character varying(100) NOT NULL
    , capture_source_from date NOT NULL
    , capture_source_to date NOT NULL
    , building_outline_lifecycle character varying(40) NOT NULL
    , begin_lifespan date NOT NULL
    , end_lifespan date
    , last_modified date NOT NULL
    , shape public.geometry(Polygon, 2193) NOT NULL
);

COMMENT ON TABLE buildings_lds.nz_building_outlines_all_sources IS
'NZ Building Outlines: All Sources contains all combinations of outline / '
'building / name / use that have existed within the building outlines '
'system, and the dates for which that combination existed. ';

COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.building_outline_id IS
'Unique identifier for the building outline. The building outline id is unique '
'to one representation of a building.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.building_id IS
'Unique identifier for a building. The building id is persistant for the same '
'building across all of the building outlines that represent it.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.name IS
'The name of the building, where known.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.use IS
'The building use, maintained for the Topo50 map series.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.suburb_locality IS
'The suburb / locality that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.town_city IS
'The town / city that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.territorial_authority IS
'The territorial authority that the majority of the building outline is '
'within. Sourced from Stats NZ.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.capture_method IS
'The method by which the geometry was captured e.g. Feature Extraction.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.capture_source_group IS
'The source from which the geometry was captured e.g. NZ Aerial Imagery.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.capture_source_id IS
'The id of the capture source area - currently all ids are a foreign key to '
'the NZ Imagery Surveys dataset.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_name IS
'The title/name of the specific capture source area.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_from IS
'The earliest date on which aerial photographs were taken as part of the related '
'imagery survey.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source_to IS
'The latest date on which aerial photographs were taken as part of the related '
'imagery survey.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.building_outline_lifecycle IS
'The lifecycle of the building outline. Lifecycles with an end_lifespan date may '
'either be "Removed" (new aerial imagery shows no evidence of the building), '
'"Replaced" (a new building outline exists captured from new aerial imagery) '
'or "Recombined" (new building outlines exist captured from new aerial imagery '
'but in an m:n relationship). Lifecycle relates to the status of the building outline only. '
'See nz_building_outlines_lifecycle to determine recombined building relationships.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.begin_lifespan IS
'The date the building outline was added to NZ Building Outlines database.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.end_lifespan IS
'The date the building outline was removed, replaced or recombined within '
'the NZ Building Outlines database.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.last_modified IS
'The most recent date on which any attribute or geometry that is part of '
'the building outline was modified.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_all_sources.shape IS
'The geometry of the building outline, represented as a polygon using '
'NZTM2000 / EPSG 2193. Internal rings are possible, multiple external rings '
'are not.';

-- NZ Building Outlines : Lifecycle
-- The lifecycle table stores the relationship between buildings when one
-- building is split into two buildings or two buildings are merged into one
-- building. This will generally occur when a building outline was erroneously
-- captured encompassing two buildings, which later becomes clear with
-- additional aerial imagery.
CREATE TABLE IF NOT EXISTS buildings_lds.nz_building_outlines_lifecycle (
      lifecycle_id integer PRIMARY KEY
    , parent_building_id integer NOT NULL
    , building_id integer NOT NULL
);

COMMENT ON TABLE buildings_lds.nz_building_outlines_lifecycle IS
'The lifecycle table stores the relationship between buildings when one '
'building is split into two buildings or two buildings are merged into one '
'building. This will generally occur when a building outline was erroneously '
'captured encompassing two buildings, which later becomes clear with '
'additional aerial imagery.';

COMMENT ON COLUMN buildings_lds.nz_building_outlines_lifecycle.lifecycle_id IS
'Unique identifier for a lifecycle.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_lifecycle.parent_building_id IS
'Foreign key to the buildings_lds.nz_building_outlines_all_sources table. All '
'records stored as parent buildings will have a date in building_end_lifespan.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_lifecycle.building_id IS
'Foreign key to the buildings_lds.nz_building_outlines_all_sources table. '
'This is the child in the relationship - (one of) the building(s) that '
'replaced the parent building.' ;
