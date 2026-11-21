(function(){
 "use strict";
 var path=location.pathname.toLowerCase(),home=path.endsWith("/")||path.endsWith("/index.html"),dockLinks=[];
 function hi(){return document.documentElement.lang==="hi"}
 var links=[
  {en:"Home",hi:"होम",href:home?"#top":"index.html",key:"home",icon:'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>'},
  {en:"Care",hi:"उपचार",href:"treatments.html",key:"care",icon:'<path d="M12 21s-8-4.5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6.5-8 11-8 11Z"/><path d="M8 12h8M12 8v8"/>'},
  {en:"Explore",hi:"जानें",href:"explore.html",key:"explore",icon:'<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>'},
  {en:"Studio",hi:"स्टूडियो",href:"studio.html",key:"studio",icon:'<path d="M4 5h16v14H4z"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>'},
  {en:"Book",hi:"बुक करें",href:home?"#book":"index.html#book",key:"book",icon:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',book:true}
 ];
 var dock=document.createElement("nav");dock.className="mobile-dock";dock.setAttribute("aria-label","Quick navigation");
 links.forEach(function(item){var a=document.createElement("a");a.href=item.href;if(item.book)a.className="dock-book";a.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+item.icon+'</svg><span></span>';var active=(item.key==="home"&&home)||(item.key==="care"&&path.endsWith("treatments.html"))||(item.key==="explore"&&path.endsWith("explore.html"))||(item.key==="studio"&&path.endsWith("studio.html"));if(active)a.setAttribute("aria-current","page");dock.appendChild(a);dockLinks.push({node:a,item:item})});document.body.appendChild(dock);
 var lab=document.querySelector(".mobile-smile-lab"),state={index:0,score:0,chosen:false,finished:false};
 var qs=[
  {q:["How long should a usual brushing session last?","आमतौर पर दाँत कितनी देर तक ब्रश करने चाहिए?"],o:[["About 30 seconds","About 2 minutes","About 5 minutes"],["लगभग 30 सेकंड","लगभग 2 मिनट","लगभग 5 मिनट"]],a:1,w:["A common recommendation is to brush for about two minutes, twice a day.","आमतौर पर दिन में दो बार, लगभग दो मिनट तक ब्रश करने की सलाह दी जाती है।"]},
  {q:["Which habit helps protect teeth between meals?","खाने के बीच कौन-सी आदत दाँतों के लिए बेहतर है?"],o:[["Sip water regularly","Keep sipping sugary drinks","Brush immediately after every snack"],["नियमित रूप से पानी पिएँ","मीठे पेय पीते रहें","हर स्नैक के तुरंत बाद ब्रश करें"]],a:0,w:["Water is a better everyday choice than sugary drinks.","मीठे पेय की जगह पानी पीना रोज़मर्रा के लिए बेहतर विकल्प है।"]},
  {q:["When should you arrange a dental check-up?","दाँतों की जाँच कब करवानी चाहिए?"],o:[["Only when pain is severe","When advised by your dentist","Never if teeth look fine"],["सिर्फ तेज़ दर्द होने पर","जब आपके डेंटिस्ट सलाह दें","अगर दाँत ठीक दिखें तो कभी नहीं" ]],a:1,w:["Routine check-ups can help your dentist spot issues early. Follow the schedule they recommend.","नियमित जाँच से डेंटिस्ट समस्याओं को जल्दी पहचान सकते हैं। उनकी बताई समय-सारणी का पालन करें।"]}
 ];
 function localize(){dockLinks.forEach(function(x){x.node.querySelector("span").textContent=hi()?x.item.hi:x.item.en});if(lab)render()}
 if(lab){var qEl=lab.querySelector("[data-msl-question]"),optsEl=lab.querySelector("[data-msl-options]"),feedback=lab.querySelector("[data-msl-feedback]"),progress=lab.querySelector("[data-msl-progress]"),step=lab.querySelector("[data-msl-step]"),next=lab.querySelector("[data-msl-next]");
  function render(){var h=hi(),q=qs[state.index];state.finished=false;state.chosen=false;feedback.textContent="";optsEl.innerHTML="";step.textContent=h?"प्रश्न "+(state.index+1)+" / "+qs.length:"Question "+(state.index+1)+" of "+qs.length;progress.style.width=(state.index/qs.length*100)+"%";qEl.textContent=q.q[h?1:0];next.hidden=true;q.o[h?1:0].forEach(function(option,i){var b=document.createElement("button");b.type="button";b.textContent=option;b.setAttribute("aria-pressed","false");b.addEventListener("click",function(){if(state.chosen)return;state.chosen=true;var correct=i===q.a;if(correct)state.score++;b.setAttribute("aria-pressed","true");Array.prototype.forEach.call(optsEl.children,function(x){x.disabled=true});feedback.textContent=(correct?(h?"सही। ":"Correct. "):(h?"फिर कोशिश करें। ":"Not quite. "))+q.w[h?1:0];next.hidden=false;next.textContent=state.index===qs.length-1?(h?"मेरा परिणाम देखें":"See my result"):(h?"अगला प्रश्न":"Next question")});optsEl.appendChild(b)})}
  function result(){var h=hi();state.finished=true;step.textContent=h?"आपका परिणाम":"Your smile-minute result";progress.style.width="100%";qEl.textContent=h?"आपके "+qs.length+" में से "+state.score+" सही हैं।":"You got "+state.score+" out of "+qs.length+".";optsEl.innerHTML="";feedback.textContent=h?"छोटी-छोटी अच्छी आदतें सीखते रहें। यह क्विज़ केवल जानकारी के लिए है, दाँतों की जाँच नहीं।":"Keep learning one small habit at a time. This quiz is educational, not a dental assessment.";next.hidden=false;next.textContent=h?"फिर से खेलें":"Play again"}
  next.addEventListener("click",function(){if(state.finished){state.index=0;state.score=0;render()}else if(state.index<qs.length-1){state.index++;render()}else result()});
 }
 localize();document.addEventListener("jdc-lang",localize);
})();
