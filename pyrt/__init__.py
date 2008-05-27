# pyrt/__init__.py
# Copyright (C) 2007, 2008 Justin Azoff JAzoff@uamail.albany.edu
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

"""
pyrt, a client for the Request Tracker REST interface

>>> from pyrt import RTClient, and_
>>> rt=RTClient('https://www/rt','justin','xxx')
>>> for t in c.ticket.find_by_status(['stalled']): print t
... 
#searches for ('status' = 'stalled')
['974',  'blah blah blah']
['1058', 'blah blah blah']
['1552', 'blah blah blah']
['1588', 'blah blah blah']
['1622', 'blah blah blah']
['1631', 'blah blah blah']

>>> search = and_([rt.ticket.c.created > '2008-02-20',rt.ticket.c.owner=='justin'])
>>> tickets = rt.ticket.search(search)
>>> for t in tickets:
...    print t
... 
#searches for ('created' > '2008-02-20' AND 'owner' = 'justin')
['1644', 'blah blah']

>>> tickets = rt.ticket.search(search, format='l')
>>> t = tickets[0]
>>> print t
[pyrt.ticket 1644]
>>> print t.Created
Tue Feb 26 12:49:34 2008
>>> print t.Resolved
Tue Feb 26 13:26:29 2008
>>> print t._fields['Resolved']
Tue Feb 26 13:26:29 2008

>>> for t in rt.ticket.search(rt.ticket.c.cf.building=='Biology'):
...     print t
... 
#searches for 'CF.{building}' = 'Biology'
['292', 'blah']
['560', 'blah']
['943', 'blah']
"""



import urllib, urllib2, urlparse
import os

import cookielib
REST_VERSION = "1.0"

from ticket import *

class RTError(Exception):
    pass

COOKIEFILE = os.path.expanduser('~/.rt_cookies.txt')

class RTClient:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        
        self.cj = cookielib.LWPCookieJar(COOKIEFILE)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
    
        try:
            self.cj.load(ignore_discard=True, ignore_expires=True)
        except IOError:
            pass

        self.logging_in = False
        #self.login()

    def _make_url(self, action):
        return "%s/REST/%s/%s" % (self.url, REST_VERSION, action)

    def _do(self, action, data=None, **args):
        """Call url with args as query args and return the result"""

        for k,v in args.items():
            if k.endswith("_"):
                del args[k]
                args[k[:-1]]=v
        
        url  = self._make_url(action)
        if not data:
            data = urllib.urlencode(args)
        raw = self.opener.open(url, data).read()
        res = self.split_res(raw)

        if 'Credentials required' in raw:
            if not self.logging_in:
                self.logging_in = True
                self.login()
                return self._do(action, data=data, **args)
            raise RTError("Credentials required")
        if 'Your username or password is incorrect' in res:
            raise RTError("Your username or password is incorrect")
        if 'Invalid query' in res:
            raise RTError("Invalid query %s" % args)
        #if 'does not exist.' in res:
        #    raise RTError("Ticket does not exist")
        #if 'You are not allowed to display ticket ' in res:
        #    raise RTError("You are not allowed to display this ticket")
        #print res
        out = forms.parse(res)
        #if 'rt_comments' in out[0]:
        #    raise RTError(''.join(out[0]['rt_comments']))
        return out

    def split_res(self, res):
        ret = res.split("\n")
        return '\n'.join(ret[2:])

    def login(self):
        #self._do('/') #need this to start the session first? O.o
        res = self._do('/search/ticket', query='id=1', user=self.username, pass_=self.password)
        self.cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)
        return res

    def _get_ticket(self):
        return Ticket(self)
    ticket = property(_get_ticket)
