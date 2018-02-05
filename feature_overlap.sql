-- New Buildings
  -- runs through the incoming data and finds the incoming geometries which do not intersect 
  -- with any geometries in the existing table 
  
CREATE TABLE new_buildings AS
SELECT incoming.*, (st_area(incoming.geom)) AS area_new
FROM 
  incoming_building_outlines AS incoming LEFT JOIN
  existing_building_outlines AS existing ON
  ST_Intersects(incoming.geom, existing.geom)
WHERE existing.id IS NULL;

-----------------------------------------------------------------------------------------------------------------
-- Removed Buildings
  -- runs through the existing data and finds the existing geometries which do not intersect
  -- with any geometries in the incoming table
  
CREATE TABLE removed_buildings AS
SELECT existing.*, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) AS area_removed
FROM 
  existing_building_outlines AS existing LEFT JOIN
  incoming_building_outlines AS incoming ON
  ST_Intersects(existing.geom, incoming.geom)
WHERE incoming.id IS NULL;

------------------------------------------------------------------------------------------------------------------------
-- Intersection of incoming building with existing buildings
  -- runs through the geometries in the incoming table and finds those which intersect existing
  -- geometries by greater than 5%. it also records a count of how many existing geometries the incoming 
  -- polygons intersect. 
  
CREATE TEMP TABLE incoming_intersect AS
SELECT incoming.*, COUNT(existing.id) AS existing_count
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > .1
GROUP BY incoming.id
ORDER BY existing_count DESC;

INSERT INTO new_buildings
SELECT incoming.id, incoming.geom, incoming.imagery_so, incoming.known_erro, (st_area(incoming.geom)) AS area_new
FROM incoming_building_outlines incoming, existing_building_outlines existing
WHERE  ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) < 0.1;

--------------------------------------------------------------------------------------------------------------------
-- Incoming Potential Matches
  -- runs through the recently created table of incoming polygons which intersect by greater than 5% and saves those, the existing intersecting id 
  -- and the calculated intersect of the incoming geometries which only intersect one existing polyon. The results are saved to a new table.
  
CREATE TABLE incoming_potential_matches AS
SELECT incoming.*, existing.id AS existing_id, (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)*100) AS Overlap
FROM
  incoming_intersect incoming,
  existing_building_outlines existing 
WHERE ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > .1 AND incoming.existing_count = 1;

DELETE FROM new_buildings
WHERE new_buildings.id IN (SELECT incoming_intersect.id FROM incoming_intersect);
----------------------------------------------------------------------------------------------------------------------
-- Merged Buildings
  -- runs through the incoming intersection table and saves the incoming geometries which intersect more than one existing geometry by greater
  -- than 5% as geometries representing the merging of multiple existing geometries. 
  
CREATE TABLE merged_buildings AS
SELECT ii.*
FROM incoming_intersect AS ii
WHERE ii.existing_count > 1;

-------------------------------------------------------------------------------------------------------------------
-- Intersection of existing buildings with incoming buildings
  -- runs through the geometries in the existing table and finds those which intersect incoming geometries by greater than 5%.
  -- It also records a count of how many incoming geometries the existing polygons intersect.
  
CREATE TEMP TABLE existing_intersect AS
SELECT existing.*, COUNT(incoming.id) AS incoming_count
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(existing.geom, incoming.geom) AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > .1
GROUP BY existing.id
ORDER BY incoming_count DESC;

INSERT INTO removed_buildings
SELECT existing.id, existing.geom, existing.imagery_so, existing.known_erro, (st_area(existing.geom)) AS area_new
FROM incoming_building_outlines incoming, existing_building_outlines existing
WHERE  ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(existing.geom)) < 0.1;

-------------------------------------------------------------------------------------------------------------------
-- Existing Potential Matches
  -- runs through the recently created table of existing polygons which intersect by greater than 5% and saves them, the incoming intersecting id
  -- and the calculated intersect of the existing geometries which only intersect one incoming polygon. The results are save to a new table
  
CREATE TABLE existing_potential_matches AS
SELECT existing.*, incoming.id AS incoming_id, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)*100) AS Overlap
FROM
  existing_intersect existing,
  incoming_building_outlines incoming 
WHERE ST_Intersects(existing.geom, incoming.geom) AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > .1 AND existing.incoming_count = 1;

DELETE FROM removed_buildings
WHERE removed_buildings.id IN (SELECT existing_intersect.id FROM existing_intersect);

