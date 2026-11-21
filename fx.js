/* Soft sounds and animations for the Jaiswal Dental Clinic website.
   Sounds are quiet, play only after the visitor taps or clicks, and can be muted. */
(function(w,d){
var reduce=w.matchMedia&&w.matchMedia("(prefers-reduced-motion: reduce)").matches;
function hi(){return d.documentElement.lang==="hi"?1:0}
var on=true;try{on=localStorage.getItem("jdc-sound")!=="0"}catch(e){}
var ac=null,master=null,gesture=false,last=0;
function ctx(){if(!ac){var C=w.AudioContext||w.webkitAudioContext;if(!C)return null;try{ac=new C();master=ac.createGain();master.gain.value=.55;master.connect(ac.destination)}catch(e){return null}}if(ac.state==="suspended")ac.resume();return ac}
function tone(f,t0,dur,type,vol,slide){var c=ac,o=c.createOscillator(),g=c.createGain(),T=c.currentTime+t0;o.type=type||"sine";o.frequency.setValueAtTime(f,T);if(slide)o.frequency.exponentialRampToValueAtTime(slide,T+dur);g.gain.setValueAtTime(0.0001,T);g.gain.linearRampToValueAtTime(vol,T+.012);g.gain.exponentialRampToValueAtTime(.0001,T+dur);o.connect(g);g.connect(master);o.start(T);o.stop(T+dur+.05)}
function noise(t0,dur,vol){var c=ac,n=c.sampleRate*dur,b=c.createBuffer(1,n,c.sampleRate),a=b.getChannelData(0),i;for(i=0;i<n;i++)a[i]=(Math.random()*2-1)*(1-i/n);var s=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain(),T=c.currentTime+t0;s.buffer=b;f.type="bandpass";f.frequency.setValueAtTime(600,T);f.frequency.exponentialRampToValueAtTime(3200,T+dur);g.gain.setValueAtTime(vol,T);g.gain.exponentialRampToValueAtTime(.0001,T+dur);s.connect(f);f.connect(g);g.connect(master);s.start(T)}
var S={
tick:function(){tone(1250,0,.05,"sine",.045)},
soft:function(){tone(310,0,.14,"sine",.06,220)},
pop:function(){tone(540,0,.09,"sine",.06);tone(810,.05,.12,"sine",.045)},
success:function(){[523,659,784,1047].forEach(function(f,i){tone(f,i*.09,.4,"triangle",.06)})},
bell:function(){[[523,1],[1046,.5],[1568,.3],[2093,.15]].forEach(function(p){tone(p[0],0,1.5,"sine",.07*p[1])})},
swoosh:function(){noise(0,.22,.05)}};
function play(n){if(!on||!gesture)return;var now=Date.now();if(n==="tick"&&now-last<45)return;last=now;if(!ctx())return;try{(S[n]||S.tick)()}catch(e){}}
["pointerdown","keydown","touchstart"].forEach(function(ev){d.addEventListener(ev,function(){gesture=true},{once:true,passive:true})});
/* sound button */
var sb=d.createElement("button");sb.type="button";sb.id="snd";sb.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 5L6 9H3v6h3l5 4z"/><path class="w1" d="M15.5 8.5a5 5 0 010 7"/><path class="w2" d="M18.5 5.5a9 9 0 010 13"/><path class="x" d="M16 9l5 6M21 9l-5 6"/></svg>';
function sl(){sb.setAttribute("aria-pressed",on);var t=on?(hi()?"आवाज़ बंद करें":"Turn sound off"):(hi()?"आवाज़ चालू करें":"Turn sound on");sb.setAttribute("aria-label",t);sb.title=t}
sb.addEventListener("click",function(){on=!on;try{localStorage.setItem("jdc-sound",on?"1":"0")}catch(e){}sl();gesture=true;if(on)play("success")});
d.body.appendChild(sb);sl();
d.addEventListener("jdc-lang",sl);var lb=d.getElementById("lang");if(lb)lb.addEventListener("click",function(){setTimeout(sl,0)});
/* tick on buttons, and a pitch-following tick on sliders */
d.addEventListener("click",function(e){var t=e.target.closest&&e.target.closest("button,a.btn,a.sbtn,[role=tab],.jbtn");if(!t||t.closest(".nd-p")||t.id==="snd")return;play("tick")});
var rl=0;d.addEventListener("input",function(e){var t=e.target;if(!t||t.type!=="range")return;var n=Date.now();if(n-rl<70)return;rl=n;if(!on||!gesture||!ctx())return;var v=(t.value-t.min)/((t.max-t.min)||1);tone(380+v*520,0,.06,"sine",.035)});
/* confetti and celebration */
function confetti(x,y){if(reduce)return;var cv=d.createElement("canvas"),dpr=Math.min(2,w.devicePixelRatio||1),W=w.innerWidth,H=w.innerHeight;cv.style.cssText="position:fixed;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:95";cv.width=W*dpr;cv.height=H*dpr;cv.setAttribute("aria-hidden","true");d.body.appendChild(cv);var c=cv.getContext("2d");c.scale(dpr,dpr);var cols=["#c5a880","#e3cfa8","#a68963","#faf8f5","#e8478b","#f6c431","#41b36b","#3d7fe0"],ps=[],i;x=x||W/2;y=y||H*.45;for(i=0;i<90;i++)ps.push({x:x,y:y,vx:(Math.random()-.5)*13,vy:-Math.random()*14-3,r:Math.random()*6,w:6+Math.random()*6,h:3+Math.random()*4,c:cols[i%8],s:Math.random()*.3-.15});var t0=performance.now();(function f(t){var e=t-t0;c.clearRect(0,0,W,H);ps.forEach(function(p){p.vy+=.36;p.x+=p.vx;p.y+=p.vy;p.vx*=.99;p.r+=p.s;c.save();c.translate(p.x,p.y);c.rotate(p.r);c.globalAlpha=Math.max(0,1-e/2200);c.fillStyle=p.c;c.fillRect(-p.w/2,-p.h/2,p.w,p.h);c.restore()});if(e<2300)requestAnimationFrame(f);else cv.remove()})(t0)}
function celebrate(){play("success");confetti()}
w.JDCFX={play:play,confetti:confetti,celebrate:celebrate};
/* floating gold sparkles and a soft cursor glow in the dark hero areas */
if(!reduce){d.querySelectorAll(".hero,.t-hero,.s-hero,.e-hero,.t-cta,.s-cta,.e-cta").forEach(function(h){
h.classList.add("fx-host");var cv=d.createElement("canvas");cv.className="fx-cv";cv.setAttribute("aria-hidden","true");h.insertBefore(cv,h.firstChild);var gl=d.createElement("div");gl.className="fx-glow";gl.setAttribute("aria-hidden","true");h.insertBefore(gl,h.firstChild);
var c=cv.getContext("2d"),ps=[],vis=false,W2=1,H2=1,i;
function size(){var r=h.getBoundingClientRect(),dpr=Math.min(1.5,w.devicePixelRatio||1);W2=r.width;H2=r.height;cv.width=W2*dpr;cv.height=H2*dpr;c.setTransform(dpr,0,0,dpr,0,0)}
size();w.addEventListener("resize",size);
for(i=0;i<34;i++)ps.push({x:Math.random()*W2,y:Math.random()*H2,r:1.4+Math.random()*2.6,v:.1+Math.random()*.32,p:Math.random()*6,s:.5+Math.random()*1.1});
function star(x,y,r){c.beginPath();c.moveTo(x,y-r);c.quadraticCurveTo(x+r*.14,y-r*.14,x+r,y);c.quadraticCurveTo(x+r*.14,y+r*.14,x,y+r);c.quadraticCurveTo(x-r*.14,y+r*.14,x-r,y);c.quadraticCurveTo(x-r*.14,y-r*.14,x,y-r);c.fill()}
function f(t){if(!vis)return;c.clearRect(0,0,W2,H2);c.fillStyle="#c5a880";ps.forEach(function(p){p.y-=p.v;p.x+=Math.sin(t/2200+p.p)*.18;if(p.y<-8){p.y=H2+8;p.x=Math.random()*W2}c.globalAlpha=.18+.55*Math.abs(Math.sin(t/1100*p.s+p.p));star(p.x,p.y,p.r*2.2)});requestAnimationFrame(f)}
if("IntersectionObserver" in w)new IntersectionObserver(function(es){var v=es[0].isIntersecting;if(v&&!vis){vis=true;requestAnimationFrame(f)}else vis=v},{threshold:0}).observe(h);
h.addEventListener("pointermove",function(e){if(e.pointerType!=="mouse")return;var r=h.getBoundingClientRect();h.style.setProperty("--mx",(e.clientX-r.left)+"px");h.style.setProperty("--my",(e.clientY-r.top)+"px")})})}
/* smooth page transitions between the site's own pages */
if(!reduce)d.addEventListener("click",function(e){if(e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;var a=e.target.closest&&e.target.closest("a[href]");if(!a||a.target||a.hasAttribute("download"))return;var u;try{u=new URL(a.href,location.href)}catch(x){return}
if(u.origin!==location.origin&&location.protocol!=="file:")return;if(u.protocol!==location.protocol||!/\.html?$|\/$/.test(u.pathname))return;if(u.pathname===location.pathname)return;e.preventDefault();d.body.classList.add("leaving");setTimeout(function(){location.href=a.href},200)});
w.addEventListener("pageshow",function(e){if(e.persisted)d.body.classList.remove("leaving")});
})(window,document);
