import urllib, urllib2, urlparse
import simplejson

import cookielib
REST_VERSION = "1.0"

from ticket import *

class RTClient:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

        self.login()

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
        res  = self.opener.open(url, data).read()

        return res

    def split_res(self, res):
        ret = res.split("\n")
        return '\n'.join(ret[2:])

    def login(self):
        self._do('/') #need this to start the session first? O.o
        return self._do('/', user=self.username, pass_=self.password)

    def _get_ticket(self):
        return Ticket(self)
    ticket = property(_get_ticket)
