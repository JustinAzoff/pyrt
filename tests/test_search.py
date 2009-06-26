from pyrt import RTClient

import time
import os
RT_USER = os.getenv("RT_USER")
RT_PASS = os.getenv("RT_PASS")

def test_search_find_open():
    c=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    res = c.ticket.find_open()
    last = 0
    for id,sub in res:
        print id,sub
        assert int(last) < int(id)
        last = id
