"""
--------------------------------------------------------------------
Buildings Reference Select Statements

- capture_source_area
    - capture_source_area_id_and_name
    - capture_source_area_name_by_supplied_dataset (supplied_dataset_id)
    - capture_source_area_shape_by_title (area_title)

- reference_update_log
    - log_select_last_update

- topo 50 layers
    - select_polygon_id_by_external_id

- suburb_locality
    - suburb_locality_intersect_geom (geometry)
    - suburb_locality_town_city_by_building_outline_id (building_outline_id)
    - suburb_locality_town_city_by_bulk_outline_id (bulk_load_outline_id)

- territorial_authority
    - territorial_authority_intersect_geom (geometry)
    - territorial_authority_name
    - territorial_authority_name_by_building_outline_id (building_outline_id)
    - territorial_authority_name_by_bulk_outline_id (bulk_load_outline_id)

- territorial_authority_grid
    - refresh_ta_grid_view

- town_city
    - town_city_intersect_geometry (geometry)
    - town_city_name
    - town_city_name_by_building_outline_id (building_outline_id)
    - town_city_name_by_bulk_outline_id (bulk_load_outline_id)

--------------------------------------------------------------------
"""

# Capture Source Area

capture_source_area_id_and_name = """
SELECT csa.external_area_polygon_id, csa.area_title
FROM buildings_reference.capture_source_area csa
ORDER BY csa.area_title;
"""

capture_source_area_name_by_supplied_dataset = """
SELECT csa.area_title
FROM buildings_bulk_load.bulk_load_outlines blo
JOIN buildings_common.capture_source cs USING (capture_source_id)
JOIN buildings_reference.capture_source_area csa ON (csa.external_area_polygon_id = cs.external_source_id)
WHERE supplied_dataset_id = %s;
"""

capture_source_area_shape_by_title = """
SELECT shape
FROM buildings_reference.capture_source_area
WHERE area_title = %s;
"""

capture_source_area_intersect_geom = """
SELECT csa.external_area_polygon_id,
       csa.area_title,
       csg.value
FROM buildings_reference.capture_source_area csa
JOIN buildings_common.capture_source cs ON (csa.external_area_polygon_id = cs.external_source_id)
JOIN buildings_common.capture_source_group csg USING (capture_source_group_id)
WHERE ST_Intersects(csa.shape, %s::Geometry);
"""

# reference update log

log_select_last_update = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE {} = True
ORDER BY update_id DESC LIMIT 1;
"""

# topo 50 layers

select_polygon_id_by_external_id = """
SELECT {0}_polygon_id
FROM buildings_reference.{0}_polygons
WHERE external_{0}_polygon_id = %s;
"""

# topo 50 layers - points

select_point_id_by_external_id = """
SELECT {0}_points_id
FROM buildings_reference.{0}_points
WHERE external_{0}_points_id = %s;
"""

# admin boundaries

select_admin_bdy_id_by_external_id = """
SELECT {0}_id
FROM buildings_reference.{0}
WHERE external_{0}_id = %s;
"""

# suburb locality

suburb_locality_intersect_geom = """
SELECT suburb_locality_id, suburb_locality, town_city
FROM buildings_reference.suburb_locality
WHERE shape && ST_Expand(%s::Geometry, 1000)
ORDER BY suburb_locality;
"""

suburb_locality_town_city_by_building_outline_id = """
SELECT suburb_locality, town_city
FROM buildings_reference.suburb_locality sl,
     buildings.building_outlines bo
WHERE sl.suburb_locality_id = bo.suburb_locality_id
AND bo.building_outline_id = %s;
"""

suburb_locality_town_city_by_bulk_outline_id = """
SELECT suburb_locality, town_city
FROM buildings_reference.suburb_locality sl,
     buildings_bulk_load.bulk_load_outlines blo
WHERE sl.suburb_locality_id = blo.suburb_locality_id
AND blo.bulk_load_outline_id = %s;
"""

# territorial Authority

territorial_authority_intersect_geom = """
SELECT territorial_authority_id, name
FROM buildings_reference.territorial_authority
WHERE shape && ST_Expand(%s::Geometry, 1000)
ORDER BY name;
"""

territorial_authority_name = """
SELECT DISTINCT name
FROM buildings_reference.territorial_authority;
"""

territorial_authority_name_by_building_outline_id = """
SELECT name
FROM buildings_reference.territorial_authority ta,
     buildings.building_outlines bo
WHERE ta.territorial_authority_id = bo.territorial_authority_id
AND bo.building_outline_id = %s;
"""

territorial_authority_name_by_bulk_outline_id = """
SELECT name
FROM buildings_reference.territorial_authority ta,
     buildings_bulk_load.bulk_load_outlines blo
WHERE ta.territorial_authority_id = blo.territorial_authority_id
AND blo.bulk_load_outline_id = %s;
"""

# territorial authority grid

refresh_ta_grid_view = """
REFRESH MATERIALIZED VIEW buildings_reference.territorial_authority_grid;
"""
