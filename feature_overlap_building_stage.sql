-------------------------------------------------------------------------------------------------------------------
-- NEW BUILDINGS
-------------------------------------------------------------------------------------------------------------------
  -- runs through the supplied data and finds the geometries which do not intersect 
  -- with any geometries in the existing table 
  
INSERT INTO buildings_stage.new
SELECT supplier.supplied_outline_id, supplier.supplied_dataset_id, NULL, supplier.geom
FROM 
  buildings_stage.supplied_outlines AS supplier LEFT JOIN
  buildings_stage.existing_subset_extract AS existing ON
  ST_Intersects(supplier.geom, existing.geom)
WHERE existing.building_outline_id IS NULL;

-----------------------------------------------------------------------------------------------------------------
-- REMOVED BUILDINGS
-----------------------------------------------------------------------------------------------------------------
  -- runs through the existing data and finds the geometries which do not intersect
  -- with any geometries in the supplied table
  
INSERT INTO buildings_stage.removed
SELECT existing.building_outline_id, existing.supplied_dataset_id, NULL, existing.geom
FROM 
  buildings_stage.existing_subset_extracts existing LEFT JOIN
  buildings_stage.supplied_outlines supplier ON
  ST_Intersects(existing.geom, supplier.geom)
WHERE supplier.supplied_otuline_id IS NULL;

-----------------------------------------------------------------------------------------------------------------
-- MERGED BUILDINGS
-----------------------------------------------------------------------------------------------------------------

-- Intersection of supplied building with existing buildings
  -- runs through the geometries in the supplied table and finds those which intersect existing
  -- geometries by greater than 10%. it also records a count of how many existing geometries the supplied 
  -- polygons intersect. 


--TEMP TABLE

CREATE TEMP TABLE buildings_stage.supplier_intersect AS
SELECT supplier.supplied_outline_id, supplier.supplied_dataset_id, COUNT(existing.building_outline_id) AS existing_count, supplier.geom
FROM
  buildings_stage.supplied_outlines supplier,
  buildings_stage.existing_subset_extracts existing
WHERE ST_Intersects(supplier.geom, existing.geom) AND (st_area(st_intersection(supplier, existing.geom))/st_area(existing.geom)) > .1 AND (st_area(st_intersection(supplier, existing.geom))/st_area(supplier.geom)) > .1
GROUP BY supplier.supplied_outline_id
ORDER BY existing_count DESC;


-- INSERT INTO new
-- add the buildings that overlap by less than 10% to the new table

INSERT INTO buildings_stage.new
SELECT supplier.supplied_outline_id, supplier.supplied_dataset_id, NULL, supplier.geom
FROM buildings_stage.supplied_outlines supplier, buildings_stage.existing_subset_extracts existing
WHERE  ST_Intersects(supplier.geom, existing.geom) AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(existing.geom)) < 0.1 AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(supplier.geom)) < 0.1;


-- TEMP TABLE

CREATE TEMP TABLE buildings_stage.to_merge AS
SELECT supplier.supplied_outline_id, supplier.supplied_dataset_id, existing.building_outline_id AS e_id, st_area(st_intersection(supplier.geom, existing.geom)) AS intersection, existing.geom
FROM buildings_stage.supplied_outlines supplier, buildings_stage.existing_subset_extract existing, supplier_intersect
WHERE ST_Intersects(supplier.geom, existing.geom) AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(suplier.geom)) > .1 AND supplier_intersect.supplied_outline_id = supplier.supplied_outline_id AND supplier_intersect.existing_count > 1;


-- TEMP TABLE

CREATE TEMP TABLE buildings_stage.merged_overlap AS 
SELECT supplied_outline_id, SUM(intersection) AS total
FROM buildings_stage.to_merge
GROUP BY supplied_outline_id;


--INSERT INTO merged
-- the supplied buildings that intersect more than one existing building

INSERT INTO buildings_stage.merged
SELECT supplier.supplied_outline_id, supplier.supplied_dataset_id, NULL, merged_overlap.total AS area_covering, (merged_overlap.total/ST_area(supplier.geom))*100 AS percent_covering, supplier.geom
FROM buildings_stage.supplied_outlines as supplier, buildings_stage.merged_overlap AS merged_overlap
WHERE supplier.supplied_outline_id = merged_overlap.supplied_outline_id;

-- INSERT INTO merged_candidates
-- the existing buildings that are potential merges

