--------------------------------------------------------------------------
-- SUBURB INTERSECTION- find the id of the suburb that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.nz_locality_suburb_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    
    SELECT   nzl.id
    FROM     buildings_admin_bdys.nz_locality nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , ST_Transform(ST_SETSRID(nzl.shape, 2193),2193)
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , ST_Transform(ST_SETSRID(nzl.shape,2193), 2193)
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- SUBURB INTERSECTION- Replace the suburb values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.bulk_load_outlines_update_suburb(integer)
RETURNS integer AS
$$

    WITH update_suburb AS(
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET suburb_locality_id = nzl_intersect.nz_locality_suburb_intersect_polygon
        FROM (
            SELECT buildings.nz_locality_suburb_intersect_polygon(outlines.shape), outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) nzl_intersect
        WHERE outlines.bulk_load_outline_id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_suburb;

$$
LANGUAGE sql VOLATILE;

--------------------------------------------------------------------------
-- TOWN/CITY INTERSECTION- find the id of the town/city that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.nz_locality_town_city_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS numeric(10,0) AS
$$
    
    SELECT   nzl.city_id
    FROM     buildings_admin_bdys.nz_locality nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , ST_Transform(ST_SETSRID(nzl.shape,2193),2193)
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , ST_Transform(ST_SETSRID(nzl.shape,2193),2193)
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- TOWN/CITY INTERSECTION- Replace the town/city values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.bulk_load_outlines_update_town_city(integer)
RETURNS integer AS
$$
    
    WITH update_town_city AS(
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET town_city_id = nzl_intersect.nz_locality_town_city_intersect_polygon
        FROM (
            SELECT buildings.nz_locality_town_city_intersect_polygon(outlines.shape), outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) nzl_intersect
        WHERE outlines.bulk_load_outline_id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = $1
        RETURNING *
    )
    SELECT count(*)::integer FROM update_town_city;

$$
LANGUAGE sql VOLATILE;

--------------------------------------------------------------------------
-- TERRITORIAL AUTHORITY INTERSECTION- find the id of the TA that has the most overlap with
-- the provided building outline
--------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.territorial_authority_intersect_polygon(
    p_polygon_geometry geometry
)
RETURNS integer AS
$$
    
    SELECT   nzl.ogc_fid
    FROM     buildings_admin_bdys.territorial_authority nzl
    WHERE    ST_Intersects(
                   p_polygon_geometry
                 , ST_Transform(ST_SETSRID(nzl.shape,2193),2193)
             )
    ORDER BY ST_Area( 
                 ST_Intersection( 
                       p_polygon_geometry
                     , ST_Transform(ST_SETSRID(nzl.shape,2193),2193)
                 ) 
             ) / ST_Area(nzl.shape) DESC
    LIMIT    1;

$$
LANGUAGE sql VOLATILE;

-------------------------------------------------------------------------
-- TERRITORIAL AUTHORITY INTERSECTION- Replace the TA values with the intersection result
-- returns number of building outlines updated
-------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.bulk_load_outlines_update_territorial_authority(integer)
RETURNS integer AS
$$

    WITH update_territorial_auth AS(
        UPDATE buildings_bulk_load.bulk_load_outlines outlines
        SET territorial_authority_id = nzl_intersect.territorial_authority_intersect_polygon
        FROM (
            SELECT buildings.territorial_authority_intersect_polygon(outlines.shape), outlines.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines outlines
        ) nzl_intersect
        WHERE outlines.bulk_load_outline_id = nzl_intersect.bulk_load_outline_id AND outlines.supplied_dataset_id = $1
        RETURNING $1
    )
    SELECT count(*)::integer FROM update_territorial_auth;

$$
LANGUAGE sql VOLATILE;
