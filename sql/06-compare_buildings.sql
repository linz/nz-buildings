CREATE OR REPLACE FUNCTION buildings_bulk_load.compare_building_outlines(p_supplied_dataset_id integer)
    RETURNS void
AS $$

BEGIN

IF ( SELECT processed_date
     FROM buildings_bulk_load.supplied_datasets
     WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = p_supplied_dataset_id ) IS NULL THEN
    
        -------------------------------------------------------------------------------------------------------------------
        -- SUBSET supplied outlines by p_supplied_dataset_id parameter of function
        -------------------------------------------------------------------------------------------------------------------
        -- creates temp table of all relevant supplied outlines
        -- this temp table will be used throughout the rest of processing in place of the supplied outlines table

        CREATE TEMP TABLE supplied_bulk_load_outlines AS
        SELECT supplied.*
        FROM buildings_bulk_load.bulk_load_outlines AS supplied
        WHERE supplied.supplied_dataset_id = p_supplied_dataset_id;

        -------------------------------------------------------------------------------------------------------------------
        -- SUBSET existing subset extract table by p_supplied_dataset_id parameter of function
        -------------------------------------------------------------------------------------------------------------------
        -- creates temp table of all relevant existing extracts
        -- this temp table will be used throughout the rest of processing in place of the existing subset extracts table

        CREATE TEMP TABLE extracted_outlines AS
        SELECT existing.*
        FROM buildings_bulk_load.existing_subset_extracts AS existing
        WHERE existing.supplied_dataset_id = p_supplied_dataset_id;

        -------------------------------------------------------------------------------------------------------------------
        -- ADDED BUILDINGS
        -------------------------------------------------------------------------------------------------------------------
         -- runs through the supplied data and finds the geometries which do not intersect
         -- with any geometries in the current table

        INSERT INTO buildings_bulk_load.added
        SELECT supplied.bulk_load_outline_id,
               1 AS qa_status_id
        FROM supplied_bulk_load_outlines supplied
        LEFT JOIN extracted_outlines AS current ON ST_Intersects(supplied.shape, current.shape)
        WHERE current.building_outline_id IS NULL;

        -----------------------------------------------------------------------------------------------------------------
        -- REMOVED BUILDINGS
        -----------------------------------------------------------------------------------------------------------------
         -- runs through the current data and finds the geometries which do not intersect
         -- with any geometries in the supplied table

        INSERT INTO buildings_bulk_load.removed
        SELECT current.building_outline_id,
               1 AS qa_status_id
        FROM extracted_outlines current
        LEFT JOIN supplied_bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE supplied.bulk_load_outline_id IS NULL;

        -----------------------------------------------------------------------------------------------------------------
        -- MERGED BUILDINGS
        -----------------------------------------------------------------------------------------------------------------
         -- Intersection of supplied building with current buildings
         -- runs through the geometries in the supplied table and finds those which intersect current
         -- geometries by greater than 10%. it also records a count of how many current geometries the supplied
         -- polygons intersect.

        CREATE TEMP TABLE supplied_intersect AS
        SELECT supplied.bulk_load_outline_id,
               supplied.supplied_dataset_id,
               count(current.building_outline_id) AS existing_count,
               supplied.shape
        FROM supplied_bulk_load_outlines supplied,
             extracted_outlines current
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND (ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape)) > 0.1
        GROUP BY supplied.bulk_load_outline_id, supplied.supplied_dataset_id, supplied.shape
        ORDER BY existing_count DESC;

        ----------------------------------------
        -- ADDED BUILDINGS
        -- add the buildings that overlap by less than 10% to the new table
        ----------------------------------------
         --TEMP

        CREATE TEMP TABLE other_add_candidates AS
        SELECT bulk_load_outline_id,
               supplied_dataset_id,
               shape
        FROM supplied_bulk_load_outlines
        WHERE bulk_load_outline_id NOT IN
            ( SELECT bulk_load_outline_id
              FROM supplied_intersect )
          AND bulk_load_outline_id NOT IN
            ( SELECT bulk_load_outline_id
              FROM buildings_bulk_load.added );

         --TEMP

        CREATE TEMP TABLE add_small_intersection AS
        SELECT oa.*
        FROM other_add_candidates oa,
             extracted_outlines current
        WHERE ST_Intersects(oa.shape, current.shape)
          AND ST_Area(ST_Intersection(oa.shape, current.shape)) / ST_Area(oa.shape) < 0.1;

         --DELETE Duplicates

        DELETE
        FROM add_small_intersection
        WHERE bulk_load_outline_id IN
            ( SELECT bulk_load_outline_id
              FROM add_small_intersection
              GROUP BY bulk_load_outline_id
              HAVING count(*) > 1 );

        -- INSERT INTO
        -- add the new buildings

        INSERT INTO buildings_bulk_load.added
        SELECT bulk_load_outline_id,
               1
        FROM add_small_intersection;

        -------------------------------------------
        -- MERGED
        -------------------------------------------

        CREATE TEMP TABLE to_merge AS
        SELECT supplied.bulk_load_outline_id,
               supplied.supplied_dataset_id,
               current.building_outline_id AS e_id,
               ST_Area(ST_Intersection(supplied.shape, current.shape)) AS intersection,
               current.shape
        FROM supplied_bulk_load_outlines supplied,
             extracted_outlines current,
             supplied_intersect
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) > 0.1
          AND supplied_intersect.bulk_load_outline_id = supplied.bulk_load_outline_id
          AND supplied_intersect.existing_count > 1;

         -- DELETE Duplicates

        DELETE
        FROM to_merge
        WHERE e_id IN
            ( SELECT e_id
              FROM to_merge
              GROUP BY e_id HAVING count(*) > 1 );

        -- INSERT INTO related_prep
        -- the current buildings that are potential merges

        CREATE TEMP TABLE related_prep AS
        SELECT to_merge.bulk_load_outline_id,
               to_merge.e_id AS building_outline_id,
               1 AS qa_status_id,
               ST_Area(supplied.shape) AS area_bulk_load,
               ST_Area(current.shape) AS area_existing,
               to_merge.intersection AS area_overlap,
               to_merge.intersection / ST_Area(supplied.shape) * 100 AS percent_bulk_load_overlap,
               to_merge.intersection / ST_Area(current.shape) * 100 AS percent_existing_overlap
        FROM to_merge,
             supplied_bulk_load_outlines supplied,
             extracted_outlines current
        WHERE supplied.bulk_load_outline_id = to_merge.bulk_load_outline_id
          AND to_merge.e_id = current.building_outline_id;

        -------------------------------------------------------------------------------------------------------------------
        -- SPLIT BUILDINGS
        -------------------------------------------------------------------------------------------------------------------
         -- Intersection of current buildings with supplied buildings
         -- runs through the geometries in the current table and finds those which intersect supplied geometries by greater than 10%.
         -- It also records a count of how many supplied geometries the current polygons intersect.
         -- TEMP

        CREATE TEMP TABLE existing_intersect AS
        SELECT current.building_outline_id,
               current.supplied_dataset_id,
               COUNT(supplied.bulk_load_outline_id) AS supplied_count,
               current.shape
        FROM supplied_bulk_load_outlines supplied,
             extracted_outlines current
        WHERE ST_Intersects(current.shape, supplied.shape)
          AND ST_Area(ST_Intersection(current.shape, supplied.shape)) / ST_Area(supplied.shape) > 0.1

        GROUP BY current.building_outline_id, current.supplied_dataset_id, current.shape
        ORDER BY supplied_count DESC;

        ------------------------------------
        -- INSERT INTO Removed
        -- add the buildings with less than 10% overlap to the removed table
        ------------------------------------
        -- TEMP

        CREATE TEMP TABLE removed_add AS
        SELECT current.building_outline_id,
               current.supplied_dataset_id,
               current.shape
        FROM extracted_outlines current
        WHERE current.building_outline_id NOT IN
            ( SELECT existing_intersect.building_outline_id
              FROM existing_intersect existing_intersect );

         -- TEMP

        DELETE
        FROM removed_add
        WHERE building_outline_id IN
            ( SELECT removed.building_outline_id
              FROM buildings_bulk_load.removed removed );

         -- TEMP

        CREATE TEMP TABLE removed_add2 AS
        SELECT ra.*
        FROM removed_add ra,
             supplied_bulk_load_outlines supplied
        WHERE ST_Intersects(ra.shape, supplied.shape)
          AND ST_Area(ST_Intersection(ra.shape, supplied.shape)) / ST_Area(ra.shape) < 0.1;

         -- DELETE Duplicates

        DELETE
        FROM removed_add2
        WHERE building_outline_id IN
            ( SELECT building_outline_id
              FROM removed_add2
              GROUP BY building_outline_id HAVING count(*) > 1);

         -- INSERT INTO Removed

        INSERT INTO buildings_bulk_load.removed
        SELECT removed_add2.building_outline_id,
               1 AS qa_status_id
        FROM removed_add2;

        -------------------------------------------------
        -- SPLIT
        -------------------------------------------------
         -- TEMP

        CREATE TEMP TABLE to_split AS
        SELECT current.building_outline_id,
               supplied.bulk_load_outline_id AS s_id,
               ST_Area(ST_Intersection(supplied.shape, current.shape)) AS intersection,
               supplied.shape
        FROM supplied_bulk_load_outlines supplied,
             extracted_outlines current,
             existing_intersect
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) > 0.1
          AND existing_intersect.building_outline_id = current.building_outline_id
          AND existing_intersect.supplied_count > 1;

        -- DELETE Duplicates

        DELETE
        FROM to_split
        WHERE s_id IN
            ( SELECT s_id
              FROM to_split
              GROUP BY s_id HAVING count(*) > 1 );

        -- INSERT into related prep excluding merge / split duplicates

        INSERT INTO related_prep
        SELECT to_split.s_id AS bulk_load_outline_id,
               to_split.building_outline_id AS building_outline_id,
               1 AS qa_status_id,
               ST_Area(supplied.shape) AS area_bulk_load,
               ST_Area(current.shape) AS area_existing,
               to_split.intersection AS area_overlap,
               to_split.intersection / ST_Area(supplied.shape) * 100 AS percent_bulk_load_overlap,
               to_split.intersection / ST_Area(current.shape) * 100 AS percent_existing_overlap
        FROM extracted_outlines current,
             to_split,
             supplied_bulk_load_outlines supplied
        WHERE current.building_outline_id = to_split.building_outline_id
          AND to_split.s_id = supplied.bulk_load_outline_id
          AND NOT EXISTS
            ( SELECT to_split.s_id,
                     to_split.building_outline_id
              FROM related_prep
              WHERE to_split.s_id = bulk_load_outline_id
                AND to_split.building_outline_id = building_outline_id );

        WITH bulk_load_totals AS (
             SELECT bulk_load_outline_id,
                    sum(area_overlap) AS total_area_bulk_load_overlap,
                    sum(percent_bulk_load_overlap) AS total_percent_bulk_load_overlap
             FROM related_prep
             GROUP BY bulk_load_outline_id ),
        existing_totals AS (
             SELECT building_outline_id,
                    sum(area_overlap) AS total_area_existing_overlap,
                    sum(percent_existing_overlap) AS total_percent_existing_overlap
             FROM related_prep
             GROUP BY building_outline_id )
        INSERT INTO buildings_bulk_load.related ( bulk_load_outline_id, building_outline_id, qa_status_id, area_bulk_load, area_existing, area_overlap, percent_bulk_load_overlap, percent_existing_overlap, total_area_bulk_load_overlap, total_area_existing_overlap, total_percent_bulk_load_overlap, total_percent_existing_overlap )
        SELECT rp.bulk_load_outline_id,
               rp.building_outline_id,
               rp.qa_status_id,
               rp.area_bulk_load,
               rp.area_existing,
               rp.area_overlap,
               rp.percent_bulk_load_overlap,
               rp.percent_existing_overlap,
               bulk_load_totals.total_area_bulk_load_overlap,
               existing_totals.total_area_existing_overlap,
               bulk_load_totals.total_percent_bulk_load_overlap,
               existing_totals.total_percent_existing_overlap
        FROM related_prep rp, bulk_load_totals, existing_totals
        WHERE rp.bulk_load_outline_id = bulk_load_totals.bulk_load_outline_id
          AND rp.building_outline_id = existing_totals.building_outline_id;

        --------------------------------------------------------------------------------------------------------
        -- MATCHED PROCESSING
        -- DELETE FROM current intersect
        -- remove the split buildings from the current intersect layer

        DELETE
        FROM existing_intersect
        WHERE existing_intersect.supplied_count > 1;

        -- DELETE FROM supplied intersect
        -- remove the merged buildings from the supplied intersect layer

        DELETE
        FROM supplied_intersect
        WHERE supplied_intersect.existing_count > 1;

        -- DELETE FROM existing intersect
        -- remove from existing intersect the buildings which have been merged

        DELETE
        FROM existing_intersect
        WHERE existing_intersect.building_outline_id IN
            ( SELECT to_merge.e_id
              FROM to_merge );

        -- DELETE FROM supplied intersect
        -- remove from supplied intersect the buildings which represent splits

        DELETE
        FROM supplied_intersect
        WHERE supplied_intersect.bulk_load_outline_id IN
            ( SELECT to_split.s_id
              FROM to_split );

        -----------------------------------------------------------------------------------------------------------------
        -- MATCHED
        -----------------------------------------------------------------------------------------------------------------
        -- TEMP TABLE
        -- of all 1:1 matches and their % overlap, area difference and Hausdorff Distance

        INSERT INTO buildings_bulk_load.matched (bulk_load_outline_id, building_outline_id, qa_status_id)
        SELECT supplied.bulk_load_outline_id,
               current.building_outline_id,
               1 AS qa_status_id
        FROM supplied_intersect supplied,
             existing_intersect current
        WHERE ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) > 0.1
          AND ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) > 0.1;

        ----------------------------------------------------------------
        -- Remove remaining temp tables
        ----------------------------------------------------------------

        DISCARD TEMP;

        UPDATE buildings_bulk_load.supplied_datasets
        SET processed_date = now()
        WHERE supplied_dataset_id = p_supplied_dataset_id;

END IF;

END;

$$ LANGUAGE plpgsql;
