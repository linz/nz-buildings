ALTER TABLE building_outlines.building_canterbury_rural_15_16
ADD COLUMN imagery_source character varying(250);

UPDATE building_outlines.building_canterbury_rural_15_16
SET imagery_source = 'Canterbury 0.3m Rural Aerial Photos (2015-2016)'
