DELETE FROM eco.tracks
WHERE time_track IN (SELECT time_track
                         FROM eco.aircrafts
                         ORDER BY time_track asc
                         LIMIT 20);


DELETE FROM eco.aircraft_tracks
	WHERE track IN (SELECT track
                         FROM eco.aircraft_tracks
                         ORDER BY track asc
                         LIMIT 20);


	DELETE FROM eco.aircrafts
	WHERE icao IN (SELECT icao
                         FROM eco.aircrafts
                         ORDER BY icao asc
                         LIMIT 20);