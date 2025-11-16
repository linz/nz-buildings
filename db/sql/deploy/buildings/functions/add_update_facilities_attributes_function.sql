-- Deploy nz-buildings:buildings/functions/add_update_facilities_attributes_functions to pg

BEGIN;

------------------------------------------------------------------------------
-- Update Facilities (hospitals and schools) attributes on Building Outlines
--
-- Assumes:       - NZ Facilities is current on the LINZ Data Service (LDS).
-- Prerequisites: - NZ Facilities buildings reference data has been updated
--                  to match the LDS layer, using the Buildings QGIS Plugin.
--                - Check NZ Facilities USE values match those in the buildings.use 
--                  table, using <process>. This is required because NZ Buildings
--                  have coded values for USE. If there are errors, then NZ Facilities
--                  might need to be corrected first.
--
------------------------------------------------------------------------------

-- TODO - Add separate check before this step to check all facility USEs are
--        matching buildings.use values corresponding to USE_IDs.
--      - Add comments


-- BUILDING NAME MODIFY
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_modify()
RETURNS integer AS
$$
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
    bo_in_fac AS (
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
            AND building_name != fac_name
            AND bn_end_lifespan IS NULL
    ),
    updated AS (
        UPDATE buildings.building_name b_name
        SET end_lifespan = NOW()
        FROM bo_in_fac
        WHERE b_name.building_id = bo_in_fac.bo_building_id
    ),
    inserted AS (
		INSERT INTO buildings.building_name (building_name_id, building_id, building_name, begin_lifespan)
	    SELECT nextval('buildings.building_name_building_name_id_seq'),
	        bo_in_fac.bo_building_id,
	        bo_in_fac.fac_name,
	        NOW()
	    FROM bo_in_fac
	)
    SELECT count(*)::integer FROM bo_in_fac;
$$
LANGUAGE sql VOLATILE;


-- BUILDING USE MODIFY
CREATE OR REPLACE FUNCTION buildings.update_facilities_use_modify()
RETURNS integer AS
$$
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
    bo_in_fac AS (
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
            AND use_value != fac_use
            AND bu_end_lifespan IS NULL
    ),
    updated AS (
        UPDATE buildings.building_use b_use
        SET end_lifespan = NOW()
        FROM bo_in_fac
        WHERE b_use.building_id = bo_in_fac.bo_building_id
    ),
    inserted AS (
		INSERT INTO buildings.building_use (building_use_id, building_id, use_id, begin_lifespan)
	    SELECT nextval('buildings.building_use_building_use_id_seq'),
	        bo_in_fac.bo_building_id,
			(SELECT use_id FROM buildings.use WHERE use.value = bo_in_fac.fac_use),
	        NOW()
	    FROM bo_in_fac
	)
    SELECT count(*)::integer FROM bo_in_fac;
$$
LANGUAGE sql VOLATILE;


-- BUILDING NAME ADD
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_add()
RETURNS integer AS
$$
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
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
    ),
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
    inserted AS (
        INSERT INTO buildings.building_name (building_name_id, building_id, building_name, begin_lifespan)
        SELECT nextval('buildings.building_name_building_name_id_seq'),
            building_name_joined.building_id,
            building_name_joined.fac_name,
            NOW()
        FROM building_name_joined
    )
    SELECT count(*)::integer FROM building_name_joined;
$$
LANGUAGE sql VOLATILE;


-- BUILDING USE ADD
CREATE OR REPLACE FUNCTION buildings.update_facilities_use_add()
RETURNS integer AS
$$
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
        SELECT *
        FROM bo_intersects_fac
        WHERE bo_intersect_ratio > 0.5
    ),
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
    inserted AS (
        INSERT INTO buildings.building_use (building_use_id, building_id, use_id, begin_lifespan)
        SELECT nextval('buildings.building_use_building_use_id_seq'),
            building_use_joined.building_id,
            (SELECT use_id FROM buildings.use WHERE use.value = building_use_joined.fac_use),
            NOW()
        FROM building_use_joined
    )
    SELECT count(*)::integer FROM building_use_joined;
$$
LANGUAGE sql VOLATILE;


-- BUILDING NAME/USE REMOVE
CREATE OR REPLACE FUNCTION buildings.update_facilities_name_use_remove()
RETURNS integer AS
$$
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
        WHERE u.use_id IN (16,27) -- Hospital = 16, School = 27
            AND bu.end_lifespan IS NULL
            AND bo.end_lifespan IS NULL
    ),
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
    HAVING 
        COALESCE(SUM(ST_Area(ST_Intersection(bo.shape, f.shape))) / NULLIF(ST_Area(bo.shape), 0), 0) < 0.5
    ),
    remove_name AS (
        UPDATE buildings.building_name b_name
        SET end_lifespan = NOW()
        FROM bo_outside_fac
        WHERE b_name.building_id = bo_outside_fac.building_id
            AND b_name.end_lifespan is NULL
    ),
    remove_use AS (
        UPDATE buildings.building_use b_use
        SET end_lifespan = NOW()
        FROM bo_outside_fac
        WHERE b_use.building_id = bo_outside_fac.building_id
            AND b_use.end_lifespan is NULL
    )
    SELECT count(*)::integer FROM bo_outside_fac;
$$
LANGUAGE sql VOLATILE;


-- UPDATE FACILITIES ATTRIBUTES
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
