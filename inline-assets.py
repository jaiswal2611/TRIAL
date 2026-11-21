"""Rebuild step: copies assets/fx.js, assets/nandi-brain.js and assets/nandi.js into the four pages.
Edit the files in assets/ (for example Nandi's knowledge in nandi-brain.js), then run:  python3 tools/inline-assets.py
The pages keep working on their own, so the floating Nandi button never depends on a separate folder."""
import os,re,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
if os.path.isdir(os.path.join(ROOT,'public_html')): ROOT=os.path.join(ROOT,'public_html')
rd=lambda p:open(os.path.join(ROOT,p),encoding='utf-8').read()
parts=[rd('assets/fx.js'),rd('assets/nandi-brain.js'),rd('assets/nandi.js')]
for p in parts:
    assert '</script' not in p.lower(),'a script file contains a closing script tag'
block='<!--ND-START-->\n'+''.join('<script>\n'+p+'\n</script>\n' for p in parts)+'<!--ND-END-->\n'
for f in ['index','treatments','studio','explore']:
    path=os.path.join(ROOT,f+'.html'); t=open(path,encoding='utf-8').read()
    if '<!--ND-START-->' in t: t=re.sub(r'<!--ND-START-->.*?<!--ND-END-->\n',lambda m:block,t,flags=re.S)
    else:
        t,n=re.subn(r'<script src="assets/fx\.js" defer></script>\n<script src="assets/nandi-brain\.js" defer></script>\n<script src="assets/nandi\.js" defer></script>\n',lambda m:block,t); assert n==1,f
    open(path,'w',encoding='utf-8').write(t); print('updated',f)
