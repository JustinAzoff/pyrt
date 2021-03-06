from pyrt import RTClient, and_

import time
TS = time.ctime()
SUBJ = "test " + TS

TEXT ="""This is a sample ticket!

it was created for testing at """ + TS + """
I hope this works :-) :-)
"""

import os
RT_USER = os.getenv("RT_USER")
RT_PASS = os.getenv("RT_PASS")

def test_search_non_exist():
    rt=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    c = rt.ticket.c
    res = rt.ticket.find_open([c.cf.building=="test building", c.cf.jack=='test jack'],format='l')
    assert bool(res) == False

def test_create_ticket():
    c=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    ticket = c.ticket.create(queue='trouble', subject=SUBJ, requestor="justin", Text=TEXT,
            cf={
                'department': 'test department',
                'extension': '1234567',
                'building': 'test building',
                'room':     'test room',
                'jack':     'test jack',
                'mac':      '00:11:22:33:44:55',
            })
    i = ticket.id
    i = int(i)
    assert i > 100

def test_search_ticket_i_just_made():
    rt=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    c = rt.ticket.c
    res = rt.ticket.find_open([c.cf.building=="test building", c.cf.jack=='test jack'],format='l')
    assert bool(res) == True

    ticket = res[0]
    assert ticket['CF-building']   == 'test building'
    assert ticket['CF-jack']       == 'test jack'
    assert ticket['CF-mac']        == '00:11:22:33:44:55'
    assert ticket['CF-department'] == 'test department'
    assert ticket['Subject']       == SUBJ

    yield body_case, ticket
    yield edit_case, ticket

def body_case(tick):
    c=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    id = tick['id']
    t = c.ticket.get(id)
    attachments = t.get_attachment_ids()
    first = attachments[0]
    content = t.get_attachment(first)['Content']
    assert content.rstrip() == TEXT.rstrip()

def edit_case(tick):
    c=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    id = tick['id']
    t = c.ticket.get(id)
    old = t.Subject
    new = old + ' This is my new subject'
    t.Subject = new
    t.save()
    t = c.ticket.get(id)
    assert t.Subject == new
    

def test_close_that_ticket():
    rt=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    c = rt.ticket.c
    res = rt.ticket.find_open([c.cf.building=="test building", c.cf.jack=='test jack'],format='l')
    assert bool(res) == True
    ticket = res[0]
    id = ticket['id']
    t = rt.ticket.get(id)
    print t.edit(status='resolved')

def test_search_non_exist_again():
    rt=RTClient('http://localhost/rt/', RT_USER, RT_PASS)
    c = rt.ticket.c
    res = rt.ticket.find_open([c.cf.building=="test building", c.cf.jack=='test jack'],format='l')
    assert bool(res) == False
