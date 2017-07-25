-- Add data from 2017 capture of building_outlines in Northland, Marlborough, West Coast, Whanganui/Manawatu, Tasman.
-- update attributes for some previous errors in uploaded data.


ALTER TABLE building_outlines.building_outlines_2017_capture
ADD COLUMN imagery_source character varying(250),
ADD COLUMN known_error character varying(50);

UPDATE building_outlines.nz_building_outlines_pilot
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2015-2016)'
WHERE id = 2326763

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'Northland 0.4m Rural Aerial Photos (2014-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'Northland' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'Manawatu Whanganui 0.3m Rural Aerial Photos (2015-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'Manawatu Whanganui' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'Tasman 0.3m Rural Aerial Photos (2015-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'Tasman' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'West Coast 0.3m Rural Aerial Photos (2015-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'West Coast' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'Marlborough 0.2m Rural Aerial Photos (2015-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'Marlborough' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);

INSERT INTO building_outlines.nz_building_outlines_pilot (
geom,
imagery_source)
SELECT geom, imagery_source
FROM building_outlines.building_outlines_2017_capture;

SELECT COUNT(*) FROM building_outlines.nz_building_outlines_pilot WHERE imagery_source = 'Northland 0.4m Rural Aerial Photos (2014-2016)';

SELECT id, imagery_source, known_error, ST_AsText(geom) as geom 
FROM building_outlines.nz_building_outlines_pilot;