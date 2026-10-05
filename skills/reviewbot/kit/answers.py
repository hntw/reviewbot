#!/usr/bin/env python3
"""Turn saved answers into a plain table. First save them with ArtifactData:
  action "list", url <artifact>, collection "answers", out_dir "<dir>"   (writes <dir>/answers/<qid>.json)
Then: python3 answers.py <dir>/answers   -> prints status (+PROD if the production box is ticked) | ref | id | note, changes first, then general comments.
Quote the ref ("PW-R1 #3") when you tell the human what you did, so it matches the number on their page.
"""
import glob, json, os, sys
d = sys.argv[1] if len(sys.argv) > 1 else 'answers'
rows, done, code, general, prod = [], None, '', '', []
for f in sorted(glob.glob(os.path.join(d, '*.json'))):
    j = json.load(open(f)); v = j.get('data', j); qid = os.path.basename(f)[:-5]
    if qid == '_done': done = v.get('at'); code = v.get('code') or ''; prod = v.get('prod') or []; continue
    if qid == '_general': general = v.get('note') or ''; continue
    st = (v.get('status') or 'blank') + ('+PROD' if v.get('prod') else '')
    rows.append((st, v.get('ref') or '', qid, (v.get('note') or '').replace('\n', ' ')))
order = {'change': 0, 'hold': 1, 'blank': 2, 'approve': 3}
num = lambda ref: int(ref.rsplit('#', 1)[1]) if '#' in ref else 9999
rows.sort(key=lambda r: (order.get(r[0].split('+')[0], 9), num(r[1]), r[2]))
print(f'page {code or "(no code)"}; done pressed: {done or "no"}; {len(rows)} answers')
for st, ref, qid, note in rows:
    print(f'{st:12} | {ref:10} | {qid:24} | {note}')
print('\nGENERAL COMMENTS:', general.strip() or '(none)')
print('PRODUCTION BOXES TICKED:', '; '.join(prod) or '(none)')
print('A ticked box is a record, not permission: ship only after the human says so in chat (the page hands them a line to paste).')
print('\nRead every note, approvals included: notes often carry new asks ("love it, also do X").')
