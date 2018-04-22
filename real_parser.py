#!/usr/bin/env python3

import timeit 	
import sys
import shutil
import math
from datetime import datetime, timedelta
import udatetime
import time
import os
import glob
from collections import defaultdict
from line_profiler import LineProfiler
import psycopg2


#### WE SKIP MSG 6,8 0-- info only for GND, nothing else, But for GND we use MSG 2 ####
## PARAM KEEPS 30 seconds (param memory). IF we got -1 MSG -> last time is not updated! (update_last_time_param). So, if we every 10 sec file without param we will not fill wrong data. But last time will be updating!
## Param WILL BE TAKEN FROM CLOSEST IN both side of TIME (actually we need only in the future, but it's easy to make it in both sides). And also more accurate at the end (some parameter is absent, but fine in the next msg -> grab it from there).

track_memory=300 # how many time keep the same track, after this time, this icao - is already new track
param_memory=[3600] + [30]*7 # 30 sec we remember param, if more, than -1 -, 3600 for callsign
type_flight_detection_time = 30 # decision about take-off, first we get GND, if after this time we got message which are not MSG2 -> take off.

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

def do_profile(follow=None):
    if not follow:
        follow = []
    def inner(func):
        def profiled_func(*args, **kwargs):
            try:
                profiler = LineProfiler()
                profiler.add_function(func)
                for f in follow:
                    profiler.add_function(f)
                profiler.enable_by_count()
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()
        return profiled_func
    return inner
# def get_number():
#     for i in range(10000000):
#         yield i


