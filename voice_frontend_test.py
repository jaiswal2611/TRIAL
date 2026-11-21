"""Tests Nandi's voice code in a real browser. The ElevenLabs/PHP side is REPLACED by a mock (Playwright route),
so this proves the browser behaviour only: what Nandi sends, how it plays audio, and how it falls back.
It does NOT prove that the PHP file or your ElevenLabs account work. Run:  python3 tests/voice_frontend_test.py"""
import http.server, threading, re, os, sys, json, struct, math
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
if os.path.isdir(os.path.join(ROOT,'public_html')): ROOT=os.path.join(ROOT,'public_html')
HEAD=dict(re.findall(r'Header always set ([\w-]+) "(.*)"',open(os.path.join(ROOT,'.htaccess'),encoding='utf-8').read()))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def end_headers(s):
        for k,v in HEAD.items():
            if k!='Strict-Transport-Security': s.send_header(k,v.replace('; upgrade-insecure-requests',''))
        super().end_headers()
    def log_message(s,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H); BASE='http://127.0.0.1:%d/'%srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
def wav(seconds=3.0,rate=8000):
    n=int(rate*seconds); data=bytes(int(128+60*math.sin(2*math.pi*440*i/rate)) for i in range(n))
    return b'RIFF'+struct.pack('<I',36+n)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,1,rate,rate,1,8)+b'data'+struct.pack('<I',n)+data
AUDIO=wav()
INIT="""
window.__audio=[];const _A=window.Audio;window.Audio=function(src){const a=new _A(src);const rec={played:false,paused:false,ended:false};window.__audio.push(rec);
const p=a.play.bind(a);a.play=function(){rec.played=true;return p()};const pa=a.pause.bind(a);a.pause=function(){rec.paused=true;return pa()};a.addEventListener('ended',()=>rec.ended=true);return a};window.Audio.prototype=_A.prototype;
window.__tts=[];if(window.speechSynthesis){speechSynthesis.speak=function(u){window.__tts.push({lang:u.lang,text:u.text})};speechSynthesis.cancel=function(){}}
"""
res=[]
def ok(n,c,d=''):
    res.append(bool(c)); print(('PASS ' if c else 'FAIL ')+n+((' | '+str(d)) if d else ''))
def setup(b,mode,vw=1280,lang=None,url='index.html'):
    ctx=b.new_context(viewport={'width':vw,'height':800}); pg=ctx.new_page(); calls=[]; pg.add_init_script(INIT)
    def h(route):
        req=route.request
        try: body=json.loads(req.post_data or '{}')
        except Exception: body={}
        calls.append(body)
        if mode=='ok': route.fulfill(status=200,content_type='audio/wav',body=AUDIO)
        elif mode=='notcfg': route.fulfill(status=503,content_type='application/json',body='{"code":"not_configured","error":"x"}')
        elif mode=='rate': route.fulfill(status=429,content_type='application/json',body='{"code":"rate_limited","error":"x"}')
        elif mode=='upstream': route.fulfill(status=502,content_type='application/json',body='{"code":"voice_unavailable","error":"x"}')
        elif mode=='abort': route.abort()
        elif mode=='static404': route.fulfill(status=404,content_type='text/html',body='<h1>Not found</h1>')
        elif mode=='html200': route.fulfill(status=200,content_type='text/html',body='<html>hi</html>')
    pg.route('**/api/nandi-voice.php*',h); pg.goto(url if url.startswith('file:') else BASE+url); pg.wait_for_timeout(500)
    if lang=='hi': pg.click('#lang'); pg.wait_for_timeout(300)
    pg.click('#nd-b'); pg.wait_for_timeout(1500); return ctx,pg,calls
def ask(pg,q,wait=2200):
    pg.fill('#nd-i',q); pg.press('#nd-i','Enter'); pg.wait_for_timeout(wait)
