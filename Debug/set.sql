UPDATE eco.aircraft_tracks SET last_time = now()+time '09:00' WHERE icao='icao2';
-- UPDATE eco.aircraft_tracks SET angle_last_time = now()+time '00:11' WHERE icao='icao1';
-- UPDATE eco.aircraft_tracks SET coordinate_last_time = now()+time '00:11' WHERE icao='icao1';
-- UPDATE eco.tracks SET (speed, angle, latitude, longitude, vertical_speed) = (500, 45, 78.98, 56.23, 55) WHERE track=2;


-- CREATE TABLE eco.msg ( 
-- 	id            serial  NOT NULL,
-- 	msg_1         timestamp  ,
-- 	msg_3         timestamp  ,
-- 	msg_4         timestamp  ,
-- 	msg_5         timestamp  ,
-- 	msg_7         timestamp  , 

-- 	CONSTRAINT pk_msg PRIMARY KEY ( id )
--  );
INSERT INTO eco.tracks (track) VALUES ('10');

INSERT INTO eco.aircrafts (icao,int_array) VALUES ('icao1',{1,2,3});
INSERT INTO eco.aircrafts (icao) VALUES ('icao2');
INSERT INTO eco.aircrafts (icao) VALUES ('icao3') ON CONFLICT (icao) DO UPDATE SET engine=EXCLUDED.engine, reg_number='test' ;

INSERT INTO eco.aircraft_tracks (icao, last_time, callsign_last_time, altitude_last_time, speed_angle_vert_last_time, coordinate_last_time) VALUES ('icao1', now(), now(), now()-time '03:00', now()-time '05:00', now()-time '08:00');
INSERT INTO eco.aircraft_tracks (icao, last_time, callsign_last_time, altitude_last_time, speed_angle_vert_last_time, coordinate_last_time) VALUES ('icao1', now(), now(), now()-time '02:00', now()-time '09:00', now()-time '01:00');
INSERT INTO eco.aircraft_tracks (icao, last_time, callsign_last_time, altitude_last_time, speed_angle_vert_last_time, coordinate_last_time) VALUES ('icao2', now(), now(), now()-time '05:00', now()-time '03:12', now()-time '03:10');

INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed) VALUES (now()-time '05:00', 1, 'callsign 2', 3900, 900, 10, 67.8, 45.6, 100);
INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed) VALUES (now()-time '05:00', 2, 'callsign 2', 3600, 800, 20, 34.7, 50.3, 175);
INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed) VALUES (now()-time '09:00', 3, 'callsign 2', 3300, 700, 30, 45.4, 60.5, 150);


-- INSERT INTO eco.aircraft_tracks (icao, callsign_last_time, speed_last_time) VALUES ('icao1', now(), now()-time '03:00');
-- DELETE FROM eco.tracks WHERE time_track = any (array(SELECT time_track FROM eco.tracks ORDER BY time_track LIMIT 10));
-- INSERT INTO eco.tracks (time_track, track, altitude, longitude, latitude) VALUES (now(), 8, 3800, 100, 200);

-- ALTER TABLE eco.pk_aircraft_tracks ADD COLUMN requset_time timestamp;
-- INSERT INTO eco.tracks (time_track, track) VALUES (2, TIMESTAMP 2016-07-19 14:42:14);


-- CREATE TABLE eco.time ( 
-- 	time                timestamp,
-- 	CONSTRAINT pk_aircraft_tracks PRIMARY KEY ( time )
--  );
-- CREATE TABLE users (
--     -- make the "id" column a primary key; this also creates
--     -- a UNIQUE constraint and a b+-tree index on the column
--     id    SERIAL PRIMARY KEY,
--     name  TEXT,
--     age   INT4
-- );

-- INSERT INTO users (name, age) VALUES ('Mozart', 20);

-- SELECT currval(pg_get_serial_sequence('users', 'id'));
-- UPDATE eco.aircraft_tracks SET last_time = now(),
--                     contact_last_name = last_name

