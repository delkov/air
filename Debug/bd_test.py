#!/usr/bin/env python3


import psycopg2
from datetime import datetime, timedelta
from timeit import default_timer as timer

string='MSG,5,0,0,icao2,0,2016/12/01,18:52:46.751,2016/12/01,18:55:54.551,SVR2841,37000,50,14,55.520852,37.540712,1488,,,,,0'

string=string.rstrip().split(',')
# string=string.split(',')
MSG_NUM=int(string[1])
icao_py=string[4]

time_py_1=string[6]
time_py_1=time_py_1.replace('/','-')
time_py_2=string[7]
time_py_2=str(int(float(time_py_2.replace(':',''))))
time_py_2=time_py_2[0:2]+':'+time_py_2[2:4]+':'+time_py_2[4:]
time_py=time_py_1+' '+time_py_2

time_py = datetime.strptime(time_py, "%Y-%m-%d %H:%M:%S")


callsign_py=string[10]
altitude_py=string[11]
speed_py=string[12]
angle_py=string[13]
latitude_py=string[14]
longitude_py=string[15]      
vertical_speed_py=string[16] 



try:
    connect = psycopg2.connect(database='eco_db', user='postgres', host='localhost', password='z5UHwrg8',port=5432)
except:
    print("I am unable to connect to the database")
cursor = connect.cursor()

start=timer()

# for i in range(0,10000):
	# icao=str(i)
	# SQL ='''
	# INSERT INTO eco.aircrafts (icao,engine,reg_number) VALUES (%s,%s,%s) ON CONFLICT (icao) DO UPDATE SET reg_number=EXCLUDED.reg_number;
	# '''
	# # SQL = '''
	# INSERT INTO eco.aircrafts (icao,engine,reg_number) VALUES (%s,%s,%s);
	# '''

type_of_flight=False 
SQL = '''
INSERT INTO eco.aircraft_tracks (track,type_of_flight) VALUES (%s,%s);
'''
data =  (3,) + (type_of_flight, ) 
cursor.execute(SQL, data)



 # UPDATE eco.aircraft_tracks SET (last_time) = (%s) WHERE track=(%s);

# SQL = '''
# INSERT INTO eco.tracks (time_track, track, callsign, altitude, speed, angle, latitude, longitude, vertical_speed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (time_track) DO NOTHING;
# '''
	# data = ('icao1'+str(i)+'ver2','None','1490')
# cursor.execute(SQL, data)
# output=cursor.fetchall() ## it's a new track, but need to be ..
# print(output)
connect.commit()


print(timer()-start)

cursor.close()
connect.close()
