------------------------------------------------------------
-- Script to compare all new (most recent bulk load) outlines to the
-- existing outlines that intersect with the new outlines's capture source
-- area. The outlines are sorted into four categories:
-- added: new outlines not intersecting with any existing
-- removed: existing outlines not intersecting with any new
-- matched: new and existing outlines 1:1 match
-- related: more complex relationships between new and existing outlines
--          such as 1:many or many:1 or many:many
-------------------------------------------------------------

-- ADDED BUILDINGS

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
        AND supplied.bulk_load_status_id != 3
    ), supplied_count AS (
        -- Find all supplied building outlines that have more than or exactly one >5%
        -- overlap with the current building outlines.
        SELECT
              bulk_load_outline_id
            , count(bulk_load_outline_id)
        FROM intersects
        WHERE current_intersect > 5
        AND supplied_intersect > 5
        GROUP BY bulk_load_outline_id
        HAVING count(bulk_load_outline_id) >= 1
    )
    -- Find supplied bulk_load_outline_id that do not intersect or intersect
    -- with <5% overlap, and are therefore marked as new to the dataset.
    SELECT DISTINCT bulk_load_outline_id
    FROM buildings_bulk_load.bulk_load_outlines supplied
    LEFT JOIN buildings_bulk_load.existing_subset_extracts current ON ST_Intersects(supplied.shape, current.shape)
    LEFT JOIN intersects USING (bulk_load_outline_id)
    WHERE current.building_outline_id IS NULL
    AND supplied.supplied_dataset_id = $1
    AND supplied.bulk_load_status_id != 3
    OR (     intersects.supplied_intersect < 5
         AND supplied.bulk_load_outline_id NOT IN ( SELECT bulk_load_outline_id FROM supplied_count ))
    ;

$$
LANGUAGE sql VOLATILE;

-- REMOVED BUILDINGS

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
        HAVING count(building_outline_id) >= 1
    )
    -- Find current building_outline_id that do not intersect or intersect with
    -- <5% overlap, and are therefore marked for removal from the dataset.
    SELECT DISTINCT building_outline_id
    FROM buildings_bulk_load.existing_subset_extracts current
    LEFT JOIN buildings_bulk_load.bulk_load_outlines supplied ON (ST_Intersects(current.shape, supplied.shape) AND supplied.supplied_dataset_id = $1)
    LEFT JOIN intersects USING (building_outline_id)
    WHERE supplied.bulk_load_outline_id IS NULL
    AND current.supplied_dataset_id = $1
    OR (     intersects.current_intersect < 5
         AND current.building_outline_id NOT IN ( SELECT building_outline_id FROM current_count ) AND supplied.supplied_dataset_id = $1)
    ;

$$
LANGUAGE sql VOLATILE;

-- MATCHED BUILDINGS

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
        AND supplied.bulk_load_status_id != 3
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
    AND (   (current_intersect > 5 AND supplied_intersect > 5)
          OR (current_intersect > 90)
          OR (supplied_intersect > 90)  )
    ;

$$
LANGUAGE sql VOLATILE;

-- RELATED BUILDINGS

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
        AND supplied.bulk_load_status_id != 3
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
    AND bulk_load_outline_id NOT IN (
        SELECT bulk_load_outline_id
        FROM buildings_bulk_load.matched )
    OR bulk_load_outline_id IN (
        SELECT bulk_load_outline_id
        FROM supplied_count )
    AND (   (current_intersect > 5 AND supplied_intersect > 5)
          OR (current_intersect > 90)
          OR (supplied_intersect > 90)  )
    AND bulk_load_outline_id NOT IN (
        SELECT bulk_load_outline_id
        FROM buildings_bulk_load.matched )
    ;

$$
LANGUAGE sql VOLATILE;

