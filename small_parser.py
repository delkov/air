#!/usr/bin/env python3

import timeit 	
import sys
import shutil
import math
from datetime import datetime, timedelta
# import udatetime
import time
import os
import glob
from collections import defaultdict
# from line_profiler import LineProfiler
import psycopg2

 # change to 32637 for MOSCOW, 32652 seoul
#### WE SKIP MSG 6,8 0-- info only for GND and sometimes alt.. (usually only alter message). should be logged, nothing else, For GND we use MSG 2 ####
## PARAM KEEPS 30 seconds (param memory). IF we got "None" MSG -> last time is not updated! (update_last_time_param). So, if we every 10 sec file without param we will not fill wrong data. But last time will be updating!
## Param WILL BE TAKEN FROM CLOSEST IN both side of TIME (actually we need only in the future, but it's easy to make it in both sides). And also more accurate at the end (some parameter is absent, but fine in the next msg -> grab it from there).

track_memory=300 # how many time keep the same track, after this time, this icao - is already new track
param_memory=[3600] + [30]*7 # 30 sec we remember param, if more, than -1 -, 3600 for callsign
type_flight_detection_time = 30 # decision about take-off, first we get GND, if after this time we got message which are not MSG2 -> take off.
max_altitude_type_detection=500 # in meters. from which 
min_altitude_type_detection=100 # in meters


track_memory=timedelta(seconds=track_memory) 
type_flight_detection_time = timedelta(seconds=type_flight_detection_time) 
param_memory[0]=timedelta(seconds=param_memory[0])
param_memory[1]=timedelta(seconds=param_memory[1])
param_memory[2]=timedelta(seconds=param_memory[2])
param_memory[3]=timedelta(seconds=param_memory[3])
param_memory[4]=timedelta(seconds=param_memory[4]) 
param_memory[5]=timedelta(seconds=param_memory[5])
param_memory[6]=timedelta(seconds=param_memory[6])
param_memory[7]=timedelta(seconds=param_memory[7])

