#!/bin/bash

filename="/home/delkov/Desktop/my_ip.txt"
ip=$(wget -O - -q icanhazip.com)

if grep -q $ip $filename; then
	true
 else
 	echo $ip > $filename
    echo $ip | mail -s "IP CHANGED" delkovebay@gmail.com
fi

