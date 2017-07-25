-- Table: building_outlines.nz_building_outlines_pilot

-- DROP TABLE building_outlines.nz_building_outlines_pilot;

CREATE TABLE building_outlines.nz_building_outlines_pilot
(
  id integer NOT NULL DEFAULT nextval('nz_building_outlines_pilot_id_seq'::regclass),
  imagery_source character varying(250),
  known_error character varying(50),
  geom geometry(MultiPolygon,2193),
  CONSTRAINT building_outlines_pilot_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE building_outlines.nz_building_outlines_pilot
  OWNER TO postgres;

-- Index: building_outlines.sidx_nz_building_outlines_pilot_geom

-- DROP INDEX building_outlines.sidx_nz_building_outlines_pilot_geom;

CREATE INDEX sidx_nz_building_outlines_pilot_geom
  ON building_outlines.nz_building_outlines_pilot
  USING gist
  (geom);


INSERT INTO building_outlines.nz_building_outlines_pilot (
    geom 
    )
SELECT geom::geometry 
FROM building_outlines.newzealand_building;



