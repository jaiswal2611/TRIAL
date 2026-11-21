"""Smoke and security checks for the Jaiswal Dental Clinic static website.
Keep this tests folder OUTSIDE public_html. Run:  python3 tests/check_site.py
Needs: python3 and playwright (pip install playwright && playwright install chromium)."""
import http.server, threading, re, os, sys, json
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
if os.path.isdir(os.path.join(ROOT,'public_html')): ROOT=os.path.join(ROOT,'public_html')
HT=open(os.path.join(ROOT,'.htaccess'),encoding='utf-8').read()
HEAD=dict(re.findall(r'Header always set ([\w-]+) "(.*)"',HT))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def end_headers(s):
        for k,v in HEAD.items():
            if k!='Strict-Transport-Security': s.send_header(k,v)
        super().end_headers()
    def log_message(s,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:%d/'%port
PAGES=['index','treatments','studio','explore']; res=[]
def ok(name,cond,detail=''):
    res.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(detail) if detail else ''))
with sync_playwright() as p:
    b=p.chromium.launch()
    for pgname in PAGES:
        pg=b.new_page(viewport={'width':1280,'height':900}); errs=[]; csp=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:csp.append(m.text) if m.type=='error' and ('Content Security Policy' in m.text or 'Refused to' in m.text) else None)
        pg.goto(BASE+pgname+'.html'); pg.wait_for_timeout(700)
        ok(pgname+': no JavaScript errors',not errs,errs[:2])
        ok(pgname+': no CSP violations',not csp,csp[:2])
        ok(pgname+': footer copyright is current','© 2026 Jaiswal Dental Clinic Orthodontic & Implant Centre, Kota. All rights reserved.' in pg.inner_text('footer'))
        hrefs=set(pg.evaluate("Array.from(document.querySelectorAll('a[href]')).map(a=>a.getAttribute('href'))")); ids=set(pg.evaluate("Array.from(document.querySelectorAll('[id]')).map(e=>e.id)"))
        bad=[h for h in hrefs if (h.startswith('#') and len(h)>1 and h[1:] not in ids) or ((h.endswith('.html') or '.html#' in h) and not os.path.exists(os.path.join(ROOT,h.split('#')[0])))]
        ok(pgname+': internal links and anchors resolve',not bad,bad)
        unsafe=pg.evaluate("Array.from(document.querySelectorAll('a[target=_blank]')).filter(a=>!/noopener/.test(a.rel)).length")
        ok(pgname+': external links use rel=noopener',unsafe==0)
        ext=pg.evaluate("Array.from(document.querySelectorAll('script[src],link[rel=stylesheet]')).map(e=>e.src||e.href).filter(u=>!u.startsWith(location.origin)&&!/fonts\\.googleapis\\.com/.test(u))")
        ok(pgname+': no unexpected third-party scripts or styles',not ext,ext)
        pg.click('#lang'); pg.wait_for_timeout(300); pg.click('#lang')
        pg.click('#nd-b'); pg.wait_for_timeout(1800)
        ok(pgname+': Nandi opens',pg.is_visible('#nd-p'))
        pg.fill('#nd-i','my gums are bleeding and wont stop'); pg.press('#nd-i','Enter'); pg.wait_for_timeout(1800)
        last=pg.evaluate("var m=document.querySelectorAll('#nd-m .b');m[m.length-1].innerText")
        ok(pgname+': Nandi escalates bleeding to a call, no diagnosis','99283 00175' in last and '112' in last)
        pg.fill('#nd-i','how much does an implant cost'); pg.press('#nd-i','Enter'); pg.wait_for_timeout(1800)
        last=pg.evaluate("var m=document.querySelectorAll('#nd-m .b');m[m.length-1].innerText")
        ok(pgname+': Nandi does not invent a price',not re.search(r'(₹|Rs\.?|INR)\s?\d',last))
        pg.fill('#nd-i','<img src=x onerror=window.__x=1>'); pg.press('#nd-i','Enter'); pg.wait_for_timeout(1800)
        ok(pgname+': markup typed into Nandi is shown as text, not run',pg.evaluate("window.__x")is None and pg.evaluate("document.querySelectorAll('#nd-m img').length")==0)
        pg.close()
    m=b.new_page(viewport={'width':390,'height':800}); m.goto(BASE+'index.html'); m.wait_for_timeout(600)
    ok('mobile: no horizontal scroll on home',m.evaluate("document.documentElement.scrollWidth")<=392,m.evaluate("document.documentElement.scrollWidth"))
    s=b.new_page(viewport={'width':1280,'height':900}); s.goto(BASE+'studio.html'); s.wait_for_timeout(600); s.click('.stab[data-id="card"]'); s.wait_for_timeout(500)
    n=s.evaluate("document.querySelectorAll('#sp .fg .fb2').length"); ok('studio: 50+ greeting occasions',n>=50,n)
    s.click('.fg [data-f="diwali"]'); s.wait_for_timeout(400); ok('studio: occasion has a description and several messages',s.is_visible('.fdesc') and s.evaluate("document.querySelectorAll('.msgs .mo').length")>=5)
    s.fill('#ft','<b>x</b>'); s.wait_for_timeout(300); ok('studio: typed names are not run as markup',s.evaluate("document.querySelectorAll('#sp b').length")==0 or s.evaluate("Array.from(document.querySelectorAll('#sp b')).every(e=>!e.textContent.includes('x')||e.closest('.fb2'))"))
    t=b.new_page(viewport={'width':1280,'height':900}); t.goto(BASE+'treatments.html'); t.wait_for_timeout(500)
    for k in ['pain','weeks','strong','comfort','week']: t.click('.chip[data-k="%s"]'%k); t.wait_for_timeout(450)
    ok('finder: result links to WhatsApp 99283 00175','wa.me/919928300175' in t.get_attribute('.qres a.btn','href'))
    i=b.new_page(viewport={'width':1280,'height':900}); i.goto(BASE+'index.html?nm=Test&ti=3&wh=Sunday#book'); i.wait_for_timeout(800)
    ok('booking form: Nandi hand-off pre-fills fields',i.input_value('#n')=='Test' and i.evaluate("document.getElementById('t').selectedIndex")==3)
    b.close()
bad=[r for r in res if not r[1]]
secrets=[]
for f in os.listdir(ROOT):
    pth=os.path.join(ROOT,f)
    files=[pth] if os.path.isfile(pth) else [os.path.join(pth,x) for x in os.listdir(pth)] if os.path.isdir(pth) and f=='assets' else []
    for fp in files:
        if fp.endswith(('.html','.js','.xml','.txt')):
            txt=open(fp,encoding='utf-8',errors='ignore').read()
            for pat in [r'AIza[0-9A-Za-z_\-]{30,}',r'sk-[A-Za-z0-9]{20,}',r'(?i)(api[_-]?key|secret|password)\s*[:=]\s*["\'][^"\']{6,}']:
                if re.search(pat,txt): secrets.append((os.path.basename(fp),pat))
ok('no API keys or passwords in any shipped file',not secrets,secrets)
print('\n%d checks, %d passed, %d failed'%(len(res)+0,len(res)-len([r for r in res if not r[1]]),len([r for r in res if not r[1]])))
sys.exit(1 if [r for r in res if not r[1]] else 0)
