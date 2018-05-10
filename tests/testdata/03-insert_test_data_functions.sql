-- organisation
SELECT buildings_bulk_load.organisation_insert('Test Organisation');
-- capture source
SELECT buildings_common.capture_source_insert(1, 'test external source');
-- capture source group
SELECT buildings_common.capture_source_group_insert('Test CS Value', 'Test CS Description');
-- capture method
SELECT buildings_common.capture_method_insert('Test Capture Method');
-- lifecycle stage
SELECT buildings.lifecycle_stage_insert('Test Lifecycle Stage');
-- supplied datasets
SELECT buildings_bulk_load.supplied_datasets_insert('test_dataset', 1);
