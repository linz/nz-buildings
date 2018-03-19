CREATE OR REPLACE FUNCTION buildings_bulk_load.compare_building_outlines(p_supplied_dataset_id integer)
    RETURNS void
AS $$

BEGIN

IF (
    SELECT processed_date
    FROM buildings_bulk_load.supplied_datasets
    WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = p_supplied_dataset_id) IS NULL THEN
    
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
        -- ADDED BUILDINGS
        -------------------------------------------------------------------------------------------------------------------
         -- runs through the supplied data and finds the geometries which do not intersect
         -- with any geometries in the current table

        INSERT INTO buildings_bulk_load.added
        SELECT supplied.bulk_load_outline_id,
               1 AS qa_status_id
        FROM supplied_bulk_load_outlines supplied
        LEFT JOIN buildings_bulk_load.existing_subset_extracts AS current ON ST_Intersects(supplied.shape, current.shape)
        WHERE current.building_outline_id IS NULL;

        -----------------------------------------------------------------------------------------------------------------
        -- REMOVED BUILDINGS
        -----------------------------------------------------------------------------------------------------------------
         -- runs through the current data and finds the geometries which do not intersect
         -- with any geometries in the supplied table

        INSERT INTO buildings_bulk_load.removed
        SELECT current.building_outline_id,
               1 AS qa_status_id
        FROM buildings_bulk_load.existing_subset_extracts current
        LEFT JOIN supplied_bulk_load_outlines supplied ON ST_Intersects(current.shape, supplied.shape)
        WHERE supplied.bulk_load_outline_id IS NULL;

        -----------------------------------------------------------------------------------------------------------------
        -- MERGED BUILDINGS
        -----------------------------------------------------------------------------------------------------------------
         -- Intersection of supplied building with current buildings
         -- runs through the geometries in the supplied table and finds those which intersect current
         -- geometries by greater than 10%. it also records a count of how many current geometries the supplied
         -- polygons intersect.

        CREATE TEMP TABLE supplier_intersect AS
        SELECT supplied.bulk_load_outline_id,
               supplied.supplied_dataset_id,
               COUNT(current.building_outline_id) AS existing_count,
               supplied.shape
        FROM supplied_bulk_load_outlines supplied,
             buildings_bulk_load.existing_subset_extracts current
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND (ST_Area(ST_Intersection(supplied.shape, current.shape))/ST_Area(current.shape)) > .1
        GROUP BY supplied.bulk_load_outline_id, supplied.supplied_dataset_id, supplied.shape
        ORDER BY existing_count DESC;

        ----------------------------------------
        -- ADDED BUILDINGS
        -- add the buildings that overlap by less than 10% to the new table
        ----------------------------------------
         --TEMP

        CREATE TEMP TABLE new_add AS
        SELECT supplied.bulk_load_outline_id,
               supplied.supplied_dataset_id,
               supplied.shape
        FROM supplied_bulk_load_outlines supplied
        WHERE supplied.bulk_load_outline_id NOT IN
            (SELECT supplier_intersect.bulk_load_outline_id
             FROM supplier_intersect supplier_intersect);

         --TEMP

        DELETE
        FROM new_add
        WHERE bulk_load_outline_id IN
            (SELECT added.bulk_load_outline_id
             FROM buildings_bulk_load.added added);

         --TEMP

        CREATE TEMP TABLE new_add2 AS
        SELECT na.*
        FROM new_add na,
             buildings_bulk_load.existing_subset_extracts current
        WHERE ST_Intersects(na.shape, current.shape)
          AND ST_Area(ST_Intersection(na.shape, current.shape))/ST_Area(na.shape) < 0.1;

         --DELETE Duplicates

        DELETE
        FROM new_add2
        WHERE (bulk_load_outline_id) IN
            ( SELECT bulk_load_outline_id
             FROM new_add2
             GROUP BY bulk_load_outline_id HAVING count(*) > 1);

        -- -- SPLIT CANDIDATES NOT YET POPULATED
        -- -- delete merge candidates

        -- DELETE
        -- FROM new_add2
        -- WHERE bulk_load_outline_id IN
        --     (SELECT bulk_load_outline_id
        --      FROM buildings_bulk_load.split_candidates);

        -- INSERT INTO
        -- add the new buildings

        INSERT INTO buildings_bulk_load.added
        SELECT new_add2.bulk_load_outline_id,
               1
        FROM new_add2;

        -------------------------------------------
        --MERGED
        -------------------------------------------
        -- TEMP

        CREATE TEMP TABLE to_merge AS
        SELECT supplied.bulk_load_outline_id,
               supplied.supplied_dataset_id,
               current.building_outline_id AS e_id,
               ST_Area(ST_Intersection(supplied.shape, current.shape)) AS intersection,
               current.shape
        FROM supplied_bulk_load_outlines supplied,
             buildings_bulk_load.existing_subset_extracts current,
                                                      supplier_intersect
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND (ST_Area(ST_Intersection(supplied.shape, current.shape))/ST_Area(current.shape)) > .1
          AND supplier_intersect.bulk_load_outline_id = supplied.bulk_load_outline_id
          AND supplier_intersect.existing_count > 1;

         -- TEMP

        CREATE TEMP TABLE merged_overlap AS
        SELECT bulk_load_outline_id,
               SUM(intersection) AS total
        FROM to_merge
        GROUP BY bulk_load_outline_id;

         -- TEMP

        CREATE TEMP TABLE e_dups AS
        SELECT e_id,
               SUM(intersection),
               shape
        FROM to_merge
        WHERE (e_id) IN
            ( SELECT e_id
             FROM to_merge
             GROUP BY e_id HAVING count(*) > 1)
        GROUP BY e_id,
                 shape;

         -- DELETE Duplicates

        DELETE
        FROM to_merge
        WHERE (e_id) IN
            (SELECT e_id
             FROM to_merge
             GROUP BY e_id HAVING count(*) > 1);

        -- -- INSERT INTO merged
        -- -- the supplied buildings that intersect more than one current building

        -- INSERT INTO buildings_bulk_load.merged
        -- SELECT supplied.bulk_load_outline_id,
        --        supplied.supplied_dataset_id,
        --        1 AS qa_status_id,
        --        merged_overlap.total AS area_covering,
        --        (merged_overlap.total/ST_Area(supplied.shape))*100 AS percent_covering,
        --        supplied.shape
        -- FROM supplied_bulk_load_outlines supplied,
        --      merged_overlap AS merged_overlap
        -- WHERE supplied.bulk_load_outline_id = merged_overlap.bulk_load_outline_id;

        -- --INSERT summed duplicates

        -- INSERT INTO buildings_bulk_load.split
        -- SELECT e_dups.e_id AS bulk_load_outline_id,
        --        supplied.supplied_dataset_id AS supplied_dataset_id,
        --        1 AS qa_status_id,
        --        e_dups.sum AS area_covering,
        --        (e_dups.sum/ST_Area(supplied.shape))*100 AS percent_covering,
        --        supplied.shape
        -- FROM supplied_bulk_load_outlines supplied,
        --      e_dups
        -- WHERE supplied.bulk_load_outline_id = e_dups.e_id;

        -- INSERT INTO merged_candidates
        -- the current buildings that are potential merges

        INSERT INTO buildings_bulk_load.related ( bulk_load_outline_id, building_outline_id, qa_status_id, area_bulk_load_covering, percent_bulk_load_covering )
        SELECT build.bulk_load_outline_id,
               build.e_id AS building_outline_id,
               1 AS qa_status_id,
               build.intersection AS area_bulk_load_covering,
               build.intersection/ST_Area(supplied.shape)*100 AS percent_bulk_load_covering
        FROM to_merge build,
             supplied_bulk_load_outlines supplied
        WHERE supplied.bulk_load_outline_id = build.bulk_load_outline_id;

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
             buildings_bulk_load.existing_subset_extracts current
        WHERE ST_Intersects(current.shape, supplied.shape)
          AND (ST_Area(ST_Intersection(current.shape, supplied.shape))/ST_Area(supplied.shape)) > .1

        GROUP BY current.building_outline_id
        ORDER BY supplied_count DESC;

        ------------------------------------
        -- INSERT INTO Removed
        -- add the buildings with less than 10% overlap to the removed table
        ------------------------------------
        --TEMP

        CREATE TEMP TABLE removed_add AS
        SELECT current.building_outline_id,
               current.supplied_dataset_id,
               current.shape
        FROM buildings_bulk_load.existing_subset_extracts current
        WHERE current.building_outline_id NOT IN
            (SELECT existing_intersect.building_outline_id
             FROM existing_intersect existing_intersect);

         --TEMP

        DELETE
        FROM removed_add
        WHERE building_outline_id IN
            (SELECT removed.building_outline_id
             FROM buildings_bulk_load.removed removed);

         --TEMP

        CREATE TEMP TABLE removed_add2 AS
        SELECT ra.*
        FROM removed_add ra,
             supplied_bulk_load_outlines supplied
        WHERE ST_Intersects(ra.shape, supplied.shape)
          AND ST_Area(ST_Intersection(ra.shape, supplied.shape))/ST_Area(ra.shape) <0.1;

         --DELETE Duplicates

        DELETE
        FROM removed_add2
        WHERE (building_outline_id) IN
            ( SELECT building_outline_id
             FROM removed_add2
             GROUP BY building_outline_id HAVING count(*) > 1);

        --  -- delete merge candidates

        -- DELETE
        -- FROM removed_add2
        -- WHERE building_outline_id IN
        --     (SELECT building_outline_id
        --      FROM buildings_bulk_load.merge_candidates);

         -- INSERT INTO Removed

        INSERT INTO buildings_bulk_load.removed
        SELECT removed_add2.building_outline_id,
               1 AS qa_status_id
        FROM removed_add2;

        -------------------------------------------------
        --SPLIT
        -------------------------------------------------
         -- TEMP

        CREATE TEMP TABLE to_split AS
        SELECT current.building_outline_id,
               supplied.bulk_load_outline_id AS s_id,
               ST_Area(ST_Intersection(supplied.shape, current.shape)) AS intersection,
               supplied.shape
        FROM supplied_bulk_load_outlines supplied,
             buildings_bulk_load.existing_subset_extracts current,
             existing_intersect
        WHERE ST_Intersects(supplied.shape, current.shape)
          AND (ST_Area(ST_Intersection(supplied.shape, current.shape))/ST_Area(supplied.shape)) >.1
          AND existing_intersect.building_outline_id = current.building_outline_id
          AND existing_intersect.supplied_count > 1;

         -- TEMP

        CREATE TEMP TABLE split_overlap AS
        SELECT building_outline_id,
               SUM(intersection) AS total
        FROM to_split
        GROUP BY building_outline_id;

         -- TEMP

        CREATE TEMP TABLE dups AS
        SELECT s_id,
               SUM(intersection),
               shape
        FROM to_split
        WHERE (s_id) IN
            ( SELECT s_id
             FROM to_split
             GROUP BY s_id HAVING count(*) > 1)
        GROUP BY s_id,
                 shape;

        -- DELETE Duplicates

        DELETE
        FROM to_split
        WHERE (s_id) IN
            ( SELECT s_id
             FROM to_split
             GROUP BY s_id HAVING count(*) > 1);

        -- -- INSERT INTO split
        -- -- the multiple supplied buildings that intersect with the same current building

        -- INSERT INTO buildings_bulk_load.split
        -- SELECT to_split.s_id AS bulk_load_outline_id,
        --        supplied.supplied_dataset_id AS supplied_dataset_id,
        --        1 AS qa_status_id,
        --        to_split.intersection AS area_covering,
        --        (to_split.intersection/ST_Area(supplied.shape))*100 AS percent_covering,
        --        supplied.shape
        -- FROM supplied_bulk_load_outlines supplied,
        --      to_split
        -- WHERE supplied.bulk_load_outline_id = to_split.s_id;

        -- -- INSERT INTO split
        -- -- insert summed duplicates

        -- INSERT INTO buildings_bulk_load.split
        -- SELECT dups.s_id AS bulk_load_outline_id,
        --        supplied.supplied_dataset_id AS supplied_dataset_id,
        --        1 AS qa_status_id,
        --        dups.sum AS area_covering,
        --        (dups.sum/ST_Area(supplied.shape))*100 AS percent_covering,
        --        supplied.shape
        -- FROM supplied_bulk_load_outlines supplied,
        --      dups
        -- WHERE supplied.bulk_load_outline_id = dups.s_id;

        -- INSERT INTO related
        -- the current buildings that intersect with more than one supplied building

        INSERT INTO buildings_bulk_load.related ( bulk_load_outline_id, building_outline_id, qa_status_id, area_bulk_load_covering, percent_bulk_load_covering )
        SELECT to_split.s_id AS bulk_load_outline_id,
               split_overlap.building_outline_id AS building_outline_id,
               1 AS qa_status_id,
               split_overlap.total AS area_bulk_load_covering,
               split_overlap.total/ST_Area(current.shape)*100 AS percent_bulk_load_covering
        FROM split_overlap split_overlap,
             buildings_bulk_load.existing_subset_extracts current,
             to_split to_split,
             supplied_bulk_load_outlines supplied
        WHERE current.building_outline_id = split_overlap.building_outline_id
          AND split_overlap.building_outline_id = to_split.building_outline_id
          AND to_split.s_id = supplied.bulk_load_outline_id;

        --------------------------------------------------------------------------------------------------------
        -- BEST/TO CHECK CANDIDATE PROCESSESING
        -- DELETE FROM current intersect
        -- remove the split buildings from the current intersect layer

        DELETE
        FROM existing_intersect
        WHERE existing_intersect.supplied_count > 1;

        -- DELETE FROM supplied intersect
        -- remove the merged buildings from the supplied intersect layer

        DELETE
        FROM supplier_intersect
        WHERE supplier_intersect.existing_count > 1;

        -- DELETE FROM existing intersect
        -- remove from existing intersect the buildings which have been merged

        DELETE
        FROM existing_intersect
        WHERE existing_intersect.building_outline_id IN
            (SELECT to_merge.e_id
             FROM to_merge);

        -- DELETE FROM supplied intersect
        -- remove from supplied intersect the buildings which represent splits

        DELETE
        FROM supplier_intersect
        WHERE supplier_intersect.bulk_load_outline_id IN
            (SELECT to_split.s_id
             FROM to_split);

        -----------------------------------------------------------------------------------------------------------------
        -- BEST CANDIDATES & TO CHECK
        -----------------------------------------------------------------------------------------------------------------
        -- TEMP TABLE
        -- of all 1:1 matches and their % overlap, area difference and Hausdorff Distance

        CREATE TEMP TABLE comparisons AS
        SELECT supplied.bulk_load_outline_id,
               building.building_outline_id,
               supplied.supplied_dataset_id,
               1 AS qa_status_id,
               ST_Area(ST_Intersection(supplied.shape, building.shape))/ST_Area(supplied.shape)*100 AS supplier_overlap,
               ST_Area(ST_Intersection(supplied.shape, building.shape))/ST_Area(building.shape)*100 AS existing_overlap,
               ST_Area(building.shape) - ST_Area(supplied.shape) AS area_difference,
               ST_HausdorffDistance(supplied.shape, building.shape) AS hausdorff_distance,
               supplied.shape
        FROM supplier_intersect supplied,
             existing_intersect building
        WHERE ST_Area(ST_Intersection(supplied.shape, building.shape))/ST_Area(supplied.shape) > 0.1
          AND ST_Area(ST_Intersection(supplied.shape, building.shape))/ST_Area(building.shape) > 0.1;

        -- INSERT INTO Matched

        INSERT INTO buildings_bulk_load.matched (bulk_load_outline_id, building_outline_id, qa_status_id, area_difference, percent_difference, hausdorff_distance)
        SELECT comparisons.bulk_load_outline_id,
               comparisons.building_outline_id,
               comparisons.qa_status_id,
               comparisons.area_difference,
               ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) AS percent_difference,
               comparisons.hausdorff_distance
        FROM comparisons;

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
