
sql_delete_related_existing = 'SELECT buildings_bulk_load.related_delete_existing_outlines(%s);'

sql_delete_related_bulk = 'SELECT buildings_bulk_load.related_delete_bulk_load_outlines(%s);'

sql_delete_matched_existing = 'SELECT buildings_bulk_load.matched_delete_existing_outlines(%s);'

sql_delete_matched_bulk = 'SELECT buildings_bulk_load.matched_delete_bulk_load_outlines(%s);'

sql_delete_removed = 'SELECT buildings_bulk_load.removed_delete_existing_outlines(%s);'

sql_delete_added = 'SELECT buildings_bulk_load.added_delete_bulk_load_outlines(%s);'

sql_insert_added = 'SELECT buildings_bulk_load.added_insert_bulk_load_outlines(%s);'

sql_insert_removed = 'SELECT buildings_bulk_load.removed_insert_bulk_load_outlines(%s);'

sql_insert_matched = 'SELECT buildings_bulk_load.matched_insert_buildling_outlines(%s, %s);'


CREATE OR REPLACE FUNCTION buildings_bulk_load.related_delete_existing_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.related
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.related_delete_bulk_load_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.related
    WHERE bulk_load_outline_id = $1
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.matched_delete_existing_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.matched
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.matched_delete_bulk_load_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.matched
    WHERE bulk_load_outline_id = $1
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_delete_existing_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.removed
    WHERE building_outline_id = $1
    RETURNING building_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_delete_bulk_load_outlines(integer)
RETURNS integer AS
$$

    DELETE FROM buildings_bulk_load.added
    WHERE bulk_load_outline_id = $1
    RETURNING bulk_load_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.added_insert_bulk_load_outlines(integer)
RETURNS integer AS
$$
    INSERT INTO buildings_bulk_load.added
    VALUES ($1, 1)
    RETURNING added.bulk_load_outline_id;

$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION buildings_bulk_load.removed_insert_bulk_load_outlines(integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.removed
    VALUES ($1, 1)
    RETURNING removed.building_outline_id;

$$
LANGUAGE sql;


CREATE OR REPLACE FUNCTION buildings_bulk_load.matched_insert_buildling_outlines(integer, integer)
RETURNS integer AS
$$

    INSERT INTO buildings_bulk_load.matched(bulk_load_outline_id
                                       , building_outline_id
                                       , qa_status_id
                                       , area_bulk_load
                                       , area_existing
                                       , percent_area_difference
                                       , area_overlap
                                       , percent_bulk_load_overlap
                                       , percent_existing_overlap
                                       , hausdorff_distance)
    SELECT supplied.bulk_load_outline_id,
        current.building_outline_id,
        1,
        ST_Area(supplied.shape),
        ST_Area(current.shape),
        @(ST_Area(current.shape) - ST_Area(supplied.shape)) / ST_Area(current.shape) * 100,
        ST_Area(ST_Intersection(supplied.shape, current.shape)),
        ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(supplied.shape) * 100 ,
        ST_Area(ST_Intersection(supplied.shape, current.shape)) / ST_Area(current.shape) * 100,
        ST_HausdorffDistance(supplied.shape, current.shape)
    FROM buildings_bulk_load.bulk_load_outlines supplied,
      buildings_bulk_load.existing_subset_extracts current
    WHERE supplied.bulk_load_outline_id = $1
      AND current.building_outline_id = $2
    RETURNING matched.bulk_load_outline_id

$$
LANGUAGE sql;


-- CREATE OR REPLACE FUNCTION buildings_bulk_load.related_prep_insert_buildling_outlines(integer, integer)
-- RETURNS integer AS
-- $$

--     CREATE TEMP TABLE IF NOT EXISTS related_prep (bulk_load_outline_id integer
--                                   , building_outline_id integer
--                                   , qa_status_id integer
--                                   , area_bulk_load numeric(10,2)
--                                   , area_existing numeric(10,2)
--                                   , area_overlap numeric(10,2)
--                                   , percent_bulk_load_overlap numeric(5,2)
--                                   , percent_existing_overlap numeric(5,2));

--     INSERT INTO related_prep
--     SELECT supplied.bulk_load_outline_id,
--            current.building_outline_id,
--            1 AS qa_status_id,
--            ST_Area(supplied.shape) AS area_bulk_load,
--            ST_Area(current.shape) AS area_existing,
--            ST_Area(ST_Intersection(supplied.shape, current.shape)) AS area_overlap,
--            ST_Area(ST_Intersection(supplied.shape, current.shape))/ ST_Area(supplied.shape) * 100
--            AS percent_bulk_load_overlap,
--            ST_Area(ST_Intersection(supplied.shape, current.shape))/ ST_Area(current.shape) * 100
--            AS percent_existing_overlap
--     FROM buildings_bulk_load.bulk_load_outlines supplied,
--          buildings_bulk_load.existing_subset_extracts current
--     WHERE supplied.bulk_load_outline_id = $1
--       AND current.building_outline_id = $2
--     RETURNING related_prep.bulk_load_outline_id

-- $$
-- LANGUAGE sql;


-- CREATE OR REPLACE FUNCTION buildings_bulk_load.related_insert_buildling_outlines()
-- RETURNS integer AS
-- $$

--     WITH bulk_load_totals AS (
--         SELECT bulk_load_outline_id,
--             sum(area_overlap) AS total_area_bulk_load_overlap,
--             sum(percent_bulk_load_overlap) AS total_percent_bulk_load_overlap
--         FROM related_prep
--         GROUP BY bulk_load_outline_id ),
--         existing_totals AS (
--         SELECT building_outline_id,
--             sum(area_overlap) AS total_area_existing_overlap,
--             sum(percent_existing_overlap) AS total_percent_existing_overlap
--         FROM related_prep
--         GROUP BY building_outline_id )

--     INSERT INTO buildings_bulk_load.related(bulk_load_outline_id
--                                           , building_outline_id
--                                           , qa_status_id
--                                           , area_bulk_load
--                                           , area_existing
--                                           , area_overlap
--                                           , percent_bulk_load_overlap
--                                           , percent_existing_overlap
--                                           , total_area_bulk_load_overlap
--                                           , total_area_existing_overlap
--                                           , total_percent_bulk_load_overlap
--                                           , total_percent_existing_overlap)
--     SELECT rp.bulk_load_outline_id,
--            rp.building_outline_id,
--            rp.qa_status_id,
--            rp.area_bulk_load,
--            rp.area_existing,
--            rp.area_overlap,
--            rp.percent_bulk_load_overlap,
--            rp.percent_existing_overlap,
--            bulk_load_totals.total_area_bulk_load_overlap,
--            existing_totals.total_area_existing_overlap,
--            bulk_load_totals.total_percent_bulk_load_overlap,
--            existing_totals.total_percent_existing_overlap
--     FROM related_prep rp,
--          bulk_load_totals,
--          existing_totals
--     WHERE rp.bulk_load_outline_id = bulk_load_totals.bulk_load_outline_id
--       AND rp.building_outline_id = existing_totals.building_outline_id
--     RETURNING related.bulk_load_outline_id
-- $$
-- LANGUAGE sql;