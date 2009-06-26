#!/usr/bin/env python 
from pyrt import RTClient, and_
import sys
import getpass

from icalendar import Calendar, Event
import datetime
from dateutil.parser import parse as parse_date

def report(rt):
    tickets = rt.ticket.find_open(format='l')
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '0.1')
    for t in tickets:
        d = t.Due
        if not d:
            d = t.Created
        d = parse_date(d)
        event = Event()
        event.add('summary', t.Subject)
        event.add('dtstart', d)
        event.add('dtend', d+datetime.timedelta(hours=1))
        event.add('dtstamp', d)
        event['uid'] = '%s@rt' % t.id
        cal.add_component(event)

    f = open('example.ics', 'wb')
    f.write(cal.as_string())
    f.close()
        

def main():
    rt = RTClient('https://www/rt/','justin',getpass.getpass())
    report(rt)

if __name__ == "__main__":
    main()
