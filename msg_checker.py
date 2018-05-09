#!/usr/bin/env python3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import math
# import udatetime
from datetime import datetime
import shutil
import os
import glob
import time
import gzip
from collections import defaultdict

os.chdir("/home/delkov/Documents/air/sbs_store")

# CUTTED PARAMS
max_altitude=4000 # in meter
max_distance=92000 # 30km
forbidden_MSG=[6,8]

# station GPS coordinate
noise_station_lat=55.873796 # lat
noise_station_lon=37.515019 # lon
noise_station_alt=100 # altitude

def convert_to_cartesian(lat, lon, alt):
	No=int((6+lon)/6)
	Lo=(lon-(3+6*(No-1)))/57.29577951

	lat_rad=lat*math.pi / 180
	lon_rad=lon*math.pi / 180

	Xa = Lo**2 * (109500 - 574700 * math.sin(lat_rad) ** 2 + 863700 * math.sin(lat_rad) ** 4 - 398600 * math.sin(lat_rad) ** 6)
	Xb = Lo**2 * (278194 - 830174 * math.sin(lat_rad) **2 + 572434 * math.sin(lat_rad) ** 4 - 16010 * math.sin(lat_rad) ** 6 + Xa)
	Xc = Lo**2 * (672483.4 - 811219.9 * math.sin(lat_rad) ** 2 + 5420 * math.sin(lat_rad) ** 4 - 10.6 * math.sin(lat_rad) ** 6 + Xb)
	Xd = Lo**2 * (1594561.25 + 5336.535 * math.sin(lat_rad) ** 2 + 26.79 * math.sin(lat_rad) ** 4 + 0.149 * math.sin(lat_rad) ** 6 + Xc)
	
	x=6367558.4968 * lat_rad - math.sin(lat_rad * 2) * (16002.89 + 66.9607 * math.sin(lat_rad) ** 2 + 0.3515 * math.sin(lat_rad) ** 4 - Xd)

	Ya = Lo ** 2 * (79690 - 866190 * math.sin(lat_rad) ** 2 + 1730360 * math.sin(lat_rad) ** 4 - 945460 * math.sin(lat_rad) ** 6)
	Yb = Lo ** 2 * (270806 - 1523417 * math.sin(lat_rad) ** 2 + 1327645 * math.sin(lat_rad) ** 4 - 21701 * math.sin(lat_rad) ** 6 + Ya)
	Yc = Lo ** 2 * (1070204.16 - 2136826.66 * math.sin(lat_rad) ** 2 + 17.98 * math.sin(lat_rad) ** 4 - 11.99 * math.sin(lat_rad) ** 6 + Yb)
	
	y= (5 + 10 * No) * 10 ** 5 + Lo * math.cos(lat_rad) * (6378245 + 21346.1415 * math.sin(lat_rad) ** 2 + 107.159 * math.sin(lat_rad) ** 4 + 0.5977 * math.sin(lat_rad) ** 6 + Yc)
	z=alt

	return (x,y,z)

def calculate_distance(lat1, lon1, alt1, lat2, lon2, alt2):
	cart_1=convert_to_cartesian(lat1, lon1, alt1)
	cart_2=convert_to_cartesian(lat2, lon2, alt2)
	dist=sum(map(lambda x,y: (x-y)**2, cart_1, cart_2))**0.5
	return dist



