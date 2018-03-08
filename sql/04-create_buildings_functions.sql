CREATE OR REPLACE FUNCTION buildings_stage.compare_building_outlines(dataset integer)
    RETURNS void
AS $$
/*
Details

*/

BEGIN
------------------------------------------------------------------------------------------------------------------
-- CHECK have not processed dataset already

    -------------------------------------------------------------------------------------------------------------------
    -- SUBSET supplied outlines by dataset parameter of function
    -------------------------------------------------------------------------------------------------------------------
    -- creates temp table of all relevant supplied outlines
    -- this temp table will be used throughout the rest of processing in place of the supplied outlines table

    CREATE TEMP TABLE dataset_supplied_outlines AS
    SELECT supplier.*
    FROM buildings_stage.supplied_outlines as supplier
    WHERE supplier.supplied_dataset_id = dataset;

    -------------------------------------------------------------------------------------------------------------------
    -- NEW BUILDINGS
    -------------------------------------------------------------------------------------------------------------------
     -- runs through the supplied data and finds the geometries which do not intersect
     -- with any geometries in the current table

    INSERT INTO buildings_stage.new
    SELECT supplier.supplied_outline_id,
           supplier.supplied_dataset_id,
           1 AS qa_status_id,
           supplier.shape
    FROM dataset_supplied_outlines AS supplier
    LEFT JOIN buildings_stage.existing_subset_extracts AS current ON ST_Intersects(supplier.shape, current.shape)
    WHERE current.building_outline_id IS NULL;

     -----------------------------------------------------------------------------------------------------------------
    -- REMOVED BUILDINGS
    -----------------------------------------------------------------------------------------------------------------
     -- runs through the current data and finds the geometries which do not intersect
     -- with any geometries in the supplied table

    INSERT INTO buildings_stage.removed
    SELECT current.building_outline_id,
                    current.supplied_dataset_id,
                    1 AS qa_status_id,
                    current.shape
    FROM buildings_stage.existing_subset_extracts current
    LEFT JOIN dataset_supplied_outlines supplier ON ST_Intersects(current.shape, supplier.shape)
    WHERE supplier.supplied_outline_id IS NULL;

     -----------------------------------------------------------------------------------------------------------------
    -- MERGED BUILDINGS
    -----------------------------------------------------------------------------------------------------------------
     -- Intersection of supplied building with current buildings
     -- runs through the geometries in the supplied table and finds those which intersect current
     -- geometries by greater than 10%. it also records a count of how many current geometries the supplied
     -- polygons intersect.

    CREATE TEMP TABLE supplier_intersect AS
    SELECT supplier.supplied_outline_id,
           supplier.supplied_dataset_id,
           COUNT(current.building_outline_id) AS existing_count,
           supplier.shape
    FROM dataset_supplied_outlines supplier,
         buildings_stage.existing_subset_extracts current
    WHERE ST_Intersects(supplier.shape, current.shape)
      AND (ST_Area(ST_Intersection(supplier.shape, current.shape))/ST_Area(current.shape)) > .1
    GROUP BY supplier.supplied_outline_id, supplier.supplied_dataset_id, supplier.shape
    ORDER BY existing_count DESC;

     ----------------------------------------
    --NEW BUILDINGS
    -- add the buildings that overlap by less than 10% to the new table
    ----------------------------------------
     --TEMP

    CREATE TEMP TABLE new_add AS
    SELECT supplier.supplied_outline_id,
           supplier.supplied_dataset_id,
           supplier.shape
    FROM dataset_supplied_outlines supplier
    WHERE supplier.supplied_outline_id NOT IN
        (SELECT supplier_intersect.supplied_outline_id
         FROM supplier_intersect supplier_intersect);

     --TEMP

    DELETE
    FROM new_add
    WHERE supplied_outline_id IN
        (SELECT new.supplied_outline_id
         FROM buildings_stage.new NEW);

     --TEMP

    CREATE TEMP TABLE new_add2 AS
    SELECT na.*
    FROM new_add na,
         buildings_stage.existing_subset_extracts current
    WHERE ST_Intersects(na.shape, current.shape)
      AND ST_Area(ST_Intersection(na.shape, current.shape))/ST_Area(na.shape) < 0.1;

     --DELETE Duplicates

    DELETE
    FROM new_add2
    WHERE (supplied_outline_id) IN
        ( SELECT supplied_outline_id
         FROM new_add2
         GROUP BY supplied_outline_id HAVING count(*) > 1);

    -- SPLIT CANDIDATES NOT YET POPULATED
    -- delete merge candidates

    DELETE
    FROM new_add2
    WHERE supplied_outline_id IN
        (SELECT supplied_outline_id
         FROM buildings_stage.split_candidates);

    -- INSERT INTO
    -- add the new buildings

    INSERT INTO buildings_stage.NEW
    SELECT new_add2.supplied_outline_id,
           new_add2.supplied_dataset_id,
           1,
           new_add2.shape
    FROM new_add2;

    -------------------------------------------
    --MERGED
    -------------------------------------------
    -- TEMP

    CREATE TEMP TABLE to_merge AS
    SELECT supplier.supplied_outline_id,
           supplier.supplied_dataset_id,
           current.building_outline_id AS e_id,
           ST_Area(ST_Intersection(supplier.shape, current.shape)) AS intersection,
           current.shape
    FROM dataset_supplied_outlines supplier,
         buildings_stage.existing_subset_extracts current,
                                                  supplier_intersect
    WHERE ST_Intersects(supplier.shape, current.shape)
      AND (ST_Area(ST_Intersection(supplier.shape, current.shape))/ST_Area(current.shape)) > .1
      AND supplier_intersect.supplied_outline_id = supplier.supplied_outline_id
      AND supplier_intersect.existing_count > 1;

     -- TEMP

    CREATE TEMP TABLE merged_overlap AS
    SELECT supplied_outline_id,
           SUM(intersection) AS total
    FROM to_merge
    GROUP BY supplied_outline_id;

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

    -- INSERT INTO merged
    -- the supplied buildings that intersect more than one current building

    INSERT INTO buildings_stage.merged
    SELECT supplier.supplied_outline_id,
           supplier.supplied_dataset_id,
           1 AS qu_status_id,
           merged_overlap.total AS area_covering,
           (merged_overlap.total/ST_Area(supplier.shape))*100 AS percent_covering,
           supplier.shape
    FROM dataset_supplied_outlines AS supplier,
         merged_overlap AS merged_overlap
    WHERE supplier.supplied_outline_id = merged_overlap.supplied_outline_id;

    --INSERT summed duplicates

    INSERT INTO buildings_stage.split
    SELECT e_dups.e_id AS supplied_outline_id,
           supplier.supplied_dataset_id AS supplied_dataset_id,
           1 AS qa_status_id,
           e_dups.sum AS area_covering,
           (e_dups.sum/ST_Area(supplier.shape))*100 AS percent_covering,
           supplier.shape
    FROM dataset_supplied_outlines supplier,
         e_dups
    WHERE supplier.supplied_outline_id = e_dups.e_id;

    -- INSERT INTO merged_candidates
    -- the current buildings that are potential merges

    INSERT INTO buildings_stage.merge_candidates
    SELECT build.e_id AS building_outline_id,
           build.supplied_outline_id,
           build.supplied_dataset_id,
           build.intersection AS area_covering,
           build.intersection/ST_Area(supplier.shape)*100 AS percent_covering
    FROM to_merge build,
         dataset_supplied_outlines supplier
    WHERE supplier.supplied_outline_id = build.supplied_outline_id;

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
           COUNT(supplier.supplied_outline_id) AS supplied_count,
           current.shape
    FROM dataset_supplied_outlines supplier,
         buildings_stage.existing_subset_extracts current
    WHERE ST_Intersects(current.shape, supplier.shape)
      AND (ST_Area(ST_Intersection(current.shape, supplier.shape))/ST_Area(supplier.shape)) > .1

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
    FROM buildings_stage.existing_subset_extracts current
    WHERE current.building_outline_id NOT IN
        (SELECT existing_intersect.building_outline_id
         FROM existing_intersect existing_intersect);

     --TEMP

    DELETE
    FROM removed_add
    WHERE building_outline_id IN
        (SELECT removed.building_outline_id
         FROM buildings_stage.removed removed);

     --TEMP

    CREATE TEMP TABLE removed_add2 AS
    SELECT ra.*
    FROM removed_add ra,
         dataset_supplied_outlines supplier
    WHERE ST_Intersects(ra.shape, supplier.shape)
      AND ST_Area(ST_Intersection(ra.shape, supplier.shape))/ST_Area(ra.shape) <0.1;

     --DELETE Duplicates

    DELETE
    FROM removed_add2
    WHERE (building_outline_id) IN
        ( SELECT building_outline_id
         FROM removed_add2
         GROUP BY building_outline_id HAVING count(*) > 1);

     -- delete merge candidates

    DELETE
    FROM removed_add2
    WHERE building_outline_id IN
        (SELECT building_outline_id
         FROM buildings_stage.merge_candidates);

     -- INSERT INTO Removed

    INSERT INTO buildings_stage.removed
    SELECT removed_add2.building_outline_id,
           removed_add2.supplied_dataset_id,
           1 AS qa_status_id,
           removed_add2.shape
    FROM removed_add2;

     -------------------------------------------------
    --SPLIT
    -------------------------------------------------
     -- TEMP

    CREATE TEMP TABLE to_split AS
    SELECT current.building_outline_id,
           supplier.supplied_outline_id AS s_id,
           ST_Area(ST_Intersection(supplier.shape, current.shape)) AS intersection,
           supplier.shape
    FROM dataset_supplied_outlines supplier,
         buildings_stage.existing_subset_extracts current,
                                                  existing_intersect
    WHERE ST_Intersects(supplier.shape, current.shape)
      AND (ST_Area(ST_Intersection(supplier.shape, current.shape))/ST_Area(supplier.shape)) >.1
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

     -- INSERT INTO split
    -- the multiple supplied buildings that intersect with the same current building

    INSERT INTO buildings_stage.split
    SELECT to_split.s_id AS supplied_outline_id,
           supplier.supplied_dataset_id AS supplied_dataset_id,
           1 AS qa_status_id,
           to_split.intersection AS area_covering,
           (to_split.intersection/ST_Area(supplier.shape))*100 AS percent_covering,
           supplier.shape
    FROM dataset_supplied_outlines supplier,
         to_split
    WHERE supplier.supplied_outline_id = to_split.s_id;

     -- INSERT INTO split
    -- insert summed duplicates

    INSERT INTO buildings_stage.split
    SELECT dups.s_id AS supplied_outline_id,
           supplier.supplied_dataset_id AS supplied_dataset_id,
           1 AS qa_status_id,
           dups.sum AS area_covering,
           (dups.sum/ST_Area(supplier.shape))*100 AS percent_covering,
           supplier.shape
    FROM dataset_supplied_outlines supplier,
         dups
    WHERE supplier.supplied_outline_id = dups.s_id;

     -- INSERT INTO split_candidates
    -- the current buildings that intersect with more than one supplied building

    INSERT INTO buildings_stage.split_candidates
    SELECT to_split.s_id AS supplied_outline_id,
           supplier.supplied_dataset_id AS supplied_dataset_id,
           split_overlap.building_outline_id AS building_outline_id,
           split_overlap.total AS area_covering,
           split_overlap.total/ST_Area(current.shape)*100 AS percent_covering
    FROM split_overlap split_overlap,
         buildings_stage.existing_subset_extracts current,
         to_split to_split,
         dataset_supplied_outlines supplier
    WHERE current.building_outline_id = split_overlap.building_outline_id
      AND split_overlap.building_outline_id = to_split.building_outline_id
      AND to_split.s_id = supplier.supplied_outline_id;

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
    WHERE supplier_intersect.supplied_outline_id IN
        (SELECT to_split.s_id
         FROM to_split);

     -----------------------------------------------------------------------------------------------------------------
    -- BEST CANDIDATES & TO CHECK
    -----------------------------------------------------------------------------------------------------------------
     -- TEMP TABLE
    -- of all 1:1 matches and their % overlap, area difference and Hausdorff Distance

    CREATE TEMP TABLE comparisons AS
    SELECT supplier.supplied_outline_id,
           building.building_outline_id,
           supplier.supplied_dataset_id,
           1 AS qa_status_id,
           ST_Area(ST_Intersection(supplier.shape, building.shape))/ST_Area(supplier.shape)*100 AS supplier_overlap,
           ST_Area(ST_Intersection(supplier.shape, building.shape))/ST_Area(building.shape)*100 AS existing_overlap,
           ST_Area(building.shape) - ST_Area(supplier.shape) AS area_difference,
           ST_HausdorffDistance(supplier.shape, building.shape) AS hausdorff_distance,
           supplier.shape
    FROM supplier_intersect supplier,
         existing_intersect building
    WHERE ST_Area(ST_Intersection(supplier.shape, building.shape))/ST_Area(supplier.shape) > 0.1
      AND ST_Area(ST_Intersection(supplier.shape, building.shape))/ST_Area(building.shape) > 0.1;

     -- INSERT INTO To Check
    -- add matches that fail to meet best candidate criteria to this table

    INSERT INTO buildings_stage.check_candidates
    SELECT comparisons.supplied_outline_id,
           comparisons.building_outline_id,
           comparisons.supplied_dataset_id,
           comparisons.qa_status_id,
           comparisons.area_difference,
           ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) AS percent_difference,
           comparisons.hausdorff_distance,
           comparisons.shape
    FROM comparisons
    WHERE comparisons.hausdorff_distance >= 4
      AND ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) <= 40
      OR comparisons.hausdorff_distance >= 4
      AND ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) >= 40
      OR comparisons.hausdorff_distance <= 4
      AND ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) <= 40;

     -- INSERT INTO Best Candidates
    -- add matches that have greater than 40% overlap and less than 4 Hausdorff Distance

    INSERT INTO buildings_stage.best_candidates
    SELECT comparisons.supplied_outline_id,
           comparisons.building_outline_id,
           comparisons.supplied_dataset_id,
           comparisons.qa_status_id,
           comparisons.area_difference,
           ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) AS percent_difference,
           comparisons.hausdorff_distance,
           comparisons.shape
    FROM comparisons
    WHERE comparisons.hausdorff_distance < 4
      AND ((comparisons.supplier_overlap + comparisons.existing_overlap)/2) > 40;

     ---------------------------------------------------------------
     -- Remove remaining temp tables
    DISCARD TEMP;
    ----------------------------------------------------------------
    UPDATE buildings_stage.supplied_datasets
    SET processed_date = now()
    WHERE supplied_dataset_id = dataset

END;

$$
LANGUAGE plpgsql;
