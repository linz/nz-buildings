CREATE OR REPLACE FUNCTION buildings_bulk_load.load_building_outlines(p_supplied_dataset_id integer)
    RETURNS void
AS $$

DECLARE

    v_new_building_id integer;
    v_bulk_load_outline_id integer;
    v_new_building_outline_id integer;

BEGIN

IF (
    SELECT transfer_date
    FROM buildings_bulk_load.supplied_datasets
    WHERE buildings_bulk_load.supplied_datasets.supplied_dataset_id = p_supplied_dataset_id) IS NULL THEN

        -------------
        -- REMOVED --
        -------------

        SELECT buildings.building_outlines_update_end_lifespan(
            buildings_bulk_load.building_outlines_removed_select_by_dataset(p_supplied_dataset_id));

        SELECT buildings.buildings_update_end_lifespan(
            buildings_bulk_load.buildings_removed_select_by_dataset(p_supplied_dataset_id));

        -------------
        --  ADDED  --
        -------------

        FOR v_bulk_load_outline_id IN (
            SELECT buildings_bulk_load.added_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP

            SELECT buildings.buildings_add_record()
            INTO v_new_building_id;

            SELECT buildings.building_outlines_add_added_record(v_new_building_id, v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings_bulk_load.transferred_add_record(v_bulk_load_outline_id, v_new_building_outline_id);

        END LOOP;

        -------------
        -- MATCHED --
        -------------

        FOR v_bulk_load_outline_id IN (
            SELECT buildings_bulk_load.matched_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP

            SELECT buildings.building_outlines_add_matched_record(v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings_bulk_load.transferred_add_record(v_bulk_load_outline_id, v_new_building_outline_id);

            SELECT buildings.building_outlines_update_end_lifespan(
                buildings_bulk_load.building_outlines_matched_select_by_dataset(v_bulk_load_outline_id));

        END LOOP;

        -------------
        -- RELATED --
        -------------

        -- Create a new record in buildings where building outlines are in the related table

        FOR v_bulk_load_outline_id IN (
            SELECT buildings_bulk_load.related_select_by_dataset(p_supplied_dataset_id)
        )
        LOOP

            SELECT buildings.buildings_add_record()
            INTO v_new_building_id;

            SELECT buildings.building_outlines_add_related_record(v_new_building_id, v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings.lifecycle_add_record(v_new_building_id, v_bulk_load_outline_id);

            SELECT buildings_bulk_load.transferred_add_record(v_bulk_load_outline_id, v_new_building_outline_id);

            SELECT buildings.building_outlines_update_end_lifespan(
                buildings_bulk_load.building_outlines_related_select_by_dataset(v_bulk_load_outline_id));

            SELECT buildings.buildings_update_end_lifespan(
                buildings_bulk_load.buildings_related_select_by_dataset(v_bulk_load_outline_id));

        END LOOP;

        SELECT buildings_bulk_load.supplied_datasets_update_transfer_date(p_supplied_dataset_id);


END IF;

END;

$$ LANGUAGE plpgsql;
