(function(){
  // Decision UI for .q[data-q] blocks. Saves answers/<qid> {q, status, note, prod?, at}; general comments -> answers/_general;
  // done button -> answers/_done {at, prod: [...]}. Questions marked data-prod="1" get an explicit "Approved for production"
  // checkbox. After "done", the dock shows one plain line naming every production approval, for the human to paste into
  // chat (agents' permission checks act on the human's own chat words, not on page data).
  var qs=[].slice.call(document.querySelectorAll('.q[data-q]:not(.done)'));
  var els={}, state={}, chain={}, timers={};
  var countEl=document.getElementById('dockCount'), bar=document.getElementById('dockBar'), doneBtn=document.getElementById('doneBtn'), msg=document.getElementById('dockMsg');
  var gen=document.getElementById('generalNote'), genSv=document.getElementById('generalSave'), genTimer=0, genChain=Promise.resolve();
  var prodOut=document.getElementById('prodLine'), prodText=document.getElementById('prodText'), prodCopy=document.getElementById('prodCopy');
  qs.forEach(function(q){
    var id=q.getAttribute('data-q'), isProd=q.getAttribute('data-prod')==='1';
    var bar1=document.createElement('div'); bar1.className='qbar';
    var btns=['approve','change','hold'].map(function(v){var b=document.createElement('button');b.type='button';b.dataset.v=v;b.textContent={approve:'Approve',change:'Change',hold:'Hold'}[v];b.setAttribute('aria-pressed','false');b.disabled=true;bar1.appendChild(b);return b;});
    var sv=document.createElement('span'); sv.className='qsave'; bar1.appendChild(sv);
    q.appendChild(bar1);
    var cb=null;
    if(isProd){
      var lab=document.createElement('label'); lab.className='qprod';
      cb=document.createElement('input'); cb.type='checkbox'; cb.disabled=true;
      var span=document.createElement('span'); span.textContent='Approved for production: '+(q.getAttribute('data-prod-what')||'ship this live');
      lab.appendChild(cb); lab.appendChild(span); q.appendChild(lab);
    }
    var ta=document.createElement('textarea'); ta.id='note-'+id; ta.placeholder='Notes or changes (optional)'; ta.disabled=true; ta.setAttribute('aria-label','Notes for question '+id);
    q.appendChild(ta);
    els[id]={q:q,btns:btns,ta:ta,sv:sv,cb:cb,text:q.querySelector('.qt').textContent,what:q.getAttribute('data-prod-what')||q.querySelector('.qt').textContent};
  });
  function prodList(){
    return qs.map(function(q){return q.getAttribute('data-q');}).filter(function(id){var st=state[id]||{};return els[id].cb&&st.prod&&st.status==='approve';}).map(function(id){return els[id].what;});
  }
  function paint(){
    var n=0; qs.forEach(function(q){var id=q.getAttribute('data-q'),st=state[id]||{},e=els[id];
      e.btns.forEach(function(b){b.setAttribute('aria-pressed',String(st.status===b.dataset.v));});
      if(e.cb) e.cb.checked=!!st.prod;
      if(document.activeElement!==e.ta && typeof st.note==='string') e.ta.value=st.note;
      if(st.status) n++;});
    countEl.textContent=n+' of '+qs.length+' answered';
    bar.style.width=(qs.length?Math.round(100*n/qs.length):0)+'%';
  }
  function save(id){
    var e=els[id], st=state[id]||{};
    var body={q:e.text,status:st.status||'',note:e.ta.value,at:new Date().toISOString()};
    if(e.cb) body.prod=!!st.prod;
    e.sv.textContent='Saving...';
    chain[id]=(chain[id]||Promise.resolve()).then(function(){return window.__db.doc('answers/'+id).set(body);})
      .then(function(){e.sv.textContent='Saved';},function(err){e.sv.textContent=(err&&err.code==='invalid_argument')?'Read-only for you':'Not saved, try again';});
  }
  function saveGeneral(){
    if(!gen) return; genSv.textContent='Saving...';
    var body={note:gen.value,at:new Date().toISOString()};
    genChain=genChain.then(function(){return window.__db.doc('answers/_general').set(body);}).then(function(){genSv.textContent='Saved';},function(){genSv.textContent='Not saved, try again';});
  }
  function showProd(){
    if(!prodOut) return;
    var l=prodList();
    if(!l.length){prodOut.hidden=true;return;}
    prodText.textContent='Approved for production: '+l.join('; ')+'.';
    prodOut.hidden=false;
  }
  function start(db){
    window.__db=db;
    qs.forEach(function(q){var id=q.getAttribute('data-q'),e=els[id];
      e.btns.forEach(function(b){b.disabled=false;b.addEventListener('click',function(){var st=state[id]=Object.assign({},state[id]);st.status=(st.status===b.dataset.v)?'':b.dataset.v;if(st.status!=='approve'&&e.cb)st.prod=false;paint();save(id);if(st.status==='change')e.ta.focus();});});
      if(e.cb){e.cb.disabled=false;e.cb.addEventListener('change',function(){var st=state[id]=Object.assign({},state[id]);st.prod=e.cb.checked;if(st.prod)st.status='approve';paint();save(id);});}
      e.ta.disabled=false;
      e.ta.addEventListener('input',function(){state[id]=Object.assign({},state[id],{note:e.ta.value});e.sv.textContent='Typing...';clearTimeout(timers[id]);timers[id]=setTimeout(function(){save(id);},900);});
      e.ta.addEventListener('blur',function(){if(timers[id]){clearTimeout(timers[id]);timers[id]=0;save(id);}});
    });
    if(gen){gen.disabled=false;
      gen.addEventListener('input',function(){genSv.textContent='Typing...';clearTimeout(genTimer);genTimer=setTimeout(saveGeneral,900);});
      gen.addEventListener('blur',function(){if(genTimer){clearTimeout(genTimer);genTimer=0;saveGeneral();}});
    }
    if(prodCopy) prodCopy.addEventListener('click',function(){
      var t=prodText.textContent;
      function sel(){var r=document.createRange();r.selectNodeContents(prodText);var s=getSelection();s.removeAllRanges();s.addRange(r);prodCopy.textContent='Selected, copy it';}
      try{navigator.clipboard.writeText(t).then(function(){prodCopy.textContent='Copied';},sel);}catch(e){sel();}
    });
    doneBtn.disabled=false;
    doneBtn.addEventListener('click',function(){
      doneBtn.disabled=true; msg.textContent='Sending...';
      if(genTimer){clearTimeout(genTimer);genTimer=0;saveGeneral();}
      var l=prodList();
      db.doc('answers/_done').set({at:new Date().toISOString(),prod:l}).then(function(){
        showProd();
        msg.textContent=l.length?'Sent. To ship, paste the production line below into your Claude chat.':'Sent. Tell Claude "done" in your session and it will pick these up.';
        doneBtn.disabled=false;},function(){msg.textContent='Not sent, try again.';doneBtn.disabled=false;});
    });
    db.collection('answers').onSnapshot(function(snap){
      snap.docs.forEach(function(d){var v=d.data()||{};
        if(d.id==='_general'){if(gen&&document.activeElement!==gen&&typeof v.note==='string')gen.value=v.note;return;}
        if(d.id.charAt(0)==='_')return;
        state[d.id]={status:v.status||'',note:v.note||'',prod:!!v.prod};});
      paint();
    },function(){msg.textContent='Live updates paused; answers still save.';});
    paint();
  }
  if(window.claude&&window.claude.use){
    window.claude.use('db').then(function(db){ if(db) start(db); else {countEl.textContent='Answers can\'t save in this view'; msg.textContent='Open it signed in on claude.ai, or answer in chat.';}});
  } else { countEl.textContent='Answers can\'t save in this view'; msg.textContent='Answer in chat instead.'; }
})();
