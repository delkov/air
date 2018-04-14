DROP SCHEMA IF EXISTS eco CASCADE;

CREATE SCHEMA eco;

CREATE TABLE eco.aircrafts ( 
	icao                 text  NOT NULL,
	regid               text  ,
	mdl           text  ,
	type          text  ,
	operator           text  ,
	blank text,
	CONSTRAINT pk_aircrafts PRIMARY KEY ( icao )
 );

CREATE TABLE eco.routes ( 
	callsign                 text  NOT NULL,
	FromAirport           text  ,
	ToAirport text 
	-- CONSTRAINT pr_routes PRIMARY KEY ( callsign )
 );

-- CREATE TABLE eco.tbl2 ( 
-- 	time_2           timestamp  NOT NULL
--  );


-- INSERT INTO eco.tbl2 VALUES ('2017-09-06 15:45:58');

-- select time_1, (
--     select time_2 
--     from eco.tbl2 
--     order by case when time_1 > time_2 then age(time_1,time_2) 
--                                        else age(time_2,time_1) 
--              end 
--     fetch first 1 rows only
-- )
-- from eco.tbl1;

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE eco.noise ( 
	id                   bigserial  NOT NULL,
	time_noise           timestamp  NOT NULL,
	base_name            text  ,
	stat_1               smallint  ,
	stat_2               smallint  ,
	stat_3               smallint  ,
	leq                  real  ,
	slow                 real  ,
	spectrum 			 real[]  ,
	meteo_stat           smallint  ,
	temperature          real  ,
	humadity             real  ,
	presure              real  ,
	wind                 real  ,
	dir                  real  ,
	gps_coordinate       real[]    ,
	gps_stat			 smallint  ,
	temperature_core     smallint  ,
	temperature_mb       smallint  ,
	temperature_hdd      smallint  ,
	free_hdd             smallint  ,
	ups_stat             smallint  ,
	ups_mode             text  ,
	ups_time             smallint  ,
	track             	 bigint,
	distance             int,
	aircraft_time		timestamp,

	CONSTRAINT pk_noise PRIMARY KEY ( id )
 );

CREATE TABLE eco.aircraft_tracks ( 
	track                bigserial  NOT NULL,
	icao                 text  ,
	first_time           timestamp  ,
	last_time            timestamp  ,
	callsign_last_time   timestamp  ,
	altitude_last_time   timestamp  ,
	speed_angle_vert_last_time timestamp  ,
	coordinate_last_time timestamp  ,
	gnd_last_time timestamp,
	type_of_flight			boolean, 
	first_gnd_angle  real,
	last_gnd_angle  real,
	CONSTRAINT pk_aircraft_tracks PRIMARY KEY ( track )
 );

CREATE INDEX idx_aircraft_tracks ON eco.aircraft_tracks ( icao );

CREATE TABLE eco.tracks ( 
	id                   bigserial  NOT NULL,
	time_track           timestamp  NOT NULL,
	track                bigint  ,
	callsign             text  ,
	altitude             int  ,
	speed                smallint  ,
	angle                real  ,
	latitude             double precision  ,
	longitude            double precision  ,
	vertical_speed       smallint  ,
	CONSTRAINT pk_tracks PRIMARY KEY ( id )
 );

ALTER TABLE eco.tracks ADD COLUMN distance_1 integer;
ALTER TABLE eco.tracks ADD COLUMN geom geometry(POINT,4326);



-- MOSCOW, lat 55.873282, lon 37.515777
-- Korea house, lat 37.293873 , lon 126.978899

CREATE TABLE eco.static_points (name text, lon double precision, lat double precision, alt double precision, geom geometry(PointZ));

-- Korea
INSERT INTO eco.static_points VALUES ('Korea', 126.978899, 37.293873, 0);
WITH geom_1 AS (
	SELECT ST_Transform(ST_SetSRID(ST_MakePoint(126.978899, 37.293873), 4326), 32652) -- 32637 for MOSCOW, 32652 for Korea
	), point_3d AS (
	SELECT  ST_MakePoint(ST_X(st_transform),ST_Y(st_transform), 0) FROM geom_1
	) 
UPDATE eco.static_points SET geom = (SELECT st_makepoint FROM point_3d) WHERE name = 'Korea'; -- outut from above

-- Moscow
INSERT INTO eco.static_points (name, lon, lat, alt) VALUES('Moscow', 37.515777, 55.873282, 0);
WITH geom_1 AS (
	SELECT ST_Transform(ST_SetSRID(ST_MakePoint(37.515777, 55.873282), 4326), 32637) -- 32637 for MOSCOW, 32652 for Korea
	), point_3d AS (
	SELECT  ST_MakePoint(ST_X(st_transform),ST_Y(st_transform), 0) FROM geom_1
	) 
UPDATE eco.static_points SET geom = (SELECT st_makepoint FROM point_3d) WHERE name = 'Moscow'; -- outut from above



CREATE INDEX idx_tracks ON eco.tracks ( track );
ALTER TABLE eco.aircraft_tracks ADD CONSTRAINT fk_aircraft_tracks_aircrafts FOREIGN KEY ( icao ) REFERENCES eco.aircrafts( icao ) ON DELETE RESTRICT;
COMMENT ON CONSTRAINT fk_aircraft_tracks_aircrafts ON eco.aircraft_tracks IS '';
ALTER TABLE eco.tracks ADD CONSTRAINT fk_tracks_aircraft_tracks FOREIGN KEY ( track ) REFERENCES eco.aircraft_tracks( track );
COMMENT ON CONSTRAINT fk_tracks_aircraft_tracks ON eco.tracks IS '';

-- VERY IMPORTANT PART, psycorg need unique to check..
ALTER TABLE eco.tracks ADD UNIQUE (time_track, track);
ALTER TABLE eco.noise ADD UNIQUE (time_noise, base_name);