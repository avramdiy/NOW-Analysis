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

if __name__ == '__main__':
    run_smoke()
