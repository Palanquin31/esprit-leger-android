from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.10 — calendar/readability + intelligence/notification reliability patch.
# Preserve validated V8.6 theme, V8.7 day glance, V8.8 backup/modals and V8.9 contrast.

# ---------------------------------------------------------------------------
# 1) Notification settings: never rewrite a user's choice from DOM defaults.
# ---------------------------------------------------------------------------
old=''' loadNotificationSettings();\n saveNotificationSettings();'''
if old not in html:
    raise SystemExit('notification render load/save pair not found')
html=html.replace(old,''' loadNotificationSettings();\n if(typeof syncNotifFrequencyUiV810==='function')syncNotifFrequencyUiV810();''',1)

# Add a small native-status line without changing the existing card geometry.
anchor='<p class="note">Moyenne visée : 0 à 2 notifications par jour, maximum 4.</p>'
if anchor not in html:
    raise SystemExit('notification status anchor not found')
html=html.replace(anchor,anchor+'\n  <p class="note" id="notifAndroidStatusV810">État Android : vérification…</p>',1)

css=r'''
<style id="v810-calendar-intelligence-style">
/* --- Week view: mobile-first readable vertical agenda. --- */
.week-agenda-v810{display:flex;flex-direction:column;gap:10px;margin-top:4px;}
.week-day-card-v810{background:#fff;border:1px solid #eee6f4;border-radius:20px;padding:12px;box-shadow:0 6px 16px rgba(60,42,80,.055);}
.week-day-card-v810.is-today{border-color:rgba(185,155,255,.68);box-shadow:0 0 0 2px rgba(185,155,255,.10),0 8px 18px rgba(60,42,80,.07);}
.week-day-head-v810{display:flex;align-items:center;gap:10px;margin-bottom:9px;}
.week-day-date-v810{width:45px;min-width:45px;height:45px;border-radius:14px;background:#f3edf8;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:950;line-height:1.02;color:#44394f;}
.week-day-date-v810 small{font-size:10px;text-transform:uppercase;color:#85798f;font-weight:900;}
.week-day-title-v810{min-width:0;flex:1;}
.week-day-title-v810 b{display:block;font-size:15px;}
.week-day-title-v810 span{display:block;font-size:11px;color:var(--muted);font-weight:750;margin-top:2px;}
.week-day-open-v810{border:0;background:transparent;color:#7f6797;font-weight:900;font-size:12px;padding:7px 4px;}
.week-event-list-v810{display:flex;flex-direction:column;gap:7px;}
.week-event-row-v810{width:100%;display:grid;grid-template-columns:60px 5px minmax(0,1fr) 12px;gap:9px;align-items:center;border:1px solid #eee8f2;border-radius:14px;padding:9px 9px;background:rgba(255,255,255,.74);text-align:left;color:var(--ink);}
.week-event-time-v810{font-size:11px;font-weight:950;line-height:1.3;color:#62586c;}
.week-event-accent-v810{width:5px;height:34px;border-radius:999px;}
.week-event-main-v810{min-width:0;}
.week-event-main-v810 b{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px;}
.week-event-main-v810 span{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;color:var(--muted);font-weight:750;margin-top:2px;}
.week-member-dot-v810{width:10px;height:10px;border-radius:50%;box-shadow:0 0 0 2px rgba(0,0,0,.05);}
.week-empty-v810{font-size:12px;color:var(--muted);padding:4px 2px 2px;font-weight:750;}
body.crepuscule .week-day-card-v810{background:#2a2530!important;border-color:rgba(255,255,255,.09)!important;box-shadow:0 8px 18px rgba(0,0,0,.12)!important;}
body.crepuscule .week-day-card-v810.is-today{border-color:rgba(174,148,210,.55)!important;box-shadow:0 0 0 2px rgba(174,148,210,.10),0 8px 18px rgba(0,0,0,.14)!important;}
body.crepuscule .week-day-date-v810{background:#39323f!important;color:#f1edf3!important;}
body.crepuscule .week-day-date-v810 small,body.crepuscule .week-day-title-v810 span,body.crepuscule .week-event-main-v810 span,body.crepuscule .week-empty-v810{color:#c6bec9!important;}
body.crepuscule .week-day-open-v810{color:#c7b6da!important;}
body.crepuscule .week-event-row-v810{background:#302a37!important;border-color:rgba(255,255,255,.08)!important;color:#f1edf3!important;}
body.crepuscule .week-event-time-v810{color:#ddd5e2!important;}

/* When expanded, the collapse control remains reachable while scrolling old hours. */
.past-hours-sticky-v810{position:sticky;top:8px;z-index:4;backdrop-filter:blur(10px);}

/* Typical week: the three broad periods stay compact. */
.week-day-body .slot .slot-title{font-size:14px;font-weight:950;}
</style>
'''
if 'id="v810-calendar-intelligence-style"' not in html:
    html += css

