#!/usr/bin/env python3
"""Build a review page from review.json -> index.html (+ img/). Publish index.html as an Artifact with
capabilities {db: {}, user: {}} and files {"img/<name>": "img/<name>"} for each screenshot.

review.json shape (see review.example.json):
  title, eyebrow, lede, status: [[label, "ok"|"wait"]],
  sections: [{id, eyebrow, title, intro?, html?: raw, cards: [card], questions: [{id, text}]}]   # a section with no cards/questions is a plain text panel
  card: {id, title, you_said?, changed?, links?: [[label, url]], shots?: [[file, caption]], ask?: text, html?: raw,
         prod?: "what ships, in plain words", why?: text}   # why = a margin note on why this card exists (training/sample pages); prod adds the explicit "Approved for production" checkbox
  question: {id, text, prod?: "what ships"}
  general comments box (answers/_general) is always on; "general_prompt" overrides its label.
  answered: [{text, answer}]   # decisions already made in chat: shown as static lines, no buttons
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'review.json'))
css = open(os.path.join(HERE, 'kit.css')).read()
js = open(os.path.join(HERE, 'kit.js')).read()

def q(qid, text, prod=None):
    p = f' data-prod="1" data-prod-what="{E(prod)}"' if prod else ''
    return f'<div class="q" data-q="{E(qid)}"{p}><p class="qt">{E(text)}</p></div>'

def card(c):
    out = [f'<div class="step" id="{E(c["id"])}"><h3>{E(c["title"])}</h3>']
    if c.get('you_said'): out.append(f'<p style="color:var(--ink2);font-size:14px"><b>You said:</b> {E(c["you_said"])}</p>')
    if c.get('changed'): out.append(f'<p><b>What changed:</b> {E(c["changed"])}</p>')
    if c.get('html'): out.append(c['html'])
    if c.get('why'): out.append(f'<p class="why"><b>Why this is here:</b> {E(c["why"])}</p>')
    if c.get('links'): out.append('<div class="links">' + ''.join(f'<a href="{E(u)}">{E(l)}</a>' for l, u in c['links']) + '</div>')
    if c.get('shots'):
        out.append('<div class="shots">' + ''.join(
            f'<figure class="shot"><div class="frame"><img src="img/{E(f)}" alt="{E(cap)}" loading="lazy"></div><figcaption>{E(cap)}</figcaption></figure>'
            for f, cap in c['shots']) + '</div>')
    out.append(f'<div class="ask"><b>Your call</b>{q(c["id"], c.get("ask") or "Ship " + c["title"] + "?", c.get("prod"))}</div></div>')
    return ''.join(out)

P = [f'<div class="wrap"><p class="eye">{E(spec.get("eyebrow", ""))}</p><h1>{E(spec["title"])}</h1>']
if spec.get('lede'): P.append(f'<p class="lede">{E(spec["lede"])}</p>')
if spec.get('status'): P.append('<div class="status">' + ''.join(f'<span class="pill {k}">{E(l)}</span>' for l, k in spec['status']) + '</div>')
P.append('<div class="dock" id="dock"><b id="dockCount">Loading your answers...</b><div class="meter" aria-hidden="true"><i id="dockBar"></i></div>'
         '<button type="button" id="doneBtn" disabled>I\'m done, go</button><small id="dockMsg"></small>'
         '<div class="prodline" id="prodLine" hidden><p id="prodText"></p><button type="button" id="prodCopy">Copy</button></div></div>')
P.append('<nav class="toc" aria-label="Sections">' + ''.join(f'<a href="#{E(s["id"])}">{E(s["title"])}</a>' for s in spec['sections']) + '<a href="#general">General comments</a></nav>')
for s in spec['sections']:
    P.append(f'<section class="page" id="{E(s["id"])}"><p class="eye">{E(s.get("eyebrow", ""))}</p><h2>{E(s["title"])}</h2>')
    if s.get('intro'): P.append(f'<p>{E(s["intro"])}</p>')
    if s.get('html'): P.append(s['html'])
    P.extend(card(c) for c in s.get('cards', []))
    if s.get('questions'):
        P.append('<div class="ask"><b>Your calls</b>' + ''.join(q(x['id'], x['text'], x.get('prod')) for x in s['questions']) + '</div>')
    P.append('</section>')
if spec.get('answered'):
    P.append('<section class="page" id="answered"><p class="eye">Already settled</p><h2>Answered in chat</h2>' + ''.join(
        f'<div class="q done"><p class="qt">{E(a["text"])}</p><p class="qdone">Answered: {E(a["answer"])}</p></div>' for a in spec['answered']) + '</section>')
P.append(f'<section class="page" id="general"><p class="eye">Anything else</p><h2>General comments</h2>'
         f'<label class="genlab" for="generalNote">{E(spec.get("general_prompt", "Anything not covered above: big-picture reactions, new ideas, things to stop doing."))}</label>'
         '<textarea id="generalNote" class="gen" disabled placeholder="Write anything here"></textarea><small id="generalSave" class="qsave"></small></section>')
P.append('</div>')

fonts = spec.get('fonts', 'https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,700..900&family=Open+Sans:wght@400;600;700&display=swap')
page = (f'<title>{E(spec["title"])}</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="{fonts}">\n'
        f'<style>\n{css}</style>\n' + '\n'.join(P) + f'\n<script>\n{js}</script>\n')
open('index.html', 'w').write(page)
ids = re.findall(r'data-q="([^"]+)"', page)
dupes = sorted({i for i in ids if ids.count(i) > 1})
missing = [f for s in spec['sections'] for c in s.get('cards', []) for f, _ in c.get('shots', []) if not os.path.exists(os.path.join('img', f))]
prods = len(re.findall(r'data-q="[^"]+" data-prod="1"', page))
print(f'index.html {len(page)} bytes; {len(ids)} questions ({prods} with production checkbox); dupes: {dupes or 0}; missing shots: {missing or 0}')
