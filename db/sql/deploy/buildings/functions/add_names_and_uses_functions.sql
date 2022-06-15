-- Deploy nz-buildings:buildings/functions/add_name_and_use_functions to pg

BEGIN;

CREATE or replace function buildings.building_name_added_insert_bulk(integer, integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
bulk_loaded_name varchar(250);

BEGIN
select count(*) into bl_rw_count from
(
	SELECT true -- this returns true if a bulk load name exists
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	AND bulk_load_name IS NOT NULL ) blrc;
RAISE NOTICE 'bl_rw_count: %', bl_rw_count;

IF bl_rw_count != 0
THEN
	SELECT bulk_load_name
	INTO bulk_loaded_name
	FROM buildings_bulk_load.bulk_load_outlines
	WHERE bulk_load_outline_id = $1;
	RAISE NOTICE 'bulk_loaded_name: %', bulk_loaded_name;
	INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
	values ($2, bulk_loaded_name, now() );
END IF;
END;
$$;

CREATE or replace function buildings.building_name_matched_insert_bulk(integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
existing_rw_count int = 0;
bulk_loaded_name varchar(250) = '';
existing_building_name varchar(250) = '';
building_id_check int;
existing_name_lifespan timestamp;

BEGIN
select count(*) into bl_rw_count from
(
	SELECT true
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	and coalesce(trim(bulk_load_name),'') != '') a;

SELECT building_id
INTO building_id_check
FROM (SELECT outlines.building_id, building_outline_id, bulk_load_outline_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.matched USING (building_outline_id)
WHERE matched.bulk_load_outline_id = $1) bic;

select count(*) into existing_rw_count from
(
	SELECT true
	FROM buildings.building_name bbn
	WHERE building_id = building_id_check
	and coalesce(trim(building_name), '') != '') erwc;

SELECT bulk_load_name
INTO bulk_loaded_name
FROM buildings_bulk_load.bulk_load_outlines
WHERE bulk_load_outline_id = $1;
SELECT building_name
INTO existing_building_name
FROM buildings.building_name
WHERE building_id = building_id_check;
SELECT end_lifespan
INTO existing_name_lifespan
FROM buildings.building_name
WHERE building_id = building_id_check;

-- A if existing name exists and is different from an existing bulk load name, then
-- end lifespan of the existing building name and insert the bulk load name as a new name in the buildings table.
IF existing_building_name != bulk_loaded_name AND bl_rw_count != 0 AND existing_name_lifespan IS NULL
THEN
	UPDATE buildings.building_name
	SET end_lifespan = now()
	WHERE building_id = building_id_check;
	INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
	values (building_id_check, bulk_loaded_name, now() );

-- B if existing name doesn't exist and bulk load name exists then
-- insert a new building_id and current date as begin lifespan
ELSIF existing_rw_count = 0  AND bl_rw_count = 1
THEN
	INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
	values (building_id_check, bulk_loaded_name, now());

-- C if existing building name exists and the bulk load name is null or empty string
-- then end the lifespan of the existing building name
ELSIF existing_rw_count = 1 AND bl_rw_count = 0 AND existing_name_lifespan IS NULL
THEN

	UPDATE buildings.building_name
	SET end_lifespan = now()
	WHERE building_id = building_id_check;

-- D if the buildings building_name is the same as the bulk load name, then do nothing
ELSIF trim(bulk_loaded_name) = existing_building_name
THEN
	RAISE NOTICE 'existing building_name and bulk load name are the same';

END IF;
END;
$$;

CREATE or replace function buildings.building_name_related_insert_bulk(integer, integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
existing_rw_count int = 0;
bulk_loaded_name varchar(250);
existing_building_name_array varchar(250) array;
building_id_check_array int[];
existing_name_lifespan_array timestamp array;
end_lifespan_check timestamp;
name_check varchar(250);
multiple_ids int;
existing_name_count int;
existing_life_count int;
existing_life_is_null boolean;
existing_name varchar(250);
new_name_exists varchar(250);
X int;


BEGIN
select count(*) into bl_rw_count from
(
	SELECT true -- this returns true if a bulk load name exists
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	AND bulk_load_name IS NOT NULL ) blrc;
RAISE NOTICE 'bl_rw_count: %', bl_rw_count;

SELECT ARRAY
( SELECT building_id
FROM (SELECT outlines.building_id, building_outline_id, bulk_load_outline_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.related USING (building_outline_id)
WHERE related.bulk_load_outline_id = $1) bic) INTO building_id_check_array;
RAISE NOTICE 'building_id_check_array: %', building_id_check_array;
---------
select count(*) into existing_rw_count from
(
	SELECT true
	FROM buildings.building_name bbn
	WHERE building_id = ANY (array[building_id_check_array])
	AND building_name IS NOT NULL) erc;
RAISE NOTICE 'existing_rw_count: %', existing_rw_count;

SELECT bulk_load_name
INTO bulk_loaded_name
FROM buildings_bulk_load.bulk_load_outlines
WHERE bulk_load_outline_id = $1;
RAISE NOTICE 'bulk_loaded_name: %', bulk_loaded_name;

SELECT ARRAY
	(SELECT building_name
	FROM buildings.building_name
	WHERE building_id = ANY (array[building_id_check_array])
	) INTO existing_building_name_array;
RAISE NOTICE 'existing_building_name_array: %', existing_building_name_array;

SELECT ARRAY
	( SELECT end_lifespan
	FROM buildings.building_name
	WHERE building_id = ANY (array[building_id_check_array])
	) INTO existing_name_lifespan_array; -- this is 0 if there is no end lifespan
RAISE NOTICE 'existing_name_lifespan_array: %', existing_name_lifespan_array;


-- ONE TO MANY CHECKS

-- First check it is a one to many relationship
-- If multiple_ids is 1, then it is a one to many relationship
SELECT COUNT(*) FROM (SELECT UNNEST(building_id_check_array)) u INTO multiple_ids;
SELECT COUNT(*) FROM (SELECT UNNEST(existing_building_name_array)) eud INTO existing_name_count;
SELECT UNNEST(existing_building_name_array) INTO existing_name;
SELECT COUNT(*) FROM (SELECT UNNEST(existing_name_lifespan_array)) eul INTO existing_life_count;
SELECT exists (SELECT 1 from UNNEST(array[existing_name_lifespan_array]) s(a) WHERE a IS NULL) INTO existing_life_is_null;
RAISE NOTICE 'multiple_ids: %', multiple_ids;
RAISE NOTICE 'existing_name_count: %', existing_name_count;
RAISE NOTICE 'existing_life_count: %', existing_life_count;
RAISE NOTICE 'existing_life_is_null: %', existing_life_is_null;
RAISE NOTICE 'existing_name: %', existing_name;

IF multiple_ids = 1
THEN
			RAISE NOTICE 'Detected one multiple ids so this is a one to many relationship';
			IF existing_name_count > 0 AND
			bulk_loaded_name != ANY (array[existing_building_name_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = true
				THEN
					RAISE NOTICE 'A: existing name exists AND bulk load name is different from existing name AND bulk load name exists AND existing name end lifespan is null';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT building_name
						INTO name_check
						FROM buildings.building_name
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NULL AND name_check IS NOT NULL
						THEN
							UPDATE buildings.building_name
							SET end_lifespan = now()
							WHERE building_id = building_id_check_array[1];
							INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
							values ($2, bulk_loaded_name, now() );
						END IF;
			ELSIF existing_name_count > 0 AND
				bulk_loaded_name = ANY (array[existing_building_name_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = false
				THEN
						RAISE NOTICE 'B: existing name exists, bulk load name is the same as existing name, and existing name end lifespan exists';
						INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
							values ($2, bulk_loaded_name, now() );
			ELSIF existing_name_count = 1 AND
			bulk_loaded_name = ANY (array[existing_building_name_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = true
				THEN
						RAISE NOTICE 'C: existing name exists AND bulk load name is the same as existing name AND bulk load name exists AND existing name end lifespan is null';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT building_name
						INTO name_check
						FROM buildings.building_name
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NULL AND name_check IS NOT NULL
						THEN
							UPDATE buildings.building_name
							SET end_lifespan = now()
							WHERE building_id = building_id_check_array[1];
							INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
							values ($2, bulk_loaded_name, now() );
						END IF;
			ELSIF existing_name_count > 0 AND
			bulk_loaded_name != ANY (array[existing_building_name_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = false
				THEN
					RAISE NOTICE 'D: existing name exists AND bulk load name different from existing name AND bulk load name exists AND existing name end lifespan exists';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT building_name
						INTO name_check
						FROM buildings.building_name
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NOT NULL AND name_check IS NOT NULL
						THEN
							INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
							values ($2, bulk_loaded_name, now() );
						END IF;
			ELSIF existing_name_count = 0 AND
			bl_rw_count != 0
				THEN
					RAISE NOTICE 'D2: existing name does not exist, and bulk load name exists';
					INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
					values ($2, bulk_loaded_name, now() );

			ELSE
				RAISE NOTICE 'No updates to building name table.';
END IF;
END IF;
IF multiple_ids > 1
	THEN
	RAISE NOTICE 'multiple ids > 1 so many to one relationship';

	IF existing_name_count > 0 AND bl_rw_count != 0 AND
	existing_life_is_null = true
		THEN
		RAISE NOTICE 'E: retire existing name if one exists';
		RAISE NOTICE 'E: Existing name exists. Bulk load name exists. ';
		FOREACH X IN ARRAY array[building_id_check_array]
			LOOP
				SELECT end_lifespan
				INTO end_lifespan_check
				FROM buildings.buildings
				WHERE building_id = X;
				SELECT building_name
				INTO name_check
				FROM buildings.building_name
				WHERE building_id = X;
				SELECT building_name
				INTO new_name_exists
				FROM buildings.building_name
				WHERE building_id = $2;
				RAISE NOTICE 'Checking %: ', X;
				RAISE NOTICE 'end_lifespan_check: %', end_lifespan_check;
				RAISE NOTICE 'name_check: %', name_check;
				RAISE NOTICE 'new_name_exists: %', new_name_exists;
				IF name_check IS NOT NULL AND end_lifespan_check IS NULL AND new_name_exists IS NULL
				THEN
					RAISE NOTICE 'Loop A: bulk loaded name needs to be inserted';
					UPDATE buildings.building_name
					SET end_lifespan = now()
					WHERE building_id = X;
					INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
					values ($2, bulk_loaded_name, now() );
				END IF;
				IF name_check IS NOT NULL AND end_lifespan_check IS NULL AND new_name_exists IS NOT NULL
				THEN
					RAISE NOTICE 'Loop B: bulk loaded name already inserted';
					UPDATE buildings.building_name
					SET end_lifespan = now()
					WHERE building_id = X;
				END IF;
			END LOOP;
	ELSIF existing_name_count > 0 AND bl_rw_count = 0 AND existing_life_is_null = true
	THEN
		RAISE NOTICE 'F: Retire existing names if any exist.';
		RAISE NOTICE 'F: Existing name exists. Bulk load name does not exist or has been removed.';
		FOREACH X IN ARRAY array[building_id_check_array]
			LOOP
				UPDATE buildings.building_name
				SET end_lifespan = now()
				WHERE building_id = X;
			END LOOP;
	ELSIF existing_name_count = 0 AND bl_rw_count != 0 AND existing_life_is_null = false
	THEN
		RAISE NOTICE 'G: There are no existing names and only a bulk load name.';
		INSERT INTO buildings.building_name(building_id, building_name, begin_lifespan)
		values ($2, bulk_loaded_name, now() );
	END IF;
END IF;

END;
$$;

CREATE or replace function buildings.building_name_removed_insert_bulk(integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
removed_building_id_array int array;
existing_building_id_count int;
X int;
existing_name varchar(250);

BEGIN
SELECT ARRAY
(Select building_id FROM(
SELECT outlines.building_id, building_outline_id, supplied_dataset_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.removed USING (building_outline_id)
WHERE supplied_dataset_id = $1) arr) INTO removed_building_id_array;
RAISE NOTICE 'removed_building_id_array: %', removed_building_id_array;



SELECT COUNT(*) FROM (SELECT UNNEST(removed_building_id_array)) eud INTO existing_building_id_count;

IF existing_building_id_count != 0
THEN
	FOREACH X in ARRAY array[removed_building_id_array]
		LOOP
			SELECT building_name
			INTO existing_name
			FROM buildings.building_name
			WHERE building_id = X;
			UPDATE buildings.building_name
			SET end_lifespan = now()
			WHERE building_id = X;
			RAISE NOTICE 'building id retired: %', X;
			RAISE NOTICE 'building name retired: %', existing_name;
		END LOOP;
END IF;
END;
$$;

CREATE or replace function buildings.building_use_added_insert_bulk(integer, integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
bulk_loaded_use_id int;

BEGIN
select count(*) into bl_rw_count from
(
	SELECT true -- this returns true if a bulk load use id exists
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	AND bulk_load_use_id IS NOT NULL ) blrc;
RAISE NOTICE 'bl_rw_count: %', bl_rw_count;

IF bl_rw_count != 0
THEN
	SELECT bulk_load_use_id
	INTO bulk_loaded_use_id
	FROM buildings_bulk_load.bulk_load_outlines
	WHERE bulk_load_outline_id = $1;
	RAISE NOTICE 'bulk_loaded_use_id: %', bulk_loaded_use_id;
	INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
	values ($2, bulk_loaded_use_id, now() );
END IF;
END;
$$;

CREATE or replace function buildings.building_use_matched_insert_bulk(integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
existing_rw_count int = 0;
bulk_loaded_use_id int;
existing_building_use_id int;
building_id_check int;
existing_use_id_lifespan timestamp;


BEGIN
select count(*) into bl_rw_count from
(
	SELECT true
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	AND bulk_load_use_id IS NOT NULL ) blrc;

SELECT building_id
INTO building_id_check
FROM (SELECT outlines.building_id, building_outline_id, bulk_load_outline_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.matched USING (building_outline_id)
WHERE matched.bulk_load_outline_id = $1) bic;

select count(*) into existing_rw_count from
(
	SELECT true
	FROM buildings.building_use bbu
	WHERE building_id = building_id_check
	AND use_id IS NOT NULL) erc;

SELECT bulk_load_use_id
INTO bulk_loaded_use_id
FROM buildings_bulk_load.bulk_load_outlines
WHERE bulk_load_outline_id = $1;
SELECT use_id
INTO existing_building_use_id
FROM buildings.building_use
WHERE building_id = building_id_check;
SELECT end_lifespan
INTO existing_use_id_lifespan
FROM buildings.building_use
WHERE building_id = building_id_check;

-- A if existing use_id exists and is different from an existing bulk load use_id, then
-- end lifespan of the existing building use_id and insert the bulk load use_id as a new use_id in the buildings table.
IF existing_building_use_id != bulk_loaded_use_id AND bl_rw_count != 0 AND existing_use_id_lifespan IS NULL
THEN
	UPDATE buildings.building_use
	SET end_lifespan = now()
	WHERE building_id = building_id_check;
	INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
	values (building_id_check, bulk_loaded_use_id, now() );

-- B if existing use_id doesn't exist and bulk load use_id exists then
-- insert a new building_id and current date as begin lifespan
ELSIF existing_rw_count = 0  AND bl_rw_count = 1
THEN
	INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
	values (building_id_check, bulk_loaded_use_id, now());

-- C if existing building use_id exists and the bulk load use_id is null or empty string
-- then end the lifespan of the existing building use_id
ELSIF existing_rw_count = 1 AND bl_rw_count = 0 AND existing_use_id_lifespan IS NULL
THEN

	UPDATE buildings.building_use
	SET end_lifespan = now()
	WHERE building_id = building_id_check;

-- D if the buildings building_use_id is the same as the bulk load use_id, then do nothing
ELSIF bulk_loaded_use_id = existing_building_use_id
THEN
	RAISE NOTICE 'existing building_use_id and bulk load use_id are the same';

END IF;
END;
$$;

CREATE or replace function buildings.building_use_related_insert_bulk(integer, integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
bl_rw_count int = 0;
existing_rw_count int = 0;
bulk_loaded_use_id int;
existing_building_use_id_array int array;
building_id_check_array int[];
existing_use_id_lifespan_array timestamp array;
end_lifespan_check timestamp;
use_id_check int;
multiple_ids int;
existing_use_ids_count int;
existing_life_count int;
existing_life_is_null boolean;
existing_use_id int;
new_use_id_exists int;
X int;


BEGIN
select count(*) into bl_rw_count from
(
	SELECT true -- this returns true if a bulk load use_id exists
	FROM buildings_bulk_load.bulk_load_outlines blo
	WHERE bulk_load_outline_id = $1 -- v_bulk_load_outline_id
	AND bulk_load_use_id IS NOT NULL ) blrc;
RAISE NOTICE 'bl_rw_count: %', bl_rw_count;

SELECT ARRAY
( SELECT building_id
FROM (SELECT outlines.building_id, building_outline_id, bulk_load_outline_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.related USING (building_outline_id)
WHERE related.bulk_load_outline_id = $1) bic) INTO building_id_check_array;
RAISE NOTICE 'building_id_check_array: %', building_id_check_array;
---------
select count(*) into existing_rw_count from
(
	SELECT true
	FROM buildings.building_use bbu
	WHERE building_id = ANY (array[building_id_check_array])
	AND use_id IS NOT NULL) erc;
RAISE NOTICE 'existing_rw_count: %', existing_rw_count;

SELECT bulk_load_use_id
INTO bulk_loaded_use_id
FROM buildings_bulk_load.bulk_load_outlines
WHERE bulk_load_outline_id = $1;
RAISE NOTICE 'bulk_loaded_use_id: %', bulk_loaded_use_id;

SELECT ARRAY
	(SELECT use_id
	FROM buildings.building_use
	WHERE building_id = ANY (array[building_id_check_array])
	) INTO existing_building_use_id_array;
RAISE NOTICE 'existing_building_use_id_array: %', existing_building_use_id_array;

SELECT ARRAY
	( SELECT end_lifespan
	FROM buildings.building_use
	WHERE building_id = ANY (array[building_id_check_array])
	) INTO existing_use_id_lifespan_array; -- this is 0 if there is no end lifespan
RAISE NOTICE 'existing_use_id_lifespan_array: %', existing_use_id_lifespan_array;


-- ONE TO MANY CHECKS

-- First check it is a one to many relationship
-- If multiple_ids is 1, then it is a one to many relationship
SELECT COUNT(*) FROM (SELECT UNNEST(building_id_check_array)) u INTO multiple_ids;
SELECT COUNT(*) FROM (SELECT UNNEST(existing_building_use_id_array)) eud INTO existing_use_ids_count;
SELECT UNNEST(existing_building_use_id_array) INTO existing_use_id;
SELECT COUNT(*) FROM (SELECT UNNEST(existing_use_id_lifespan_array)) eul INTO existing_life_count;
SELECT exists (SELECT 1 from UNNEST(array[existing_use_id_lifespan_array]) s(a) WHERE a IS NULL) INTO existing_life_is_null;
RAISE NOTICE 'multiple_ids: %', multiple_ids;
RAISE NOTICE 'existing_use_ids_count: %', existing_use_ids_count;
RAISE NOTICE 'existing_life_count: %', existing_life_count;
RAISE NOTICE 'existing_life_is_null: %', existing_life_is_null;
RAISE NOTICE 'existing_use_id: %', existing_use_id;

IF multiple_ids = 1
THEN
			RAISE NOTICE 'Detected one multiple ids so this is a one to many relationship';
			IF existing_use_ids_count > 0 AND
			bulk_loaded_use_id != ANY (array[existing_building_use_id_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = true
				THEN
					RAISE NOTICE 'A: existing use id exists AND bulk load use id different from existing use id AND bulk load use id exists AND existing use end lifespan is null';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT use_id
						INTO use_id_check
						FROM buildings.building_use
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NULL AND use_id_check IS NOT NULL
						THEN
							UPDATE buildings.building_use
							SET end_lifespan = now()
							WHERE building_id = building_id_check_array[1];
							INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
							values ($2, bulk_loaded_use_id, now() );
						END IF;
			ELSIF existing_use_ids_count > 0 AND
				bulk_loaded_use_id = ANY (array[existing_building_use_id_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = false
				THEN
						RAISE NOTICE 'B: existing use id exists, bulk load use id is the same as existing use id, and existing use id end lifespan exists';
						INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
							values ($2, bulk_loaded_use_id, now() );
			ELSIF existing_use_ids_count = 1 AND
			bulk_loaded_use_id = ANY (array[existing_building_use_id_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = true
				THEN
						RAISE NOTICE 'C: existing use id exists AND bulk load use id is the same as existing use id AND bulk load use id exists AND existing use end lifespan is null';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT use_id
						INTO use_id_check
						FROM buildings.building_use
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NULL AND use_id_check IS NOT NULL
						THEN
							UPDATE buildings.building_use
							SET end_lifespan = now()
							WHERE building_id = building_id_check_array[1];
							INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
							values ($2, bulk_loaded_use_id, now() );
						END IF;
			ELSIF existing_use_ids_count > 0 AND
			bulk_loaded_use_id != ANY (array[existing_building_use_id_array])  AND
				bl_rw_count != 0 AND
				existing_life_is_null = false
				THEN
					RAISE NOTICE 'D: existing use id exists AND bulk load use id different from existing use id AND bulk load use id exists AND existing use id end lifespan exists';
						SELECT end_lifespan
						INTO end_lifespan_check
						FROM buildings.buildings
						WHERE building_id = building_id_check_array[1];
						SELECT use_id
						INTO use_id_check
						FROM buildings.building_use
						WHERE building_id = building_id_check_array[1];
						If end_lifespan_check IS NOT NULL AND use_id_check IS NOT NULL
						THEN
							INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
							values ($2, bulk_loaded_use_id, now() );
						END IF;
			ELSIF existing_use_ids_count = 0 AND
			bl_rw_count != 0
				THEN
					RAISE NOTICE 'D2: existing use_id does not exist, and bulk load use id exists';
					INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
					values ($2, bulk_loaded_use_id, now() );
			ELSE
				RAISE NOTICE 'No updates to building use table.';
END IF;
END IF;
IF multiple_ids > 1
	THEN
	RAISE NOTICE 'multiple ids > 1 so many to one relationship';

	IF existing_use_ids_count > 0 AND bl_rw_count != 0 AND
	existing_life_is_null = true
		THEN
		RAISE NOTICE 'E: retire existing use ids if one exists';
		RAISE NOTICE 'E: Existing use id exists. Bulk load use id exists. ';
		FOREACH X IN ARRAY array[building_id_check_array]
			LOOP
				SELECT end_lifespan
				INTO end_lifespan_check
				FROM buildings.buildings
				WHERE building_id = X;
				SELECT use_id
				INTO use_id_check
				FROM buildings.building_use
				WHERE building_id = X;
				SELECT use_id
				INTO new_use_id_exists
				FROM buildings.building_use
				WHERE building_id = $2;
				RAISE NOTICE 'Checking %: ', X;
				RAISE NOTICE 'end_lifespan_check: %', end_lifespan_check;
				RAISE NOTICE 'use_id_check: %', use_id_check;
				RAISE NOTICE 'new_use_id_exists: %', new_use_id_exists;
				IF use_id_check IS NOT NULL AND end_lifespan_check IS NULL AND new_use_id_exists IS NULL
				THEN
					RAISE NOTICE 'Loop A: bulk loaded use id needs to be inserted';
					UPDATE buildings.building_use
					SET end_lifespan = now()
					WHERE building_id = X;
					INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
					values ($2, bulk_loaded_use_id, now() );
				END IF;
				IF use_id_check IS NOT NULL AND end_lifespan_check IS NULL AND new_use_id_exists IS NOT NULL
				THEN
					RAISE NOTICE 'Loop B: bulk loaded use id already inserted';
					UPDATE buildings.building_use
					SET end_lifespan = now()
					WHERE building_id = X;
				END IF;
			END LOOP;
	ELSIF existing_use_ids_count > 0 AND bl_rw_count = 0 AND existing_life_is_null = true
	THEN
		RAISE NOTICE 'F: Retire existing use ids if any exist.';
		RAISE NOTICE 'F: Existing use id exists. Bulk load use id does not exist or has been removed.';
		FOREACH X IN ARRAY array[building_id_check_array]
			LOOP
				UPDATE buildings.building_use
				SET end_lifespan = now()
				WHERE building_id = X;
			END LOOP;
	ELSIF existing_use_ids_count = 0 AND bl_rw_count != 0 AND existing_life_is_null = false
	THEN
		RAISE NOTICE 'G: There are no existing use ids and only a bulk use id.';
		INSERT INTO buildings.building_use(building_id, use_id, begin_lifespan)
		values ($2, bulk_loaded_use_id, now() );
	END IF;
END IF;

END;
$$;

CREATE or replace function buildings.building_use_removed_insert_bulk(integer)
returns void
LANGUAGE 'plpgsql'
AS
$$

DECLARE
removed_building_id_array int array;
existing_building_id_count int;
X int;
existing_use_id int;

BEGIN
SELECT ARRAY
(Select building_id FROM(
SELECT outlines.building_id, building_outline_id, supplied_dataset_id
FROM buildings.building_outlines outlines
JOIN buildings_bulk_load.removed USING (building_outline_id)
WHERE supplied_dataset_id = $1) arr) INTO removed_building_id_array;
RAISE NOTICE 'removed_building_id_array: %', removed_building_id_array;

SELECT COUNT(*) FROM (SELECT UNNEST(removed_building_id_array)) eud INTO existing_building_id_count;

IF existing_building_id_count != 0
THEN
	FOREACH X in ARRAY array[removed_building_id_array]
		LOOP
			SELECT use_id
			INTO existing_use_id
			FROM buildings.building_use
			WHERE building_id = X;
			UPDATE buildings.building_use
			SET end_lifespan = now()
			WHERE building_id = X;
			RAISE NOTICE 'building id retired: %', X;
			RAISE NOTICE 'building use_id retired: %', existing_use_id;
		END LOOP;
END IF;
END;
$$;

COMMIT;
