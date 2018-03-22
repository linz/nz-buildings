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

        -- Update end_lifespan in building_outlines

        UPDATE buildings.building_outlines
        SET end_lifespan = now()
        WHERE building_outline_id IN
            (SELECT removed.building_outline_id
            FROM buildings_bulk_load.removed
            JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
            WHERE current.supplied_dataset_id = p_supplied_dataset_id - 1);


        -- Update end_lifespan in buildings

        UPDATE buildings.buildings
        SET end_lifespan = now()
        WHERE building_id IN
            (SELECT outlines.building_id
            FROM buildings.building_outlines outlines
            JOIN buildings_bulk_load.removed USING (building_outline_id)
            JOIN buildings_bulk_load.existing_subset_extracts current USING (building_outline_id)
            WHERE current.supplied_dataset_id = p_supplied_dataset_id - 1);

        -------------
        --  ADDED  --
        -------------

        FOR v_bulk_load_outline_id IN (SELECT bulk_load_outline_id
                                      FROM buildings_bulk_load.added
                                      JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id)
                                      WHERE supplied.supplied_dataset_id = p_supplied_dataset_id
                                    )
        LOOP

        -- Create a new record in buildings

        INSERT INTO buildings.buildings(building_id)
        VALUES (default)
        RETURNING building_id INTO v_new_building_id;


        -- Create a new record in building_outlines

        INSERT INTO buildings.building_outlines(building_id
                                              , capture_method_id
                                              , capture_source_id
                                              , lifecycle_stage_id
                                              , suburb_locality_id
                                              , town_city_id
                                              , territorial_authority_id
                                              , begin_lifespan
                                              , shape)
        SELECT v_new_building_id,
               supplied.capture_method_id,
               supplied.capture_source_id,
               1,
               supplied.suburb_locality_id,
               supplied.town_city_id,
               supplied.territorial_authority_id,
               supplied.begin_lifespan,
               supplied.shape
        FROM buildings_bulk_load.bulk_load_outlines supplied
        WHERE supplied.bulk_load_outline_id = v_bulk_load_outline_id
        RETURNING building_outline_id INTO v_new_building_outline_id;


        -- Add new records in transferred table

        INSERT INTO buildings_bulk_load.transferred
        VALUES(v_bulk_load_outline_id, v_new_building_outline_id);


        END LOOP;

        -------------
        -- MATCHED --
        -------------

        FOR v_bulk_load_outline_id IN (SELECT bulk_load_outline_id
                                      FROM buildings_bulk_load.matched
                                      JOIN buildings_bulk_load.bulk_load_outlines supplied USING (bulk_load_outline_id)
                                      WHERE supplied.supplied_dataset_id = p_supplied_dataset_id)

        LOOP

        -- Create a new record in building_outlines and transfer the buidling_id from replaced record

        INSERT INTO buildings.building_outlines(building_id
                                              , capture_method_id
                                              , capture_source_id
                                              , lifecycle_stage_id
                                              , suburb_locality_id
                                              , town_city_id
                                              , territorial_authority_id
                                              , begin_lifespan
                                              , shape)
        SELECT building.building_id
             , supplied.capture_method_id
             , supplied.capture_source_id
             , 1
             , supplied.suburb_locality_id
             , supplied.town_city_id
             , supplied.territorial_authority_id
             , supplied.begin_lifespan
             , supplied.shape
        FROM buildings_bulk_load.bulk_load_outlines supplied
        JOIN (SELECT outlines.building_id as building_id,
                     matched.bulk_load_outline_id as bulk_load_outline_id
             FROM buildings.building_outlines outlines
             JOIN buildings_bulk_load.matched USING (building_outline_id)
             WHERE matched.bulk_load_outline_id = v_bulk_load_outline_id) building USING (bulk_load_outline_id)
        WHERE supplied.bulk_load_outline_id = v_bulk_load_outline_id
        RETURNING building_outline_id INTO v_new_building_outline_id;


        -- Add new records in transferred table

        INSERT INTO buildings_bulk_load.transferred
        VALUES (v_bulk_load_outline_id, v_new_building_outline_id);


        -- Update end_lifespan in building_outlines for the replaced buildings

        UPDATE buildings.building_outlines
        SET end_lifespan = now()
        WHERE building_outline_id IN
            (SELECT matched.building_outline_id
            FROM buildings_bulk_load.matched
            WHERE matched.bulk_load_outline_id = v_bulk_load_outline_id);

        END LOOP;

        -------------
        -- RELATED --
        -------------

        -- Create a new record in buildings where building outlines are in the related table

        FOR v_bulk_load_outline_id IN (SELECT supplied.bulk_load_outline_id
                                      FROM buildings_bulk_load.bulk_load_outlines supplied
                                      WHERE supplied.bulk_load_outline_id IN (
                                      	SELECT related.bulk_load_outline_id FROM buildings_bulk_load.related)
                                        AND supplied.supplied_dataset_id = p_supplied_dataset_id
                                    )
        LOOP

        INSERT INTO buildings.buildings(building_id)
        VALUES (default)
        RETURNING building_id INTO v_new_building_id;


        -- Create a new record in building_outlines where building outlines are in the related table

        INSERT INTO buildings.building_outlines(building_id
                                              , capture_method_id
                                              , capture_source_id
                                              , lifecycle_stage_id
                                              , suburb_locality_id
                                              , town_city_id
                                              , territorial_authority_id
                                              , begin_lifespan
                                              , shape)
        SELECT v_new_building_id,
               supplied.capture_method_id,
               supplied.capture_source_id,
               1,
               supplied.suburb_locality_id,
               supplied.town_city_id,
               supplied.territorial_authority_id,
               supplied.begin_lifespan,
               supplied.shape
        FROM buildings_bulk_load.bulk_load_outlines supplied
        WHERE supplied.bulk_load_outline_id = v_bulk_load_outline_id
        RETURNING building_outline_id INTO v_new_building_outline_id;


        -- Create records in lifecycle table

        INSERT INTO buildings.lifecycle(parent_building_id, building_id)
        SELECT outlines.building_id, v_new_building_id
        FROM buildings_bulk_load.related
        JOIN buildings.building_outlines outlines USING (building_outline_id)
        WHERE related.bulk_load_outline_id = v_bulk_load_outline_id;


        -- Add new records in transferred table

        INSERT INTO buildings_bulk_load.transferred
        VALUES(v_bulk_load_outline_id, v_new_building_outline_id);


        -- Update end_lifespan in building_outlines for the replaced buildings

        UPDATE buildings.building_outlines
        SET end_lifespan = now()
        WHERE building_outline_id IN
            (SELECT related.building_outline_id
            FROM buildings_bulk_load.related
            WHERE related.bulk_load_outline_id = v_bulk_load_outline_id);


        -- Update end_lifespan in buildings for the replaced buildings

        UPDATE buildings.buildings
        SET end_lifespan = now()
        WHERE building_id IN
            (SELECT outlines.building_id
            FROM buildings.building_outlines outlines
            JOIN buildings_bulk_load.related USING (building_outline_id)
            WHERE related.bulk_load_outline_id = v_bulk_load_outline_id);

        END LOOP;


        UPDATE buildings_bulk_load.supplied_datasets
        SET transfer_date = now()
        WHERE supplied_dataset_id = p_supplied_dataset_id;

END IF;

END;

$$ LANGUAGE plpgsql;