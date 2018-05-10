-- organisation
SELECT buildings_bulk_load.organisation_insert('Test Organisation');
-- capture source
SELECT buildings_common.capture_source_insert(1, 'Test External Source');
-- capture source group
SELECT buildings_common.capture_source_group_insert('Test CS Value', 'Test CS Description');
-- capture method
SELECT buildings_common.capture_method_insert('Test Capture Method');
-- lifecycle stage
SELECT buildings.lifecycle_stage_insert('Test Lifecycle Stage');
-- supplied datasets
SELECT buildings_bulk_load.supplied_datasets_insert('Test Dataset', 1);
-- bulk load outline
SELECT buildings_bulk_load.bulk_load_outlines_insert(1, NULL, 1, 5, 1, 1, NULL, 1, '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441');
-- building
SELECT buildings.buildings_insert();
-- building outline
SELECT buildings.building_outlines_insert(1000029, 5, 1, 1, 1, NULL, 1, now(), '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441');
-- existing subset extract
SELECT buildings_bulk_load.existing_subset_extracts_insert(1000000, 1, '0106000020910800000100000001030000000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441');