--------------------------------------------------------------------------------------------------------------------
-- 'Exploded' Buildings
  -- runs through the existing intersection tbale and saves the existing geometries which intersect more than one incoming geometry
  -- by greater than 5% as geometries representing the explosion (from one to many) of existing polygons.
  
CREATE TABLE exploded_buildings AS
SELECT ei.*
FROM existing_intersect AS ei
WHERE ei.incoming_count > 1;

-------------------------------------------------------------------------------------------------------------
-- remove from existing_potential_matches those that are in merged_buildings
DELETE FROM existing_potential_matches
WHERE existing_potential_matches.incoming_id IN (SELECT merged_buildings.id FROM merged_buildings);

-- remove from incoming_potential_matches those that are in exploded_buildings
DELETE FROM incoming_potential_matches
WHERE incoming_potential_matches.existing_id IN (SELECT exploded_buildings.id FROM exploded_buildings);

-------------------------------------------------------------------------------------------------------------
-- fix to potential match layers to ensure they have equal numbers of buildings. 
-- different numbers can be caused by two/more buildings intersecting a single other building
-- but not by enough to be encorperated into the merged/exploded tables initially.
    
CREATE TEMP TABLE m_duplicates AS
SELECT incoming_id AS id, 
 COUNT(incoming_id) AS Num
FROM existing_potential_matches
GROUP BY incoming_id
HAVING ( COUNT(incoming_id) > 1 );

INSERT INTO merged_buildings
SELECT incoming.id, incoming.geom, incoming.imagery_so, incoming.known_erro, m_duplicates.Num AS existing_count
FROM incoming_building_outlines incoming, m_duplicates
WHERE  incoming.id IN (
    SELECT id FROM m_duplicates);

DELETE FROM existing_potential_matches
WHERE existing_potential_matches.incoming_id IN (SELECT merged_buildings.id FROM merged_buildings);

DELETE FROM incoming_potential_matches
WHERE incoming_potential_matches.id IN (SELECT merged_buildings.id FROM merged_buildings);

CREATE TEMP TABLE e_duplicates AS
SELECT existing_id AS id, 
 COUNT(existing_id) AS Num
FROM incoming_potential_matches
GROUP BY existing_id
HAVING ( COUNT(existing_id) > 1 );

INSERT INTO exploded_buildings
SELECT existing.id, existing.geom, existing.imagery_so, existing.known_erro, e_duplicates.Num AS incoming_count
FROM existing_building_outlines existing, e_duplicates
WHERE  existing.id IN (
    SELECT id FROM e_duplicates);

DELETE FROM incoming_potential_matches
WHERE incoming_potential_matches.existing_id IN (SELECT exploded_buildings.id FROM exploded_buildings);

DELETE FROM existing_potential_matches
WHERE existing_potential_matches.id IN (SELECT exploded_buildings.id FROM exploded_buildings);

-------------------------------------------------------------------------------------------------------------
-- fix to potential match layers to ensure they have equal numebrs of buildings. 
-- different numbers can be caused by new/removed buildings intersecting new/removed buildings.

--insert into removed_buildings
create TEMP table add_removed AS
SELECT DISTINCT existing.id
FROM existing_potential_matches existing
WHERE id NOT IN (SELECT DISTINCT existing_id FROM incoming_potential_matches);

INSERT INTO removed_buildings
SELECT existing.id, existing.geom, existing.imagery_so, existing.known_erro, (st_area(existing.geom)) AS area_removed
FROM existing_building_outlines existing
WHERE  existing.id IN (
   SELECT id FROM add_removed);

DELETE FROM existing_potential_matches
WHERE existing_potential_matches.id IN (SELECT add_removed.id FROM add_removed);

-- insert into new buildings
create TEMP table new_add AS
SELECT DISTINCT incoming.id
FROM incoming_potential_matches incoming
WHERE id NOT IN (SELECT DISTINCT incoming_id FROM existing_potential_matches);

INSERT INTO new_buildings
SELECT incoming.id, incoming.geom, incoming.imagery_so, incoming.known_erro, (st_area(incoming.geom)) AS area_new
FROM incoming_building_outlines incoming
WHERE  incoming.id IN (
   SELECT id FROM new_add);

DELETE FROM incoming_potential_matches
WHERE incoming_potential_matches.id IN (SELECT new_add.id FROM new_add);

