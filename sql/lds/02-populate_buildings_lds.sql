------------------------------------------------------------------------------
-- Populate buildings_lds schema in preparation for loading data to LDS
------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION buildings_lds.nz_building_outlines_insert()
RETURNS integer AS
$$

    WITH populate_nz_building_outlines AS (
        INSERT INTO buildings_lds.nz_building_outlines (
              building_outline_id
            , building_id
            , name
            , use
            , suburb_locality
            , town_city
            , territorial_authority
            , capture_method
            , capture_source
            , external_source_id
            , outline_begin_lifespan
            , building_begin_lifespan
            , name_begin_lifespan
            , use_begin_lifespan
            , shape
        )
        SELECT
              building_outlines.building_outline_id
            , building_outlines.building_id
            , building_name.building_name
            , use.value
            , suburb_locality.suburb_4th
            , town_city.name
            , territorial_authority.name
            , capture_method.value
            , capture_source_group.value
            , capture_source.external_source_id
            , building_outlines.begin_lifespan
            , buildings.begin_lifespan
            , building_name.begin_lifespan
            , building_use.begin_lifespan
            , building_outlines.shape
        FROM buildings.building_outlines
        JOIN buildings.buildings USING (building_id)
        LEFT JOIN buildings.building_name USING (building_id)
        LEFT JOIN buildings.building_use USING (building_id)
        LEFT JOIN buildings.use USING (use_id)
        JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
        JOIN buildings_common.capture_method USING (capture_method_id)
        JOIN buildings_common.capture_source USING (capture_source_id)
        JOIN buildings_common.capture_source_group USING (capture_source_group_id)
        JOIN buildings_admin_bdys.suburb_locality ON suburb_locality.suburb_locality_id = building_outlines.suburb_locality_id
        JOIN buildings_admin_bdys.town_city ON town_city.town_city_id = building_outlines.town_city_id
        JOIN buildings_admin_bdys.territorial_authority ON territorial_authority.territorial_authority_id = building_outlines.territorial_authority_id
        WHERE building_outlines.end_lifespan IS NULL
        AND buildings.end_lifespan IS NULL
        AND building_name.end_lifespan IS NULL
        AND building_use.end_lifespan IS NULL
        ORDER BY building_outlines.building_outline_id
        RETURNING *
    )
    SELECT count(*)::integer FROM populate_nz_building_outlines;

$$
LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION buildings_lds.nz_building_outlines_full_history_insert()
RETURNS integer AS
$$

    WITH populate_nz_building_outlines_full_history AS (
        INSERT INTO buildings_lds.nz_building_outlines_full_history (
              building_outline_id
            , building_id
            , name
            , use
            , suburb_locality
            , town_city
            , territorial_authority
            , capture_method
            , capture_source
            , external_source_id
            , building_lifecycle
            , record_begin_lifespan
            , record_end_lifespan
            , shape
        )
        WITH full_history AS (
            SELECT
                  building_outlines.building_outline_id
                , building_outlines.building_id
                , building_name.building_name As name
                , use.value AS use
                , greatest(building_outlines.begin_lifespan, buildings.begin_lifespan, building_name.begin_lifespan, building_use.begin_lifespan) AS record_begin_lifespan
                , least(building_outlines.end_lifespan, buildings.end_lifespan, building_name.end_lifespan, building_use.end_lifespan) AS record_end_lifespan
            FROM buildings.building_outlines
            JOIN buildings.buildings USING (building_id)
            LEFT JOIN buildings.building_name USING (building_id)
            LEFT JOIN buildings.building_use USING (building_id)
            LEFT JOIN buildings.use USING (use_id)
            GROUP BY
                  building_outlines.building_outline_id
                , building_outlines.building_id
                , building_name.building_name
                , use.value
                , building_outlines.begin_lifespan
                , building_outlines.end_lifespan
                , buildings.begin_lifespan
                , buildings.end_lifespan
                , building_name.begin_lifespan
                , building_name.end_lifespan
                , building_use.begin_lifespan
                , building_use.end_lifespan
        )
        SELECT
              full_history.building_outline_id
            , full_history.building_id
            , full_history.name
            , full_history.use
            , suburb_locality.suburb_4th
            , town_city.name
            , territorial_authority.name
            , capture_method.value
            , capture_source_group.value
            , capture_source.external_source_id
            , lifecycle_stage.value
            , full_history.record_begin_lifespan
            , full_history.record_end_lifespan
            , building_outlines.shape
        FROM full_history
        JOIN buildings.building_outlines USING (building_outline_id)
        JOIN buildings.buildings ON full_history.building_id = buildings.building_id
        JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
        JOIN buildings_common.capture_method USING (capture_method_id)
        JOIN buildings_common.capture_source USING (capture_source_id)
        JOIN buildings_common.capture_source_group USING (capture_source_group_id)
        JOIN buildings_admin_bdys.suburb_locality ON suburb_locality.suburb_locality_id = building_outlines.suburb_locality_id
        JOIN buildings_admin_bdys.town_city ON town_city.town_city_id = building_outlines.town_city_id
        JOIN buildings_admin_bdys.territorial_authority ON territorial_authority.territorial_authority_id = building_outlines.territorial_authority_id
        ORDER BY full_history.building_outline_id
        RETURNING *
    )
    SELECT count(*)::integer FROM populate_nz_building_outlines_full_history;

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
    TRUNCATE buildings_lds.nz_building_outlines_full_history;
    TRUNCATE buildings_lds.nz_building_outlines_lifecycle;

    VALUES 
          ('nz_building_outlines' , buildings_lds.nz_building_outlines_insert())
        , ('nz_building_outlines_full_history' , buildings_lds.nz_building_outlines_full_history_insert())
        , ('nz_building_outlines_lifecycle' , buildings_lds.nz_building_outlines_lifecycle_insert())
    ;

$$
LANGUAGE sql VOLATILE;
