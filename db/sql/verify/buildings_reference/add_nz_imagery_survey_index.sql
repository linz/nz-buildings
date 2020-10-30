-- Verify nz-buildings:buildings_reference/add_nz_imagery_survey_index on pg

BEGIN;

SELECT
      imagery_survey_id
    , shape
    , name
    , imagery_id
    , index_id
    , set_order
    , ground_sample_distance
    , accuracy
    , supplier
    , licensor
    , flown_from
    , flown_to
FROM buildings_reference.nz_imagery_survey_index
WHERE FALSE;

ROLLBACK;
