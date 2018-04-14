import math

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
	# e_kv=2*alpha_wgs-alpha_wgs**2
	# N=a_wgs/math.sqrt(1-e_kv*math.math.sin(lat_rad)**2)
	# # pri nt(N)

	# x=(N+alt)*math.cos(lat_rad)*math.cos(lon_rad)
	# y=(N-alt)*math.cos(lat_rad)*math.math.sin(lon_rad)
	# z=( (1-e_kv)*N+alt )*math.math.sin(lat_rad)

	return (x,y,z)


def distance(lon1, lat1, alt1, lon2, lat2, alt2):
	cart_1=convert_to_cartesian(lon1, lat1, alt1)
	cart_2=convert_to_cartesian(lon2, lat2, alt2)


	dist=sum(map(lambda x,y: (x-y)**2, cart_1, cart_2))**0.5
	return dist
	# print()



# home_1=55.873796
# home_2=37.515019
# home_3=0

# point_1=55.8019
# point_2=37.6162
# point_3=10000
# Korea house, lat 37.293873 , lon 126.978899
# lake, lat 37.2888457, lon 126.974846 



home_1=37.293873
home_2=126.978899
home_3=0

point_1=37.2888457
point_2=126.974846 
point_3=0



print(distance(home_1,home_2,home_3,point_1,point_2,point_3))