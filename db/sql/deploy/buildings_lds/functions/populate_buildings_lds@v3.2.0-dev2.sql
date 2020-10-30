-- Deploy nz-buildings:buildings_lds/functions/populate_buildings_lds to pg

BEGIN;

------------------------------------------------------------------------------
-- Populate buildings_lds schema in preparation for loading data to LDS
------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION buildings_lds.nz_building_outlines_insert()
RETURNS integer AS
$$

    WITH populate_nz_building_outlines AS (
        INSERT INTO buildings_lds.nz_building_outlines (
              building_id
            , name
            , use
            , suburb_locality
            , town_city
            , territorial_authority
            , capture_method
            , capture_source_group
            , capture_source_id
            , capture_source_name
            , capture_source_from
            , capture_source_to
            , last_modified
            , shape
        )
        SELECT
              buildings.building_id
            , COALESCE(building_name.building_name, '') AS name
            , COALESCE(use.value, 'Unknown') AS use
            , COALESCE(suburb_locality.suburb_4th, suburb_locality.suburb_3rd, suburb_locality.suburb_2nd, suburb_locality.suburb_1st) AS suburb_locality
            , COALESCE(town_city.name, '') AS town_city
            , territorial_authority.name AS territorial_authority
            , capture_method.value AS capture_method
            , capture_source_group.value AS capture_source_group
            , LEFT(capture_source.external_source_id, 4)::integer AS capture_source_id
            , nz_imagery_survey_index.name AS capture_source_name
            , nz_imagery_survey_index.flown_from AS capture_source_from
            , nz_imagery_survey_index.flown_to AS capture_source_to
            , GREATEST(building_outlines.begin_lifespan, COALESCE(building_outlines.end_lifespan, '1900-01-01 00:00:00'), COALESCE(building_outlines.last_modified, '1900-01-01 00:00:00'))::date AS last_modified
            , building_outlines.shape
        FROM buildings.building_outlines
        JOIN buildings.buildings USING (building_id)
        LEFT JOIN buildings.building_name ON buildings.building_id = building_name.building_id
        AND building_name.end_lifespan IS NULL
        LEFT JOIN buildings.building_use ON buildings.building_id = building_use.building_id
        AND building_use.end_lifespan IS NULL
        LEFT JOIN buildings.use USING (use_id)
        JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
        JOIN buildings_common.capture_method USING (capture_method_id)
        JOIN buildings_common.capture_source USING (capture_source_id)
        JOIN aerial_lds.nz_imagery_survey_index ON LEFT(capture_source.external_source_id, 4)::integer = nz_imagery_survey_index.imagery_survey_id
        JOIN buildings_common.capture_source_group USING (capture_source_group_id)
        JOIN buildings_reference.suburb_locality ON suburb_locality.suburb_locality_id = building_outlines.suburb_locality_id
        LEFT JOIN buildings_reference.town_city ON town_city.town_city_id = building_outlines.town_city_id
        JOIN buildings_reference.territorial_authority ON territorial_authority.territorial_authority_id = building_outlines.territorial_authority_id
        WHERE building_outlines.end_lifespan IS NULL
        AND buildings.end_lifespan IS NULL
        ORDER BY buildings.building_id
        RETURNING *
    )
    SELECT count(*)::integer FROM populate_nz_building_outlines;

$$
LANGUAGE sql VOLATILE;