INSERT INTO buildings_stage.merge_candidates
SELECT build.e_id AS building_outline_id, build.supplied_outline_id, build.supplied_dataset_id, build.intersection AS area_covering, build.intersection/ST_area(supplier.geom)*100 AS percent_covering
FROM buildings_stage.to_merge build, buildings_stage.supplied_outlines supplier
WHERE supplier.supplied_outline_id = build.supplied_outline_id;

-------------------------------------------------------------------------------------------------------------------
-- SPLIT BUILDINGS
-------------------------------------------------------------------------------------------------------------------

-- Intersection of existing buildings with supplied buildings
  -- runs through the geometries in the existing table and finds those which intersect supplied geometries by greater than 10%.
  -- It also records a count of how many supplied geometries the existing polygons intersect.
  
-- TEMP TABLE

CREATE TEMP TABLE buildings_stage.existing_intersect AS
SELECT existing.building_outline_id, existing.supplied_dataset_id, COUNT(supplier.supplied_outline_id) AS supplied_count
FROM
  buildings_stage.supplied_outlines supplier,
  buildings_stage.existing_subset_extract existing
WHERE ST_Intersects(existing.geom, supplier.geom) AND (st_area(st_intersection(existing.geom, supplier.geom))/st_area(existing.geom)) > .1 AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(supplier.geom)) >.1
GROUP BY existing.building_outline_id
ORDER BY supplied_count DESC;

-- INSERT INTO Removed
-- add the buildings with less than 10% overlap to the removed table

INSERT INTO buildings_stage.removed
SELECT existing.building_outline_id, existing.supplied_dataset_id, NULL, existing.geom
FROM buildings_stage.supplied_outlines supplier, buildings_stage.existing_subset_extract existing
WHERE  ST_Intersects(supplier.geom, existing.geom) AND ((st_area(st_intersection(supplier.geom, existing.geom))/st_area(existing.geom)) < 0.1 OR (st_area(st_intersection(supplier.geom, existing.geom))/st_area(supplier.geom)) < 0.1);

-- TEMP TABLE

CREATE TEMP TABLE buildings_stage.to_split AS
SELECT existing.building_outline_id, supplier.supplied_outline_id AS s_id, st_area(st_intersection(supplier.geom, existing.geom)) AS intersection, supplier.geom
FROM buildings_stage.supplied_outlines supplier, buildings_stage.existing_subset_extract existing, existing_intersect
WHERE ST_Intersects(supplier.geom, existing.geom) AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(existing.geom)) >.1 AND (st_area(st_intersection(supplier.geom, existing.geom))/st_area(supplier.geom)) > .1 AND existing_intersect.building_outline_id = existing.building_outline_id AND existing_intersect.supplied_count > 1;

-- TEMP TABLE

CREATE TEMP TABLE buildings_stage.split_overlap AS 
SELECT building_outline_id, SUM(intersection) AS total
FROM buildings_stage.to_split
GROUP BY building_outline_id;

-- INSERT INTO split
-- the multiple supplied buildings that intersect with the same existing building

INSERT INTO buildings_stage.split
SELECT supplier.supplied_outline_id AS supplied_outline_id, supplier.supplied_dataset_id AS supplied_dataset_id, NULL AS qa_status_id, to_split.intersection AS area_covering, (to_split.intersection/ST_area(supplier.geom))*100 AS percent_covering, supplier.geom
FROM buildings_stage.supplied_outlines supplier, buildings_stage.to_split split
WHERE supplier.supplied_outline_id = to_split.s_id;

-- INSERT INTO split_candidates
-- the existing buildings that intersect with more than one supplied building

INSERT INTO buildings_stage.split_candidates
SELECT split_overlap.building_outline_id AS building_outline_id, to_split.s_id AS supplied_outline_id, supplier.supplied_dataset_id AS supplied_dataset_id, split_overlap.total AS area_covering, split_overlap.total/ST_area(existing.geom)*100 AS percent_covering
FROM buildings_stage.split_overlap split_overlap, buildings_stage.existing_subset_extract existing, buildings_stage.to_split to_split, buildings_stage.supplied_outlines supplier
WHERE existing.building_outline_id = build.building_outline_id AND build.building_outline_id = to_split.building_outline_id AND to_split.s_id = supplier.supplied_outline_id;

-----------------------------------------------------------------------------------------------------------------

