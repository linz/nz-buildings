-- Deploy nz-buildings:buildings_bulk_load/functions/remove_small_tanks to pg

BEGIN;

-- bulk_load_outlines_remove_small_tanks (change bulk load status of circular buildings less than 16sqm)
    -- params: integer supplied_dataset_id
    -- return: number of small tanks that have been removed

CREATE OR REPLACE FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_tanks(integer)
RETURNS void AS
$$

    WITH small_tanks AS (
        UPDATE buildings_bulk_load.bulk_load_outlines
        SET bulk_load_status_id = 3
        WHERE bulk_load_outline_id IN (
            SELECT b.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines b
            WHERE (12.566370614*((ST_area(b.shape))/((ST_Perimeter(b.shape))*(ST_Perimeter(b.shape))))) >= 0.8
            AND (12.566370614*((ST_area(b.shape))/((ST_Perimeter(b.shape))*(ST_Perimeter(b.shape))))) <= 1.3
            AND ST_Area(b.shape) <= 16
            AND b.bulk_load_outline_id NOT IN (
                SELECT bulk_load_outline_id
                FROM buildings_bulk_load.deletion_description
            )
        )
        AND supplied_dataset_id = $1 
        RETURNING *
    )
    INSERT INTO buildings_bulk_load.deletion_description (bulk_load_outline_id, description)
    SELECT bulk_load_outline_id, 'Circlular building smaller than 16m2'
    FROM small_tanks;

$$
LANGUAGE sql VOLATILE;

COMMENT ON FUNCTION buildings_bulk_load.bulk_load_outlines_remove_small_tanks(integer) IS
'Update bulk load status in bulk_load_outlines table of circular outlines less than 16sqm';

COMMIT;
