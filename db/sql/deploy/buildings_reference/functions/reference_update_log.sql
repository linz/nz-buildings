-- Deploy buildings:buildings_reference/functions/reference_update_log to pg

BEGIN;

--------------------------------------------
-- buildings_reference.reference_update_log

-- Functions

-- reference_update_log_insert_log
    -- params: list varchar the columns to be set as true
    -- return: integer update_id

--------------------------------------------

-- Functions

-- reference_update_log_insert_log
    -- params: list varchar the columns to be set as true
    -- return: integer update_id

CREATE OR REPLACE FUNCTION buildings_reference.reference_update_log_insert_log(p_list varchar[])
RETURNS integer AS
$$
    INSERT INTO buildings_reference.reference_update_log (river, lake, pond, swamp, lagoon, canal, coastlines_and_islands, capture_source_area, territorial_authority, territorial_authority_grid, suburb_locality, town_city)
    VALUES(CASE WHEN ('river' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('lake' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('pond' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('swamp' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('lagoon' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('canal' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('coastlines_and_islands' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('capture_source_area' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('territorial_authority' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('territorial_authority_grid' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('suburb_locality' = ANY(p_list)) THEN True ELSE False END,
           CASE WHEN ('town_city' = ANY(p_list)) THEN True ELSE False END
    )
    RETURNING update_id;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_reference.reference_update_log_insert_log(varchar[]) IS
'Insert new log into reference log table';

COMMIT;