def main():
	txt_list=sorted(glob.glob('sbs.2*'), key = lambda file: os.path.getctime(file)) # find all txt in the folders
	
	icao_list = defaultdict(list) #making a dict of lists where ID is the key
	for txt_temp in txt_list:
		print(txt_temp)
		with open(txt_temp,'r', encoding='utf-8') as txt:	
			all_strings=txt.readlines()

		bad_string_counter=False		
		## SEPARATE ALL LINES BY ICAO && RESTRORE BAD STRING && REMOVE MSG 6,8 ##
		for string in all_strings:
			string=string.split(',')
			MSG_NUM=int(string[1])
			# if MSG_NUM in forbidden_MSG:
				# print(MSG_NUM)

			if len(string) == 22 and MSG_NUM not in forbidden_MSG:
				# print('FULL STRING', string)
				string=[string[1],string[4],string[6],string[7],string[10],string[11],string[12],string[13],string[14],string[15],string[16]]
				# print('CUTED STRING', string)
				icao_list[string[1]].append(string) #appending the lines by icao
			else:
				bad_string_counter = not bad_string_counter
				if bad_string_counter:
					prev_string=string # first bad line -> second also bad
					# print('1st', prev_string)
				else:
					# print('2nd', string)
					string=prev_string[:-1]+string
					# print(string) # reconstructed string
					if MSG_NUM not in forbidden_MSG:
						string=[string[1],string[4],string[6],string[7],string[10],string[11],string[12],string[13],string[14],string[15],string[16]]
						icao_list[string[1]].append(string) #appending the lines by icao	


		## CHECK ALTITUDE & DISTANCE is FINE
		icao_good_list=[]
		for temp_icao in icao_list: 
			# print('TEMP_ICAO', temp_icao)
			icao_is_fine, icao_altitude_is_fine, icao_distance_is_fine = False, False, False
			for string in icao_list[temp_icao]:
				# check altitude is fine
				if string[5]:
					altitude=int(string[5])*0.3048 # transform from ft to meter
					if altitude<max_altitude: # this is transit aircraft, too high
						icao_altitude_is_fine=True 

				# check distance is fine
				if string[5] and string[8] and string[9]: # 5 is alt, 8 is lat, 9 is lon
					aircraft_lat=float(string[8])
					aircraft_lon=float(string[9])
					aircraft_alt=int(string[5])*0.3048
					distance_to_station=calculate_distance(noise_station_lat, noise_station_lon, noise_station_alt, aircraft_lat, aircraft_lon, aircraft_alt)
					# print('distance', distance_to_station)
					if distance_to_station < max_distance:
						icao_distance_is_fine=True

				if icao_altitude_is_fine and icao_distance_is_fine:
					# print('ICAO IS FINE')
					icao_good_list.append(temp_icao)
					icao_is_fine=True # to break external loop
					break # skip other checking string for this icao


		# STRING: ICAO(1), DATE(2), TIME(3), CALLSIGN(4), ALT(5), GS(6), TRK(7), LAT(8), LON(9), VR(10)  // 0-10

		# make 1 second from multiple us data
		cutted_icao_list = defaultdict(list) #making a dict of lists where ID is the key
		print('ICAO GOOD LIST')
		for temp_icao in icao_good_list:
			# print('TEMP ICAO', temp_icao)
			first_string=True
			icao_amount_strings=len(icao_list[temp_icao])
			# print('HOW MANY STRING FOR THIS ICAO', icao_amount_strings)
			string_counter=0
			for string in icao_list[temp_icao]:
				string_counter+=1
				MSG_NUM=int(string[0])
				year,month,day=map(int,string[2].split('/'))
				str_time=string[3].split('.')[0] # used for calculation
				hour, minute, second = map(int,str_time.split(":"))
				new_time=datetime(year,day,month,hour,minute,second)
				new_param=string[1:4]+['']*7

				if MSG_NUM==1: 
					new_param[3]=string[4] # callsign
			
				elif MSG_NUM==2: 
					new_param[4]=string[5] # alt
					new_param[5]=string[6] # speed
					new_param[6]=string[7] # angle 
					new_param[7]=string[8] # lat
					new_param[8]=string[9] # lon

				elif MSG_NUM==3:
					new_param[4]=string[5] # alt
					new_param[7]=string[8] # lat 
					new_param[8]=string[9] # lon

				elif MSG_NUM==4:
					new_param[5]=string[6] # speed
					new_param[6]=string[7] # angle
					new_param[9]=string[10] # vert

				elif MSG_NUM in [5,7]:
					new_param[4]=string[5] # alt

				if not first_string:
					# print('OLD PARAM', old_param)
					# print('NEW PARAM', new_param)
					if new_time == old_time:
						# print('same time')
						# TAKE LAST PARAM (by time) and add absent from previous msg
						for x in range(7):
							if new_param[x+3] is '' and old_param[x+3] is not '':
								new_param[x+3]=old_param[x+3]
					else:
						# print('diff time')
						old_param[2]=old_str_time # make last time + remove us
						cutted_icao_list[temp_icao].append(old_param)
				else:
					first_string=False

				if string_counter == icao_amount_strings:
					new_param[2]=str_time
					cutted_icao_list[temp_icao].append(new_param)
				
				old_time=new_time
				old_str_time=str_time # just for writing to txt 
				old_param=new_param[:]



		# print('\n', 'BEFORE ALL REDUCTION')
		# for k in dict(icao_list):
		# 	print(k)
		# 	for x in icao_list[k]:
		# 		print(x) 

		# print('\n', 'DISTANCE & ALT')
		# for x in icao_good_list:
		# 	# for x in cutted_icao_list[k]:
		# 	print(x) 

		# print('\n','AFTER 1s && DISTANCE & ALT')
		# for k in dict(cutted_icao_list):
		# 	print(k)
		# 	for x in cutted_icao_list[k]:
		# 		print(x) 


		## CREATE FINAL TXT
		with open('test'+str(txt_temp[:-3]+'_sorted.txt'), 'w+') as new_txt:
			for temp_icao in cutted_icao_list:
				for string in cutted_icao_list[temp_icao]:
					new_txt.write(','.join(string)+',\n')
					# print(string)


# start = time.time()
main()
# end = time.time()

# print('TIME', end-start)