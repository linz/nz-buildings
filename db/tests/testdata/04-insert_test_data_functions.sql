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
-- -- supplied datasets
SELECT buildings_bulk_load.supplied_datasets_insert('Test Dataset', 1);
-- supplied outline
SELECT buildings_bulk_load.supplied_outlines_insert(3, NULL, '010300002091080000010000000500000008247ADF76A93C41203492F8263155418BEE6ABAA9A93C414BD3F7EB263155414A4F05C7A9A93C41227DE4CA1C315541CD3F76A076A93C4106D73FE71C31554108247ADF76A93C41203492F826315541');
-- bulk load outline
SELECT buildings_bulk_load.bulk_load_outlines_insert_supplied(3, 1, 5, 1001);
-- building
SELECT buildings.buildings_insert();
-- building outline
SELECT buildings.building_outlines_insert(1000029, 5, 1001, 1, 101, NULL, 10001, now()::timestamp, '0103000020910800000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441');
-- existing subset extract
SELECT buildings_bulk_load.existing_subset_extracts_insert(1000000, 3, '0103000020910800000100000005000000000000009FB33A4100000080BCB35441000000009FB33A4100000080AEB3544100000000D8B33A4100000080AEB3544100000000D8B33A4100000080BCB35441000000009FB33A4100000080BCB35441');
-- update suburb
SELECT buildings_reference.bulk_load_outlines_update_suburb(3);
-- update town_city
SELECT buildings_reference.bulk_load_outlines_update_town_city(3);
-- update TA
SELECT buildings_reference.bulk_load_outlines_update_territorial_authority(3);
