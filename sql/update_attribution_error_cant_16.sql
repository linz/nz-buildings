SELECT nzbo.id, nzbo.geom, nzbo.imagery_source, nzbo.known_error FROM building_outlines.nz_building_delivery_part_one_canterbury can, building_outlines.nz_building_outlines_pilot nzbo
WHERE ST_Equals(can.geom , nzbo.geom)
AND nzbo.imagery_source = 'Waimakariri 0.075m Urban Aerial Photos (2015-2016)';
--1690

/*
--'Canterbury 0.3m Rural Aerial Photos (2014-2015)'

UPDATE building_outlines.building_outlines_2017_capture
SET imagery_source = 'Northland 0.4m Rural Aerial Photos (2014-2016)' FROM building_outlines.regional_coverage_2017
WHERE regional_coverage_2017.imgarea = 'Northland' AND ST_Intersects(building_outlines_2017_capture.geom, regional_coverage_2017.geom);
*/

Begin Transaction; 

UPDATE  building_outlines.nz_building_outlines_pilot nzbo
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2014-2015)' FROM building_outlines.nz_building_delivery_part_one_canterbury can
WHERE ST_Equals(can.geom , nzbo.geom) AND nzbo.imagery_source = 'Waimakariri 0.075m Urban Aerial Photos (2015-2016)';

SELECT nzbo.id, nzbo.geom, nzbo.imagery_source, nzbo.known_error FROM building_outlines.nz_building_delivery_part_one_canterbury can, building_outlines.nz_building_outlines_pilot nzbo
WHERE ST_Equals(can.geom , nzbo.geom)
AND nzbo.imagery_source = 'Waimakariri 0.075m Urban Aerial Photos (2015-2016)';

Commit;


