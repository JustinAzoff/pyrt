class Ticket:
    def __init__(self, rtclient):
        self.rt = rtclient
    def search(self, query=None,format='',orderby='id'):
        page = self.rt._do('search/ticket', query=query, format=format, orderby=orderby)
        
        data = self.rt.split_res(page)

        if format=='i':
            return data

        if not format:
            ret = []
            for line in data:
                ret.append(line.split(': ', 1))
            return ret
 
    def find_by_status(self, status=[], **kwargs):
        q = ' or '.join("status='%s'" % s for s in status)
        return self.search(query=q, **kwargs)

    def find_open(self, **kwargs):
        """Find any ticket whose status is new, open, or stalled"""
        return self.find_by_status(['new','open','stalled'], **kwargs)

    def find_by_cf(self, mapping, **kwargs):
        crit = []
        t = "'CF.{%s}' = '%s'"
        for k, v in mapping.items():
            crit.append(t % (k,v))

        q = " AND ".join(crit)
        return self.search(q, **kwargs)

    def find_by_ip(self, ip, **kwargs):
        return self.find_by_cf({'ip':ip}, **kwargs)

__all__ = ["Ticket"]
