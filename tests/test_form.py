from pyrt import forms

def check_dict(d, exp):
    d = d.copy()
    for k,v in exp.items():
        assert k in d
        assert k==k and  d[k]==v
        del d[k]
    assert d == {}

def do_test_generate_and_parse(idict,exp=None):
    if not exp:
        exp = idict
    out = forms.generate(idict)
    output = forms.parse(out.split('\n'))
    check_dict(output, exp)

def test_generate_and_parse():
    tests = []
    tests.append({'name': None})
    tests.append([{'name': ''},{'name':None}])
    tests.append({'name': 'justin'})
    tests.append({'name': 'justin', 'text':'''hi there
this is a lot of text
    with an indent
there'''})


    for x in tests:
        if hasattr(x, 'keys'):
            yield do_test_generate_and_parse, x
        else:
            yield do_test_generate_and_parse, x[0],x[1]