js=r'''
<script id="v810-calendar-intelligence-script">
(function(){
  /* ---------------- Notification settings persistence ---------------- */
  const NOTIF_IDS_V810=['notifAppointments','notifTasks','notifBestMoment','notifBusyDay','notifSuccess'];
  window.syncNotifFrequencyUiV810=function(){
    const value=document.getElementById('notifFrequency')?.value||'Équilibré';
    document.querySelectorAll('.freq-btn').forEach(b=>b.classList.toggle('active',b.dataset.freq===value));
  };
  function persistNotificationsV810(){
    try{if(typeof saveNotificationSettings==='function')saveNotificationSettings();}catch(e){console.warn('notification save V8.10',e);}
    setTimeout(()=>{try{if(typeof syncNativeNotificationsV66==='function')syncNativeNotificationsV66();}catch(e){}},40);
  }
  document.addEventListener('change',e=>{
    if(NOTIF_IDS_V810.includes(e.target?.id)){persistNotificationsV810();}
  });
  const previousSetNotifFrequencyV810=window.setNotifFrequency;
  window.setNotifFrequency=function(value){
    if(typeof previousSetNotifFrequencyV810==='function')previousSetNotifFrequencyV810(value);
    window.syncNotifFrequencyUiV810();persistNotificationsV810();
  };
  if(!localStorage.getItem('esprit_notifications'))persistNotificationsV810();
  else {try{loadNotificationSettings();window.syncNotifFrequencyUiV810();}catch(e){}}

  window.refreshNativeNotificationStatusV810=function(){
    const el=document.getElementById('notifAndroidStatusV810');if(!el)return;
    try{
      if(window.AndroidNotifications&&typeof AndroidNotifications.status==='function'){
        const raw=AndroidNotifications.status();const d=JSON.parse(raw||'{}');
        if(d.enabled&&d.channelEnabled)el.textContent='✅ Notifications Android autorisées.';
        else if(!d.enabled)el.textContent='⚠️ Notifications désactivées dans Android : les rappels ne pourront pas apparaître.';
        else el.textContent='⚠️ Canal de rappels désactivé dans Android.';
        return;
      }
    }catch(e){}
    el.textContent='ℹ️ État Android vérifié lors de l’utilisation de l’application.';
  };
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)setTimeout(window.refreshNativeNotificationStatusV810,100);});
  setTimeout(window.refreshNativeNotificationStatusV810,700);

  /* ---------------- Day-view folding hardening ---------------- */
  function asDateV810(v){const d=v instanceof Date?v:new Date(v);return isNaN(d)?new Date():d;}
  function sameLocalDayV810(a,b){a=asDateV810(a);b=asDateV810(b);return a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();}
  function hhmmV810(d){return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');}
  function eventStyleV810(e){const bg=eventUserColor(e),fg=typeof contrastTextV89==='function'?contrastTextV89(bg):'#111';return `background:${bg};--task-color:${eventTaskColor(e)};color:${fg}!important`;}
  if(typeof window.pastHoursExpandedV87!=='boolean')window.pastHoursExpandedV87=false;
  window.renderDay=function(){
    const now=new Date(),sel=asDateV810(selectedDate),today=sameLocalDayV810(sel,now),allEvents=eventsForDate(sel)||[];
    const currentHour=now.getHours(),contextualStart=today?Math.max(0,currentHour-1):0;
    const expanded=!!window.pastHoursExpandedV87,startHour=(today&&!expanded)?contextualStart:0;let out='';
    if(today&&contextualStart>0&&!expanded){
      const hiddenCount=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)<contextualStart).length;
      const lastHidden=contextualStart-1,range=lastHidden===0?'00h':`00h–${String(lastHidden).padStart(2,'0')}h`;
      out+=`<button type="button" class="past-hours-toggle-v87" onclick="togglePastHoursV87(event)"><b>Plus tôt aujourd’hui · ${range}</b><span>${hiddenCount?hiddenCount+' activité'+(hiddenCount>1?'s':'')+' · ':''}Afficher ▾</span></button>`;
    }
    if(today&&contextualStart>0&&expanded){
      out+=`<button type="button" class="past-hours-toggle-v87 past-hours-sticky-v810" onclick="togglePastHoursV87(event)"><b>⌃ Replier les heures passées</b><span>Retour à l’heure actuelle</span></button>`;
    }
    for(let h=startHour;h<24;h++){
      const hs=String(h).padStart(2,'0')+':00',ev=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)===h),current=today&&h===currentHour;
      const marker=current?`<div class="now-marker-v87">Maintenant · ${hhmmV810(now)}</div>`:'';
      out+=`<div class="hour-row ${current?'current-hour-v87':''}"><div class="hour">${hs}</div><div class="hour-content">${marker}${ev.map(e=>`<div class="event-pill v89-auto-contrast" style="${eventStyleV810(e)}" onclick='openDetails(${JSON.stringify(e)})'>${emoji(e.type)} ${e.title}<div class="event-meta">${e.start}-${e.end} · ${e.person}</div></div>`).join('')}</div></div>`;
    }
    calendar.innerHTML=out;
  };

  /* ---------------- Mobile-first week agenda ---------------- */
  function minsV810(t){const p=String(t||'00:00').split(':').map(Number);return (p[0]||0)*60+(p[1]||0);}
  function durationV810(e){let d=minsV810(e?.end)-minsV810(e?.start);if(d<0)d+=1440;return Math.max(0,d);}
  function fmtDurationV810(mins){const h=Math.floor(mins/60),m=mins%60;return h?(m?`${h}h${String(m).padStart(2,'0')}`:`${h}h`):`${m} min`;}
  window.openWeekDayV810=function(offset){
    selectedDate=addDays(weekStart(selectedDate),Number(offset)||0);view='jour';
    document.querySelectorAll('.tabs .tab').forEach(b=>b.classList.toggle('active',(b.textContent||'').trim()==='Journée'));
    if(typeof render==='function')render();
  };
  window.renderWeek=function(){
    planningTitle.textContent='Semaine';const startW=weekStart(selectedDate),now=new Date();
    const cards=days.map((name,i)=>{
      const date=addDays(startW,i),ev=(eventsForDate(date)||[]).slice().sort((a,b)=>minsV810(a.start)-minsV810(b.start));
      const total=ev.reduce((s,e)=>s+durationV810(e),0),today=sameLocalDayV810(date,now),dow=name.slice(0,3),dayNum=date.getDate();
      const summary=ev.length?`${ev.length} activité${ev.length>1?'s':''} · ${fmtDurationV810(total)}`:'Journée libre';
      const rows=ev.map(e=>`<button type="button" class="week-event-row-v810" onclick='openDetails(${JSON.stringify(e)})'><span class="week-event-time-v810">${e.start}<br>${e.end}</span><span class="week-event-accent-v810" style="background:${eventTaskColor(e)}"></span><span class="week-event-main-v810"><b>${emoji(e.type)} ${e.title}</b><span>${e.person} · ${e.type}</span></span><span class="week-member-dot-v810" style="background:${eventUserColor(e)}"></span></button>`).join('');
      return `<section class="week-day-card-v810 ${today?'is-today':''}"><div class="week-day-head-v810"><div class="week-day-date-v810"><small>${dow}</small>${dayNum}</div><div class="week-day-title-v810"><b>${name}${today?' · Aujourd’hui':''}</b><span>${summary}</span></div><button type="button" class="week-day-open-v810" onclick="openWeekDayV810(${i})">Voir ›</button></div><div class="week-event-list-v810">${rows||'<div class="week-empty-v810">Aucune activité planifiée.</div>'}</div></section>`;
    }).join('');
    calendar.innerHTML=`<div class="week-agenda-v810">${cards}</div>`;
  };

  /* ---------------- Typical week: Matin / Après-midi / Nuit only ---------------- */
  const WEEK_SLOTS_V810=[['matin','Matin'],['apresmidi','Après-midi'],['nuit','Nuit']];
  function safeIdV810(s){return String(s).replace(/[^a-zA-Z0-9_-]/g,'_');}
  function personOptionsV810(selected){const names=Object.keys(people);if(!names.length)names.push(firstUserName());return names.map(n=>`<option value="${n}" ${n===selected?'selected':''}>${n}</option>`).join('');}
  function typeOptionsV810(selected){const ts=['Travail','École','Rendez-vous','Sport','Courses','Repas','Temps pour soi','Tâche'];return ts.map(t=>`<option value="${t}" ${t===selected?'selected':''}>${emoji(t)} ${t}</option>`).join('');}
  function defaultsV810(k){return k==='matin'?['08:00','12:00']:k==='apresmidi'?['12:00','20:00']:['21:00','23:59'];}
  function mergedLegacySlotV810(daySlots,key,label){
    if(key!=='apresmidi')return daySlots.find(x=>x.label===label)||null;
    const c=daySlots.filter(x=>['Après-midi','Apres-midi','Midi','Soir'].includes(x.label));if(!c.length)return null;
    const starts=c.map(x=>x.start||'12:00').sort(),ends=c.map(x=>x.end||'20:00').sort();
    return {...c[0],label:'Après-midi',start:starts[0],end:ends[ends.length-1]};
  }
  window.updateWeekDaySummaryV82=function(day){
    const count=WEEK_SLOTS_V810.filter(([key])=>document.getElementById(`active_${day}_${key}`)?.checked).length;
    const rest=document.getElementById('rest_'+day)?.checked;const el=document.getElementById('weeksummary_'+safeIdV810(day));
    if(el)el.textContent=rest?'Repos':count?`${count} créneau${count>1?'x':''}`:'À compléter';
  };
  window.openWeekTemplate=function(editMode=false){
    if(!editMode){editingWeekTemplateId=null;tempSelectedWeeks=[];if(document.getElementById('weekName'))weekName.value='Semaine type';if(document.getElementById('weekCycle'))weekCycle.value='Semaine A';}
    const wf=document.getElementById('weekForms');if(!wf)return alert('Formulaire semaine introuvable.');
    wf.innerHTML=days.map(d=>`<div class="week-day-accordion" id="weekday_${safeIdV810(d)}"><button type="button" class="week-day-head" onclick="toggleWeekDayV82('${d}')"><span>${d}</span><span class="week-day-summary" id="weeksummary_${safeIdV810(d)}">À compléter</span><span class="chevron">⌄</span></button><div class="week-day-body"><label style="display:flex;align-items:center;gap:8px;margin:4px 0 8px"><input type="checkbox" id="rest_${d}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV82('${d}')"> Repos complet</label>${WEEK_SLOTS_V810.map(([key,label])=>{const [a,b]=defaultsV810(key);return `<div class="slot"><div class="slot-title">${label}</div><label style="font-weight:800;display:flex;gap:8px;align-items:center"><input type="checkbox" id="active_${d}_${key}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV82('${d}')"> Ajouter ce créneau</label><div class="grid2"><div><label>Début</label><input type="time" id="s_${d}_${key}" value="${a}"></div><div><label>Fin</label><input type="time" id="e_${d}_${key}" value="${b}"></div></div><div class="week-slot-extra"><div><label>Membre</label><select id="wp_${d}_${key}" onchange="updateWeekSlotColorsV82('${d}','${key}')">${personOptionsV810(firstUserName())}</select></div><div><label>Type d’activité</label><select id="wt_${d}_${key}" onchange="updateWeekSlotColorsV82('${d}','${key}')">${typeOptionsV810('Travail')}</select></div></div><div class="week-color-preview"><span class="week-color-dot" id="wpdot_${d}_${key}" style="background:${people[firstUserName()]||'#B99BFF'}"></span> membre <span class="week-color-dot" id="wtdot_${d}_${key}" style="background:${colors.Travail||'#FF9EB5'}"></span> activité</div></div>`}).join('')}</div></div>`).join('');
    if(typeof renderWeekPickCalendar==='function')renderWeekPickCalendar();const modal=document.getElementById('weekModal');if(modal){modal.classList.add('show');updateFloatingVisibility();}
  };
  window.saveWeekTemplate=function(){
    const slotsToSave=[];days.forEach(d=>{const rest=document.getElementById('rest_'+d);if(rest?.checked)return;WEEK_SLOTS_V810.forEach(([key,label])=>{const active=document.getElementById(`active_${d}_${key}`);if(active?.checked)slotsToSave.push({day:d,label,type:document.getElementById(`wt_${d}_${key}`)?.value||'Travail',start:document.getElementById(`s_${d}_${key}`)?.value||defaultsV810(key)[0],end:document.getElementById(`e_${d}_${key}`)?.value||defaultsV810(key)[1],person:document.getElementById(`wp_${d}_${key}`)?.value||firstUserName()});});});
    const name=(document.getElementById('weekName')?.value||'').trim(),cycle=document.getElementById('weekCycle')?.value||'Semaine A',appliedWeeks=[...(tempSelectedWeeks||[])];
    if(!name)return alert('Donne un nom à ta semaine type.');if(!slotsToSave.length)return alert('Ajoute au moins un créneau.');if(!appliedWeeks.length)return alert('Choisis au moins une semaine concernée.');
    const payload={id:editingWeekTemplateId||'week_'+Date.now(),name,cycle,appliedWeeks,slots:slotsToSave};if(editingWeekTemplateId)weekTemplates=weekTemplates.map(t=>t.id===editingWeekTemplateId?payload:t);else weekTemplates.push(payload);editingWeekTemplateId=null;tempSelectedWeeks=[];closeModals();render();
  };
  window.editWeekTemplate=function(id){
    const t=weekTemplates.find(w=>w.id===id);if(!t)return;editingWeekTemplateId=id;window.openWeekTemplate(true);weekName.value=t.name;weekCycle.value=t.cycle||'Semaine A';tempSelectedWeeks=[...(t.appliedWeeks||[])];
    days.forEach(d=>{const daySlots=(t.slots||[]).filter(s=>s.day===d);WEEK_SLOTS_V810.forEach(([key,label])=>{const s=mergedLegacySlotV810(daySlots,key,label),active=document.getElementById(`active_${d}_${key}`);if(active)active.checked=!!s;if(s){const st=document.getElementById(`s_${d}_${key}`),en=document.getElementById(`e_${d}_${key}`),ps=document.getElementById(`wp_${d}_${key}`),ts=document.getElementById(`wt_${d}_${key}`);if(st)st.value=s.start;if(en)en.value=s.end;if(ps)ps.value=s.person||firstUserName();if(ts)ts.value=s.type||'Travail';if(typeof updateWeekSlotColorsV82==='function')updateWeekSlotColorsV82(d,key);}});const rest=document.getElementById('rest_'+d);if(rest)rest.checked=daySlots.length===0;window.updateWeekDaySummaryV82(d);});
    renderWeekPickCalendar();
  };

  /* ---------------- Score and advice always use the same snapshot ---------------- */
  function taskListV810(date){const target=String(dayNameFromDate(date)||'').toLowerCase();return (Array.isArray(floating)?floating:[]).filter(t=>(Array.isArray(t.days)?t.days:[]).some(d=>{d=String(d).toLowerCase();return d===target||d==='peu importe';}));}
  function scoreBandV810(s){return s>=80?'very-calm':s>=65?'calm':s>=50?'balanced':s>=35?'loaded':'pressure';}
  function snapshotV810(){const ev=eventsForDate(selectedDate)||[],ft=taskListV810(selectedDate),minutes=ev.reduce((s,e)=>s+durationV810(e),0),score=(typeof scoreWithTasksV67==='function'?scoreWithTasksV67():computeSerenityScore(ev));return {ev,ft,minutes,score,band:scoreBandV810(score)};}
  function leadV810(x){
    if(x.band==='very-calm')return '🌿 Ton score confirme une journée très sereine. ';if(x.band==='calm')return '🌱 Ton score indique une journée sereine. ';if(x.band==='balanced')return '🍃 Ton score est équilibré : garde encore un peu de marge. ';if(x.band==='loaded')return '🍂 Ton score montre une journée chargée : évite d’ajouter du facultatif. ';return '🌪️ Ton score indique une forte charge : concentre-toi sur l’essentiel et protège les temps de récupération. ';
  }
  function contextualCandidatesV810(x){
    const c=[];
    if(x.score<50&&x.minutes<180)c.push({id:'hidden-load',text:'Le planning n’explique pas toute la baisse du score : fatigue, tâches à placer, notes en attente ou charge familiale peuvent aussi peser.'});
    if(x.minutes>=480)c.push({id:'dense',text:'Le calendrier est déjà très rempli ; les activités facultatives sont les premières à reporter.'});
    else if(x.minutes>=300)c.push({id:'breath',text:'Garde si possible une vraie transition entre les gros blocs de la journée.'});
    if(x.ft.length)c.push({id:'floating',text:`${x.ft.length} tâche(s) restent à placer : répartis-les plutôt que de les ajouter à un moment déjà dense.`});
    if(mood==='fatigue'||mood==='epuisee')c.push({id:'fatigue',text:'Ta fatigue est prise en compte : une pause ou une activité douce a plus de valeur qu’une tâche supplémentaire.'});
    if(x.score>=65)c.push({id:'margin',text:'Profite de la marge actuelle sans chercher à remplir tous les créneaux libres.'});
    c.push({id:'screen',text:'Ce soir, 30 à 45 minutes sans écran peuvent créer un vrai sas de fin de journée.'});
    c.push({id:'stretch',text:'Une pause de 3 minutes pour la nuque, les épaules et quelques respirations suffit déjà à couper un enchaînement.'});
    if(liveWeather?.rain)c.push({id:'weather-rain',text:'S’il faut sortir aujourd’hui, regrouper les déplacements peut économiser du temps et de l’énergie.'});
    else if(liveWeather&&liveWeather.temperature>=30)c.push({id:'weather-heat',text:`Avec environ ${Math.round(liveWeather.temperature)}°C, privilégie les activités extérieures tôt ou tard.`});
    return c;
  }
  function chooseContextV810(x,cands){
    if(!cands.length)return {id:'default',text:'Garde une petite marge dans ta journée si tu peux.'};
    const key=`${selectedDate.getFullYear()}-${selectedDate.getMonth()+1}-${selectedDate.getDate()}:${Math.floor(new Date().getHours()/6)}:${x.band}:${x.ev.length}:${x.minutes}:${x.ft.length}:${mood}`;
    let h=[];try{h=JSON.parse(localStorage.getItem('esprit_advice_history_v810')||'[]')||[];}catch(e){}
    let pool=cands.filter(a=>!h.slice(-3).includes(a.id));if(!pool.length)pool=cands;const seed=Array.from(key).reduce((s,ch)=>s+ch.charCodeAt(0),0),pick=pool[seed%pool.length];h.push(pick.id);localStorage.setItem('esprit_advice_history_v810',JSON.stringify(h.slice(-8)));return pick;
  }
  window.dayAdviceV810=function(){const x=snapshotV810(),pick=chooseContextV810(x,contextualCandidatesV810(x));return {score:x.score,text:leadV810(x)+pick.text};};
  window.advice=function(){return window.dayAdviceV810().text;};
  window.refreshDayIntelligenceV67=function(showDetails){
    try{const r=window.dayAdviceV810(),label=r.score>=80?'Très serein':r.score>=65?'Serein':r.score>=50?'Équilibré':r.score>=35?'Chargé':'Sous pression',icon=r.score>=80?'🌿':r.score>=65?'🌱':r.score>=50?'🍃':r.score>=35?'🍂':'🌪';const sn=document.getElementById('serenityScoreNum');if(sn)sn.textContent=`${r.score}/100`;const se=document.getElementById('serenity');if(se)se.textContent=label;const round=document.querySelector('.stable-hero .hero-stat-card .hero-round-icon');if(round)round.textContent=icon;const adv=document.getElementById('advice');if(adv)adv.textContent=r.text;const out=document.getElementById('freeAdviceResultV67');if(out&&!isPremium){out.innerHTML=`<b>Score actuel : ${r.score}/100</b><br>${r.text}`;out.style.display=showDetails?'block':out.style.display;}}catch(e){console.warn('V8.10 score/advice sync',e);}
  };

  setTimeout(()=>{try{window.refreshNativeNotificationStatusV810();window.refreshDayIntelligenceV67(false);}catch(e){}},250);
})();
</script>
'''
if 'id="v810-calendar-intelligence-script"' not in html:
    html += js

