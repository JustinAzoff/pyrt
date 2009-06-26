#!/usr/bin/env python 
from pyrt import RTClient, and_, or_
import sys
import getpass

import datetime
from dateutil.parser import parse as parse_date
import cPickle

def num_open(rt, day):
    o = rt.ticket.search(and_([
        rt.ticket.c.Created < day,
        or_([rt.ticket.c.Status!='resolved', rt.ticket.c.Resolved > day])
        ]))
        
    return len(o)

def report(rt):
    now = datetime.datetime.now()
    start = datetime.datetime(2007, 1, 1, 12, 0)

    day = datetime.timedelta(days=1)
    cur = start


    while cur < now:
        print cur, num_open(rt, cur)
        cur += day

def main():
    rt = RTClient('https://www/rt/','justin',getpass.getpass())
    report(rt)

if __name__ == "__main__":
    main()
