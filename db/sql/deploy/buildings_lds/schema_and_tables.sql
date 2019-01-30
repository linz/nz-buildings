-- Deploy buildings:buildings_lds/schema_and_tables to pg

BEGIN;

------------------------------------------------------------------------------
-- Create buildings LDS schema and tables

-- Tables:
-- nz_building_outlines
-- nz_building_outlines_full_history
-- nz_building_outlines_lifecycle

------------------------------------------------------------------------------

SET client_min_messages TO WARNING;

CREATE SCHEMA buildings_lds;

COMMENT ON SCHEMA buildings_lds IS
'Schema that holds tables published via the LINZ Data Service.';

-- NZ Building Outlines
-- NZ Building Outlines contains the current depiction of building outlines.
CREATE TABLE buildings_lds.nz_building_outlines (
      building_outline_id integer NOT NULL
    , building_id integer NOT NULL
    , name character varying(250)
    , use character varying(40)
    , suburb_locality character varying(80) NOT NULL
    , town_city character varying(80)
    , territorial_authority character varying(80) NOT NULL
    , capture_method character varying(250) NOT NULL
    , capture_source character varying(250) NOT NULL
    , external_source_id character varying(250)
    , outline_begin_lifespan timestamptz NOT NULL
    , building_begin_lifespan timestamptz NOT NULL
    , name_begin_lifespan timestamptz
    , use_begin_lifespan timestamptz
    , shape public.geometry(Polygon, 2193) NOT NULL
);

COMMENT ON TABLE buildings_lds.nz_building_outlines IS
'NZ Building Outlines contains the current depiction of building outlines.';

COMMENT ON COLUMN buildings_lds.nz_building_outlines.building_outline_id IS
'Unique identifier for the building outline. The building outline id is unique '
'to one representation of a building.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.building_id IS
'Unique identifier for a building. The building id is persistant for the same '
'building across all of the building outlines that represent it.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.name IS
'The name of the building, where known.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.use IS
'The building use, maintained for the Topo50 map series.';
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
'The method by which the geometry was captured.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.capture_source IS
'The source from which the geometry was captured.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.external_source_id IS
'An externally managed identifier that relates the building outline to its '
'source.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.outline_begin_lifespan IS
'The date that the building outline was added to the system.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.building_begin_lifespan IS
'The date that the building was added to the system.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.name_begin_lifespan IS
'The date that the name was added to the system.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.use_begin_lifespan IS
'The date that the use was added to the system.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines.shape IS
'The geometry of the building outline, represented as a polygon using '
'NZTM2000 / EPSG 2193. Internal rings are possible, multiple external rings '
'are not.';

-- NZ Building Outlines : Full History
-- NZ Building Outlines: Full History contains all combinations of outline /
-- building / name / use that have existed within the building outlines
-- system, and the dates for which that combination existed.
CREATE TABLE buildings_lds.nz_building_outlines_full_history (
      extract_id serial PRIMARY KEY
    , building_outline_id integer NOT NULL
    , building_id integer NOT NULL
    , name character varying(250)
    , use character varying(40)
    , suburb_locality character varying(80) NOT NULL
    , town_city character varying(80)
    , territorial_authority character varying(80) NOT NULL
    , capture_method character varying(250) NOT NULL
    , capture_source character varying(250) NOT NULL
    , external_source_id character varying(250)
    , building_lifecycle character varying(40) NOT NULL
    , record_begin_lifespan timestamptz NOT NULL
    , record_end_lifespan timestamptz
    , shape public.geometry(Polygon, 2193) NOT NULL
);

COMMENT ON TABLE buildings_lds.nz_building_outlines_full_history IS
'NZ Building Outlines: Full History contains all combinations of outline / '
'building / name / use that have existed within the building outlines '
'system, and the dates for which that combination existed. ';

COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.extract_id IS
'Unique identifier for the full history extract from the building outlines '
'system. This identifier is required by the LINZ Data Service in order to '
'determine changesets.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.building_outline_id IS
'Unique identifier for the building outline. The building outline id is unique '
'to one representation of a building.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.building_id IS
'Unique identifier for a building. The building id is persistant for the same '
'building across all of the building outlines that represent it.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.name IS
'The name of the building, where known.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.use IS
'The building use, maintained for the Topo50 map series.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.suburb_locality IS
'The suburb / locality that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.town_city IS
'The town / city that the majority of the building outline is within. '
'Sourced from NZ Localities (an NZ Fire Service owned dataset).';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.territorial_authority IS
'The territorial authority that the majority of the building outline is '
'within. Sourced from Stats NZ.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.capture_method IS
'The method by which the geometry was captured.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.capture_source IS
'The source from which the geometry was captured.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.external_source_id IS
'An externally managed identifier that relates the building outline to its '
'source.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.building_lifecycle IS
'The lifecycle of the building. Note that the lifecycle may be "Current" even '
'though there is a more recent record for the building (with a new building '
'outline, for example). Lifecycle relates to the status of the building only. '
'See nz_building_outlines_lifecycle to determine building relationships.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.record_begin_lifespan IS
'The date that this combination of attributes became current in the system.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.record_end_lifespan IS
'The date that this combination of attributes was ended dated in the system. '
'Current records will not have an end date.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_full_history.shape IS
'The geometry of the building outline, represented as a polygon using '
'NZTM2000 / EPSG 2193. Internal rings are possible, multiple external rings '
'are not.';

-- NZ Building Outlines : Lifecycle
-- The lifecycle table stores the relationship between buildings when one
-- building is split into two buildings or two buildings are merged into one
-- building. This will generally occur when a building outline was erroneously
-- captured encompassing two buildings, which later becomes clear with
-- additional aerial imagery.
CREATE TABLE buildings_lds.nz_building_outlines_lifecycle (
      lifecycle_id integer NOT NULL
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
'Foreign key to the buildings_lds.nz_building_outlines_full_history table. All '
'records stored as parent buildings will have a date in building_end_lifespan.';
COMMENT ON COLUMN buildings_lds.nz_building_outlines_lifecycle.building_id IS
'Foreign key to the buildings_lds.nz_building_outlines_full_history table. '
'This is the child in the relationship - (one of) the building(s) that '
'replaced the parent building.' ;

COMMIT;
