-- Deploy nz-buildings:buildings/functions/add_update_facilities_attributes_functions to pg

BEGIN;

------------------------------------------------------------------------------
-- Update Facilities (hospitals and schools) attributes on Building Outlines
--
-- Prerequisites: - NZ Facilities buildings reference data has been updated
--                  to match the LDS layer, using the Buildings QGIS Plugin.
--                - Check NZ Facilities attribute errors, using:
--                      SELECT * FROM buildings_reference.facility_attribute_errors()
--                  This will find features with USE values that do not match those
--                  in buildings.use, and also features with null USE or NAME.
--                  Any errors detected will need to be manually corrected in
--                  NZ Facilities, prior to updating NZ Buildings attributes
--                  using this function.
--
-- This function can be run by using:
--     SELECT * FROM buildings.update_facilities_attributes()
------------------------------------------------------------------------------

------------------------------------------------------------------------------
-- BUILDING NAME MODIFY
-- Where building NAME does not match facility polygon NAME, modify building NAME.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_modify()
RETURNS integer AS
$$
    -- Select buildings and names intersecting facility polygons, excluding retired buildings
    WITH bo_intersects_fac AS (
        SELECT 
            building_id AS bo_building_id,
            building_name_id,
            building_name,
            bn_end_lifespan,
            fac.name AS fac_name,
            ST_Area(ST_Intersection(bo.shape, fac.shape)) / NULLIF(ST_Area(bo.shape), 0) AS bo_intersect_ratio
        FROM buildings_reference.nz_facilities fac
        JOIN (
            SELECT DISTINCT
                bo.building_id,
                bn.building_name_id,
                bn.building_name,
                bn.end_lifespan AS bn_end_lifespan,
                bo.shape
            FROM buildings.building_outlines bo
            JOIN buildings.building_name bn USING (building_id)
			WHERE bo.end_lifespan is NULL
        ) bo ON ST_Intersects(bo.shape, fac.shape)
    ),
    -- Filter buildings:
    --   - More than half the geometry within facility polygon
    --   - Has a different name to facility name
    --   - Has a current name
    bo_in_fac AS (
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
            AND building_name != fac_name
            AND bn_end_lifespan IS NULL
    ),
    -- Retire old building name
    updated AS (
        UPDATE buildings.building_name b_name
        SET end_lifespan = NOW()
        FROM bo_in_fac
        WHERE b_name.building_id = bo_in_fac.bo_building_id
    ),
    -- Add new building name 
    inserted AS (
		INSERT INTO buildings.building_name (building_name_id, building_id, building_name, begin_lifespan)
	    SELECT nextval('buildings.building_name_building_name_id_seq'),
	        bo_in_fac.bo_building_id,
	        bo_in_fac.fac_name,
	        NOW()
	    FROM bo_in_fac
	)
    -- Return count for reporting 
    SELECT count(*)::integer FROM bo_in_fac;
$$
LANGUAGE sql VOLATILE;


------------------------------------------------------------------------------
-- BUILDING USE MODIFY
-- Where building USE does not match facility polygon USE, modify building USE.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_use_modify()
RETURNS integer AS
$$
    -- Select buildings and uses intersecting facility polygons, excluding retired buildings
    WITH bo_intersects_fac AS (
        SELECT 
            building_id AS bo_building_id,
            building_use_id,
            use_value,
            bu_end_lifespan,
            fac.use AS fac_use,
            ST_Area(ST_Intersection(bo.shape, fac.shape)) / NULLIF(ST_Area(bo.shape), 0) AS bo_intersect_ratio
        FROM buildings_reference.nz_facilities fac
        JOIN (
            SELECT DISTINCT
                bo.building_id,
                bu.building_use_id,
                u.value AS use_value,
                bu.end_lifespan AS bu_end_lifespan,
                bo.shape
            FROM buildings.building_outlines bo
            JOIN buildings.building_use bu USING (building_id)
			JOIN buildings.use u USING (use_id)
			WHERE bo.end_lifespan is NULL
        ) bo ON ST_Intersects(bo.shape, fac.shape)
    ),
    -- Filter buildings:
    --   - More than half the geometry within facility polygon
    --   - Has a different use to facility use
    --   - Has a current use
    bo_in_fac AS (
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
            AND use_value != fac_use
            AND bu_end_lifespan IS NULL
    ),
    -- Retire old building use
    updated AS (
        UPDATE buildings.building_use b_use
        SET end_lifespan = NOW()
        FROM bo_in_fac
        WHERE b_use.building_id = bo_in_fac.bo_building_id
    ),
    -- Add new building use 
    inserted AS (
		INSERT INTO buildings.building_use (building_use_id, building_id, use_id, begin_lifespan)
	    SELECT nextval('buildings.building_use_building_use_id_seq'),
	        bo_in_fac.bo_building_id,
			(SELECT use_id FROM buildings.use WHERE use.value = bo_in_fac.fac_use),
	        NOW()
	    FROM bo_in_fac
	)
    -- Return count for reporting
    SELECT count(*)::integer FROM bo_in_fac;
