import socket
import sys
import logging
import time
import datetime
from logging.handlers import TimedRotatingFileHandler
import os
import select

# from timeit import default_timer as timer


#### 100 MSG is 10 K! our buffer s 65k. time is 0.005.. should be checked real time between reading. (not 0.005, actually it 0.0052 since som timme for writing to file) & how many package received.

print('START')
os.chdir("/home/delkov/Documents/air/sbs_store")
log_file = "sbs"
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(log_file, when="s", interval=10, backupCount=0) # write each 10 sec to diff file
logger.addHandler(handler)
timeout_in_seconds=0.005 # how much to wait.. 0 means polling all time, but CPU 100%. let's make 5ms;
buffer_size=32768 # 32K = 32*1024; but it will be 65535 (cutted..)

while True:
	time.sleep(1) # avoid flood before reconnect
	try:
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('localhost', 1489)
		sock.connect(server_address)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)  # Buffer size 8192
		# print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))  # read uffer size 
		# sock.setblocking(0) # set non-blocking
		print('Attempt to connect')
		# counter=0;

		while 1:
			# print(counter)
			# start=timer()
			read_ready = select.select([sock], [], [], timeout_in_seconds)
			if read_ready[0]: # we have what to read
				# counter=0;
				data = sock.recv(buffer_size)
				if not data:
					print('no data')
					break
				# print(data)
				logger.info(data.rstrip().decode('UTF-8'))
			else:
				pass
				# print('TIMEOUT, no data in buffer.. ')
				# counter=counter+1;
			# print(timer()-start)
	except Exception as e:
		print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\n' +str(e))

	# finally:
		# print('PROGAM FINISHED')
		# sock.close()