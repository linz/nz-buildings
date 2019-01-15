"""
--------------------------------------------------------------------
Buildings Reference Select Statements

- canal_polygons
    -canal_polygon_id_by_external_id (external_canal_polygon_id)

- capture_source_area
    - capture_source_area_id_and_name
    - capture_source_area_name_by_supplied_dataset (supplied_dataset_id)
    - capture_source_area_shape_by_title (area_title)

- lagoon_polygons
    - lagoon_polygon_id_by_external_id

- lake_polygons
    - lake_polygon_id_by_external_id

- pond_polygons
    - pond_polygon_id_by_external_id

- reference_update_log
    - update_log_canal_date
    - update_log_lagoon_date
    - update_log_lake_date
    - update_log_pond_date
    - update_log_river_date

- river_polygons
    - river_polygon_id_by_external_id

- suburb_locality
    - suburb_locality_intersect_geom (geometry)
    - suburb_locality_suburb_4th
    - suburb_locality_suburb_4th_by_building_outline_id (building_outline_id)
    - suburb_locality_suburb_4th_by_bulk_outline_id (bulk_load_outline_id)

- territorial_authority
    - territorial_authority_intersect_geom (geometry)
    - territorial_authority_name
    - territorial_authority_name_by_building_outline_id (building_outline_id)
    - territorial_authority_name_by_bulk_outline_id (bulk_load_outline_id)

- town_city
    - town_city_intersect_geometry (geometry)
    - town_city_name
    - town_city_name_by_building_outline_id (building_outline_id)
    - town_city_name_by_bulk_outline_id (bulk_load_outline_id)

--------------------------------------------------------------------
"""

# canal polygons

canal_polygon_id_by_external_id = """
SELECT canal_polygon_id
FROM buildings_reference.canal_polygons
WHERE external_canal_polygon_id = %s;
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
SELECT csa.external_area_polygon_id
FROM buildings_reference.capture_source_area csa
WHERE ST_Intersects(csa.shape, %s::Geometry);
"""

# lagoon polygons

lagoon_polygon_id_by_external_id = """
SELECT lagoon_polygon_id
FROM buildings_reference.lagoon_polygons
WHERE external_lagoon_polygon_id = %s;
"""

# lake polygons

lake_polygon_id_by_external_id = """
SELECT lake_polygon_id
FROM buildings_reference.lake_polygons
WHERE external_lake_polygon_id = %s;
"""

# pond polygons

pond_polygon_id_by_external_id = """
SELECT pond_polygon_id
FROM buildings_reference.pond_polygons
WHERE external_pond_polygon_id = %s;
"""

# reference update log

update_log_canal_date = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE canals = True
ORDER BY update_id DESC LIMIT 1;
"""

update_log_lagoon_date = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE lagoons = True
ORDER BY update_id DESC LIMIT 1;
"""

update_log_lake_date = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE lakes = True
ORDER BY update_id DESC LIMIT 1;
"""

update_log_pond_date = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE ponds = True
ORDER BY update_id DESC LIMIT 1;
"""

update_log_river_date = """
SELECT update_date
FROM buildings_reference.reference_update_log
WHERE rivers = True
ORDER BY update_id DESC LIMIT 1;
"""

# river polygons

river_polygon_id_by_external_id = """
SELECT river_polygon_id
FROM buildings_reference.river_polygons
WHERE external_river_polygon_id = %s;
"""

# suburb locality

suburb_locality_intersect_geom = """
SELECT suburb_locality_id, suburb_4th
FROM buildings_reference.suburb_locality
WHERE shape && ST_Expand(%s::Geometry, 1000)
ORDER BY suburb_4th;
"""

suburb_locality_suburb_4th = """
SELECT DISTINCT suburb_4th
FROM buildings_reference.suburb_locality;
"""

suburb_locality_suburb_4th_by_building_outline_id = """
SELECT suburb_4th
FROM buildings_reference.suburb_locality sl,
     buildings.building_outlines bo
WHERE sl.suburb_locality_id = bo.suburb_locality_id
AND bo.building_outline_id = %s;
"""

suburb_locality_suburb_4th_by_bulk_outline_id = """
SELECT suburb_4th
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

# town city

town_city_intersect_geometry = """
SELECT town_city_id, name
FROM buildings_reference.town_city
WHERE ST_Intersects(shape, ST_Buffer(%s::Geometry, 1000))
ORDER BY name
"""

town_city_name = """
SELECT DISTINCT name
FROM buildings_reference.town_city;
"""

town_city_name_by_building_outline_id = """
SELECT name
FROM buildings_reference.town_city tc,
     buildings.building_outlines bo
WHERE tc.town_city_id = bo.town_city_id
AND bo.building_outline_id = %s;
"""

town_city_name_by_bulk_outline_id = """
SELECT name
FROM buildings_reference.town_city tc,
     buildings_bulk_load.bulk_load_outlines blo
WHERE tc.town_city_id = blo.town_city_id
AND blo.bulk_load_outline_id = %s;
"""
