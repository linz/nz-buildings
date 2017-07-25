-- Add Imagery souce attribution to dataset. 

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Canterbury 0.4m Rural Aerial Photos (2012-2013)' FROM canterbury_rural_12_13
WHERE ST_Intersects(nz_building_outlines_pilot.geom, canterbury_rural_12_13.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Canterbury 0.4m Rural Aerial Photos (2013-2014)' FROM canterbury_rural_13_14
WHERE ST_Intersects(nz_building_outlines_pilot.geom, canterbury_rural_13_14.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2014-15)' FROM canterbury_rural_14_15
WHERE ST_Intersects(nz_building_outlines_pilot.geom, canterbury_rural_14_15.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Hawkes Bay 0.3m Rural Aerial Photos (2014-15)' FROM hawkes_bay_14_15
WHERE ST_Intersects(nz_building_outlines_pilot.geom, hawkes_bay_14_15.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Otago 0.4m Rural Aerial Photos (2013-14)' FROM otago_rural_13_14
WHERE ST_Intersects(nz_building_outlines_pilot.geom, otago_rural_13_14.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Waikato 0.5m Rural Aerial Photos (2012-2013)' FROM waikato_rural_12_13
WHERE ST_Intersects(nz_building_outlines_pilot.geom, waikato_rural_12_13.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Waikato District 0.1m Urban Aerial Photos (2014)' FROM waikato_urban_14
WHERE ST_Intersects(nz_building_outlines_pilot.geom, waikato_urban_14.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Christchurch 0.075m Urban Aerial Photos (2015-2016)' FROM christchurch_urban_15_16
WHERE ST_Intersects(nz_building_outlines_pilot.geom, christchurch_urban_15_16.geom);

UPDATE nz_building_outlines_pilot
SET imagery_source = 'Waimakariri 0.075m Urban Aerial Photos (2015-2016)' FROM waimakariri_urban_15_16
WHERE ST_Intersects(nz_building_outlines_pilot.geom, waimakariri_urban_15_16.geom);


SELECT a.imagery_source, a.id FROM nz_building_outlines_pilot a
WHERE a.imagery_source IS null;

-- Add additional Building Outlines
INSERT INTO building_outlines.nz_building_outlines_pilot (
geom)
SELECT geom
FROM building_outlines.building_canterbury_rural_15_16_no_overlap;

UPDATE building_outlines.nz_building_outlines_pilot
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2015-2016)'
WHERE imagery_source IS Null

-- Add Error Messages to buildings identified with markups.

SELECT * FROM known_error
order by descriptio;

UPDATE nz_building_outlines_pilot
SET known_error = 'driveway' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'driveway';

UPDATE nz_building_outlines_pilot
SET known_error = 'orchard' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'orchard';

UPDATE nz_building_outlines_pilot
SET known_error = 'waterbody' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'waterbody';

UPDATE nz_building_outlines_pilot
SET known_error = 'silage' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'silage';

UPDATE nz_building_outlines_pilot
SET known_error = 'vehicle' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'vehicle';

UPDATE nz_building_outlines_pilot
SET known_error = 'swimming pool' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'swimming pool';

UPDATE nz_building_outlines_pilot
SET known_error = 'inaccurate capture' FROM known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom)
AND descriptio = 'miscapture';

SELECT * FROM nz_building_outlines_pilot, known_error
WHERE ST_Intersects(nz_building_outlines_pilot.geom, known_error.geom) 
AND known_error is null;

-- Add extra canterbury data

ALTER TABLE building_outlines.building_canterbury_rural_15_16
ADD COLUMN imagery_source character varying(250);

UPDATE building_outlines.building_canterbury_rural_15_16
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2015-2016)'