-- DELETE FROM existing intersect
-- remove the split buildings from the existing intersect layer

DELETE FROM buildings_stage.existing_intersect
WHERE buildings_stage.existing_intersect.supplied_count > 1;

-- DELETE FROM supplied intersect
-- remove the merged buildings from the supplied intersect layer

DELETE FROM buildings_stage.supplied_intersect
WHERE buildings_stage.supplied_intersect.existing_count > 1;

-- DELETE FROM existing intersect
-- remove from existing intersect the buildings which have been merged

DELETE FROM buildings_stage.existing_intersect
WHERE buildings_stage.existing_intersect.building_outline_id IN (SELECT to_merge.e_id FROM buildings_stage.to_merge);

-- DELETE FROM supplied intersect
-- remove from supplied intersect the buildings which represent splits

DELETE FROM buildings_stage.supplied_intersect
WHERE buildings_stage.supplied_intersect.supplied_outline_id IN (SELECT to_split.s_id FROM buildings.to_split);

----------------------------------------------------------------
DROP TABLE buildings_stage.to_split; -- drop temp table
DROP TABLE buildings_stage.split_overlap; --drop temp table
DROP TABLE buildings_stage.to_merge; -- drop temp table
DROP TABLE buildings_stage.merged_overlap; --drop temp table
----------------------------------------------------------------

-----------------------------------------------------------------------------------------------------------------
-- BEST CANDIDATES & TO CHECK
-----------------------------------------------------------------------------------------------------------------

-- TEMP TABLE
-- of all 1:1 matches and their % overlap, area difference and Hausdorff Distance

CREATE TEMP TABLE buildings_stage.comparisons AS
SELECT supplier.supplier_outline_id, building.building_outline_id, NULL AS supplied_dataset_id, NULL AS qa_status_id, ST_area(ST_intersection(supplier.geom, building.geom))/ST_area(supplier.geom)*100 AS supplier_overlap, ST_area(ST_intersection(supplier.geom, building.geom))/ST_area(building.geom)*100 AS existing_overlap, ST_area(building.geom) - ST_area(supplier.geom) AS area_difference, ST_hausdorffDistance(supplier.geom, building.geom) AS hausdorff_distance, supplier.geom
FROM supplied_intersect supplier, existing_intersect building
WHERE ST_area(ST_intersection(supplier.geom, building.geom))/ST_area(supplier.geom) > 0.1 AND ST_area(ST_intersection(supplier.geom, building.geom))/ST_area(building.geom) > 0.1;


-- INSERT INTO To Check
-- add matches that fail to meet best candidate criteria to this table

INSERT INTO buildings_stage.to_check
SELECT comparisons.supplier_outline_id, comparisons.building_outline_id, comparisons.supplied_dataset_id, comparisons.qu_status_id, comparisons.supplier_overlap, comparisons.existing_overlap, comparisons.area_difference, comparisons.hausdorff_distance, comparisons.geom
FROM buildings_stage.comparisons comparisons
WHERE comparisons.hausdorff_distance >= 4 AND ((comparisons.supplied_overlap + comparisons.existing_overlap)/2) <= 40 OR comparisons.hausdorff_distance >= 4 AND ((comparisons.supplied_overlap + comparisons.existing_overlap)/2) >= 40 OR comparisons.hausdorff_distance <= 4 AND ((comparisons.supplied_overlap + comparisons.existing_overlap)/2) <= 40;

-- INSERT INTO Best Candidates
-- add matches that have greater than 40% overlap and less than 4 Hausdorff Distance

INSERT INTO buildings_stage.best_candidates
SELECT comparisons.supplier_outline_id, comparisons.building_outline_id, comparisons.supplied_dataset_id, comparisons.qu_status_id, comparisons.supplier_overlap, comparisons.existing_overlap, comparisons.area_difference, comparisons.hausdorff_distance, comparisons.geom
FROM buildings_stage.comparisons comparisons
WHERE comparisons.hausdorff_distance < 4 AND ((comparisons.supplied_overlap + comparisons.existing_overlap)/2) > 40;

---------------------------------------------------------------
 -- Remove remaining temp tables
 DROP TABLE buildings_stage.existing_intersect;
 DROP TABLE buildings_stage.supplied_intersect;
 DROP TABLE buildings_stage.comparisons;
 ---------------------------------------------------------------------------------------------------------------


