-- add new outline to buildings and existing subset extract to deal with second removed test
INSERT INTO buildings.buildings(building_id, begin_lifespan, end_lifespan) VALUES (1035, '2018-01-01 09:00:00 GMT+12', NULL);
INSERT INTO buildings.building_outlines (building_outline_id, building_id, capture_method_id, capture_source_id, lifecycle_stage_id, suburb_locality_id, town_city_id, territorial_authority_id, begin_lifespan, end_lifespan, shape)
VALUES (1035, 1035, 5, 1, 1, 1, 100, 1, '2018-01-01 09:00:00 GMT+12', NULL, '01060000209108000001000000010300000001000000050000006AFCA14C43A83C41B8C7145119315541AB8052A85EA83C418C54F17519315541EF66995E5EA83C41672D83B5143155416AFCA14C43A83C41672D83B5143155416AFCA14C43A83C41B8C7145119315541');
SELECT buildings_bulk_load.existing_subset_extracts_insert(1035, 2, (SELECT shape from buildings.building_outlines where building_outline_id = 1035));
-- insert 10000000 building outline to existing subsets extrac table to deal with matched test
SELECT buildings_bulk_load.existing_subset_extracts_insert(1000000, 2, (SELECT shape from buildings.building_outlines where building_outline_id = 1000000));
-- update existing entries to supplied dataset 2 to deal with related test
UPDATE buildings_bulk_load.existing_subset_extracts SET supplied_dataset_id = 2 WHERE building_outline_id = 1001;
UPDATE buildings_bulk_load.existing_subset_extracts SET supplied_dataset_id = 2 WHERE building_outline_id = 1002;
