-- Deploy buildings:buildings_common/default_values to pg

BEGIN;

-- capture_method
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

-- capture_source_group
INSERT INTO buildings_common.capture_source_group (value, description) VALUES ('NZ Aerial Imagery', 'external_source_id will link to the imagery_survey_id from https://data.linz.govt.nz/layer/95677-nz-imagery-surveys/');

COMMIT;
