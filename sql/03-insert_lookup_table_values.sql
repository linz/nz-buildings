-- LOOKUP TABLE INSERTS

-- Capture Method

INSERT INTO buildings.capture_method (value) VALUES ('Unknown');
INSERT INTO buildings.capture_method (value) VALUES ('Derived');
INSERT INTO buildings.capture_method (value) VALUES ('Derived From Cadastre');
INSERT INTO buildings.capture_method (value) VALUES ('Derived From Scanned Map');
INSERT INTO buildings.capture_method (value) VALUES ('Feature Extraction');
INSERT INTO buildings.capture_method (value) VALUES ('GPS');
INSERT INTO buildings.capture_method (value) VALUES ('GPS Differential');
INSERT INTO buildings.capture_method (value) VALUES ('GPS Mobile');
INSERT INTO buildings.capture_method (value) VALUES ('Trace');
INSERT INTO buildings.capture_method (value) VALUES ('Trace Stereophotography');
INSERT INTO buildings.capture_method (value) VALUES ('Trace Orthophotography');
INSERT INTO buildings.capture_method (value) VALUES ('Trace Other Image');
INSERT INTO buildings.capture_method (value) VALUES ('Engineering Survey Data');
INSERT INTO buildings.capture_method (value) VALUES ('Estimated');

-- Capture Source Group

INSERT INTO buildings.capture_source_group (value) VALUES ('NZ Aerial Imagery');

-- Lifecycle Stage

INSERT INTO buildings.lifecycle_stage (value) VALUES ('Current');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Disused');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Replaced');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Under Construction');
INSERT INTO buildings.lifecycle_stage (value) VALUES ('Unknown');

-- Organisation

INSERT INTO buildings_stage.organisation (value) VALUES ('Ecopia');

-- QA Status

INSERT INTO buildings_stage.qa_status (value) VALUES ('Not Checked');
INSERT INTO buildings_stage.qa_status (value) VALUES ('Okay');
INSERT INTO buildings_stage.qa_status (value) VALUES ('Pending');
INSERT INTO buildings_stage.qa_status (value) VALUES ('Refer to Supplier');
