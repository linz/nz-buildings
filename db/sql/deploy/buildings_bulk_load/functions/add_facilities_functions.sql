-- Deploy nz-buildings:buildings_bulk_load/functions/add_facilities_functions to pg

BEGIN;

Create or replace function buildings_bulk_load.load_facility_names()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_name = name
FROM
(SELECT bulk_load_outline_id, name
FROM buildings_bulk_load.bulk_load_outlines blo
JOIN
((WITH added_facility_intersects AS
( SELECT bulk_load_outline_id, fac.name, ST_Area(ST_Intersection(supplied.shape, fac.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect
FROM facilities_lds.nz_facilities fac
JOIN
(SELECT bulk_load_outline_id, qa_status_id, shape
FROM buildings_bulk_load.added supplied
JOIN buildings_bulk_load.added_outlines addedshapes USING (bulk_load_outline_id)
WHERE qa_status_id = 1) supplied ON ST_Intersects(supplied.shape, fac.shape))
SELECT *
FROM added_facility_intersects
WHERE supplied_intersect > 50)) s1 USING (bulk_load_outline_id)) added
WHERE added.bulk_load_outline_id = blo.bulk_load_outline_id;
end;
$$;


Create or replace function buildings_bulk_load.load_facility_use_id()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_use_id = use_id
FROM
(SELECT bulk_load_outline_id,
 	CASE use
 		WHEN 'hospital' THEN 16
 		WHEN 'school' THEN 27
 	END use_id
 FROM
 (SELECT bulk_load_outline_id, use
  FROM buildings_bulk_load.bulk_load_outlines blo
  JOIN
  ((WITH added_facility_intersects AS
	( SELECT bulk_load_outline_id,
	 	lower(fac.use) AS use,
	 	ST_Area(ST_Intersection(supplied.shape, fac.shape)) / ST_Area(supplied.shape) * 100 AS supplied_intersect
	 FROM facilities_lds.nz_facilities fac
	 JOIN
	 (SELECT bulk_load_outline_id, qa_status_id, shape
	  FROM buildings_bulk_load.added supplied
	  JOIN buildings_bulk_load.added_outlines addedshapes USING (bulk_load_outline_id)
	  WHERE qa_status_id = 1) supplied
	 ON ST_Intersects(supplied.shape, fac.shape))
	SELECT *
	FROM added_facility_intersects
	WHERE supplied_intersect > 50)) s1 USING (bulk_load_outline_id)) use_select)
	added WHERE added.bulk_load_outline_id = blo.bulk_load_outline_id;
end;
$$;


Create or replace function buildings_bulk_load.load_matched_names()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_name = building_name
FROM
(SELECT building_name, building_id, bulk_load_outline_id, building_outline_id
FROM buildings.building_name bn
JOIN
(SELECT building_outline_id, building_id, bulk_load_outline_id
FROM buildings.building_outlines
JOIN
(SELECT bulk_load_outline_id, building_outline_id, qa_status_id
FROM buildings_bulk_load.matched
JOIN buildings_bulk_load.matched_bulk_load_outlines
USING (bulk_load_outline_id)
WHERE qa_status_id = 1) s1 USING (building_outline_id)) s3 USING (building_id)) s4
WHERE blo.bulk_load_outline_id = s4.bulk_load_outline_id;
end;
$$;


Create or replace function buildings_bulk_load.load_matched_use_id()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_use_id = use_id
FROM
(SELECT use_id, building_id, bulk_load_outline_id, building_outline_id
FROM buildings.building_use bu
JOIN
(SELECT building_outline_id, building_id, bulk_load_outline_id
FROM buildings.building_outlines
JOIN
(SELECT bulk_load_outline_id, building_outline_id, qa_status_id
FROM buildings_bulk_load.matched
JOIN buildings_bulk_load.matched_bulk_load_outlines USING (bulk_load_outline_id)
WHERE qa_status_id = 1) s1 USING (building_outline_id)) s3 USING (building_id)) s4
WHERE blo.bulk_load_outline_id = s4.bulk_load_outline_id;
end;
$$;



Create or replace function buildings_bulk_load.load_related_names()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_name = building_name
FROM
(SELECT building_name, building_id, bulk_load_outline_id, building_outline_id
FROM buildings.building_name bn
JOIN
(SELECT building_outline_id, building_id, bulk_load_outline_id
FROM buildings.building_outlines
JOIN
(SELECT bulk_load_outline_id, building_outline_id, qa_status_id
FROM buildings_bulk_load.related
JOIN buildings_bulk_load.related_bulk_load_outlines
USING (bulk_load_outline_id)
WHERE qa_status_id = 1) s1 USING (building_outline_id)) s3 USING (building_id)) s4
WHERE blo.bulk_load_outline_id = s4.bulk_load_outline_id;
end;
$$;


Create or replace function buildings_bulk_load.load_related_use_id()
	returns void
	language plpgsql
as
$$
begin
UPDATE buildings_bulk_load.bulk_load_outlines blo set bulk_load_use_id = use_id
FROM
(SELECT use_id, building_id, bulk_load_outline_id, building_outline_id
FROM buildings.building_use bu
JOIN
(SELECT building_outline_id, building_id, bulk_load_outline_id
FROM buildings.building_outlines
JOIN
(SELECT bulk_load_outline_id, building_outline_id, qa_status_id
FROM buildings_bulk_load.related
JOIN buildings_bulk_load.related_bulk_load_outlines USING (bulk_load_outline_id)
WHERE qa_status_id = 1) s1 USING (building_outline_id)) s3 USING (building_id)) s4
WHERE blo.bulk_load_outline_id = s4.bulk_load_outline_id;
end;
$$;

COMMIT;