$$
LANGUAGE sql VOLATILE;


------------------------------------------------------------------------------
-- BUILDING NAME ADD
-- Where building has no NAME and facility polygon has NAME, add building NAME.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_add()
RETURNS integer AS
$$
    -- Select buildings intersecting facility polygons, excluding retired buildings
    WITH bo_in_fac AS (
        WITH bo_intersects_fac AS (
            SELECT 
                building_id,
                fac.name AS fac_name,
                ST_Area(ST_Intersection(bo.shape, fac.shape)) / NULLIF(ST_Area(bo.shape), 0) AS bo_intersect_ratio
            FROM buildings_reference.nz_facilities fac
            JOIN (
                SELECT
                    bo.building_id,
                    bo.shape
                FROM buildings.building_outlines bo
                WHERE bo.end_lifespan is NULL
            ) bo ON ST_Intersects(bo.shape, fac.shape)
        )
        -- Filter buildings to those with more than half the geometry within facility polygon
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
    ),
    -- Join building name table using LEFT JOIN because building name will be empty
    building_name_joined AS (
    SELECT
        bo_in_fac.fac_name,
        bo_in_fac.building_id,
        bn.building_name_id,
        bn.building_name
    FROM bo_in_fac
    LEFT JOIN buildings.building_name bn USING (building_id)
    WHERE bn.building_name is NULL
    ),
    -- Add new building name 
    inserted AS (
        INSERT INTO buildings.building_name (building_name_id, building_id, building_name, begin_lifespan)
        SELECT nextval('buildings.building_name_building_name_id_seq'),
            building_name_joined.building_id,
            building_name_joined.fac_name,
            NOW()
        FROM building_name_joined
    )
    -- Return count for reporting 
    SELECT count(*)::integer FROM building_name_joined;
$$
LANGUAGE sql VOLATILE;


------------------------------------------------------------------------------
-- BUILDING USE ADD
-- Where building has no USE and facility polygon has USE, add building USE.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_use_add()
RETURNS integer AS
$$
    -- Select buildings intersecting facility polygons, excluding retired buildings
    WITH bo_in_fac AS (
        WITH bo_intersects_fac AS (
            SELECT 
                building_id,
                fac.use AS fac_use,
                ST_Area(ST_Intersection(bo.shape, fac.shape)) / NULLIF(ST_Area(bo.shape), 0) AS bo_intersect_ratio
            FROM buildings_reference.nz_facilities fac
            JOIN (
                SELECT
                    bo.building_id,
                    bo.shape
                FROM buildings.building_outlines bo
                WHERE bo.end_lifespan is NULL
            ) bo ON ST_Intersects(bo.shape, fac.shape)
        )
        -- Filter buildings to those with more than half the geometry within facility polygon
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
    ),
    -- Join building use table using LEFT JOIN because building use will be empty
    building_use_joined AS (
    SELECT
        bo_in_fac.fac_use,
        bo_in_fac.building_id,
        bu.building_use_id,
        u.value
    FROM bo_in_fac
    LEFT JOIN buildings.building_use bu USING (building_id)
    LEFT JOIN buildings.use u USING (use_id)
    WHERE bu.building_use_id is NULL
    ),
    -- Add new building use 
    inserted AS (
        INSERT INTO buildings.building_use (building_use_id, building_id, use_id, begin_lifespan)
        SELECT nextval('buildings.building_use_building_use_id_seq'),
            building_use_joined.building_id,
            (SELECT use_id FROM buildings.use WHERE use.value = building_use_joined.fac_use),
            NOW()
        FROM building_use_joined
    )
    -- Return count for reporting 
    SELECT count(*)::integer FROM building_use_joined;
