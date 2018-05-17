-- ADDED

CREATE OR REPLACE FUNCTION buildings_bulk_load.find_added(
      p_supplied_dataset_id integer
)
RETURNS TABLE(
      bulk_load_outline_id integer
) AS
$$

    WITH intersects AS (
        -- Join current and supplied building outlines based on intersect
        -- and get the percentage of their areas that intersect.
        SELECT 
              current.building_outline_id
            , supplied.bulk_load_outline_id
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(current.shape) * 100 AS current_intersect
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect 
        FROM buildings_bulk_load.existing_subset_extracts current
        JOIN buildings_bulk_load.bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE current.supplied_dataset_id = $1
        AND supplied.supplied_dataset_id = $1
    ), supplied_count AS (
        -- Find all supplied building outlines that have more exactly one >5%
        -- overlap with the current building outlines.
        SELECT
              bulk_load_outline_id
            , count(bulk_load_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY bulk_load_outline_id
        HAVING count(bulk_load_outline_id) = 1
    )
    -- Find supplied bulk_load_outline_id that do not intersect or intersect
    -- with <5% overlap, and are therefore marked as new to the dataset.
    SELECT bulk_load_outline_id
    FROM buildings_bulk_load.bulk_load_outlines supplied
    LEFT JOIN buildings_bulk_load.existing_subset_extracts current ON ST_Intersects(supplied.shape, current.shape)
    LEFT JOIN intersects USING (bulk_load_outline_id)
    WHERE current.building_outline_id IS NULL
    OR (     intersects.supplied_intersect < 5
         AND supplied.bulk_load_outline_id NOT IN ( SELECT bulk_load_outline_id FROM supplied_count ))
    ;

$$
LANGUAGE sql VOLATILE;

-- REMOVED

CREATE OR REPLACE FUNCTION buildings_bulk_load.find_removed(
      p_supplied_dataset_id integer
)
RETURNS TABLE(
      building_outline_id integer
) AS
$$

    WITH intersects AS (
        -- Join current and supplied building outlines based on intersect
        -- and get the percentage of their areas that intersect.
        SELECT 
              current.building_outline_id
            , supplied.bulk_load_outline_id
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(current.shape) * 100 AS current_intersect
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect 
        FROM buildings_bulk_load.existing_subset_extracts current
        JOIN buildings_bulk_load.bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE current.supplied_dataset_id = $1
        AND supplied.supplied_dataset_id = $1
    ), current_count AS (
        -- Find all current building outlines that have exactly one >5%
        -- overlap with the supplied building outlines.
        SELECT
              building_outline_id
            , count(building_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY building_outline_id
        HAVING count(building_outline_id) = 1
    )
    -- Find current building_outline_id that do not intersect or intersect with
    -- <5% overlap, and are therefore marked for removal from the dataset.
    SELECT building_outline_id
    FROM buildings_bulk_load.existing_subset_extracts current
    LEFT JOIN buildings_bulk_load.bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
    LEFT JOIN intersects USING (building_outline_id)
    WHERE supplied.bulk_load_outline_id IS NULL
    OR (     intersects.current_intersect < 5
         AND current.building_outline_id NOT IN ( SELECT building_outline_id FROM current_count ))
    ;

$$
LANGUAGE sql VOLATILE;

-- MATCHED

CREATE OR REPLACE FUNCTION buildings_bulk_load.find_matched(
      p_supplied_dataset_id integer
)
RETURNS TABLE(
      building_outline_id integer
    , bulk_load_outline_id integer
) AS
$$

    WITH intersects AS (
        -- Join current and supplied building outlines based on intersect
        -- and get the percentage of their areas that intersect.
        SELECT 
              current.building_outline_id
            , supplied.bulk_load_outline_id
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(current.shape) * 100 AS current_intersect
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect 
        FROM buildings_bulk_load.existing_subset_extracts current
        JOIN buildings_bulk_load.bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE current.supplied_dataset_id = $1
        AND supplied.supplied_dataset_id = $1
    ), current_count AS (
        -- Find all current building outlines that have exactly one >5%
        -- overlap with the supplied building outlines.
        SELECT
              building_outline_id
            , count(building_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY building_outline_id
        HAVING count(building_outline_id) = 1
    ), supplied_count AS (
        -- Find all supplied building outlines that have exactly one >5%
        -- overlap with the current building outlines.
        SELECT
              bulk_load_outline_id
            , count(bulk_load_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY bulk_load_outline_id
        HAVING count(bulk_load_outline_id) = 1
    )
    -- Find and return the combination of id's that are involved in 1:1
    -- intersects
    SELECT
          intersects.building_outline_id
        , intersects.bulk_load_outline_id
    FROM intersects
    WHERE building_outline_id IN (
        SELECT building_outline_id
        FROM current_count )
    AND bulk_load_outline_id IN (
        SELECT bulk_load_outline_id
        FROM supplied_count )
    ;

$$
LANGUAGE sql VOLATILE;

-- RELATED

CREATE OR REPLACE FUNCTION buildings_bulk_load.find_related(
      p_supplied_dataset_id integer
)
RETURNS TABLE(
      building_outline_id integer
    , bulk_load_outline_id integer
) AS
$$

    WITH intersects AS (
        -- Join current and supplied building outlines based on intersect
        -- and get the percentage of their areas that intersect.
        SELECT 
              current.building_outline_id
            , supplied.bulk_load_outline_id
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(current.shape) * 100 AS current_intersect
            , ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect 
        FROM buildings_bulk_load.existing_subset_extracts current
        JOIN buildings_bulk_load.bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE current.supplied_dataset_id = $1
        AND supplied.supplied_dataset_id = $1
    ), current_count AS (
        -- Find all current building outlines that have more than one >5%
        -- overlap with the supplied building outlines.
        SELECT
              building_outline_id
            , count(building_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY building_outline_id
        HAVING count(building_outline_id) > 1
    ), supplied_count AS (
        -- Find all supplied building outlines that have more than one >5%
        -- overlap with the current building outlines.
        SELECT
              bulk_load_outline_id
            , count(bulk_load_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY bulk_load_outline_id
        HAVING count(bulk_load_outline_id) > 1
    )
    -- Find and return the combination of id's that are involved in m:n
    -- intersects
    SELECT
          intersects.building_outline_id
        , intersects.bulk_load_outline_id
    FROM intersects
    WHERE building_outline_id IN (
        SELECT building_outline_id
        FROM current_count )
    OR bulk_load_outline_id IN (
        SELECT bulk_load_outline_id
        FROM supplied_count )
    ;

$$
LANGUAGE sql VOLATILE;

-- OVERALL PROCESS

CREATE OR REPLACE FUNCTION buildings_bulk_load.compare_building_outlines(p_supplied_dataset_id integer)
    RETURNS void AS 
$$

BEGIN

IF ( SELECT processed_date
     FROM buildings_bulk_load.supplied_datasets
     WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = p_supplied_dataset_id ) IS NULL THEN

        -- ADDED

        INSERT INTO buildings_bulk_load.added (bulk_load_outline_id, qa_status_id)
        SELECT
              bulk_load_outline_id
            , 2 AS qa_status_id
        FROM buildings_bulk_load.find_added(p_supplied_dataset_id);

        -- REMOVED

        INSERT INTO buildings_bulk_load.removed (building_outline_id, qa_status_id)
        SELECT
              building_outline_id
            , 2 AS qa_status_id
        FROM buildings_bulk_load.find_removed(p_supplied_dataset_id);

        -- MATCHED

        INSERT INTO buildings_bulk_load.matched (bulk_load_outline_id, building_outline_id, qa_status_id)
        SELECT
              bulk_load_outline_id
            , building_outline_id
            , 2 AS qa_status_id
        FROM buildings_bulk_load.find_matched(p_supplied_dataset_id);

        -- RELATED

        INSERT INTO buildings_bulk_load.related (bulk_load_outline_id, building_outline_id, qa_status_id)
        SELECT
              bulk_load_outline_id
            , building_outline_id
            , 2 AS qa_status_id
        FROM buildings_bulk_load.find_related(p_supplied_dataset_id);

        -- UPDATE processed_date IN supplied_datasets

        UPDATE buildings_bulk_load.supplied_datasets
        SET processed_date = now()
        WHERE supplied_dataset_id = p_supplied_dataset_id;

END IF;

END;

$$ LANGUAGE plpgsql;
