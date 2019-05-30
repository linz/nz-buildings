
-- buildings_common.capture_method

INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (1, 'Unknown');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (2, 'Derived');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (3, 'Derived From Cadastre');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (4, 'Derived From Scanned Map');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (5, 'Feature Extraction');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (6, 'GPS');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (7, 'GPS Differential');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (8, 'GPS Mobile');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (9, 'Trace');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (10, 'Trace Stereophotography');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (11, 'Trace Orthophotography');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (12, 'Trace Other Image');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (13, 'Engineering Survey Data');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (14, 'Estimated');
INSERT INTO buildings_common.capture_method (capture_method_id, value) VALUES (15, 'Test Capture Method');

-- buildings_common.capture_source_group

INSERT INTO buildings_common.capture_source_group (capture_source_group_id, value, description) VALUES (1, 'NZ Aerial Imagery', 'external_source_id will link to the imagery_survey_id from https://data.linz.govt.nz/layer/95677-nz-imagery-surveys/');
INSERT INTO buildings_common.capture_source_group (capture_source_group_id, value, description) VALUES (2, 'Test CS Value', 'Test CS Description');

-- buildings_common.capture_source

INSERT INTO buildings_common.capture_source (capture_source_id, capture_source_group_id, external_source_id) VALUES (1001, 1, '1');
INSERT INTO buildings_common.capture_source (capture_source_id, capture_source_group_id, external_source_id) VALUES (1, 1, 'Test External Source');
