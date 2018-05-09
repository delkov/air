#!/usr/bin/env python3

import socket
import sys
import logging
import time
import udatetime
from logging.handlers import TimedRotatingFileHandler
import os
import select

# from timeit import default_timer as timer


#### 100 MSG is 10 K! our buffer s 65k. time is 0.005.. should be checked real time between reading. (not 0.005, actually it 0.0052 since som timme for writing to file) & how many package received.
## Use pypy CPU 11.3%, MEM 0.4% instead of CPU 15.5%, MEME 0.1% (python 3.5)

print('START')
os.chdir("/home/delkov/Documents/air/sbs_store")
log_file = "sbs"
logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(log_file, when="s", interval=10, backupCount=0) # write each 10 sec to diff file
logger.addHandler(handler)
timeout_in_seconds=0.05 # how much to wait.. 0 means polling all time, but CPU 100%. let's make 5ms; CPU is same, like for 50ms.
  # top -p $(pgrep python3*)  or ps -aux| grep pyth*| sort -nrk 4 | head'
buffer_size=32768# 32768 # 32K = 32*1024; but it will be 65535 (OS is twiced this value, start from 1000. so it is cutted to 65535..)
read_size=buffer_size #buffer_size # play with this param -- CPU LOOKS same for 10k & 32k -> it reads only what we have.. not empty bytes. so keep it like buffer_size

while True:
	time.sleep(5) # avoid flood before reconnect
	try:
		# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('localhost', 1489)
		sock.connect(server_address)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)  # SO_RCVBUF means receive buffer
		# print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))  # read uffer size 
		# sock.setblocking(0) # set non-blocking
		
		print('Attempt to connect')
		# counter=0;

		while True:
			# print(counter)
			# start=timer()
			read_ready = select.select([sock], [], [], timeout_in_seconds) # used like event trigger
			if read_ready[0]: # we have what to read
				data = sock.recv(read_size) 
				if not data:
					print('no data')
					break
				print(data)
				logger.info(data.rstrip().decode('UTF-8'))
			else:
				pass
				# print('TIMEOUT, no data in buffer.. ')
			# print(timer()-start)
	except Exception as e:
		print(str(e) +' '+ udatetime.now_to_string())

	# finally:
		# print('PROGAM FINISHED')
		# sock.close()