$$
LANGUAGE sql VOLATILE;


------------------------------------------------------------------------------
-- BUILDING NAME/USE REMOVE
-- Where building has NAME/USE with no matching facility polygon, remove NAME/USE.
-- Only remove NAME/USE for USE types included in NZ Facilities, currently
-- these are Hospitals and Schools.  Other USE types do not have corresponding
-- facility polygons to compare, so removal of NAME and USE needs to be in the same
-- function.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_use_remove()
RETURNS integer AS
$$
    -- Select buildings with a use that is included in NZ Facilities, excluding retired uses and retired buildings
    WITH bo_has_use AS (
        SELECT
            building_id,
            bn.building_name_id AS bn_building_name_id,
            bn.building_name AS bn_building_name,
            bu.building_use_id AS bu_building_use_id,
            u.value AS u_value,
            bo.shape
        FROM buildings.building_outlines bo
        JOIN buildings.building_name bn USING (building_id)
        JOIN buildings.building_use bu USING (building_id)
        JOIN buildings.use u USING (use_id)
        WHERE u.use_id IN (16,27) -- use_id 16 = Hospital, 27 = School
            AND bu.end_lifespan IS NULL
            AND bo.end_lifespan IS NULL
    ),
    -- Join facility polygons using intersects and LEFT JOIN because we want to include those with no intersect
    bo_outside_fac AS (
    SELECT 
        building_id,
        bn_building_name_id,
        bn_building_name,
        bu_building_use_id,
        u_value,
        bo.shape
    FROM bo_has_use bo
    LEFT JOIN buildings_reference.nz_facilities f
    ON ST_Intersects(bo.shape, f.shape)
    GROUP BY building_id,
            bn_building_name_id,
            bn_building_name,
            bu_building_use_id,
            u_value,
            bo.shape
    -- Filter buildings to those that don't intersect, or are less than half within, facility polygons
    HAVING 
        COALESCE(SUM(ST_Area(ST_Intersection(bo.shape, f.shape))) / NULLIF(ST_Area(bo.shape), 0), 0) < 0.5
    ),
    -- Remove building name
    remove_name AS (
        UPDATE buildings.building_name b_name
        SET end_lifespan = NOW()
        FROM bo_outside_fac
        WHERE b_name.building_id = bo_outside_fac.building_id
            AND b_name.end_lifespan is NULL
    ),
    -- Remove building use
    remove_use AS (
        UPDATE buildings.building_use b_use
        SET end_lifespan = NOW()
        FROM bo_outside_fac
        WHERE b_use.building_id = bo_outside_fac.building_id
            AND b_use.end_lifespan is NULL
    )
    -- Return count for reporting 
    SELECT count(*)::integer FROM bo_outside_fac;
$$
LANGUAGE sql VOLATILE;


------------------------------------------------------------------------------
-- UPDATE FACILITIES ATTRIBUTES
-- Wrapper to run all update facilities functions.
-- Returns a table with each update type and the count of buildings updated.
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings.update_facilities_attributes()
RETURNS TABLE(update_type text, count integer) AS
$$
BEGIN

	RETURN QUERY
    SELECT 'Building NAME modified'::text AS update_type,
	buildings.update_facilities_name_modify()::integer AS count;

	RETURN QUERY
    SELECT 'Building USE modified'::text AS update_type,
	buildings.update_facilities_use_modify()::integer AS count;

    RETURN QUERY
    SELECT 'Building NAME added'::text AS update_type,
	buildings.update_facilities_name_add()::integer AS count;

    RETURN QUERY
    SELECT 'Building USE added'::text AS update_type,
	buildings.update_facilities_use_add()::integer AS count;

    RETURN QUERY
    SELECT 'Building NAME/USE removed'::text AS update_type,
	buildings.update_facilities_name_use_remove()::integer AS count;
    
	
END;
$$
LANGUAGE plpgsql VOLATILE;

COMMIT;
