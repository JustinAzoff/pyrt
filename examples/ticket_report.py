#!/usr/bin/env python 
from pyrt import RTClient, and_
import sys
import getpass
import csv

def report(rt, queue, start_date,outfile):
    tickets = rt.ticket.search(and_([rt.ticket.c.queue==queue, rt.ticket.c.created>=start_date]),format='l')

    f = open(outfile, 'w')
    c = csv.writer(f)
    c.writerow("id subject requestors creator created resolved".split())
    for t in tickets:
        c.writerow((t.id, t.Subject, t.Requestors, t.Creator, t.Created, t.Resolved))
    f.close()

def main():
    q  = sys.argv[1]
    sd = sys.argv[2]
    of = sys.argv[3]
    rt = RTClient('https://www/rt/','justin',getpass.getpass())
    report(rt, q, sd, of)

if __name__ == "__main__":
    main()
