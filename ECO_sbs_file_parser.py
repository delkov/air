# import timeit
import sys
import shutil
import math
import psycopg2
from datetime import datetime, timedelta
import time
import os
import glob

#### WE SKIP MSG 6,8 0-- info only for GND, nothing else, But for GND we use MSG 2 ####

## MUST DELETE	
track_memory=300 # after - new track
param_memory=[3600] + [30]*7 # 30 sec we remember param, if more, than -1 -, 3600 for callsign
max_req_speed=[3600]+[0]*7
# max_req_speed=0 # the bigger the more strict (problem with diff. msg. msg7 taken -> msg 2 reject this second.. and so on, so let it be 0)
type_flight_detection_time = 30 # decision about take-off

# ## UPDATE (IF NEW MSG AT THE SAME TIME) + UPDATE LAST_TIME
def upd_msg_1(param_to_write):
  x = list(param_to_write)
  x[2] = callsign_py
  ## UPDATE LAST_TIME FOR THIS PARAM
  # if callsign_py
  SQL='UPDATE eco.aircraft_tracks SET (callsign_last_time) = (%s) WHERE track=(%s); UPDATE eco.tracks SET (callsign) = (%s) WHERE track=(%s);'

  data=(time_py, last_track, callsign_py, last_track)
  

  cursor.execute(SQL, data)
  return tuple(x)

def upd_msg_2(param_to_write):
	x = list(param_to_write)
	x[3] = int(float(altitude_py))
	x[4] = float(speed_py)
	x[5] = float(angle_py)
	x[6] = float(latitude_py)
	x[7] = float(longitude_py)

	# update ground angle
	if not first_gnd_angle: # just first is ok [+ code: or first_gnd_angle==None]: # FIRST GND MSG
		# print('FIRST GND MSG')
		
		if altitude_py > 100 and angle_py!=-1:  # means REALLY fly not rolling
			SQL='''
			UPDATE eco.aircraft_tracks SET (coordinate_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (speed_angle_vert_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (gnd_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (first_gnd_angle) = (%s) WHERE track=(%s); # NOT ROLLING SHOULD BE!!
			'''	
			data=(time_py, last_track, time_py, last_track, time_py, last_track, time_py, last_track, angle_py, last_track)

		else:
			SQL='''
			UPDATE eco.aircraft_tracks SET (coordinate_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (speed_angle_vert_last_time) = (%s) WHERE track=(%s);
			UPDATE eco.aircraft_tracks SET (gnd_last_time) = (%s) WHERE track=(%s);
			'''	
			data=(time_py, last_track, time_py, last_track, time_py, last_track, time_py, last_track)




	else: # NOT FIRST GND MSG
		# print('NOT FIRST GND MSG')
		SQL='''
		UPDATE eco.aircraft_tracks SET (coordinate_last_time) = (%s) WHERE track=(%s);
		UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);
		UPDATE eco.aircraft_tracks SET (speed_angle_vert_last_time) = (%s) WHERE track=(%s);
		UPDATE eco.aircraft_tracks SET (gnd_last_time) = (%s) WHERE track=(%s);
		UPDATE eco.aircraft_tracks SET (last_gnd_angle) = (%s) WHERE track=(%s);
		'''
		data=(time_py, last_track, time_py, last_track, time_py, last_track, time_py, last_track, angle_py, last_track)




	cursor.execute(SQL, data)
	return tuple(x)