def main():

	def gnd_detection(icao_query, param_from_msg):
		print('try GND detect')
		successful=None
		altitude_py=param_from_msg[3]
		angle_py=param_from_msg[5]
		vertical_speed_py=param_from_msg[8]
		if altitude_py is not None and (altitude_py < max_altitude_type_detection) and (altitude_py > min_altitude_type_detection):
			if vertical_speed_py is not None and angle_py is not None: # from MSG 4 they have to be not NULL at same time
				successful=True
				if vertical_speed_py > 0:
					type_of_flight=True # True means TAKE-OFF (first letter is t, so..)
					print('TAKING-OFF, angle is: ', angle_py)
				else:
					type_of_flight=False # False means LANDING
					print('LANDING, angle is: ', angle_py)

				SQL='''
					UPDATE eco.aircraft_tracks SET (type_of_flight, vpp_angle) = (%s, %s) WHERE track=(%s);
				'''
				data=(type_of_flight, angle_py, last_track)
				icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

		return successful





	def upd_icao_query(icao_query, param_from_msg):
		SQL = '''
		INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s)
		ON CONFLICT (time_track,track) DO UPDATE SET callsign=EXCLUDED.callsign, altitude=EXCLUDED.altitude, speed=EXCLUDED.speed, angle=EXCLUDED.angle,  latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,	vertical_speed= EXCLUDED.vertical_speed;
		'''
		icao_query.append(cursor.mogrify(SQL, tuple(param_from_msg)).decode('utf-8'))


	# TRY CONNECT TO DB
	try:
		connect = psycopg2.connect(database='eco_db', user='postgres', host='localhost', password='z5UHwrg8', port=5432)
		cursor = connect.cursor()
	except psycopg2.OperationalError as e:
		print("Can\'t connect to db" + '\n' +str(e)+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

	# CHANGE DIR 
	os.chdir("/home/delkov/Documents/air/sbs_store")
	destination_path="/home/delkov/Documents/air/sbs_store/smth_wrong" # if here -> file is wrong
	store_path="/home/delkov/Documents/air/sbs_store/smth_wrong/bd_was_dead" # if here -> db was bad
	print('PROGRAM START WORKING..'+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

	Main_loop=True;
	while Main_loop:
		start = time.time()
		
		txt_list=sorted(glob.glob('*sorted.txt'), key = lambda file: os.path.getctime(file)) # find all txt in the folders
		for txt_temp in txt_list:
			total_query_for_distance=[]
			icao_query=[]
			icao_list = defaultdict(list) #making a dict of lists where ID is the key
			print(txt_temp)
			
			## SEPARATE WHOLE FILE AT ONCE BY LINES
			with open(txt_temp,'r', encoding='utf-8') as txt:	
				all_strings=txt.readlines()

			bad_string_counter=False
			# ## SEPARATE ALL LINES BY ICAO ## ACTUALLY THEY ALREADY COME SORTED WAY..
			for string in all_strings:
				string=string.split(',')
				icao_list[string[0]].append(string) #appending the lines by icao

			## LOOP FOR CURRENT ICAO ---- MAIN LOOP ----------------------------------------------------------
			for temp_icao in icao_list:
				first_time_icao=True
				# print('TEMP ICAO', temp_icao)
				## LOOP FOR ALL STRING FOR THIS ICAO
				for string in icao_list[temp_icao]:
					# print(string)
					## PARSING PARAMS, if empty -> None, this None will be replaced by previous param below.
					# STRING: ICAO(0), DATE(1), TIME(2), CALLSIGN(3), ALT(4), GS(5), TRK(6), LAT(7), LON(8), VR(9)  // 0-10
					year,month,day=map(int,string[1].split('/'))
					str_time=string[2].split('.')[0] 
					hour, minute, second = map(int,str_time.split(":"))

					icao_py, time_py= string[0], datetime(year,day,month,hour,minute,second)					
					callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  string[3],string[4],string[5],string[6],string[7],string[8],string[9] # since in MSG  not all are presented -> default
					
					if not callsign_py:
						callsign_py=None
					if not altitude_py:
						altitude_py=None
					else:
						altitude_py=float(altitude_py)*0.3048 ## transform to meter from ft to calculate distance rigth way. From gps -- postgis calculating meter -> here also meter.
					if not speed_py:
						speed_py=None
					else:
						speed_py=float(speed_py)*1.852 ## transform to km/h from knots
					if not angle_py:
						angle_py=None
					if not latitude_py:
						latitude_py=None
					if not longitude_py:
						longitude_py=None
					if not vertical_speed_py:
						vertical_speed_py=None
					else:
						vertical_speed_py=float(int(vertical_speed_py))*0.051 ## meter per second


					if first_time_icao:
						# print('icao FIRST time')
						first_time_icao=False
						# TRY TO FIND CLOSEST TRACK FOR THIS ICAO AND TIME!! 
						SQL="""
						SELECT track,first_time,	last_time,callsign_last_time,altitude_last_time,speed_angle_last_time,coordinate_last_time,vert_speed_last_time,	type_of_flight  from eco.aircraft_tracks where icao=(%s) ORDER BY case when last_time > (%s) then last_time - (%s) else (%s) - last_time end limit 1;
						"""
						data=(icao_py,time_py,time_py,time_py)
						cursor.execute(SQL, data)
						time_answer=cursor.fetchall()
						if time_answer:
							time_answer=time_answer[0]

						# TRACK IS EXIST AND NOT TOO OLD, FROM BOTH SIDE OF TIME.. --> we should write from old to new ot new to old
						if time_answer and (time_py-time_answer[2] <= track_memory and time_answer[2] - time_py <= track_memory):
							# print('track OLD')
							last_time_param=[time_answer[3],time_answer[4],time_answer[5],time_answer[5],time_answer[6],time_answer[6],time_answer[7]] # only params last time
							last_track=time_answer[0]

							## FOR GROUND 
							type_of_flight=time_answer[8]
							print('type of flight', type_of_flight)

							# TAKE PREVIOUS PARAM
							SQL="""
							(SELECT callsign,altitude,speed,angle,latitude,longitude,vertical_speed FROM eco.tracks WHERE track=(%s)  ORDER BY case WHEN time_track > (%s) then time_track - (%s) else (%s) - time_track end LIMIT 1)
							"""
							data=(last_track, time_py, time_py, time_py)
							cursor.execute(SQL, data)
							previous_param= cursor.fetchall()[0]

							# UPDATE PARAM FROM PREVIOUS MSG, we make list to check it in the loop -- more easy, compact
							param_from_msg=[time_py, last_track, callsign_py,altitude_py,speed_py,angle_py,latitude_py,longitude_py,vertical_speed_py]
							for x in range(7):
								if param_from_msg[x+2] == None:
									if last_time_param[x] and (time_py-last_time_param[x] < param_memory[x]) and (last_time_param[x]-time_py < param_memory[x]):
										param_from_msg[x+2]=previous_param[x]
								else:	
									last_time_param[x]=time_py

							# FOR GROUND
							if type_of_flight is None:
								type_of_flight=gnd_detection(icao_query,param_from_msg)

									
							## NOW WE HAVE UPDATED PARAMS in param_from_msg
							upd_icao_query(icao_query, param_from_msg)


						else: ## TRACK IS TOO OLD OR DOESNT EXIST
							# print('track NEW')

							type_of_flight=None
							# !!!!!!!!!!!!!!!!!!! TO SASHA ADD icao info if not exist -- alone script to serf BD!!!!!!!!11
							SQL = '''
							INSERT INTO eco.aircrafts (icao) VALUES (%s) ON CONFLICT (icao) DO NOTHING;
							INSERT INTO eco.aircraft_tracks (icao, first_time) VALUES (%s, %s) RETURNING track;
							'''
							data = (icao_py, icao_py, time_py)
							cursor.execute(SQL, data)
							last_track=cursor.fetchall()[0][0] ## 

							## write_last_time for next iteration
							param_from_msg=[time_py,last_track, 	callsign_py,altitude_py,speed_py,angle_py,latitude_py,longitude_py,vertical_speed_py]
							last_time_param=[None]*7
							
							for x in range(7):
								if param_from_msg[x+2] is not None:
									last_time_param[x]=time_py
							
							# FOR GROUND
							if type_of_flight is None:
								type_of_flight=gnd_detection(icao_query,param_from_msg)

							upd_icao_query(icao_query, param_from_msg)


					# icao is not first time
					else:
						# print('icao NOT first time')

						# take this param from first-time-icao block
						previous_param=param_from_msg[:]						
						# params from parsing
						param_from_msg=[time_py,last_track, 	callsign_py,altitude_py,speed_py,angle_py,latitude_py,longitude_py,vertical_speed_py]
						for x in range(7): 
							if param_from_msg[x+2] == None:
								if last_time_param[x] and (time_py-last_time_param[x] < param_memory[x]) and (last_time_param[x]-time_py < param_memory[x]):
									param_from_msg[x+2]=previous_param[x+2]
							else:	
								last_time_param[x]=time_py
						

						# FOR GROUND
						if type_of_flight is None:
							type_of_flight= gnd_detection(icao_query,param_from_msg)

						upd_icao_query(icao_query, param_from_msg) # last-time will be updated at the end


				#-------------- END LOOP FOR CURRENT ICAO --------------
				# UPDATE LAST-TIME FOR ALL PARAMS AT THE END FOR CURRENT ICAO & CALLSIGN (it keeps 1 hr, so it's fine)
				SQL='''
				UPDATE eco.aircraft_tracks SET (last_time, callsign_last_time, altitude_last_time, speed_angle_last_time, coordinate_last_time, vert_speed_last_time) = (%s,%s,%s,%s,%s,%s) WHERE track=(%s);
				UPDATE eco.tracks SET (callsign) = (%s) WHERE track=(%s);
				'''
				try:
					data=(time_py, last_time_param[0],last_time_param[1],last_time_param[2],last_time_param[4],last_time_param[6],last_track,	param_from_msg[2],last_track);
				except:
					print('last_time_problem..', last_time_param)

				icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

				# UPDATE DISTANCE FOR CURRENT ICAO
				# change to 32637 for MOSCOW, 32652 seoul; 4326 means geoid
				SQL='''
					UPDATE eco.tracks
					SET    distance_1 = ST_3DDistance(ST_MakePoint(ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),32637)),
                                               ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),32637)), altitude), 
                                               (SELECT geom FROM eco.static_points WHERE name='Moscow'))
	 				WHERE track=(%s)                                              
					AND   latitude IS NOT NULL
					AND   longitude IS NOT NULL
					AND   altitude IS NOT NULL;
				'''
				data=(last_track,)
				icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

			# ----------- 	END LOOP FOR ICAO IN ICAO_LIST --------------
			# TOTAL QUERY FOR CURRENT TXT
			full_query_from_txt=''.join([x for x in icao_query])
			try:
				cursor.execute(full_query_from_txt)
			except Exception as e:
				print(str(e))
				
			connect.commit() # this commit is needed to get last_track
			# os.remove(txt_temp)
		# ---------------  END LOOP FOR TXT in TXT_LIST -----------------

		end = time.time()
		print('TOTAL TIME', end-start)
		Main_loop=False
		# time.sleep(10)

	## CLOSE BD AFTER EXIT
	print('CLOSE DB CONNECTION')
	cursor.close()
	connect.close()


main()
# print(time.process_time())