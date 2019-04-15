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
            , capture_source
            , external_source_id
            , building_begin_lifespan
            , name_begin_lifespan
            , use_begin_lifespan
            , shape
        )
        SELECT
              building_outlines.building_id
            , building_name.building_name
            , use.value
            , suburb_locality.suburb_4th
            , town_city.name
            , territorial_authority.name
            , capture_method.value
            , capture_source_group.value
            , capture_source.external_source_id
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
        JOIN buildings_reference.suburb_locality ON suburb_locality.suburb_locality_id = building_outlines.suburb_locality_id
        LEFT JOIN buildings_reference.town_city ON town_city.town_city_id = building_outlines.town_city_id
        JOIN buildings_reference.territorial_authority ON territorial_authority.territorial_authority_id = building_outlines.territorial_authority_id
        WHERE building_outlines.end_lifespan IS NULL
        AND buildings.end_lifespan IS NULL
        AND building_name.end_lifespan IS NULL
        AND building_use.end_lifespan IS NULL
        ORDER BY buildings.building_id
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
        WITH events AS (
            SELECT building_id, begin_lifespan AS change
            FROM buildings.buildings
            UNION
            SELECT building_id, end_lifespan AS change
            FROM buildings.buildings
            UNION
            SELECT building_id, begin_lifespan AS change
            FROM buildings.building_outlines
            UNION
            SELECT building_id, end_lifespan AS change
            FROM buildings.building_outlines
            UNION
            SELECT building_id, begin_lifespan AS change
            FROM buildings.building_name
            UNION
            SELECT building_id, end_lifespan AS change
            FROM buildings.building_name
            UNION
            SELECT building_id, begin_lifespan AS change
            FROM buildings.building_use
            UNION
            SELECT building_id, end_lifespan AS change
            FROM buildings.building_use
            ORDER BY 1, 2
        ), unique_events AS (
            SELECT
                  row_number() OVER() AS change_id
                , *
            FROM events
        ), record_dates AS (
            SELECT
                  a.building_id
                , a.change AS record_begin_lifespan
                , b.change AS record_end_lifespan
            FROM unique_events a
            JOIN unique_events b USING (building_id)
            WHERE (a.change_id + 1) = b.change_id
        )
        SELECT
              bo.building_outline_id
            , rd.building_id
            , bn.building_name
            , u.value
            , suburb_locality.suburb_4th
            , town_city.name
            , territorial_authority.name
            , capture_method.value
            , capture_source_group.value
            , capture_source.external_source_id
            , lifecycle_stage.value
            , rd.record_begin_lifespan
            , rd.record_end_lifespan
            , bo.shape
        FROM record_dates rd
        JOIN buildings.buildings b ON rd.building_id = b.building_id
            AND rd.record_begin_lifespan >= b.begin_lifespan
            AND COALESCE(rd.record_end_lifespan, now()) <= COALESCE(b.end_lifespan, now())
        JOIN buildings.building_outlines bo ON rd.building_id = bo.building_id
            AND rd.record_begin_lifespan >= bo.begin_lifespan
            AND COALESCE(rd.record_end_lifespan, now()) <= COALESCE(bo.end_lifespan, now())
        JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
        JOIN buildings_common.capture_method USING (capture_method_id)
        JOIN buildings_common.capture_source USING (capture_source_id)
        JOIN buildings_common.capture_source_group USING (capture_source_group_id)
        JOIN buildings_reference.suburb_locality ON suburb_locality.suburb_locality_id = bo.suburb_locality_id
        LEFT JOIN buildings_reference.town_city ON town_city.town_city_id = bo.town_city_id
        JOIN buildings_reference.territorial_authority ON territorial_authority.territorial_authority_id = bo.territorial_authority_id
        LEFT JOIN buildings.building_name bn ON rd.building_id = bn.building_id
            AND rd.record_begin_lifespan >= bn.begin_lifespan
            AND COALESCE(rd.record_end_lifespan, now()) <= COALESCE(bn.end_lifespan, now())
        LEFT JOIN buildings.building_use bu ON rd.building_id = bu.building_id
            AND rd.record_begin_lifespan >= bu.begin_lifespan
            AND COALESCE(rd.record_end_lifespan, now()) <= COALESCE(bu.end_lifespan, now())
        LEFT JOIN buildings.use u USING (use_id)
        ORDER BY bo.building_outline_id, rd.record_begin_lifespan
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
