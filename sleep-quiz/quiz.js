/* Dreaming Ages wind-down check. Plain JS, no cookies, no storage, no network calls. Email/copy my results uses mailto + clipboard only. */
(function(){
  var KIT = 'https://kit-dreaming-ages.kit.com/d09dc2b5c3', OF={"r": "Give your racing mind somewhere calm to go", "s": "A steady Monday note for a steadier week", "l": "Quiet stories for light sleepers, once a week", "g": "Keep your good nights coming"};
  var R = window.DA_REF||{}, SB='../sleep-guide/', GB='../sleep-guide/', ST={"r": [6, 8, 10], "s": [1, 2, 5], "l": [7, 3, 10], "g": [1, 2, 5]}; function sup(keys){return (keys||[]).map(function(k){return R[k]?'<sup><a href="'+SB+'#src-'+R[k]+'">'+R[k]+'</a></sup>':'';}).join('');}
  var YT = function(id){return 'https://www.youtube.com/watch?v='+id+'&amp;list=PLOHsZ3iVZVdw';};
  // r = racing mind, s = shifting schedule, l = light sleeper, h = harmony points (0-3, higher is calmer)
  var Q = [
    {k:'Falling asleep', t:'How long does it usually take you to drift off?', o:[
      ['🌙','Just a few minutes',{h:3}],
      ['🕯️','About 15 to 30 minutes',{r:1,h:2}],
      ['⏳','Half an hour to an hour',{r:2,h:1}],
      ['🦉','Often more than an hour',{r:3,h:0}]]},
    {k:'Your mind at night', t:'When your head meets the pillow, your thoughts tend to\u2026', o:[
      ['☁️','Drift off quietly with me',{h:3}],
      ['📋','Run through tomorrow\u2019s plans',{r:1,h:2}],
      ['🔁','Replay the day or worry a little',{r:2,h:1}],
      ['🌀','Spin and won\u2019t switch off',{r:3,h:0}]]},
    {k:'In the night', t:'How often do you wake up and find it hard to get back to sleep?', o:[
      ['😴','Hardly ever',{h:3}],
      ['🌗','A night or two a week',{l:1,h:2}],
      ['🌘','Three or more nights a week',{l:2,h:1}],
      ['🌑','Most nights',{l:3,h:0}]]},
    {k:'What stirs you', t:'If something disturbs your sleep, it\u2019s usually\u2026', o:[
      ['✨','Nothing much, I sleep through',{h:3}],
      ['🔊','Noise, light or a restless partner',{l:2,h:1}],
      ['🌡️','Feeling too warm',{l:2,h:1}],
      ['🌅','Waking too early and staying awake',{l:1,r:1,h:1}]]},
    {k:'Your rhythm', t:'How much does your wake-up time change across the week?', o:[
      ['⏰','Barely, within half an hour',{h:3}],
      ['🗓️','About an hour on weekends',{s:1,h:2}],
      ['🛌','Two hours or more on days off',{s:2,h:1}],
      ['🔀','It\u2019s all over the place, or I work shifts',{s:3,h:0}]]},
    {k:'Your last hour', t:'What does your last hour before bed usually look like?', o:[
      ['📖','A book, a bath, something calm',{h:3}],
      ['📺','TV on the sofa',{s:1,h:2}],
      ['📱','Scrolling my phone in bed',{s:1,r:1,h:1}],
      ['💼','Catching up on work or messages',{r:2,h:0}]]},
    {k:'Afternoon & evening', t:'After lunch, what\u2019s usually in your cup or glass?', o:[
      ['🫖','Water or caffeine-free tea',{h:3}],
      ['☕','One coffee or tea in the afternoon',{l:1,h:2}],
      ['☕☕','Several caffeinated drinks',{l:2,r:1,h:1}],
      ['🍷','A drink or two most evenings',{l:2,h:1}]]},
    {k:'During the day', t:'By mid-afternoon, how do you usually feel?', o:[
      ['🌞','Bright and steady',{h:3}],
      ['🍃','A small dip, then fine',{h:2}],
      ['🥱','Often drowsy',{s:1,h:1}],
      ['😵\u200d💫','I struggle to stay awake',{s:1,h:0,flag:1}]]}
  ];
  var P = {
    r:{name:'The Racing Mind', blurb:'Your body is ready for rest before your thoughts are. A few calm habits may help your mind put the day down.',
       tips:[['Park tomorrow on paper','Spend five minutes writing tomorrow\u2019s to-do list before bed, so your thoughts have somewhere to wait.',['scullin','mayo']],
             ['Breathe slower than you think','In for 4, out for 6, for a few minutes. Or tense and release each muscle group from your toes upward.',['edinger','jerath','cc']],
             ['Don\u2019t wrestle with sleep','If you\u2019ve been awake for what feels like 20 minutes, get up, sit somewhere dim, and come back when sleepy.',['aasm','schutte']]],
       eps:[['raJcWLf-178','The Silk Road','A slow caravan journey with a steady rhythm to follow'],['XAQAb2puQ8Y','Feudal Japan','Quiet temples, tea and evening rain']]},
    s:{name:'The Shifting Schedule', blurb:'Your body clock gets mixed signals when bedtimes and mornings move around. A steadier rhythm may make nights easier.',
       tips:[['Pick one wake-up time','Keep it every day, weekends included. It\u2019s the anchor everything else hangs on.',['aasm','cdc','nhsins']],
             ['Get morning light','Spend some time outside, or by a bright window, soon after you wake.',['blume','mayo']],
             ['Set a \u201cscreens down\u201d reminder','An hour before bed, dim the lamps and put the phone somewhere out of reach.',['cdc','chang','cc']]],
       eps:[['XgBRHvoxty0','Ancient Egypt','Life by the rhythm of the Nile and the sun'],['WoPYw0nuvA0','Ancient Greece','Olive groves, starlight and old philosophers']]},
    l:{name:'The Light Sleeper', blurb:'You can fall asleep, but the night doesn\u2019t always let you stay there. A calmer room and an earlier last coffee may help.',
       tips:[['Make the room cool, dark and quiet','Blackout curtains or a mask, earplugs or a steady soft sound, and a slightly cool room.',['cdc','nhsins','sftemp']],
             ['Move caffeine earlier','Aim for none in the six or so hours before bed, and go easy on evening alcohol, which can break up later sleep.',['drake','nhsins','ebrahim']],
             ['If you wake, skip the clock','Clock-watching tends to wake the mind. Picture a calm scene, or let a quiet story play low.',['schutte','harvey']]],
       eps:[['8GVZ6SVsAnE','The Vikings','Longships, fjords and fireside sagas'],['2_El8CXvGPQ','Samhain','Autumn firelight and old Celtic tales']]},
    g:{name:'The Steady Sleeper', blurb:'Your nights are in good shape. A small tune-up may help you keep them that way when life gets busy.',
       tips:[['Protect your anchor','Keep your wake-up time steady, even after a late night.',['aasm','nhsins']],
             ['Daylight and movement','Time outdoors and regular activity during the day may help your nights.',['cdc','mayo']],
             ['Keep a short wind-down ritual','The same few calm steps in the last hour tell your body that rest is on its way.',['nhsemm','cc']]],
       eps:[['WoPYw0nuvA0','Ancient Greece','Olive groves, starlight and old philosophers'],['8GVZ6SVsAnE','The Vikings','Longships, fjords and fireside sagas']]}
  };
  var BADGE = {
    r:'<circle cx="75" cy="75" r="62" fill="#141d47" stroke="#e3c77d" stroke-opacity=".5"/><path d="M90 40a36 36 0 1 0 22 58 30 30 0 0 1-22-58z" fill="#f1dc9c"/><g fill="none" stroke="#e3c77d" stroke-width="2" stroke-linecap="round" opacity=".85"><path d="M30 52c8-10 22-8 24 2s-10 12-12 4"/><path d="M104 108c6-8 18-6 19 2s-8 9-10 3"/></g><g fill="#fff6d8"><circle cx="112" cy="46" r="2"/><circle cx="40" cy="104" r="1.6"/><circle cx="58" cy="30" r="1.3"/></g>',
    s:'<circle cx="75" cy="75" r="62" fill="#141d47" stroke="#e3c77d" stroke-opacity=".5"/><circle cx="75" cy="75" r="34" fill="none" stroke="#e3c77d" stroke-width="2.5"/><path d="M75 52v23l15 10" stroke="#f1dc9c" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M39 75a36 36 0 0 1 72 0" fill="none" stroke="#f1dc9c" stroke-opacity=".35" stroke-width="10"/><circle cx="38" cy="40" r="9" fill="#f1dc9c"/><path d="M114 32a9 9 0 1 0 5 15 7 7 0 0 1-5-15z" fill="#c6cbe2"/>',
    l:'<circle cx="75" cy="75" r="62" fill="#141d47" stroke="#e3c77d" stroke-opacity=".5"/><path d="M60 100c-2-24 12-48 40-62-8 20-10 42-30 58" fill="none" stroke="#f1dc9c" stroke-width="2.5" stroke-linejoin="round"/><path d="M60 100l40-62M66 86l10 2M72 74l12 0M80 62l11-2" stroke="#e3c77d" stroke-width="1.6" stroke-linecap="round"/><path d="M40 52a14 14 0 1 0 9 24 11 11 0 0 1-9-24z" fill="#f1dc9c"/><g fill="#fff6d8"><circle cx="110" cy="100" r="1.8"/><circle cx="100" cy="116" r="1.3"/></g>',
    g:'<circle cx="75" cy="75" r="62" fill="#141d47" stroke="#e3c77d" stroke-opacity=".5"/><circle cx="75" cy="64" r="26" fill="#f1dc9c"/><circle cx="66" cy="58" r="4" fill="#e3c77d" opacity=".5"/><circle cx="83" cy="72" r="3" fill="#e3c77d" opacity=".45"/><path d="M28 106c14-10 26-10 40 0s26 10 40 0 14-6 14-6" fill="none" stroke="#c6cbe2" stroke-width="2.4" stroke-linecap="round" opacity=".7"/><path d="M36 118c12-8 22-8 34 0s22 8 34 0" fill="none" stroke="#c6cbe2" stroke-width="2" stroke-linecap="round" opacity=".45"/>'
  };
  var root=document.getElementById('quiz'); if(!root) return;
  var ans=[], i=-1, bar=null, io=null, closed=false, cur=null;
  function stickyOff(){ if(bar) bar.classList.remove('on'); if(io){io.disconnect();io=null;} }
  function stickyOn(){ if(closed) return; if(!bar){ bar=document.createElement('div'); bar.className='sticky-offer'; bar.setAttribute('role','region'); bar.setAttribute('aria-label','Free bedtime companion');
      bar.innerHTML='<span><b>Free Bedtime Companion</b> + one quiet email a week</span><a class="btn" href="'+KIT+'" target="_blank" rel="noopener">Get it</a><button class="x" type="button" aria-label="Close">\u00d7</button>';
      bar.querySelector('.x').addEventListener('click',function(){closed=true;stickyOff();}); document.body.appendChild(bar);}
    var card=document.getElementById('offer'); if(!card) return;
    io={f:function(){ var r=card.getBoundingClientRect(); bar.classList.toggle('on', r.bottom<0); }, disconnect:function(){ removeEventListener('scroll',io.f); }};
    addEventListener('scroll',io.f,{passive:true}); io.f(); }
  // Email/copy my results: builds plain text locally. Nothing is sent to us; mailto: only opens the visitor's own email app.
  var SITE='https://dreamingages.com', MAXBODY=1800, MAXURL=2000;
  function plain(s){return String(s).replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/\u2026/g,'...').replace(/[\u2013\u2014]/g,'-');}
  function mailText(best,flag,mode){
    var p=P[best], L=[];
    L.push('Your sleep style: '+p.name,'',p.blurb,'','Three things to try:');
    p.tips.forEach(function(tp,n){ L.push((n+1)+'. '+tp[0]+(mode<2?': '+tp[1]:'')); });
    L.push('','Step-by-step guide: '+SITE+'/sleep-guide/');
    if(mode<1){ var e=p.eps[0]; L.push('A story for tonight: '+e[1]+' '+YT(e[0]).replace('&amp;','&')); }
    if(flag) L.push('','Feeling very sleepy in the day, even after a full night, is worth mentioning to a doctor.');
    L.push('','This is a light self-check, not medical advice.','More help: '+SITE+'/sleep-guide/#help','','Take the check again: '+SITE+'/sleep-quiz/','','Dreaming Ages - slow, calm history to fall asleep to');
    return plain(L.join('\n'));
  }
  var SUBJ='My Dreaming Ages sleep check results';
  function mailto(best,flag){
    for(var mode=0;mode<3;mode++){ var b=mailText(best,flag,mode), u='mailto:?subject='+encodeURIComponent(SUBJ)+'&body='+encodeURIComponent(b.replace(/\n/g,'\r\n'));
      if((b.length<=MAXBODY && u.length<=MAXURL) || mode===2) return {url:u,body:b,mode:mode}; }
  }
  window.DA_MAIL={text:mailText,mailto:mailto,subject:SUBJ,P:P};
  function copyText(t,done){
    function legacy(){ var a=document.createElement('textarea'); a.value=t; a.setAttribute('readonly',''); a.style.cssText='position:fixed;top:0;left:0;opacity:0';
      document.body.appendChild(a); a.select(); a.setSelectionRange(0,t.length); var ok=false; try{ok=document.execCommand('copy');}catch(e){} document.body.removeChild(a); done(ok); }
    if(navigator.clipboard && window.isSecureContext){ navigator.clipboard.writeText(t).then(function(){done(true);},legacy); } else legacy();
  }
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function top(){
    var pct = i<0?0:(i>=Q.length?100:Math.round((i+1)/Q.length*100));
    return '<div class="qtop'+(i<0?' pre':'')+'"><button class="back'+(i>0&&i<Q.length?' show':'')+'" type="button" data-back>\u2039 Back</button><div class="bar" aria-hidden="true"><i style="width:'+pct+'%"></i></div><div class="count">'+(i>=0&&i<Q.length?(i+1)+'/'+Q.length:'')+'</div></div>';
  }
  function swap(html,focusSel){
    var sc=root.querySelector('.screen');
    var go=function(){root.innerHTML=top()+'<div class="screen out">'+html+'</div>';
      var s=root.querySelector('.screen'); requestAnimationFrame(function(){requestAnimationFrame(function(){s.classList.remove('out');});}); setTimeout(function(){s.classList.remove('out');},80);
      var f=root.querySelector(focusSel||'h2,.q-title'); if(f){f.setAttribute('tabindex','-1'); f.focus({preventScroll:true});}
      var bar=root.querySelector('.bar i'); if(bar){var w=bar.style.width; bar.style.width=(i<=0?0:Math.round(i/Q.length*100))+'%'; requestAnimationFrame(function(){bar.style.width=w;});}
      var fill=root.querySelector('.meter .fill'); if(fill){var fw=fill.getAttribute('data-w'); requestAnimationFrame(function(){requestAnimationFrame(function(){fill.style.width=fw+'%';});});}
    };
    if(sc && !matchMedia('(prefers-reduced-motion: reduce)').matches){sc.classList.add('out'); setTimeout(go,300);} else go();
  }
  function intro(){ i=-1; stickyOff();
    swap('<div class="intro"><div class="q-kicker">Your wind-down check</div><h2>Find your sleep style</h2><p>Eight quick taps, no typing, under two minutes. You\u2019ll get a calm little plan and a story to try tonight.</p><div class="chips"><span class="chip">\u23F1 2 minutes</span><span class="chip">\uD83D\uDD12 Nothing is saved</span><span class="chip">\uD83C\uDF19 Just for you</span></div><button class="btn" type="button" data-start>Begin \u2192</button></div>','h2');
  }
  function ask(){ stickyOff();
    var q=Q[i], h='<div class="q-kicker">'+esc(q.k)+'</div><div class="q-title" role="heading" aria-level="2">'+esc(q.t)+'</div><div class="opts" role="list">';
    q.o.forEach(function(o,n){h+='<button type="button" role="listitem" class="opt'+(ans[i]===n?' sel':'')+'" data-a="'+n+'"><span class="em" aria-hidden="true">'+o[0]+'</span><span>'+esc(o[1])+'</span></button>';});
    swap(h+'</div>');
  }
  function result(){
    var t={r:0,s:0,l:0,h:0,flag:0};
    ans.forEach(function(a,n){var w=Q[n].o[a][2]; for(var k in w) t[k]+=w[k];});
    var best='g', max=0; ['r','l','s'].forEach(function(k){ if(t[k]>max){max=t[k];best=k;} });
    if(max<3) best='g';
    var p=P[best], score=Math.round(t.h/(Q.length*3)*100);
    var band = score>=80?'Mostly in tune':score>=55?'A few loose threads':'Plenty of room to soften';
    var h='<div class="res"><svg class="badge" viewBox="0 0 150 150" role="img" aria-label="'+esc(p.name)+' badge">'+BADGE[best]+'</svg>'+
      '<div class="kick">Your sleep style</div><h2>'+esc(p.name)+'</h2><p class="blurb">'+esc(p.blurb)+'</p>'+
      '<div class="meter"><div class="lbl"><span>Evening calm</span><span>'+band+'</span></div><div class="track"><div class="fill" data-w="'+score+'"></div></div></div>'+
      '<div class="sub-h">Three things to try</div><ol class="tips">';
    p.tips.forEach(function(tp,n){var sn=ST[best][n]; h+='<li><span class="n">'+(n+1)+'</span><div><b>'+esc(tp[0])+'</b><span>'+esc(tp[1])+sup(tp[2])+'</span><a class="go" href="'+GB+'#step-'+sn+'">Step '+sn+' in the guide \u2192</a></div></li>';});
    h+='</ol>';
    var mt=mailto(best,t.flag); cur={best:best,flag:t.flag};
    h+='<div class="keep"><div class="keep-row"><a class="btn ghost sm" href="'+esc(mt.url)+'" data-mail>\u2709\uFE0F Email my results to myself</a><button class="btn ghost sm" type="button" data-copy>\uD83D\uDCCB Copy my results</button></div><p class="keep-note" role="status" aria-live="polite">Opens your own email app, with the To line left blank. Nothing is sent to us.</p></div>';
    h+='<div class="offer" id="offer"><div class="ok">Free bedtime companion</div><h3>'+esc(OF[best])+'</h3><p>Join the Dreaming Ages list for slow, calm history to fall asleep to.</p><ul><li><b>A free Bedtime Companion PDF</b> for every episode, with maps, timelines, and the people and places behind each story</li><li><b>One quiet email on Mondays</b> with that week\u2019s new sleep stories</li><li><b>A small history curiosity</b> to read by lamplight</li></ul><a class="btn" href="'+KIT+'" target="_blank" rel="noopener">Send me the free companion \u2192</a><p class="fine">Every episode, companion and email is free, with no paywall or paid plan. One quiet email a week. Unsubscribe with one click. Your quiz answers aren\u2019t sent with your email.</p></div>';
    h+='<div class="sub-h">Stories for tonight</div><div class="eps">';
    p.eps.forEach(function(e){h+='<a class="ep" href="'+YT(e[0])+'" target="_blank" rel="noopener"><span class="play"><svg viewBox="0 0 16 16"><path d="M3 1.5v13l11-6.5z"/></svg></span><span><b>'+esc(e[1])+'</b><small>'+esc(e[2])+'</small></span></a>';});
    h+='</div>';
    if(t.flag) h+='<p class="care">Feeling very sleepy in the day, even after a full night, is worth mentioning to a doctor, especially if someone has noticed loud snoring or pauses in your breathing.'+sup(['nhsosa'])+'</p>';
    h+='<div class="actions"><button class="btn ghost" type="button" data-again>Take it again</button></div>'+
      '<p class="fine">This is a friendly self-check, not a medical test, and it isn\u2019t medical advice. Your answers stay on this page and aren\u2019t saved or sent anywhere, unless you choose to email or copy them yourself. If poor sleep has lasted more than about three months, or is affecting your days, please talk to a doctor.'+sup(['nhsins'])+' Loud snoring, gasping or choking at night can be a sign of sleep apnoea, so it\u2019s worth getting checked.'+sup(['nhsosa'])+' <a href="../sleep-guide/#help">More help</a>.</p></div>';
    i=Q.length; swap(h,'h2'); setTimeout(stickyOn,900);
  }
  root.addEventListener('click',function(e){
    var m=e.target.closest('[data-mail]'); if(m && cur){ m.href=mailto(cur.best,cur.flag).url; var n0=root.querySelector('.keep-note'); if(n0) n0.textContent='Opening your email app\u2026 If nothing happens, use \u201cCopy my results\u201d and paste them into an email or note.'; return; }
    var b=e.target.closest('button'); if(!b) return;
    if(b.hasAttribute('data-copy') && cur){ var note=root.querySelector('.keep-note'), txt='My Dreaming Ages sleep check results\n\n'+mailText(cur.best,cur.flag,0);
      copyText(txt,function(ok){ b.textContent=ok?'\u2714\uFE0F Copied':'\uD83D\uDCCB Copy my results'; if(note) note.textContent=ok?'Copied. Paste it into an email, a note or a message to yourself.':'Couldn\u2019t copy here. Try the email button instead.'; setTimeout(function(){b.textContent='\uD83D\uDCCB Copy my results';},2500); }); return; }
    if(b.hasAttribute('data-start')){i=0;ans=[];ask();}
    else if(b.hasAttribute('data-again')){intro();}
    else if(b.hasAttribute('data-back')){ if(i>0){i--;ask();} }
    else if(b.hasAttribute('data-a')){
      ans[i]=+b.getAttribute('data-a'); b.classList.add('sel');
      setTimeout(function(){ i++; if(i<Q.length) ask(); else result(); },220);
    }
  });
  intro();
  // test hook for screenshots only: ?demo=r|s|l|g&q=N
  var m=location.search.match(/demo=([rslg])/), qm=location.search.match(/[?&]q=(\d)/);
  if(qm){i=+qm[1];ans=[];ask();}
  if(m){var pick={r:[3,3,0,0,0,3,0,1],s:[1,0,0,0,3,2,0,2],l:[1,0,3,1,0,0,3,1],g:[0,0,0,0,0,0,0,1]}[m[1]]; ans=pick; result();}
})();
