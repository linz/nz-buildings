-- Deploy nz-buildings:buildings_bulk_load/functions/load_to_production to pg

BEGIN;

--------------------------------------------------------------------
-- script to load data from the bulk load stage to the buildings schema
--------------------------------------------------------------------

CREATE OR REPLACE FUNCTION buildings_bulk_load.load_building_outlines(p_supplied_dataset_id integer)
RETURNS void
AS $$

DECLARE

    v_new_building_id integer;
    v_bulk_load_outline_id integer;
    v_new_building_outline_id integer;
    v_old_building_id integer;

BEGIN

IF (SELECT buildings_bulk_load.supplied_datasets_select_transfer_date(p_supplied_dataset_id)) IS NULL THEN

        -------------
        -- REMOVED --
        -------------

        PERFORM buildings.building_outlines_update_end_lifespan(
            buildings_bulk_load.building_outlines_removed_select_by_dataset(p_supplied_dataset_id));

        SELECT buildings.building_name_removed_insert_bulk(p_supplied_dataset_id)
        SELECT buildings.building_use_removed_insert_bulk(p_supplied_dataset_id)

        PERFORM buildings.buildings_update_end_lifespan(
            buildings_bulk_load.buildings_removed_select_by_dataset(p_supplied_dataset_id));

        -------------
        --  ADDED  --
        -------------

        FOREACH v_bulk_load_outline_id IN ARRAY (
            SELECT buildings_bulk_load.added_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP

            SELECT buildings.buildings_insert()
            INTO v_new_building_id;

            SELECT buildings.building_outlines_insert_bulk(v_new_building_id, v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings.building_name_added_insert_bulk(v_bulk_load_outline_id, v_new_building_id)
            SELECT buildings.building_use_added_insert_bulk(v_bulk_load_outline_id, v_new_building_id)

            PERFORM buildings_bulk_load.transferred_insert(v_bulk_load_outline_id, v_new_building_outline_id);

        END LOOP;

        -------------
        -- MATCHED --
        -------------
        -- matched_select_by_dataset gives the bulk_load_outline_id from the matched table
        -- Given the bulk_load_outline_id, the function:matched_find_building_id gives the building_id from buildings.building_outlines table and assigns it the old_building_id value.
        -- building_outlines_insert_bulk takes the old_building_id, and the bulk_load_outline_id,
        --             and extracts some of the columns contents from buildings_bulk_load.bulk_load_outlines,
        --             then inserts the new? building_id, building_outline_id, and these column values into the buildings.building_outlines table,
        --             then it returns the new building_outline_id, which is serial and created new.
        -- The buildings_bulk_load.transferred_insert function then transfers the building_outline_id that was created in bulk load and adds it to
        FOREACH v_bulk_load_outline_id IN ARRAY (
            SELECT buildings_bulk_load.matched_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP
            SELECT buildings_bulk_load.matched_find_building_id(v_bulk_load_outline_id)
            INTO v_old_building_id;

            SELECT buildings.building_outlines_insert_bulk(v_old_building_id ,v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings.building_name_matched_insert_bulk(v_bulk_load_outline_id);

            SELECT buildings.building_use_matched_insert_bulk(v_bulk_load_outline_id);


            PERFORM buildings_bulk_load.transferred_insert(v_bulk_load_outline_id, v_new_building_outline_id);

            PERFORM buildings.building_outlines_update_end_lifespan(
                buildings_bulk_load.building_outlines_matched_select_by_dataset(v_bulk_load_outline_id));

        END LOOP;

        -------------
        -- RELATED --
        -------------

        -- Create a new record in buildings where building outlines are in the related table

        FOREACH v_bulk_load_outline_id IN ARRAY (
            SELECT buildings_bulk_load.related_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP

            SELECT buildings.buildings_insert()
            INTO v_new_building_id;

            SELECT buildings.building_outlines_insert_bulk(v_new_building_id, v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings.building_use_related_insert_bulk(v_bulk_load_outline_id, v_new_building_id);
            SELECT buildings.building_name_related_insert_bulk(v_bulk_load_outline_id, v_new_building_id);

            PERFORM buildings.lifecycle_add_record(v_new_building_id, v_bulk_load_outline_id);

            PERFORM buildings_bulk_load.transferred_insert(v_bulk_load_outline_id, v_new_building_outline_id);



            PERFORM buildings.building_outlines_update_end_lifespan(
                buildings_bulk_load.building_outlines_related_select_by_dataset(v_bulk_load_outline_id));

            PERFORM buildings.buildings_update_end_lifespan(
                buildings_bulk_load.buildings_related_select_by_dataset(v_bulk_load_outline_id));

        END LOOP;

        PERFORM buildings_bulk_load.supplied_datasets_update_transfer_date(p_supplied_dataset_id);


END IF;

END;

$$
LANGUAGE plpgsql;

COMMIT;