def upd_msg_3(param_to_write):
  x = list(param_to_write)
  x[3] = int(float(altitude_py))
  # print(type(x[6]))
  if latitude_py!=-1:
  	x[6] = float(latitude_py)
  if longitude_py!=-1:
  	x[7] = float(longitude_py)
  ## UPDATE LAST_TIME FOR THIS PARAM
  SQL='''
  UPDATE eco.aircraft_tracks SET (coordinate_last_time) = (%s) WHERE track=(%s);
  UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);
  '''
  data=(time_py, last_track, time_py, last_track)
  cursor.execute(SQL, data)



  if latitude_py!=-1 and longitude_py!=-1 and altitude_py!=-1:

   SQL='''WITH geom_1 AS (
	SELECT ST_Transform(ST_SetSRID(ST_MakePoint(%s, %s), 4326),32652) -- change to 32637 for MOSCOW, 32652 seoul
	), point_3d AS (
	SELECT  ST_MakePoint(ST_X(st_transform),ST_Y(st_transform), %s) FROM geom_1
	), static_points AS (SELECT geom FROM eco.static_points WHERE name='Korea')   --- CHANGE NAME!!

    SELECT ST_3DDistance(st_makepoint, geom) FROM point_3d, static_points;
    '''
   data=(longitude_py, latitude_py, altitude_py)
   cursor.execute(SQL, data)
   param_answer= cursor.fetchone()[0]
   # print(param_answer)
   x[9] = int(float(param_answer))


  return tuple(x)

def upd_msg_4(param_to_write):
  x = list(param_to_write)
  x[4] = int(float(speed_py))
  x[5] = float(angle_py)
  x[8] = int(float(vertical_speed_py))
  ## UPDATE LAST_TIME FOR THIS PARAM
  SQL='UPDATE eco.aircraft_tracks SET (speed_angle_vert_last_time) = (%s) WHERE track=(%s);'
  data=(time_py, last_track)
  cursor.execute(SQL, data)
  # print(len(x))
  return tuple(x)

def upd_msg_5(param_to_write):
  x = list(param_to_write)
  x[3] = int(float(altitude_py))
  ## UPDATE LAST_TIME FOR THIS PARAM
  SQL='UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);'
  data=(time_py, last_track)
  cursor.execute(SQL, data)
  return tuple(x)

def upd_msg_7(param_to_write):
  x = list(param_to_write)
  x[3] = int(float(altitude_py))
  ## UPDATE LAST_TIME FOR THIS PARAM
  SQL='UPDATE eco.aircraft_tracks SET (altitude_last_time) = (%s) WHERE track=(%s);'
  data=(time_py, last_track)
  cursor.execute(SQL, data)
  return tuple(x)

upd_msg = {
	1 : upd_msg_1,
	2 : upd_msg_2,
	3 : upd_msg_3,
	4 : upd_msg_4,
	5 : upd_msg_5,	
	7 : upd_msg_7,
}

try:
	connect = psycopg2.connect(database='eco_db', user='postgres', host='localhost', password='z5UHwrg8', port=5432)
	# connect.autocommit = True
	# cursor = connect.cursor()
