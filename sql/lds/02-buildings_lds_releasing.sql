------------------------------------------------------------------------------
-- Release building outlines onto LDS
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_bulk_load.release_to_lds()
    RETURNS void
AS $$

BEGIN

	INSERT INTO buildings_lds.nz_building_outlines (building_outline_id
	                                              , building_id
	                                              , suburb_locality
	                                              , town_city
	                                              , territorial_authority
	                                              , capture_method
	                                              , capture_source
	                                              , lifecycle_stage
	                                              , outline_begin_lifespan
	                                              , building_begin_lifespan
	                                              , shape)
	SELECT
	      building_outlines.building_outline_id
	    , building_outlines.building_id
	    , nz_locality.suburb_4th
	    , nz_locality.city_name
	    , territorial_authority.name
	    , capture_method.value
	    , capture_source_group.value
	    , lifecycle_stage.value
	    , building_outlines.begin_lifespan
	    , buildings.begin_lifespan
	    , building_outlines.shape
	FROM buildings.building_outlines
	JOIN buildings.buildings USING (building_id)
	JOIN buildings.lifecycle_stage USING (lifecycle_stage_id)
	JOIN buildings_common.capture_method USING (capture_method_id)
	JOIN buildings_common.capture_source USING (capture_source_id)
	JOIN buildings_common.capture_source_group USING (capture_source_group_id)
	JOIN admin_bdys.nz_locality ON nz_locality.id=building_outlines.suburb_locality_id
	JOIN admin_bdys.territorial_authority ON territorial_authority.ogc_fid=building_outlines.territorial_authority_id
	WHERE building_outlines.end_lifespan IS NULL;


	UPDATE buildings_lds.nz_building_outlines
	SET name = building_name.building_name
	  , name_begin_lifespan = building_name.begin_lifespan
	FROM buildings.building_name
	WHERE building_name.building_id = nz_building_outlines.building_id;


	UPDATE buildings_lds.nz_building_outlines
	SET use = use.value
	  , use_begin_lifespan = building_use.begin_lifespan
	FROM buildings.building_use
	JOIN buildings.use USING (use_id)
	WHERE building_use.building_id = nz_building_outlines.building_id;

END;

$$ LANGUAGE plpgsql;