# Update the explanatory week-template copy.
html=html.replace('Entre toute ta semaine en une seule fois : matin, midi, soir, nuit et repos.',
                  'Entre toute ta semaine en une seule fois : matin, après-midi, nuit et repos.',1)

# ---------------------------------------------------------------------------
# 2) Native notification audit: exact calendar dates + templates + status.
# ---------------------------------------------------------------------------
java_dir=root/'app/src/main/java/com/espritlibre/app'
receiver=java_dir/'NotificationReceiver.java'
receiver.write_text(r'''package com.espritlibre.app;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class NotificationReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent){
        NotificationScheduler.ensureChannel(context);
        String title=intent.getStringExtra("title"),text=intent.getStringExtra("text");
        int id=intent.getIntExtra("id",(int)(System.currentTimeMillis()%100000));
        Intent open=new Intent(context,MainActivity.class);open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi=PendingIntent.getActivity(context,id,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(context,NotificationScheduler.CHANNEL_ID):new Notification.Builder(context);
        String safeTitle=(title==null||title.trim().isEmpty())?"L'Esprit Léger":title;
        String safeText=(text==null||text.trim().isEmpty())?"Un rappel t'attend.":text;
        b.setSmallIcon(R.drawable.ic_notification_leaf).setContentTitle(safeTitle).setContentText(safeText).setContentIntent(pi).setAutoCancel(true).setStyle(new Notification.BigTextStyle().bigText(safeText));
        ((NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE)).notify(id,b.build());
    }
}
''',encoding='utf-8')