-------------------------------------------------------------------------------------------------------------
DROP TABLE incoming_intersect;  -- temp table
DROP TABLE existing_intersect;  -- temp table
DROP TABLE e_duplicates;  -- temp table
DROP TABLE m_duplicates;  -- temp table
DROP TABLE add_removed;  -- temp table
DROP TABLE new_add;  -- temp table
-------------------------------------------------------------------------------------------------------------
-- Comparisons of Overlaps
  -- runs through the two potential match tables and extracts the matching incoming and existing ids and % overlaps and presents these and 
  -- the calculated difference in a new table
  
CREATE TABLE comparisons AS
SELECT incoming.id AS incoming_id, incoming.overlap AS incoming_overlap, existing.id AS existing_id, existing.overlap AS existing_overlap, (existing.overlap - incoming.overlap) AS percent_difference, ST_Area(existing.geom) - ST_Area(incoming.geom) AS area_difference, ST_HausdorffDistance(incoming.geom, existing.geom) AS Hausdorff_Distance
FROM incoming_potential_matches incoming, existing_potential_matches existing
WHERE existing.incoming_id = incoming.id;

--------------------------------------------------------------------------------------------
-- Best Candidates and those to be Checked
  --creating temporary tables to store the incoming and existing building ids and related information
  -- the buildings to be checked are saved in the shapefile 'to_check' and those with a high level of
  -- confidence are saved to the table best candidates

CREATE TEMP TABLE to_check AS
SELECT comparisons.incoming_id, comparisons.incoming_overlap, comparisons.existing_id, comparisons.existing_overlap, comparisons.area_difference, comparisons.hausdorff_distance
FROM comparisons
WHERE comparisons.hausdorff_distance >= 4 and ((comparisons.incoming_overlap + comparisons.existing_overlap)/2) <= 40 OR comparisons.hausdorff_distance >= 4 and ((comparisons.incoming_overlap + comparisons.existing_overlap)/2) >= 40 OR comparisons.hausdorff_distance <= 4 and ((comparisons.incoming_overlap + comparisons.existing_overlap)/2) <= 40;

CREATE TEMP TABLE best_candidates AS
SELECT comparisons.incoming_id, comparisons.incoming_overlap, comparisons.existing_id, comparisons.existing_overlap, comparisons.area_difference, comparisons.hausdorff_distance
FROM comparisons
WHERE comparisons.hausdorff_distance < 4 and ((comparisons.incoming_overlap + comparisons.existing_overlap)/2) > 40;

-- table containing the incoming buildings to be checked with the existing building it intersects
-- the % overlap and hausdorff difference included as fields
CREATE TABLE incoming_buildings_to_check AS
SELECT incoming.id, incoming.imagery_so, incoming.known_erro, incoming.geom, to_check.existing_id, to_check.incoming_overlap, to_check.hausdorff_distance
FROM incoming_building_outlines AS incoming, to_check
WHERE incoming.id = to_check.incoming_id;

-- table containing the existing buildings to be checked with the incoming building it intersects
-- the % overlap and hausdorff difference included as fields
CREATE TABLE existing_buildings_to_check AS
SELECT existing.id, existing.imagery_so, existing.known_erro, existing.geom, to_check.incoming_id, to_check.existing_overlap, to_check.hausdorff_distance
FROM existing_building_outlines AS existing, to_check
WHERE existing.id = to_check.existing_id;

-- table containing the incoming buildings with a high level of confidence. Included as fields area also the existing
-- intersecting building, the % overlap and hausdorff difference
CREATE TABLE incoming_buildings_best_candidates AS
SELECT incoming.id, incoming.imagery_so, incoming.known_erro, incoming.geom, best_candidates.existing_id, best_candidates.incoming_overlap, best_candidates.hausdorff_distance
FROM incoming_building_outlines AS incoming, best_candidates
WHERE incoming.id = best_candidates.incoming_id;

-- table containing the existing buildings with a high level of confidence. Included as fields area also the incoming
-- intersecting building, the % overlap and hausdorff difference
CREATE TABLE existing_buildings_best_candidates AS
SELECT existing.id, existing.imagery_so, existing.known_erro, existing.geom, best_candidates.incoming_id, best_candidates.existing_overlap, best_candidates.hausdorff_distance
FROM existing_building_outlines AS existing, best_candidates
WHERE existing.id = best_candidates.existing_id;

---------------------------------------------------------------------------------------
-- Removing unecessary temp tables
DROP TABLE to_check;  --temp table
DROP TABLE best_candidates; --temp table