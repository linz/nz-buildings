"""
--------------------------------------------------------------------
Buildings Select Statements

- building_outlines
    - building_outlines
    - building_outlines_capture_method_id_by_building_outline_id (building+putline_id)
    - building_outlines_end_lifespan_by_building_outline_id (building_outline_id)
    - building_outline_shape_by_building_outline_id (building_outline_id)
    - building_outlines_suburb_locality_id_by_building_outline_id
    - building_outlines_town_city_id_by_building_outline_id

- lifecycle_stage
    - lifecycle_stage_by_value (value)
    - lifecycle_stage_id_by_value (value)
    - lifecycle_stage_value
    - lifecycle_stage_value_by_building_outline_id (building_outline_id)

--------------------------------------------------------------------
"""

# building outlines

building_outlines = """
SELECT *
FROM buildings.building_outlines bo
WHERE ST_Intersects(bo.shape, %s)
AND bo.building_outline_id NOT IN ( SELECT building_outline_id FROM buildings_bulk_load.removed );
"""

building_outlines_capture_method_id_by_building_outline_id = """
SELECT capture_method_id
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outlines_end_lifespan_by_building_outline_id = """
SELECT end_lifespan
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outline_shape_by_building_outline_id = """
SELECT shape
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outlines_suburb_locality_id_by_building_outline_id = """
SELECT suburb_locality_id
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outlines_territorial_authority_id_by_building_outline = """
SELECT territorial_authority_id
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""

building_outlines_town_city_id_by_building_outline_id = """
SELECT town_city_id
FROM buildings.building_outlines
WHERE building_outline_id = %s;
"""


# lifecycle stage

lifecycle_stage_by_value = """
SELECT *
FROM buildings.lifecycle_stage
WHERE value = %s;
"""

lifecycle_stage_id_by_value = """
SELECT lifecycle_stage_id
FROM buildings.lifecycle_stage
WHERE value = %s;
"""

lifecycle_stage_value = """
SELECT value
FROM buildings.lifecycle_stage;
"""

lifecycle_stage_value_by_building_outline_id = """
SELECT ls.value
FROM buildings.lifecycle_stage ls,
     buildings.building_outlines bo
WHERE bo.building_outline_id = %s
AND bo.lifecycle_stage_id = ls.lifecycle_stage_id;
"""
