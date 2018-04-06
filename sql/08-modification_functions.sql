--------------------------------------------------------------------------
-- SUBURB INTERSECTION- find the id of the suburb that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_suburb_locality_intersect_poly(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    
    SELECT   nzl.id
    FROM     admin_bdys.nz_locality nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , nzl.shape
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , nzl.shape
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql STABLE;

-------------------------------------------------------------------------
-- SUBURB INTERSECTION- Replace the suburb values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_bulk_load_outlines_update_suburb(p_supplied_dataset_id integer)
RETURNS integer AS
$$

DECLARE
    v_rows_updated integer;

BEGIN

    UPDATE buildings_bulk_load.bulk_load_outlines outlines
    SET suburb_locality_id = nzl_intersect.fn_suburb_locality_intersect_poly
    FROM (
        SELECT buildings.fn_suburb_locality_intersect_poly(outlines.shape), outlines.id
        FROM buildings_bulk_load.bulk_load_outlines outlines
    ) nzl_intersect
    WHERE outlines.id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = p_supplied_dataset_id;

    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;

    RETURN v_rows_updated;

END;

$$
LANGUAGE plpgsql;

--------------------------------------------------------------------------
-- TOWN/CITY INTERSECTION- find the id of the town/city that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_town_city_locality_intersect_poly(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    
    SELECT   nzl.city_id
    FROM     admin_bdys.nz_locality nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , nzl.shape
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , nzl.shape
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql STABLE;

-------------------------------------------------------------------------
-- TOWN/CITY INTERSECTION- Replace the town/city values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_bulk_load_outlines_update_town_city(p_supplied_dataset_id integer)
RETURNS integer AS
$$

DECLARE
    v_rows_updated integer;

BEGIN

    UPDATE buildings_bulk_load.bulk_load_outlines outlines
    SET town_city_id = nzl_intersect.fn_town_city_locality_intersect_poly
    FROM (
        SELECT buildings.fn_town_city_locality_intersect_poly(outlines.shape), outlines.id
        FROM buildings_bulk_load.bulk_load_outlines outlines
    ) nzl_intersect
    WHERE outlines.id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = p_supplied_dataset_id;

    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;

    RETURN v_rows_updated;

END;

$$
LANGUAGE plpgsql;

--------------------------------------------------------------------------
-- TERRITORIAL AUTHORITY INTERSECTION- find the id of the TA that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_territorial_authority_locality_intersect_poly(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    
    SELECT   nzl.ogc_fid
    FROM     admin_bdys.territorial_authority nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , nzl.shape
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , nzl.shape
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql STABLE;

-------------------------------------------------------------------------
-- TERRITORIAL AUTHORITY INTERSECTION- Replace the TA values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_bulk_load_outlines_update_territorial_authority(p_supplied_dataset_id integer)
RETURNS integer AS
$$

DECLARE
    v_rows_updated integer;

BEGIN

    UPDATE buildings_bulk_load.bulk_load_outlines outlines
    SET town_city_id = nzl_intersect.fn_territorial_authority_locality_intersect_poly
    FROM (
        SELECT buildings.fn_territorial_authority_locality_intersect_poly(outlines.shape), outlines.id
        FROM buildings_bulk_load.bulk_load_outlines outlines
    ) nzl_intersect
    WHERE outlines.id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = p_supplied_dataset_id;

    GET DIAGNOSTICS v_rows_updated = ROW_COUNT;

    RETURN v_rows_updated;

END;

$$
LANGUAGE plpgsql;

-------------------------------------------------------------------
--BUILDINGS insert into
-------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_buildings_insert()
RETURNS integer AS
$$

    INSERT INTO buildings.buildings(
          building_id
        , begin_lifespan
    )
    VALUES (
          DEFAULT -- sequence
        , DEFAULT -- now()
    )
    RETURNING building_id;

$$
LANGUAGE sql STABLE;

----------------------------------------------------------------
-- BUILDING OUTLINES insert into
----------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.fn_building_outlines_insert(
      p_building_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_lifecycle_stage_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
    , p_begin_lifespan timestamptz
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings.building_outlines(
          building_outline_id
        , building_id
        , capture_method_id
        , capture_source_id
        , lifecycle_stage_id
        , suburb_locality_id
        , town_city_id
        , territorial_authority_id
        , begin_lifespan
        , shape
    )
    VALUES (
          DEFAULT -- sequence
        , p_building_id
        , p_capture_method_id
        , p_capture_source_id
        , p_lifecycle_stage_id
        , p_suburb_locality_id
        , p_town_city_id
        , p_territorial_authority_id
        , p_begin_lifespan
        , p_shape
    )
    RETURNING building_outline_id;

$$
LANGUAGE sql STABLE;

-------------------------------------------------------------------------
-- BULK LOAD OUTLINES insert into
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_insert(
      p_supplied_dataset_id integer
    , p_external_outline_id integer
    , p_bulk_load_status_id integer
    , p_capture_method_id integer
    , p_capture_source_id integer
    , p_suburb_locality_id integer
    , p_town_city_id integer
    , p_territorial_authority_id integer
    , p_begin_lifespan timestamptz
    , p_shape geometry
)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.bulk_load_outlines(
          bulk_load_outline_id
        , supplied_dataset_id
        , external_outline_id
        , bulk_load_status_id
        , capture_method_id
        , capture_source_id
        , suburb_locality_id
        , town_city_id
        , territorial_authority_id
        , begin_lifespan
        , shape
    )
    VALUES (
          DEFAULT -- sequence
        , p_supplied_dataset_id
        , p_external_outline_id
        , p_bulk_load_status_id
        , p_capture_method_id
        , p_capture_source_id
        , NULL --p_suburb_locality_id
        , NULL --p_town_city_id
        , NULL --p_territorial_authority_id
        , NULL --p_begin_lifespan
        , p_shape
    )
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql STABLE;