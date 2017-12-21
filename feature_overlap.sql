-- New Buildings
  -- runs through the incoming data and finds the incoming geometries which do not intersect 
  -- with any geometries in the existing table 
CREATE TABLE new_buildings AS
SELECT incoming.*, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(incoming.geom)) AS area_new
FROM 
  incoming_building_outlines AS incoming LEFT JOIN
  existing_building_outlines AS existing ON
  ST_Intersects(incoming.geom,existing.geom)
WHERE existing.id IS NULL;


-- Removed Buildings
  -- runs through the existing data and finds the existing geometries which do not intersect
  -- with any geometries in the incoming table
CREATE TABLE removed_buildings AS
SELECT existing.*, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) AS area_removed
FROM 
  existing_building_outlines AS existing LEFT JOIN
  incoming_building_outlines AS incoming ON
  ST_Intersects(existing.geom,incoming.geom)
WHERE incoming.id IS NULL;


-- Intersection of incoming building with existing buildings
  -- runs through the geometries in the incoming table and finds those which intersect existing
  -- geometries by greater than 5%. it also records a count of how many existing geometries the incoming 
  -- polygons intersect. 
CREATE TABLE incoming_intersect AS
SELECT incoming.*, COUNT(existing.id) AS existing_count
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > .06
GROUP BY incoming.id
ORDER BY existing_count DESC;


-- Incoming Potential Matches
  -- runs through the recently created table of incoming polygons which intersect by greater than 5% and saves those, the existing intersecting id 
  -- and the calculated intersect of the incoming geometries which only intersect one existing polyon. The results are saved to a new table.
CREATE TABLE incoming_potential_matches AS
SELECT incoming.*, existing.id AS existing_id, (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)*100) AS Overlap
FROM
  incoming_intersect incoming,
  existing_building_outlines existing 
WHERE ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > .06 AND incoming.existing_count = 1;


-- Merged Buildings
  -- runs through the incoming intersection table and saves the incoming geometries which intersect more than one existing geometry by greater
  -- than 5% as geometries representing the merging of multiple existing geometries. 
CREATE TABLE merged_buildings AS
SELECT ii.*
FROM incoming_intersect AS ii
WHERE ii.existing_count > 1;


-- Intersection of existing buildings with incoming buildings
  -- runs through the geometries in the existing table and finds those which intersect incoming geometries by greater than 5%.
  -- It also records a count of how many incoming geometries the existing polygons intersect.
CREATE TABLE existing_intersect AS
SELECT existing.*, COUNT(incoming.id) AS incoming_count
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(existing.geom, incoming.geom) AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > .06
GROUP BY existing.id
ORDER BY incoming_count DESC;


-- Existing Potential Matches
  -- runs through the recently created table of existing polygons which intersect by greater than 5% and saves them, the incoming intersecting id
  -- and the calculated intersect of the existing geometries which only intersect one incoming polygon. The results are save to a new table
CREATE TABLE existing_potential_matches AS
SELECT existing.*, incoming.id AS incoming_id, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)*100) AS Overlap
FROM
  existing_intersect existing,
  incoming_building_outlines incoming 
WHERE ST_Intersects(existing.geom, incoming.geom) AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > .06 AND existing.incoming_count = 1;


-- 'Exploded' Buildings
  -- runs through the existing intersection tbale and saves the existing geometries which intersect more than one incoming geometry
  -- by greater than 5% as geometries representing the explosion (from one to many) of existing polygons.
CREATE TABLE exploded_buildings AS
SELECT ei.*
FROM existing_intersect AS ei
WHERE ei.incoming_count > 1;


-- add incoming buildings with less than 5% overlap to new buildings
    -- nb: no buildings in the subset fit this criteria 
    -- runs through incoming and existing layers and finds the existing buildings that intersect with an incoming geometry. Of those that intersect, 
    -- the incoming buildings that intersect only one existing building by less than 5% are considered new buildings and are added to the 
    -- new building table 

CREATE TABLE new_building_small_overlap AS
SELECT incoming.*, COUNT(existing.id) AS existing_count 
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(incoming.geom, existing.geom) AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > .00
GROUP BY incoming.id
ORDER BY existing_count DESC;

INSERT INTO new_buildings
SELECT incoming.id, incoming.geom, incoming.imagery_so, incoming.known_erro, (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) AS area
FROM new_building_small_overlap incoming, existing_building_outlines existing
WHERE incoming.existing_count = 1 AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) > 0.00 AND (st_area(st_intersection(incoming.geom, existing.geom))/st_area(incoming.geom)) < .05;


-- add existing buildings with less than 5% overlap to removed buildings 
    -- nb: not buildings in the subset fit this criteria
    -- runs through incoming and existing layers and finds the incoming buildings that intersect existing buildings. Of those that intersect, 
    -- the existing buildings that intersect only one incoming building by less than 5% are considered removed buildings and are added to the
    -- removed building table

CREATE TABLE removed_building_small_overlap AS
SELECT existing.*, COUNT(incoming.id) AS incoming_count 
FROM
  incoming_building_outlines incoming,
  existing_building_outlines existing
WHERE ST_Intersects(existing.geom, incoming.geom) AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > .0
GROUP BY existing.id
ORDER BY incoming_count DESC;

INSERT INTO removed_buildings
SELECT existing.id, existing.geom, existing.imagery_so, existing.known_erro, (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) AS area
FROM removed_building_small_overlap existing, incoming_building_outlines incoming
WHERE existing.incoming_count = 1 AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) > 0.00 AND (st_area(st_intersection(existing.geom, incoming.geom))/st_area(existing.geom)) < .05;

-- Removing uncessary tables
DROP TABLE incoming_intersect;  -- intermediate table
DROP TABLE existing_intersect;  -- intermediate table
DROP TABLE new_building_small_overlap;  -- intermediate table
DROP TABLE removed_building_small_overlap; -- intermediate table


-- Comparisons of Overlaps
  -- runs through the two potential match tables and extracts the matching incoming and existing ids and % overlaps and presents these and 
  -- the calculated difference in a new table
CREATE TABLE comparisons AS
SELECT incoming.id AS incoming_id, incoming.overlap AS incoming_overlap, existing.id AS existing_id, existing.overlap AS existing_overlap, (existing.overlap - incoming.overlap) AS percent_difference, ST_Area(existing.geom) - ST_Area(incoming.geom) AS area_difference, ST_HausdorffDistance(incoming.geom, existing.geom) AS Hausdorff_Distance
FROM incoming_potential_matches incoming, existing_potential_matches existing
WHERE existing.incoming_id = incoming.id;


-- Final Best Candidates
-- it is always desired to present the most recent building outlines, therefore the incoming buildings.?
CREATE TABLE best_candidates AS
SELECT * FROM incoming_building_outlines