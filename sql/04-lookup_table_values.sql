-- LOOKUP TABLE INSERTS

-- Capture Method

INSERT INTO buildings_common.capture_method (value) VALUES ('Unknown');
INSERT INTO buildings_common.capture_method (value) VALUES ('Derived');
INSERT INTO buildings_common.capture_method (value) VALUES ('Derived From Cadastre');
INSERT INTO buildings_common.capture_method (value) VALUES ('Derived From Scanned Map');
INSERT INTO buildings_common.capture_method (value) VALUES ('Feature Extraction');
INSERT INTO buildings_common.capture_method (value) VALUES ('GPS');
INSERT INTO buildings_common.capture_method (value) VALUES ('GPS Differential');
INSERT INTO buildings_common.capture_method (value) VALUES ('GPS Mobile');
INSERT INTO buildings_common.capture_method (value) VALUES ('Trace');
INSERT INTO buildings_common.capture_method (value) VALUES ('Trace Stereophotography');
INSERT INTO buildings_common.capture_method (value) VALUES ('Trace Orthophotography');
INSERT INTO buildings_common.capture_method (value) VALUES ('Trace Other Image');
INSERT INTO buildings_common.capture_method (value) VALUES ('Engineering Survey Data');
INSERT INTO buildings_common.capture_method (value) VALUES ('Estimated');

-- Capture Source Group

INSERT INTO buildings_common.capture_source_group (value, description) VALUES ('NZ Aerial Imagery', 'Replace with link to LDS table...');

-- Lifecycle Stage

INSERT INTO buildings.lifecycle_stage (value) VALUES ('Current');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Disused');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Replaced');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Under Construction');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Unknown');

-- Use

INSERT INTO buildings.use (value) VALUES ('Abattoir');
INSERT INTO buildings.use (value) VALUES ('Camp');
INSERT INTO buildings.use (value) VALUES ('Cement Works');
INSERT INTO buildings.use (value) VALUES ('Church');
INSERT INTO buildings.use (value) VALUES ('Energy Facility');
INSERT INTO buildings.use (value) VALUES ('Factory');
INSERT INTO buildings.use (value) VALUES ('Fertilizer Works');
INSERT INTO buildings.use (value) VALUES ('Fire Lookout');
INSERT INTO buildings.use (value) VALUES ('Forest Headquarters');
INSERT INTO buildings.use (value) VALUES ('Gas Compound');
INSERT INTO buildings.use (value) VALUES ('Greenhouse');
INSERT INTO buildings.use (value) VALUES ('Gun Club');
INSERT INTO buildings.use (value) VALUES ('Gun Emplacement');
INSERT INTO buildings.use (value) VALUES ('Hall');
INSERT INTO buildings.use (value) VALUES ('Homestead');
INSERT INTO buildings.use (value) VALUES ('Hospital');
INSERT INTO buildings.use (value) VALUES ('Hut');
INSERT INTO buildings.use (value) VALUES ('Lodge');
INSERT INTO buildings.use (value) VALUES ('Marae');
INSERT INTO buildings.use (value) VALUES ('Methanol Plant');
INSERT INTO buildings.use (value) VALUES ('Mill');
INSERT INTO buildings.use (value) VALUES ('Natural Gas Plant');
INSERT INTO buildings.use (value) VALUES ('Observatory');
INSERT INTO buildings.use (value) VALUES ('Power Generation');
INSERT INTO buildings.use (value) VALUES ('Prison');
INSERT INTO buildings.use (value) VALUES ('Salt Works');
INSERT INTO buildings.use (value) VALUES ('School');
INSERT INTO buildings.use (value) VALUES ('Shelter');
INSERT INTO buildings.use (value) VALUES ('Shingle Works');
INSERT INTO buildings.use (value) VALUES ('Silo');
INSERT INTO buildings.use (value) VALUES ('Stamping Battery');
INSERT INTO buildings.use (value) VALUES ('Substation');
INSERT INTO buildings.use (value) VALUES ('Surf Club');
INSERT INTO buildings.use (value) VALUES ('Synthetic Fuel Plant');
INSERT INTO buildings.use (value) VALUES ('University');
INSERT INTO buildings.use (value) VALUES ('Visitor Centre');
INSERT INTO buildings.use (value) VALUES ('Water Treatment Plant');

-- Organisation

INSERT INTO buildings_bulk_load.organisation (value) VALUES ('Ecopia');

-- Bulk Load Status

INSERT INTO buildings_bulk_load.bulk_load_status (value) VALUES ('Supplied');
INSERT INTO buildings_bulk_load.bulk_load_status (value) VALUES ('Added During QA');

-- QA Status

INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Manually Altered Relationship');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Not Checked');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Okay');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Pending');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Refer to Supplier');