CREATE OR REPLACE FUNCTION buildings_lds.nz_building_outlines_all_sources_insert()
RETURNS integer AS
$$

    WITH populate_nz_building_outlines_all_sources AS (
        INSERT INTO buildings_lds.nz_building_outlines_all_sources (
              building_outline_id
            , building_id
            , name
            , use
            , suburb_locality
            , town_city
            , territorial_authority
            , capture_method
            , capture_source_group
            , capture_source_id
            , capture_source_name
            , capture_source_from
            , capture_source_to
            , building_outline_lifecycle
            , begin_lifespan
            , end_lifespan
            , last_modified
            , shape
        )
        WITH transfer_dates AS (
            SELECT DISTINCT transfer_date
            FROM buildings_bulk_load.supplied_datasets
        )
        , deleted_in_production AS (
            SELECT building_outlines.building_outline_id, supplied_datasets.processed_date, supplied_datasets.transfer_date, building_outlines.begin_lifespan, building_outlines.end_lifespan
            FROM buildings.building_outlines
            JOIN buildings_bulk_load.transferred ON building_outlines.building_outline_id = transferred.new_building_outline_id
            JOIN buildings_bulk_load.bulk_load_outlines USING (bulk_load_outline_id)
            JOIN buildings_bulk_load.supplied_datasets USING (supplied_dataset_id)
            WHERE building_outlines.end_lifespan IS NOT NULL
            AND building_outlines.end_lifespan NOT IN (
                SELECT transfer_date
                FROM transfer_dates
            )
        )
        , removed AS (
            SELECT b1.building_outline_id
            FROM buildings.building_outlines b1
            LEFT JOIN buildings.building_outlines b2 ON b1.building_id = b2.building_id AND b1.building_outline_id != b2.building_outline_id AND b2.end_lifespan IS NULL
            LEFT JOIN buildings.lifecycle l ON b1.building_id = l.parent_building_id
            LEFT JOIN deleted_in_production d ON b1.building_outline_id = d.building_outline_id
            WHERE b1.end_lifespan IS NOT NULL
            AND b2.building_outline_id IS NULL
            AND l.parent_building_id IS NULL
            AND d.building_outline_id IS NULL
        )
        , replaced AS (
            SELECT b1.building_outline_id
            FROM buildings.building_outlines b1
            JOIN buildings.building_outlines b2 ON b1.building_id = b2.building_id AND b1.building_outline_id != b2.building_outline_id AND b1.end_lifespan = b2.begin_lifespan AND b2.end_lifespan IS NULL
            WHERE b1.end_lifespan IS NOT NULL
        )
        , recombined AS (
            SELECT b.building_outline_id
            FROM buildings.building_outlines b
            JOIN buildings.lifecycle l ON b.building_id = l.parent_building_id
            WHERE b.end_lifespan IS NOT NULL
        )
        , building_outline_lifecycle AS (
            SELECT building_outline_id, 'Removed' AS status
            FROM removed
            UNION
            SELECT building_outline_id, 'Replaced' AS status
            FROM replaced
            UNION
            SELECT building_outline_id, 'Recombined' AS status
            FROM recombined
        )
        SELECT
              building_outlines.building_outline_id
            , buildings.building_id
            , COALESCE(building_name.building_name, '') AS name
            , COALESCE(use.value, 'Unknown') AS use
            , COALESCE(suburb_locality.suburb_4th, suburb_locality.suburb_3rd, suburb_locality.suburb_2nd, suburb_locality.suburb_1st) AS suburb_locality
            , COALESCE(town_city.name, '') AS town_city
            , territorial_authority.name AS territorial_authority
            , capture_method.value AS capture_method
            , capture_source_group.value AS capture_source_group
            , LEFT(capture_source.external_source_id, 4)::integer AS capture_source_id
            , nz_imagery_survey_index.name AS capture_source_name
            , nz_imagery_survey_index.flown_from AS capture_source_from
            , nz_imagery_survey_index.flown_to AS capture_source_to
            , COALESCE(building_outline_lifecycle.status, 'Current') AS building_outline_lifecycle
            , building_outlines.begin_lifespan::date AS begin_lifespan
            , building_outlines.end_lifespan::date AS end_lifespan
            , GREATEST(building_outlines.begin_lifespan, COALESCE(building_outlines.end_lifespan, '1900-01-01 00:00:00'), COALESCE(building_outlines.last_modified, '1900-01-01 00:00:00'))::date AS last_modified
            , building_outlines.shape
        FROM buildings.building_outlines
        JOIN buildings.buildings USING (building_id)
        LEFT JOIN buildings.building_name ON buildings.building_id = building_name.building_id
        AND building_name.end_lifespan IS NULL
        LEFT JOIN buildings.building_use ON buildings.building_id = building_use.building_id
        AND building_use.end_lifespan IS NULL
        LEFT JOIN buildings.use USING (use_id)
        JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
        JOIN buildings_common.capture_method USING (capture_method_id)
        JOIN buildings_common.capture_source USING (capture_source_id)
        JOIN aerial_lds.nz_imagery_survey_index ON LEFT(capture_source.external_source_id, 4)::integer = nz_imagery_survey_index.imagery_survey_id
        JOIN buildings_common.capture_source_group USING (capture_source_group_id)
        JOIN buildings_reference.suburb_locality ON suburb_locality.suburb_locality_id = building_outlines.suburb_locality_id
        LEFT JOIN buildings_reference.town_city ON town_city.town_city_id = building_outlines.town_city_id
        JOIN buildings_reference.territorial_authority ON territorial_authority.territorial_authority_id = building_outlines.territorial_authority_id
        LEFT JOIN deleted_in_production USING (building_outline_id)
        LEFT JOIN building_outline_lifecycle USING (building_outline_id)
        ORDER BY building_outlines.building_outline_id
        RETURNING *
        )
    SELECT count(*)::integer FROM populate_nz_building_outlines_all_sources;

$$
LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION buildings_lds.nz_building_outlines_lifecycle_insert()
RETURNS integer AS
$$

    WITH populate_nz_building_outlines_lifecycle AS (
        INSERT INTO buildings_lds.nz_building_outlines_lifecycle (
              lifecycle_id
            , parent_building_id
            , building_id
        )
        SELECT
              lifecycle_id
            , parent_building_id
            , building_id
        FROM buildings.lifecycle
        RETURNING *
    )
    SELECT count(*)::integer FROM populate_nz_building_outlines_lifecycle;

$$
LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION buildings_lds.populate_buildings_lds()
RETURNS TABLE(
      table_name text
    , rows_inserted integer
) AS
$$

    TRUNCATE buildings_lds.nz_building_outlines;
    TRUNCATE buildings_lds.nz_building_outlines_all_sources;
    TRUNCATE buildings_lds.nz_building_outlines_lifecycle;

    VALUES
          ('nz_building_outlines' , buildings_lds.nz_building_outlines_insert())
        , ('nz_building_outlines_all_sources' , buildings_lds.nz_building_outlines_all_sources_insert())
        , ('nz_building_outlines_lifecycle' , buildings_lds.nz_building_outlines_lifecycle_insert())
    ;

$$
LANGUAGE sql VOLATILE;

COMMIT;
