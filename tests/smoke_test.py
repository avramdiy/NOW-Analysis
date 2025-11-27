import os, sys
# ensure project root is on sys.path so imports work when running under different python setups
sys.path.insert(0, os.getcwd())
from app import data

def run_smoke():
    app = data.app
    client = app.test_client()
    r = client.get('/')
    print('STATUS', r.status_code)
    txt = r.get_data(as_text=True)
    print('LEN', len(txt))
    print(txt[:400])
    # check that 'OpenInt' was removed and the three period headings appear
    has_openint = 'OpenInt' in txt
    p1 = 'Period 1: 2012-06-29 through 2013-12-31' in txt
    p2 = 'Period 2: 2014-01-01 through 2015-12-31' in txt
    p3 = 'Period 3: 2016-01-01 through 2017-11-10' in txt
    print('HAS_OPENINT', has_openint)
    print('HAS_P1', p1, 'HAS_P2', p2, 'HAS_P3', p3)

if __name__ == '__main__':
    run_smoke()