except psycopg2.OperationalError as e:
	print("Can\'t connect to db" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' +str(e))

os.chdir("/home/delkov/Documents/air/sbs_store")
destination_path="/home/delkov/Documents/air/sbs_store/smth_wrong" # if here -> file is wrong
store_path="/home/delkov/Documents/air/sbs_store/smth_wrong/bd_was_dead" # if here -> db was bad

print('PROGRAM start working..'+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

while True:
	# txt_list=glob.glob('sbs.2*') # find all txt in the folders
	print('FIND NEW LIST')
	cursor = connect.cursor()

	txt_list=sorted(glob.glob('sbs.2*'),	key = lambda file: os.path.getctime(file)) # find all txt in the folders

	# try:
	# print('AZAZAZA')
	for txt_temp in txt_list:
		print(txt_temp)
		start = time.time()

		with open(txt_temp,'r', encoding='utf-8') as txt:
		# with open(txt_temp,'rb') as txt:
			# data=str(txt.read(),'utf-8').splitlines()
			SQL_FINAL=[]

			for string in txt:

				string=string.rstrip().split(',')
				# print(string)
				MSG_NUM=int(string[1])

				# SKIP NOT USEFUL MSG
				if MSG_NUM==6 or MSG_NUM==8:
					continue

				icao_py=string[4]
				time_py_1=string[6].replace('/','-')
				time_py_2=str(string[7].split('.')[0])
				# print(time_py_2)
				time_py=datetime.strptime(time_py_1+' '+time_py_2, "%Y-%m-%d %H:%M:%S")
				
				## not possible to make depends ony on MSG, because sometimes not all field there are // should be checked.
				callsign_py=string[10]
				if not callsign_py:
					callsign_py=-1
				altitude_py=string[11]
				if not altitude_py:
					altitude_py=-1
				else:
					altitude_py=float(altitude_py)*0.3048 ## transform to meter from ft to calculate distance rigth way. From gps -- postgis calculating meter -> here also meter.
				speed_py=string[12]
				if not speed_py:
					speed_py=-1
				else:
					speed_py=float(speed_py)*1.852 ## transform to km/h from knots
				angle_py=string[13]
				if not angle_py:
					angle_py=-1
				latitude_py=string[14]
				if not latitude_py:
					latitude_py=-1
				longitude_py=string[15]
				if not longitude_py:
					longitude_py=-1      
				vertical_speed_py=string[16]
				if not vertical_speed_py:
					vertical_speed_py=-1
				else:
					vertical_speed_py=float(vertical_speed_py)*0.051 ## meter per second



				first_gnd_angle=None


				# TRY TO FIND CLOSEST TRACK FOR THIS ICAO AND TIME!!
				SQL="""
				SELECT * from eco.aircraft_tracks where icao=(%s) ORDER BY case when last_time > (%s) then last_time - (%s) else (%s) - last_time end limit 1;
				"""
				data=(icao_py,time_py,time_py,time_py,)
				cursor.execute(SQL, data)
				time_answer=cursor.fetchall()

				# EXIST AND NOT TOO OLD
				if time_answer and (time_py-time_answer[0][3] <= timedelta(seconds=track_memory) and time_answer[0][3] - time_py <= timedelta(seconds=track_memory)):
					# print('EXIST, MUST BE ADDED')
					last_track=time_answer[0][0] 

					last_msg_time={
					1 : time_answer[0][4],
					2 : time_answer[0][8],
					3 : time_answer[0][7],
					4 : time_answer[0][6],
					5 : time_answer[0][5],
					7 : time_answer[0][5],
					}


					## FOR GROUND ----------
					type_of_flight=time_answer[0][9]
					first_gnd_angle=time_answer[0][10]
					last_gnd_angle=time_answer[0][11]

					# we detect only take-off, other flight means landing. if no last_msg_2 -> no GND signal -> nor landing neither take-off 
					if not type_of_flight:
						if last_msg_time[2] and time_py - last_msg_time[2] > timedelta(seconds=type_flight_detection_time):
							print('Detect TAKE-OFF at time MSG2 TIME', last_msg_time[2])
							type_of_flight=1 # 1 means take-off
							SQL = '''
							UPDATE eco.aircraft_tracks SET (type_of_flight) = (%s) WHERE track=(%s);
							'''
							data =  (type_of_flight, ) + (last_track,) 
							cursor.execute(SQL, data)

					### END GROUND ----------
					# SPEED OF CURRNET MSG IS OK
					if last_msg_time[MSG_NUM] is None or time_py-last_msg_time[MSG_NUM] >= timedelta(seconds=max_req_speed[MSG_NUM]) or last_msg_time[MSG_NUM] -time_py >= timedelta(seconds=max_req_speed[MSG_NUM]) :
						# OBTAIN ALL PREVIUS INFO (NOT NULL) BESIDES CALLSIGN because cant use UNION (TEXT and INT)

						SQL="""
						(SELECT altitude FROM eco.tracks WHERE track=(%s) AND altitude IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT speed FROM eco.tracks WHERE track=(%s) AND speed IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT angle FROM eco.tracks WHERE track=(%s) AND angle IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT latitude FROM eco.tracks WHERE track=(%s) AND latitude IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT longitude FROM eco.tracks WHERE track=(%s) AND longitude IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT vertical_speed FROM eco.tracks WHERE track=(%s) AND vertical_speed IS NOT NULL ORDER BY time_track desc LIMIT 1)
						UNION ALL
						(SELECT distance_1 FROM eco.tracks WHERE track=(%s) AND distance_1 IS NOT NULL ORDER BY time_track desc LIMIT 1)
						"""
						data=(last_track, last_track, last_track, last_track, last_track, last_track,last_track)
						cursor.execute(SQL, data)
						param_answer= cursor.fetchall()
					
						# QUERY FOR CALLSIGN
						SQL="""
						(SELECT callsign FROM eco.tracks WHERE track=(%s) AND callsign IS NOT NULL ORDER BY time_track desc LIMIT 1)
						"""
						data=(last_track, )
						cursor.execute(SQL, data)
						callsign_answer= cursor.fetchall()

						# JOIN CALLSIGN & OTHER PARAMS VALUES!!
						total_param=callsign_answer + param_answer
						# print(total_param, 'LEN', len(total_param))
						# TOTAL LAST_TIME FOR ALL PARAMS
						last_time_param=[time_answer[0][4], time_answer[0][5], time_answer[0][6], time_answer[0][6], time_answer[0][7], time_answer[0][7], time_answer[0][6], time_answer[0][7]]
						# CREATE A SQL QUERY
						param_to_write=()
						for x in range(8):
							# print(x, 'last_time_param[x]:', last_time_param[x])
							# print('total_param[x]', total_param[x][0])
							# PREVIOUS PARAM IS NOT TOO OLD, else -1
							if last_time_param[x] is None or ( (time_py-last_time_param[x] < timedelta(seconds=param_memory[x])) and (last_time_param[x]-time_py < timedelta(seconds=param_memory[x]))):
								param_to_write+=(total_param[x][0],)
							else:
								param_to_write+=(-1,)	

						# TOTAL SQL QUERY
						param_to_write=(time_py, )+(last_track,)+param_to_write
						# CALL FUNCTION, THAT UPDATED TABLE
						new_param_to_write=upd_msg[MSG_NUM](param_to_write) # UPDATE LAST_TIME + change param


						# ADD TO TRACK + UPDATE GENERAL LAST_TIME
						# SQL_FINAL_LIST.mogrify('INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed, distance_1) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s) ON CONFLICT (time_track,track) DO UPDATE SET callsign=EXCLUDED.callsign, altitude=EXCLUDED.altitude, speed=EXCLUDED.speed, angle=EXCLUDED.angle,  latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,	vertical_speed= EXCLUDED.vertical_speed, distance_1= EXCLUDED.distance_1; UPDATE eco.aircraft_tracks SET (last_time) = (%s) WHERE track=(%s);')
						# SQL_FINAL_DATA.append(new_param_to_write + (time_py,) + (last_track,))

						# SQL_FINAL
						# SQL_FINAL.append(cursor.mogrify("INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed, distance_1) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s) ON CONFLICT (time_track,track) DO UPDATE SET callsign=EXCLUDED.callsign, altitude=EXCLUDED.altitude, speed=EXCLUDED.speed, angle=EXCLUDED.angle,  latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,	vertical_speed= EXCLUDED.vertical_speed, distance_1= EXCLUDED.distance_1; UPDATE eco.aircraft_tracks SET (last_time) = (%s) WHERE track=(%s)", new_param_to_write + (time_py,) + (last_track,)))


						SQL = '''
						INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed, distance_1) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s)
						ON CONFLICT (time_track,track) DO UPDATE SET callsign=EXCLUDED.callsign, altitude=EXCLUDED.altitude, speed=EXCLUDED.speed, angle=EXCLUDED.angle,  latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,	vertical_speed= EXCLUDED.vertical_speed, distance_1= EXCLUDED.distance_1;
						UPDATE eco.aircraft_tracks SET (last_time) = (%s) WHERE track=(%s);
						'''
						data = new_param_to_write + (time_py,) + (last_track,)
						cursor.execute(SQL, data)
					else:
						print('FLOOD')
					# 	pass

				else: ## TRACK IS TOO OLD OR DOESNT EXIST
					# print('TOO OLD OR DOESNT EXIST')
				
					# ADD TO aircraft_tracks
					# !!!!!!!!!!!!!!!!!!! TO SASHA ADD icao info if not exist -- alone s2cript to serf BD!!!!!!!!11
					
					SQL = '''
					INSERT INTO eco.aircrafts (icao) VALUES (%s) ON CONFLICT (icao) DO NOTHING;
					INSERT INTO eco.aircraft_tracks (icao, first_time, last_time) VALUES (%s, %s, %s) RETURNING track;
					'''

					data = (icao_py,) + (icao_py,) + (time_py,)*2
					cursor.execute(SQL, data)
					last_track=cursor.fetchall()[0][0] ## it's a new track, but need to be ..
				
					# try:
					# ADD TO tracks
					param_to_write=(time_py,)+(last_track,)+(-1,)*8
					new_param_to_write=upd_msg[MSG_NUM](param_to_write)
					# except Exception as err000:
						# os.remove(txt_temp)
						# print(str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) +' '+ str(err000) + '\n')

					SQL = '''
					INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed, distance_1) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s) ON CONFLICT (time_track,track) DO UPDATE SET callsign=EXCLUDED.callsign, altitude=EXCLUDED.altitude, speed=EXCLUDED.speed, angle=EXCLUDED.angle,  latitude=EXCLUDED.latitude, longitude=EXCLUDED.longitude,	vertical_speed= EXCLUDED.vertical_speed, distance_1= EXCLUDED.distance_1;
					UPDATE eco.aircraft_tracks SET (last_time) = (%s) WHERE track=(%s);
					'''
					data = new_param_to_write + (time_py,) + (last_track,)
					cursor.execute(SQL, data)
		
				# connect.commit() ## USE conn.autocommit = True INSTEAD 
		
		## UNCOMMENT
		# print(SQL_FINAL[0:2])
		# cursor.execute(SQL_FINAL)
		end = time.time()
		print('TIME', end - start)
		os.remove(txt_temp)
		connect.commit()
	# #IF SOME ERROR THEN
	# except Exception as err:
	# 	# print('EXCEPTION')
	# 	# cursor.close()
	# 	# connect.close()
	# 	try:
	# 		connect = psycopg2.connect(database='eco_db', user='postgres', host='localhost', password='z5UHwrg8', port=5432)
	# 		cursor = connect.cursor()
	# 	except:
	# 		print('again failed to connect to DB')
	# 	# print to supervisor log
	# 	shutil.move(txt_temp, destination_path+"/"+txt_temp.split('.')[0]+'_'+str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) +'.txt')
	# 	print(str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) +' '+ str(err) + '\n')



	# except Exception as err:
	# 	try:
	# 		connect = psycopg2.connect(database='eco_db', user='postgres', host='localhost', password='z5UHwrg8', port=5432)
	# 		cursor = connect.cursor()
	# 		print('SQL is connected fine','\n')
	# 		print('some error.. with file' + txt_temp)
	# 		shutil.move(txt_temp, destination_path+"/"+str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))+'_'+txt_temp)

	# 	except:
	# 		print('again failed to connect to DB', err)
	# 		# sql_dead=1/

	# 		# if not sql_dead:

	# 		shutil.move(txt_temp, store_path+"/"+str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))+'_'+txt_temp)


	# 	#print to supervisor
	# 	print(str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) +' '+ str(err) + '\n')




## CLOSE BD AFTER EXIT
	time.sleep(0.9)
	print('CLOSE')
cursor.close()
connect.close()