CREATE OR REPLACE FUNCTION buildings_bulk_load.reassign_related_ids(
    p_supplied_dataset_id integer
)
RETURNS TABLE(
      reassigned_building_outline_id integer
    , original_building_outline_id integer
    , reassigned_bulk_load_outline_id integer
    , original_bulk_load_outline_id integer
) AS
$$

    WITH found_related AS (
        SELECT
              building_outline_id
            , bulk_load_outline_id
        FROM buildings_bulk_load.find_related(p_supplied_dataset_id)
    ), reassigned_ids AS (
        SELECT
              row_number() OVER() AS new_id
            , source_id
            , category
        FROM (
            SELECT
                  building_outline_id AS source_id
                , 'building_outline_id' AS category
            FROM found_related
            GROUP BY building_outline_id
            UNION
            SELECT
                  bulk_load_outline_id AS source_id
                , 'bulk_load_outline_id' AS category
            FROM found_related
            GROUP BY bulk_load_outline_id
        ) sources
    )
    SELECT
          a.new_id::integer AS reassigned_building_outline_id
        , a.source_id::integer AS original_building_outline_id
        , b.new_id::integer AS reassigned_bulk_load_outline_id
        , b.source_id::integer AS original_bulk_load_outline_id
    FROM found_related
    JOIN reassigned_ids a ON building_outline_id = a.source_id AND a.category = 'building_outline_id'
    JOIN reassigned_ids b ON bulk_load_outline_id = b.source_id AND b.category = 'bulk_load_outline_id';

$$
LANGUAGE sql VOLATILE;


-- OVERALL PROCESS

CREATE OR REPLACE FUNCTION buildings_bulk_load.compare_building_outlines(p_supplied_dataset_id integer)
    RETURNS void AS
$$

DECLARE
    v_row_count integer;

BEGIN

