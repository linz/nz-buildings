-- Deploy nz-buildings:buildings/default_values to pg

BEGIN;

-- lifecycle_stage
INSERT INTO buildings.lifecycle_stage (value) VALUES
('Current'),
('Disused'),
('Replaced'),
('Under Construction'),
('Unknown');

-- use
INSERT INTO buildings.use (value) VALUES
('Abattoir'),
('Camp'),
('Cement Works'),
('Church'),
('Energy Facility'),
('Factory'),
('Fertilizer Works'),
('Fire Lookout'),
('Forest Headquarters'),
('Gas Compound'),
('Greenhouse'),
('Gun Club'),
('Gun Emplacement'),
('Hall'),
('Homestead'),
('Hospital'),
('Hut'),
('Lodge'),
('Marae'),
('Methanol Plant'),
('Mill'),
('Natural Gas Plant'),
('Observatory'),
('Power Generation'),
('Prison'),
('Salt Works'),
('School'),
('Shelter'),
('Shingle Works'),
('Silo'),
('Stamping Battery'),
('Substation'),
('Surf Club'),
('Synthetic Fuel Plant'),
('University'),
('Visitor Centre'),
('Water Treatment Plant');

COMMIT;
