#!/usr/bin/env python3

import timeit

# start = time.time()
def f():
	MSG='MSG,7,0,0,601100,0,2017/01/05,20:35:07.373,2017/01/05,20:34:17.373,,2588,,,,,,,,,0'
	# for i in range(1,1e5):
	MSG.count(',')

# print(time.time()-start)

print(timeit.repeat("for _ in range(1): f()", "from __main__ import f", number=1))


