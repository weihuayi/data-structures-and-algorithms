"""Audit the standard checker result without treating unknown D019 players as passed.

The shared browser checker reports 'incomplete' for unrecognized custom buttons.
Its *other* checks must pass, and the independent D019 player test must run.
"""
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: check_shared_scope.py <report.json> <checker_exit_code>')
    p=Path(sys.argv[1]);exit_code=int(sys.argv[2]);r=json.loads(p.read_text(encoding='utf-8'))
    if not r.get('decks') or len(r['decks'])!=1:
        raise SystemExit('Expected D019-only standard report')
    all_checks=r['decks'][0].get('checks',[])
    bad_static=[x for x in all_checks if x.get('status')!='pass']
    if bad_static:
        raise SystemExit('Standard static/semantic checks not all passed: '+repr(bad_static[:4]))
    b=r.get('browser',{})
    other=[x for x in b.get('checks',[]) if x.get('status')!='pass']
    if not other and exit_code==0 and b.get('status')=='pass':
        print('PASS: standard D019 browser checks fully supported')
        return
    allowed={(8,'1280x720'),(22,'1280x720'),(8,'1440x900'),(22,'1440x900')}
    actual={(x.get('page'),x.get('viewport')) for x in other}
    if exit_code!=2 or r.get('status')!='incomplete' or b.get('status')!='incomplete':
        raise SystemExit('Unexpected standard checker failure / incomplete result')
    if actual!=allowed or len(other)!=len(allowed) or any(x.get('check')!='interaction-coverage' or x.get('status')!='uncovered' for x in other):
        raise SystemExit('Unexpected uncovered checks: '+repr(other[:8]))
    print('EXPECTED STANDARD LIMITATION: four D019 player controls are uncovered by generic checker; '
          'all other standard checks pass. D019-specific browser validation is mandatory next step.')

if __name__=='__main__':main()