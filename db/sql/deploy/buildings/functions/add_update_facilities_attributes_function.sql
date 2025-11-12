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
--      - Add missing building names and uses.
--      - Retire building names and uses outside of facility polygons. Beware of Supermarkets.
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
	
END;
$$
LANGUAGE plpgsql VOLATILE;

COMMIT;