scheduler=java_dir/'NotificationScheduler.java'
scheduler.write_text(r'''package com.espritlibre.app;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public final class NotificationScheduler {
    public static final String CHANNEL_ID="esprit_leger_rappels";
    private static final String PREF="esprit_native_notifications";
    private static final String TAG="EspritNotifications";
    private NotificationScheduler(){}

    public static void ensureChannel(Context c){if(Build.VERSION.SDK_INT>=26){NotificationManager nm=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);NotificationChannel ch=new NotificationChannel(CHANNEL_ID,"Rappels L'Esprit Léger",NotificationManager.IMPORTANCE_DEFAULT);ch.setDescription("Rendez-vous, tâches et conseils d'organisation");nm.createNotificationChannel(ch);}}
    private static Calendar dayStart(Calendar in){Calendar c=(Calendar)in.clone();c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);return c;}
    private static Calendar parseDate(String iso){try{String[] p=iso.split("-");Calendar c=Calendar.getInstance();c.set(Integer.parseInt(p[0]),Integer.parseInt(p[1])-1,Integer.parseInt(p[2]),0,0,0);c.set(Calendar.MILLISECOND,0);return c;}catch(Exception e){return null;}}
    private static void setTime(Calendar c,String hhmm){String[] p=(hhmm==null?"09:00":hhmm).split(":");int h=9,m=0;try{h=Integer.parseInt(p[0]);m=p.length>1?Integer.parseInt(p[1]):0;}catch(Exception ignored){}c.set(Calendar.HOUR_OF_DAY,h);c.set(Calendar.MINUTE,m);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);}
    private static String iso(Calendar c){return String.format(Locale.ROOT,"%04d-%02d-%02d",c.get(Calendar.YEAR),c.get(Calendar.MONTH)+1,c.get(Calendar.DAY_OF_MONTH));}
    private static String frDay(Calendar c){String[] d={"","Dimanche","Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"};return d[c.get(Calendar.DAY_OF_WEEK)];}
    private static Calendar weekMonday(Calendar c){Calendar x=dayStart(c);int delta=(x.get(Calendar.DAY_OF_WEEK)+5)%7;x.add(Calendar.DAY_OF_YEAR,-delta);return x;}
    private static boolean eventOccurs(JSONObject e,Calendar date){
        String dateS=e.optString("date","");String rep=e.optString("repeat","Aucune");
        if(!dateS.isEmpty()){
            Calendar target=parseDate(dateS);if(target==null)return false;Calendar d=dayStart(date),t=dayStart(target);if(d.before(t))return false;
            if("Aucune".equals(rep))return iso(d).equals(iso(t));
            if("Chaque semaine".equals(rep)||"Semaine A".equals(rep)||"Semaine B".equals(rep))return d.get(Calendar.DAY_OF_WEEK)==t.get(Calendar.DAY_OF_WEEK);
            if("Tous les jours d'école".equals(rep))return d.get(Calendar.DAY_OF_WEEK)>=Calendar.MONDAY&&d.get(Calendar.DAY_OF_WEEK)<=Calendar.FRIDAY;
            if("Chaque mois".equals(rep))return d.get(Calendar.DAY_OF_MONTH)==t.get(Calendar.DAY_OF_MONTH);
            return iso(d).equals(iso(t));
        }
        String day=e.optString("day","");if("Aujourd'hui".equals(day))return iso(date).equals(iso(Calendar.getInstance()));return frDay(date).equals(day);
    }
    private static int duration(String a,String b){try{String[] x=a.split(":"),y=b.split(":");int aa=Integer.parseInt(x[0])*60+Integer.parseInt(x[1]),bb=Integer.parseInt(y[0])*60+Integer.parseInt(y[1]);int d=bb-aa;if(d<0)d+=1440;return Math.max(0,d);}catch(Exception e){return 0;}}
    private static boolean isTaskReminderType(String type){return "Tâche".equals(type)||"Courses".equals(type)||"Sport".equals(type)||"Temps pour soi".equals(type)||"Repas".equals(type);}
    private static void cancelOld(Context c){AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Set<String> ids=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getStringSet("ids",Collections.emptySet());for(String x:ids){try{int id=Integer.parseInt(x);PendingIntent pi=PendingIntent.getBroadcast(c,id,new Intent(c,NotificationReceiver.class),PendingIntent.FLAG_NO_CREATE|PendingIntent.FLAG_IMMUTABLE);if(pi!=null){am.cancel(pi);pi.cancel();}}catch(Exception ignored){}}c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().remove("ids").apply();}
    private static void schedule(Context c,int id,long when,String title,String text,Set<String> ids){if(when<=System.currentTimeMillis()+30000)return;AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Intent in=new Intent(c,NotificationReceiver.class);in.putExtra("id",id);in.putExtra("title",title);in.putExtra("text",text);PendingIntent pi=PendingIntent.getBroadcast(c,id,in,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);if(Build.VERSION.SDK_INT>=23)am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,pi);else am.set(AlarmManager.RTC_WAKEUP,when,pi);ids.add(String.valueOf(id));}
    private static ArrayList<JSONObject> eventsForDate(JSONObject st,Calendar date){
        ArrayList<JSONObject> out=new ArrayList<>();JSONArray ev=st.optJSONArray("events");if(ev!=null)for(int i=0;i<ev.length();i++){JSONObject e=ev.optJSONObject(i);if(e!=null&&eventOccurs(e,date))out.add(e);}
        JSONArray templates=st.optJSONArray("weekTemplates");if(templates!=null){String wk=iso(weekMonday(date)),day=frDay(date);for(int i=0;i<templates.length();i++){JSONObject t=templates.optJSONObject(i);if(t==null)continue;JSONArray weeks=t.optJSONArray("appliedWeeks");boolean active=false;if(weeks!=null)for(int j=0;j<weeks.length();j++)if(wk.equals(weeks.optString(j))){active=true;break;}if(!active)continue;JSONArray slots=t.optJSONArray("slots");if(slots==null)continue;for(int j=0;j<slots.length();j++){JSONObject s=slots.optJSONObject(j);if(s==null||!day.equals(s.optString("day")))continue;JSONObject x=new JSONObject();try{x.put("type",s.optString("type","Travail"));x.put("title",t.optString("name","Semaine type")+" · "+s.optString("label","Créneau"));x.put("start",s.optString("start","09:00"));x.put("end",s.optString("end","10:00"));x.put("person",s.optString("person",""));}catch(Exception ignored){}out.add(x);}}}
        Collections.sort(out,new Comparator<JSONObject>(){public int compare(JSONObject a,JSONObject b){return a.optString("start","09:00").compareTo(b.optString("start","09:00"));}});return out;
    }

    public static synchronized void reschedule(Context c,String stateJson,String settingsJson){
        ensureChannel(c);cancelOld(c);Set<String> ids=new HashSet<>();
        try{
            JSONObject st=new JSONObject(stateJson==null?"{}":stateJson),set=new JSONObject(settingsJson==null?"{}":settingsJson);
            boolean appointments=set.optBoolean("appointments",true),tasks=set.optBoolean("tasks",true),best=set.optBoolean("bestMoment",true),busy=set.optBoolean("busyDay",true),success=set.optBoolean("success",false);
            String freq=set.optString("frequency","Équilibré");int cap=freq.contains("Peu")?1:(freq.contains("Plus")?4:2);
            Calendar today=dayStart(Calendar.getInstance());HashMap<String,Integer> perDay=new HashMap<>(),minutesByDate=new HashMap<>();
            for(int off=0;off<21;off++){
                Calendar date=(Calendar)today.clone();date.add(Calendar.DAY_OF_YEAR,off);String dateKey=iso(date);ArrayList<JSONObject> list=eventsForDate(st,date);int minutes=0;for(JSONObject e:list)minutes+=duration(e.optString("start","09:00"),e.optString("end","10:00"));minutesByDate.put(dateKey,minutes);
                for(JSONObject e:list){int n=perDay.getOrDefault(dateKey,0);if(n>=cap)break;String type=e.optString("type","Tâche");boolean rdv="Rendez-vous".equals(type),taskLike=isTaskReminderType(type);if(!((rdv&&appointments)||(taskLike&&tasks)))continue;Calendar at=(Calendar)date.clone();setTime(at,e.optString("start","09:00"));at.add(Calendar.MINUTE,rdv?-30:-15);String title=e.optString("title","Activité"),start=e.optString("start","09:00");int id=Math.abs((dateKey+start+title+type).hashCode());String text=rdv?("« "+title+" » est prévu à "+start+"."):("« "+title+" » est prévu à "+start+" dans ton planning.");schedule(c,id,at.getTimeInMillis(),rdv?"Rendez-vous bientôt":"Rappel du planning",text,ids);perDay.put(dateKey,n+1);}
                if(busy&&(list.size()>=4||minutes>=360)&&perDay.getOrDefault(dateKey,0)<cap){Calendar at=(Calendar)date.clone();setTime(at,"08:00");int id=Math.abs(("busy"+dateKey).hashCode());schedule(c,id,at.getTimeInMillis(),"Journée chargée","Ton planning est dense aujourd'hui. Garde une marge et évite d'ajouter une activité facultative.",ids);perDay.put(dateKey,perDay.getOrDefault(dateKey,0)+1);}
            }
            JSONArray floating=st.optJSONArray("floating");int floatingCount=floating==null?0:floating.length();
            if(best&&floatingCount>0){String bestDate=null;int min=Integer.MAX_VALUE;for(int off=0;off<7;off++){Calendar d=(Calendar)today.clone();d.add(Calendar.DAY_OF_YEAR,off);String k=iso(d),m=minutesByDate.getOrDefault(k,0)<min?k:null;if(m!=null){min=minutesByDate.getOrDefault(k,0);bestDate=k;}}if(bestDate!=null&&perDay.getOrDefault(bestDate,0)<cap){Calendar at=parseDate(bestDate);setTime(at,"09:30");int id=Math.abs(("best"+bestDate).hashCode());schedule(c,id,at.getTimeInMillis(),"Bon moment pour alléger ta liste",floatingCount+" tâche(s) restent à placer. Cette journée possède actuellement davantage de marge.",ids);}}
            if(success){Calendar sun=(Calendar)today.clone();int delta=(Calendar.SUNDAY-sun.get(Calendar.DAY_OF_WEEK)+7)%7;sun.add(Calendar.DAY_OF_YEAR,delta);setTime(sun,"19:00");String k=iso(sun);if(perDay.getOrDefault(k,0)<cap){schedule(c,Math.abs(("success"+k).hashCode()),sun.getTimeInMillis(),"Décharge réussie 🌿","Prends une minute pour regarder ce que tu as terminé, déplacé ou réussi à alléger cette semaine.",ids);}}
        }catch(Exception e){Log.w(TAG,"Notification reschedule failed",e);}
        c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putStringSet("ids",ids).apply();
    }
}
''',encoding='utf-8')