def voice_on(pg):
    if pg.get_attribute('#nd-v','aria-pressed')!='true': pg.click('#nd-v'); pg.wait_for_timeout(200)
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    # 1 English success
    ctx,pg,calls=setup(b,'ok'); voice_on(pg); ask(pg,'what are your timings today?')
    a=pg.evaluate('window.__audio'); ok('English: Nandi asks the server for the English voice',len(calls)>=1 and calls[-1].get('lang')=='en',calls[-1:] )
    ok('English: request carries only lang and text (no voice ID, no key)',set(calls[-1].keys())=={'lang','text'})
    ok('English: audio from the server is played',any(x['played'] for x in a),a)
    ok('English: browser voice is not used when ElevenLabs works',pg.evaluate('window.__tts.length')==0)
    ok('English: sent text is at most 450 characters',all(len(c['text'])<=450 for c in calls))
    ok('English: key never appears in page or storage',not re.search(r'sk_[A-Za-z0-9]{10}|xi-api-key',pg.content()+json.dumps(pg.evaluate('JSON.stringify([localStorage,sessionStorage])'))))
    # close while playing stops audio
    ask(pg,'where is the clinic',1500); pg.click('#nd-x'); pg.wait_for_timeout(300)
    ok('Closing Nandi stops audio that is still playing',any(x['paused'] for x in pg.evaluate('window.__audio')))
    ctx.close()
    # 2 Hindi success
    ctx,pg,calls=setup(b,'ok',lang='hi'); voice_on(pg); ask(pg,'क्लिनिक कहाँ है')
    ok('Hindi: Nandi asks for the Hindi voice',len(calls)>=1 and calls[-1].get('lang')=='hi',calls[-1:] and calls[-1].get('lang'))
    ok('Hindi: the text sent is Hindi (Devanagari)',bool(re.search(r'[\u0900-\u097f]',calls[-1]['text'])) if calls else False)
    ok('Hindi: audio is played',any(x['played'] for x in pg.evaluate('window.__audio')))
    ctx.close()
    # 3 not configured -> fallback, and stops asking
    ctx,pg,calls=setup(b,'notcfg'); voice_on(pg); ask(pg,'what are your timings today?')
    t=pg.evaluate('window.__tts'); ok('Missing key: falls back to the browser voice (en-IN)',len(t)>=1 and t[0]['lang']=='en-IN',t)
    n1=len(calls); ask(pg,'where is the clinic?')
    ok('Missing key: Nandi stops calling the server for the rest of the visit',len(calls)==n1 and len(pg.evaluate('window.__tts'))>=2,(n1,len(calls)))
    ctx.close()
    ctx,pg,calls=setup(b,'notcfg',lang='hi'); voice_on(pg); ask(pg,'क्लिनिक कहाँ है'); t=pg.evaluate('window.__tts')
    ok('Hindi fallback uses hi-IN browser voice',len(t)>=1 and t[0]['lang']=='hi-IN',t); ctx.close()
    # 4 rate limited -> fallback but tries again later
    ctx,pg,calls=setup(b,'rate'); voice_on(pg); ask(pg,'what are your timings today?'); n1=len(calls); ask(pg,'where is the clinic?')
    ok('Rate limit (429): falls back, and tries ElevenLabs again next time',len(pg.evaluate('window.__tts'))>=2 and len(calls)>n1,(n1,len(calls))); ctx.close()
    # 5 upstream failure
    ctx,pg,calls=setup(b,'upstream'); voice_on(pg); ask(pg,'what are your timings today?'); ok('ElevenLabs/server failure (502): falls back to browser voice',len(pg.evaluate('window.__tts'))>=1 and not any(x['played'] for x in pg.evaluate('window.__audio'))); ctx.close()
    # 6 network failure
    ctx,pg,calls=setup(b,'abort'); voice_on(pg); ask(pg,'what are your timings today?'); ok('Network failure: falls back to browser voice',len(pg.evaluate('window.__tts'))>=1); ctx.close()
    # 7 static host with no PHP (404) and odd 200 HTML
    ctx,pg,calls=setup(b,'static404'); voice_on(pg); ask(pg,'what are your timings today?'); n1=len(calls); ask(pg,'where is the clinic?')
    ok('Static hosting without PHP (404): browser voice, and no repeated requests',len(pg.evaluate('window.__tts'))>=2 and len(calls)==n1); ctx.close()
    ctx,pg,calls=setup(b,'html200'); voice_on(pg); ask(pg,'what are your timings today?'); ok('A non-audio 200 reply is not played; falls back',len(pg.evaluate('window.__tts'))>=1 and not any(x['played'] for x in pg.evaluate('window.__audio'))); ctx.close()
    # 8 voice off -> no calls
    ctx,pg,calls=setup(b,'ok'); ask(pg,'what are your timings today?'); ok('Voice switched off: no server calls, no audio',len(calls)==0 and not pg.evaluate('window.__audio') and not pg.evaluate('window.__tts')); ctx.close()
    # 9 mobile
    ctx,pg,calls=setup(b,'ok',vw=390); voice_on(pg); ask(pg,'what are your timings today?'); ok('Mobile (390px wide): ElevenLabs audio plays',any(x['played'] for x in pg.evaluate('window.__audio'))); ctx.close()
    # 10 file:// has no PHP
    ctx,pg,calls=setup(b,'ok',url='file://'+os.path.join(ROOT,'index.html')); voice_on(pg); ask(pg,'what are your timings today?'); ok('Opened as a file (no PHP): uses browser voice, makes no server calls',len(calls)==0 and len(pg.evaluate('window.__tts'))>=1); ctx.close()
    # 11 every page has the voice code and no JS errors with CSP
    for pgname in ['index','treatments','studio','explore']:
        ctx=b.new_context(); q=ctx.new_page(); errs=[]; q.on('pageerror',lambda e:errs.append(str(e))); q.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'Content Security' in m.text else None)
        q.goto(BASE+pgname+'.html'); q.wait_for_timeout(500); ok(pgname+': no JavaScript or CSP errors',not errs,errs[:1]); ctx.close()
    b.close()
print('\n%d checks, %d passed, %d failed'%(len(res),sum(res),len(res)-sum(res))); sys.exit(0 if all(res) else 1)
