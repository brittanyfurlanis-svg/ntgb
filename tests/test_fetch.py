import json, os, sys, csv, io, shutil, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import fetch_gbb as f
FIX=os.path.join(os.path.dirname(__file__),'fixtures')
def fake_fetch(name):
    with open(os.path.join(FIX,f.FILES[name]),encoding='utf-8') as fh: return list(csv.DictReader(fh))
f.fetch=fake_fetch
tmp=tempfile.mkdtemp(); f.SITE_DATA=os.path.join(tmp,'site','data'); f.HIST=os.path.join(tmp,'hist')
f.main()
latest=json.load(open(os.path.join(f.SITE_DATA,'latest.json')))
assert '2026-09-06' in latest['actual'] and latest['actual']['2026-09-06']['580030-580001'][1]==26.292, latest['actual']['2026-09-06']['580030-580001']
assert '580050-590001' in latest['actual']['2026-09-06'], 'NGP QLD row must be kept'
assert all(k.split('-')[0] in {str(i) for i in f.FACILITY_IDS} for d in latest['actual'].values() for k in d)
assert '2026-09-12' in latest['forecast']
conn=json.load(open(os.path.join(f.HIST,'connection','2026-08-09.json'))); assert len(conn)==2 and conn[1]['qty']==7.057
assert os.path.exists(os.path.join(f.HIST,'actual','2026-09-06.json'))
print('tests ok; lastUpdated =',latest['lastUpdated'])