IF ( SELECT processed_date
     FROM buildings_bulk_load.supplied_datasets
     WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = p_supplied_dataset_id ) IS NULL THEN

        -- ADDED

        INSERT INTO buildings_bulk_load.added (bulk_load_outline_id, qa_status_id)
        SELECT
              bulk_load_outline_id
            , 1 AS qa_status_id
        FROM buildings_bulk_load.find_added(p_supplied_dataset_id);

        -- REMOVED

        INSERT INTO buildings_bulk_load.removed (building_outline_id, qa_status_id)
        SELECT
              building_outline_id
            , 1 AS qa_status_id
        FROM buildings_bulk_load.find_removed(p_supplied_dataset_id);

        -- MATCHED

        INSERT INTO buildings_bulk_load.matched (bulk_load_outline_id, building_outline_id, qa_status_id)
        SELECT
              bulk_load_outline_id
            , building_outline_id
            , 1 AS qa_status_id
        FROM buildings_bulk_load.find_matched(p_supplied_dataset_id);

        -- RELATED

        WITH uniquely_identified_related AS (
            -- Select output from reassign_related_ids()
            SELECT
                  reassigned_building_outline_id AS building_outline_id
                , original_building_outline_id
                , reassigned_bulk_load_outline_id AS bulk_load_outline_id
                , original_bulk_load_outline_id
            FROM buildings_bulk_load.reassign_related_ids(p_supplied_dataset_id)
        )
        INSERT INTO buildings_bulk_load.related (related_group_id, bulk_load_outline_id, building_outline_id, qa_status_id)
        WITH RECURSIVE rels AS (
            SELECT
                  t.bulk_load_outline_id
                , t.building_outline_id
                , array[t.bulk_load_outline_id, t.building_outline_id] AS all_ids_array
            FROM uniquely_identified_related t
              UNION
            SELECT
                  t.bulk_load_outline_id
                , t.building_outline_id
                , uniq(sort(array[
                      t.bulk_load_outline_id
                    , t.building_outline_id
                    , rels.building_outline_id
                  ]::int[] || rels.all_ids_array::int[])) AS all_ids_array
            FROM uniquely_identified_related t, rels
            WHERE rels.bulk_load_outline_id = t.building_outline_id
            OR rels.building_outline_id = t.building_outline_id
            OR rels.bulk_load_outline_id = t.bulk_load_outline_id
        ), length_of_arrays AS (
          -- Find the maximum length array
          SELECT
                rels.bulk_load_outline_id
              , max(array_length(rels.all_ids_array, 1)) AS maximum
          FROM rels
          GROUP BY rels.bulk_load_outline_id
        ), groups AS (
        -- Select only those arrays that are maximum length for the bulk_load_outline_id
            SELECT
                  nextval('buildings_bulk_load.related_groups_related_group_id_seq') AS related_group_id
                , rels.all_ids_array
            FROM rels
            JOIN length_of_arrays USING (bulk_load_outline_id)
            WHERE array_length(rels.all_ids_array, 1) = length_of_arrays.maximum
            GROUP BY rels.all_ids_array
        ), unnest_groups AS (
        -- Unnest arrays in order to rejoin
            SELECT
                  related_group_id
                , unnest(all_ids_array) AS all_ids
            FROM groups
        ), reassigned_id_result AS (
        -- Revert ids back to original
            SELECT
                  ug.related_group_id
                , t.original_bulk_load_outline_id AS bulk_load_outline_id
                , t.original_building_outline_id AS building_outline_id
                , 1 AS qa_status_id
            FROM unnest_groups ug
            JOIN uniquely_identified_related t ON t.bulk_load_outline_id = ug.all_ids
        )
        -- Cross join using new group_id to get all combinations
        -- This is then inserted into the related table
        SELECT DISTINCT
              a.related_group_id
            , a.bulk_load_outline_id
            , b.building_outline_id
            , a.qa_status_id
        FROM reassigned_id_result a
        JOIN reassigned_id_result b ON a.related_group_id = b.related_group_id
        ;

        GET DIAGNOSTICS v_row_count = ROW_COUNT;

        -- If no rows were inserted in the previous statement, we don't need to create
        -- any new related_groups
        IF v_row_count != 0 THEN

            INSERT INTO buildings_bulk_load.related_groups(related_group_id)
            SELECT
                  generate_series(coalesce(max(related_group_id) + 1, 1)
                , currval('buildings_bulk_load.related_groups_related_group_id_seq'))
            FROM buildings_bulk_load.related_groups;

        END IF;

        -- Insert Bulk Load Outlines that don't get sorted into ADDED

        INSERT INTO buildings_bulk_load.added(bulk_load_outline_id, qa_status_id)
        SELECT blo.bulk_load_outline_id, 1 AS qa_status_id
        FROM buildings_bulk_load.bulk_load_outlines blo
        LEFT JOIN buildings_bulk_load.added added ON added.bulk_load_outline_id = blo.bulk_load_outline_id
        LEFT JOIN buildings_bulk_load.matched matched ON matched.bulk_load_outline_id = blo.bulk_load_outline_id
        LEFT JOIN buildings_bulk_load.related related ON related.bulk_load_outline_id = blo.bulk_load_outline_id
        WHERE blo.supplied_dataset_id = p_supplied_dataset_id
        AND blo.bulk_load_status_id != 3
        AND added.bulk_load_outline_id IS NULL
        AND matched.bulk_load_outline_id IS NULL
        AND related.bulk_load_outline_id IS NULL;

        -- Insert Existing Subset Extracts Outlines that don't get sorted into REMOVED

        INSERT INTO buildings_bulk_load.removed(building_outline_id, qa_status_id)
        SELECT ex.building_outline_id, 1 AS qa_status_id
        FROM buildings_bulk_load.existing_subset_extracts ex
        LEFT JOIN buildings_bulk_load.removed removed ON removed.building_outline_id = ex.building_outline_id
        LEFT JOIN buildings_bulk_load.matched matched ON matched.building_outline_id = ex.building_outline_id
        LEFT JOIN buildings_bulk_load.related related ON related.building_outline_id = ex.building_outline_id
        WHERE ex.supplied_dataset_id = p_supplied_dataset_id
        AND removed.building_outline_id IS NULL
        AND matched.building_outline_id IS NULL
        AND related.building_outline_id IS NULL;

        -- UPDATE processed_date IN supplied_datasets

        UPDATE buildings_bulk_load.supplied_datasets
        SET processed_date = now()
        WHERE supplied_dataset_id = p_supplied_dataset_id;

END IF;

END;

$$ LANGUAGE plpgsql;
