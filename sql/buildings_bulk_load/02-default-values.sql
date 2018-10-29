
-- organisation
INSERT INTO buildings_bulk_load.organisation (value) VALUES ('Ecopia');

-- bulk_load_status
INSERT INTO buildings_bulk_load.bulk_load_status (value) VALUES ('Supplied');
INSERT INTO buildings_bulk_load.bulk_load_status (value) VALUES ('Added During QA');
INSERT INTO buildings_bulk_load.bulk_load_status (value) VALUES ('Deleted During QA');

-- qa_status
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Not Checked');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Okay');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Pending');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Refer to Supplier');
INSERT INTO buildings_bulk_load.qa_status (value) VALUES ('Not Removed');