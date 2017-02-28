#!/usr/bin/env python3

import threading    
lock = threading.Lock()

# not locked yet !

my_list = []
item = (2,5)

with lock: # now call __enter__
    my_list.append(item)
    my_list.append( ([4,7,8.9],"ma",5) )

print(my_list)
