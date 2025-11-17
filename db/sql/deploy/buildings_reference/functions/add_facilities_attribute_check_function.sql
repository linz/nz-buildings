-- Deploy nz-buildings:buildings_reference/functions/add_facilities_attribute_check to pg

------------------------------------------------------------------------------
-- Checks NZ Facilities (hospitals and schools) attributes are valid in buildings_reference.
--
-- This function should be run and errors corrected, prior to running the
-- "buildings.update_facilities_attributes" function.
--
-- Attribute errors checked:
--     - Invaild USE (that doesn't match the NZ Buildings coded values for USE)
--     - Null USE
--     - Null NAME
--
-- This function can be run by using:
--     SELECT * FROM buildings_reference.facility_attribute_errors()
------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION buildings_reference.facility_attribute_errors()
RETURNS TABLE (
	error_type text,
	error_count integer,
	error_attributes text[],
	facility_ids integer[]
)
LANGUAGE sql
AS $$
	-- Find features with invalid use
	WITH invalid_use AS (
		SELECT *
		FROM buildings_reference.nz_facilities
   		WHERE use NOT IN ('Hospital','School')
		ORDER BY facility_id
	),
	-- Find features with null use
	null_use AS (
		SELECT *
		FROM buildings_reference.nz_facilities
   		WHERE use IS NULL
		ORDER BY facility_id
	),
	-- Find features with null name
	null_name AS (
		SELECT *
		FROM buildings_reference.nz_facilities
   		WHERE name IS NULL
		ORDER BY facility_id
	)
	-- Report features with invalid use
    SELECT
		'Invalid Use' AS error_type,
		COUNT(*) AS error_count,
		ARRAY_AGG(use) AS error_attributes,
		ARRAY_AGG(facility_id) AS facility_ids
	FROM invalid_use
	-- Report featues with null use
	UNION ALL
	SELECT
		'Empty Use' AS error_type,
		COUNT(*) AS error_count,
		ARRAY_AGG(use) AS error_attributes,
		ARRAY_AGG(facility_id) AS facility_ids
	FROM null_use
	-- Report features with null name
	UNION ALL
	SELECT
		'Empty Name' AS error_type,
		COUNT(*) AS error_count,
		ARRAY_AGG(name) AS error_attributes,
		ARRAY_AGG(facility_id) AS facility_ids
	FROM null_name;
$$;
