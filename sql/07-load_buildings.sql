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

            SELECT buildings.buildings_add_added_record()
            INTO v_new_building_id;

            SELECT buildings.building_outlines_add_added_record(v_new_building_id, v_bulk_load_outline_id)
            INTO v_new_building_outline_id;

            SELECT buildings_bulk_load.transferred_update(v_bulk_load_outline_id, v_new_building_outline_id);

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

            SELECT buildings_bulk_load.transferred_update(v_bulk_load_outline_id, v_new_building_outline_id);

            SELECT buildings.building_outlines_update_end_lifespan(
                buildings_bulk_load.building_outlines_matched_select_by_dataset(v_bulk_load_outline_id));

        END LOOP;

        -------------
        -- RELATED --
        -------------

        -- Create a new record in buildings where building outlines are in the related table

        FOR v_bulk_load_outline_id IN (
            SELECT supplied.bulk_load_outline_id
            FROM buildings_bulk_load.bulk_load_outlines supplied
            WHERE supplied.bulk_load_outline_id IN (
                SELECT related.bulk_load_outline_id
                FROM buildings_bulk_load.related
            )
            AND supplied.supplied_dataset_id = p_supplied_dataset_id
        )
        LOOP

            INSERT INTO buildings.buildings(building_id)
            VALUES (DEFAULT)
            RETURNING building_id INTO v_new_building_id;


            -- Create a new record in building_outlines where building outlines are in the related table

            INSERT INTO buildings.building_outlines(
                  building_id
                , capture_method_id
                , capture_source_id
                , lifecycle_stage_id
                , suburb_locality_id
                , town_city_id
                , territorial_authority_id
                , begin_lifespan
                , shape
            )
            SELECT
                  v_new_building_id
                , supplied.capture_method_id
                , supplied.capture_source_id
                , 1
                , supplied.suburb_locality_id
                , supplied.town_city_id
                , supplied.territorial_authority_id
                , supplied.begin_lifespan
                , supplied.shape
            FROM buildings_bulk_load.bulk_load_outlines supplied
            WHERE supplied.bulk_load_outline_id = v_bulk_load_outline_id
            RETURNING building_outline_id INTO v_new_building_outline_id;

            -- Create records in lifecycle table

            INSERT INTO buildings.lifecycle(
                  parent_building_id
                , building_id
            )
            SELECT
                  outlines.building_id
                , v_new_building_id
            FROM buildings_bulk_load.related
            JOIN buildings.building_outlines outlines USING (building_outline_id)
            WHERE related.bulk_load_outline_id = v_bulk_load_outline_id;

            -- Add new records in transferred table

            INSERT INTO buildings_bulk_load.transferred
            VALUES(v_bulk_load_outline_id, v_new_building_outline_id);

            -- Update end_lifespan in building_outlines for the replaced buildings

            UPDATE buildings.building_outlines
            SET end_lifespan = now()
            WHERE building_outline_id IN (
                SELECT related.building_outline_id
                FROM buildings_bulk_load.related
                WHERE related.bulk_load_outline_id = v_bulk_load_outline_id
            );


            -- Update end_lifespan in buildings for the replaced buildings

            UPDATE buildings.buildings
            SET end_lifespan = now()
            WHERE building_id IN (
                SELECT outlines.building_id
                FROM buildings.building_outlines outlines
                JOIN buildings_bulk_load.related USING (building_outline_id)
                WHERE related.bulk_load_outline_id = v_bulk_load_outline_id
            );

        END LOOP;

        UPDATE buildings_bulk_load.supplied_datasets
        SET transfer_date = now()
        WHERE supplied_dataset_id = p_supplied_dataset_id;

END IF;

END;

$$ LANGUAGE plpgsql;