# Add native notification status to the existing bridge without touching V8.6 theme code.
mainp=java_dir/'MainActivity.java'
main=mainp.read_text(encoding='utf-8')
status_method=r'''
        @JavascriptInterface public String status(){
            try{
                NotificationManager nm=(NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
                boolean enabled=Build.VERSION.SDK_INT<24 || nm.areNotificationsEnabled();
                boolean channelEnabled=true;
                if(Build.VERSION.SDK_INT>=26){NotificationChannel ch=nm.getNotificationChannel(NotificationScheduler.CHANNEL_ID);channelEnabled=ch==null || ch.getImportance()!=NotificationManager.IMPORTANCE_NONE;}
                return "{\"enabled\":"+enabled+",\"channelEnabled\":"+channelEnabled+"}";
            }catch(Exception e){return "{\"enabled\":true,\"channelEnabled\":true}";}
        }
'''
if '@JavascriptInterface public String status()' not in main:
    anchor='''        @JavascriptInterface public void sync(String stateJson,String settingsJson){\n            context.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).edit().putString("state",stateJson).putString("settings",settingsJson).apply();\n            NotificationScheduler.reschedule(context,stateJson,settingsJson);\n        }'''
    if anchor not in main:
        raise SystemExit('NotificationBridge sync anchor not found')
    main=main.replace(anchor,anchor+status_method,1)
mainp.write_text(main,encoding='utf-8')

# Sanity checks.
for marker in ['id="v86-native-theme-controller"','id="v87-fluid-glance-script"','id="v88-backup-restore"','id="v89-stability-intelligence-script"','id="v810-calendar-intelligence-script"']:
    if marker not in html: raise SystemExit('missing baseline marker '+marker)
if 'loadNotificationSettings();\n saveNotificationSettings();' in html: raise SystemExit('notification overwrite pair still present')
if "['matin','Matin'],['apresmidi','Après-midi'],['nuit','Nuit']" not in js: raise SystemExit('three-slot typical week missing')
if 'R.drawable.ic_notification_leaf' not in receiver.read_text(encoding='utf-8'): raise SystemExit('leaf notification icon missing')

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.10"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1));b=b[:m.start(1)]+str(max(old+1,810))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.10 calendar/readability/intelligence/notification patch applied')