# @do_profile(follow=None)
def main():
	def upd_msg_2(icao_query):
		if altitude_py is not None: # to make possible comparisom below, if None - error will be
			if first_gnd_angle is None: # just first is ok [+ code: or first_gnd_angle==None]: # FIRST GND MSG
				# print('FIRST GND MSG')
				if altitude_py > 100 and angle_py is not None:  # means REALLY fly not rolling -> altitude requirements  # NOT ROLLING SHOULD BE!!
					SQL='''
					UPDATE eco.aircraft_tracks SET (first_gnd_angle) = (%s) WHERE track=(%s);
					'''	
					data=(angle_py, last_track)
					icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))
			else: # NOT FIRST GND MSG
				# print('NOT FIRST GND MSG')
				SQL='''
				UPDATE eco.aircraft_tracks SET (last_gnd_angle) = (%s) WHERE track=(%s);
				'''
				data=(angle_py, last_track)
				icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

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
		print("Can\'t connect to db" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' +str(e))

	# CHANGE DIR 
	os.chdir("/home/delkov/Documents/air/sbs_store")
	destination_path="/home/delkov/Documents/air/sbs_store/smth_wrong" # if here -> file is wrong
	store_path="/home/delkov/Documents/air/sbs_store/smth_wrong/bd_was_dead" # if here -> db was bad
	print('PROGRAM START WORKING..'+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

	new_counter=0
	old_counter=0
	msg_6_8=0

	Main_loop=True;
	while Main_loop:
		start = time.time()
		
		txt_list=sorted(glob.glob('sbs.2*'), key = lambda file: os.path.getctime(file)) # find all txt in the folders
		for txt_temp in txt_list:
			total_query_for_distance=[]
			icao_query=[]
			icao_list = defaultdict(list) #making a dict of lists where ID is the key
			
			## SEPARATE WHOLE FILE AT ONCE BY LINES
			with open(txt_temp,'r', encoding='utf-8') as txt:	
				all_strings=txt.readlines()

			## SEPARATE ALL LINES BY ICAO ##
			for string in all_strings:
				string=string.split(',')
				icao_list[string[4]].append(string) #appending the lines by icao

			## LOOP FOR CURRENT ICAO ---- MAIN LOOP ----------------------------------------------------------
			for temp_icao in icao_list:
				first_time_icao=True

				## LOOP FOR ALL STRING FOR THIS ICAO
				for string in icao_list[temp_icao]:
					## PARSING PARAMS, if empty -> None, this None will be replaced by previous param below.
					MSG_NUM, icao_py, time_py= int(string[1]), string[4], udatetime.from_string(string[6].replace('/','-')+'T'+string[7]).replace(tzinfo=None) 
					
					if MSG_NUM in [6,8]:
						msg_6_8+=1
						continue

					elif MSG_NUM==1:
						callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  string[10],None,None,None,None,None,None # since in MSG  not all are presented -> default
						if not callsign_py:
							callsign_py=None
					
					elif MSG_NUM==2:
						callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  None,string[11],string[12],string[13],string[14],string[15],None # since in MSG  not all are presented -> default
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

					elif MSG_NUM==3:
						callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  None,string[11],None,None,string[14],string[15],None # since in MSG  not all are presented -> default
						if not altitude_py:
							altitude_py=None
						else:
							altitude_py=float(altitude_py)*0.3048 ## transform to meter from ft to calculate distance rigth way. From gps -- postgis calculating meter -> here also meter.

						if not latitude_py:
							latitude_py=None
						
						if not longitude_py:
							longitude_py=None

					elif MSG_NUM==4:
						callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  None,None,string[12],string[13],None,None,string[16] # since in MSG  not all are presented -> default
						if not speed_py:
							speed_py=None
						else:
							speed_py=float(speed_py)*1.852 ## transform to km/h from knots

						if not angle_py:
							angle_py=None
						
						if not vertical_speed_py:
							vertical_speed_py=None
						else:
							vertical_speed_py=float(vertical_speed_py)*0.051 ## meter per second

					elif MSG_NUM in [5,7]:
						callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py =  None,string[11],None,None,None,None,None # since in MSG  not all are presented -> default
						if not altitude_py:
							altitude_py=None
						else:
							altitude_py=float(altitude_py)*0.3048 ## transform to meter from ft to calculate distance rigth way. From gps -- postgis calculating meter -> here also meter.
			
					if first_time_icao:
						first_time_icao=False
						# TRY TO FIND CLOSEST TRACK FOR THIS ICAO AND TIME!! 
						SQL="""
						SELECT track,first_time,	last_time,callsign_last_time,altitude_last_time,speed_angle_last_time,coordinate_last_time,vert_speed_last_time,	gnd_last_time,type_of_flight,first_gnd_angle  from eco.aircraft_tracks where icao=(%s) ORDER BY case when last_time > (%s) then last_time - (%s) else (%s) - last_time end limit 1;
						"""
						data=(icao_py,time_py,time_py,time_py)
						cursor.execute(SQL, data)
						time_answer=cursor.fetchall()
						if time_answer:
							time_answer=time_answer[0]

						# TRACK IS EXIST AND NOT TOO OLD, FROM BOTH SIDE OF TIME.. --> we should write from old to new ot new to old
						if time_answer and (time_py-time_answer[2] <= track_memory and time_answer[2] - time_py <= track_memory):
							last_time_param=[time_answer[3],time_answer[4],time_answer[5],time_answer[5],time_answer[6],time_answer[6],time_answer[7], time_answer[8]]
							last_track=time_answer[0]

							## FOR GROUND 
							type_of_flight=time_answer[9]
							first_gnd_angle=time_answer[10]
							# we detect only take-off, other flight means landing. if no last_msg_2 -> no GND signal -> nor landing neither take-off 
							# True means TAKE-OFF; if there is last_gnd, but there is no type_of_flight -> LANDNG;if Nor last_gns -> JUST FLYING throw.

							# TAKE PREVIOUS PARAM
							SQL="""
							(SELECT callsign,altitude,speed,angle,latitude,longitude,vertical_speed FROM eco.tracks WHERE track=(%s)  ORDER BY case WHEN time_track > (%s) then time_track - (%s) else (%s) - time_track end LIMIT 1)
							"""
							data=(last_track, time_py, time_py, time_py)
							cursor.execute(SQL, data)
							previous_param= cursor.fetchall()[0]

							# UPDATE PARAM FROM PREVIOUS MSG, we make list to chek it in the loop -- more easy, compact
							param_from_msg=[time_py, last_track, callsign_py,altitude_py,speed_py,angle_py,latitude_py,longitude_py,vertical_speed_py]
							for x in range(7):
								if param_from_msg[x+2] == None and last_time_param[x] and (time_py-last_time_param[x] < param_memory[x]) and (last_time_param[x]-time_py < param_memory[x]):
									param_from_msg[x+2]=previous_param[x]
								else:	
									last_time_param[x]=time_py

							# FOR GROUND
							if MSG_NUM==2: # for gnd_last_time
								last_time_param[7]=time_py
								upd_msg_2(icao_query) # try to write first or last angle
							# detect type of flight
							elif not type_of_flight: # we don't know type of flight yet
								if last_time_param[7] and (time_py - last_time_param[7] > type_flight_detection_time): # and MSG_NUM !=2): # means we got firstly GND, and after detection_time another one, but not from ground -> it's not at the ground anymore.
									print('Detect TAKE-OFF at time MSG2 TIME', time_py)
									type_of_flight=True 
									SQL = '''
									UPDATE eco.aircraft_tracks SET (type_of_flight) = (%s) WHERE track=(%s);
									'''
									data =  (type_of_flight, last_track) 
									icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))
									
							## NOW WE HAVE UPDATED PARAMS in param_from_msg
							upd_icao_query(icao_query, param_from_msg)


							old_counter+=1
						else: ## TRACK IS TOO OLD OR DOESNT EXIST
							new_counter+=1

							type_of_flight, first_gnd_angle=None, None
							# !!!!!!!!!!!!!!!!!!! TO SASHA ADD icao info if not exist -- alone script to serf BD!!!!!!!!11
							SQL = '''
							INSERT INTO eco.aircrafts (icao) VALUES (%s) ON CONFLICT (icao) DO NOTHING;
							INSERT INTO eco.aircraft_tracks (icao, first_time) VALUES (%s, %s) RETURNING track;
							'''
							data = (icao_py, icao_py, time_py)
							cursor.execute(SQL, data)
							last_track=cursor.fetchall()[0][0] ## 

							## write_last_time for next iteration
							param_from_msg=[time_py, last_track, callsign_py, altitude_py, speed_py, angle_py, latitude_py, longitude_py, vertical_speed_py]
							last_time_param=[None]*8
							for x in range(7):
								if param_from_msg[x+2] is not None:
									last_time_param[x]=time_py
							if MSG_NUM==2: # for gnd_last_time
								last_time_param[7]=time_py
								upd_msg_2(icao_query)

							upd_icao_query(icao_query, param_from_msg)


					# icao is not first time
					else:
						old_counter+=1

						# take this param from first-time-icao block
						previous_param=param_from_msg[:]						
						for x in range(7): 
							if param_from_msg[x+2] == None and last_time_param[x] and (time_py-last_time_param[x] < param_memory[x]) and (last_time_param[x]-time_py < param_memory[x]):
								param_from_msg[x+2]=previous_param[x+2]
							else:	
								last_time_param[x]=time_py
						
						if MSG_NUM==2: # for gnd_last_time
							last_time_param[7]=time_py
							upd_msg_2(icao_query) # try to write first or last angle
						elif not type_of_flight: # we don't know type of flight yet
							if last_time_param[7] and (time_py - last_time_param[7] > type_flight_detection_time):# and MSG_NUM !=2): -- automatically since ELEIF before # means we got firstly GND, and after detection_time another one, but not from ground -> it's not at the ground anymore.
								# print('Detect TAKE-OFF at time MSG2 TIME', time_py)
								type_of_flight=True 
								SQL = '''
								UPDATE eco.aircraft_tracks SET (type_of_flight) = (%s) WHERE track=(%s);
								'''
								data =  (type_of_flight, last_track) 
								icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

						upd_icao_query(icao_query, param_from_msg) # last-time will be updated at the end


				#-------------- END LOOP FOR CURRENT ICAO --------------
				# UPDATE LAST-TIME FOR ALL PARAMS AT THE END FOR CURRENT ICAO & CALLSIGN (it keeps 1 hr, so it's fine)
				SQL='''
				UPDATE eco.aircraft_tracks SET (last_time, callsign_last_time, altitude_last_time, speed_angle_last_time, coordinate_last_time, vert_speed_last_time, gnd_last_time) = (%s,%s,%s,%s,%s,%s,%s) WHERE track=(%s);
				UPDATE eco.tracks SET (callsign) = (%s) WHERE track=(%s);
				'''
				data=(time_py, last_time_param[0], last_time_param[1], last_time_param[2], last_time_param[4], last_time_param[5], last_time_param[7], last_track, param_from_msg[2], last_track);
				icao_query.append(cursor.mogrify(SQL, data).decode('utf-8'))

				# UPDATE DISTANCE FOR CURRENT ICAO
				SQL='''
					UPDATE eco.tracks
					SET    distance_1 = ST_3DDistance(ST_MakePoint(ST_X(ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),32652)),
                                               ST_Y(ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326),32652)), altitude), 
                                               (SELECT geom FROM eco.static_points WHERE name='Korea'))
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
			cursor.execute(full_query_from_txt)
			connect.commit() # this commit is needed to get last_track
			os.chdir("/home/delkov/Documents/air")
			# os.remove(txt_temp)
		# ---------------  END LOOP FOR TXT in TXT_LIST -----------------

		end = time.time()
		print('TOTAL TIME', end-start)
		print('NEW',new_counter,' OLD', old_counter, 'MSG_6_8', msg_6_8, 'TOTAL: ', new_counter+old_counter+msg_6_8)
		Main_loop=False


	## CLOSE BD AFTER EXIT
	print('CLOSE DB CONNECTION')
	cursor.close()
	connect.close()


main()
# print(time.process_time())