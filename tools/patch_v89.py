from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.9 — stability + readable colors + smarter non-repetitive suggestions.
# Preserve the validated V8.6 theme, V8.7 glance calendar and V8.8 modal/backup behavior.

# 1) Memo preview: show all ordinary notes in normal daily use (up to 6) rather than an old hard cap of 2.
old='const memoItems=[...thoughts.slice(0,4), ...appNotes.slice(0,2).map(n=>n.text)].slice(0,6);'
new='const memoItems=[...thoughts.slice(0,2), ...appNotes.slice(0,6).map(n=>n.text)].slice(0,8);'
count=html.count(old)
print('memo occurrences',count)
if count<1: raise SystemExit('memo preview hard cap not found')
html=html.replace(old,new)

css=r'''
<style id="v89-stability-intelligence-style">
/* Selected weeks must remain visible after Twilight's generic calendar rule. */
body.crepuscule .week-picker-day.week-selected{
  background:linear-gradient(135deg,#75639a,#a85f7c) !important;
  color:#fff !important;
  border:2px solid rgba(245,237,250,.92) !important;
  box-shadow:0 0 0 2px rgba(129,114,170,.28),0 5px 13px rgba(0,0,0,.22) !important;
  opacity:1 !important;
}
body.crepuscule .week-tag{
  background:#342d3c !important;color:#eee7f2 !important;border:1px solid rgba(255,255,255,.10) !important;
}
/* Color-coded content owns its contrast, independently of Light/Twilight. */
.event-pill.v89-auto-contrast,.event-pill.v89-auto-contrast .event-meta{color:inherit !important;}
.event-pill.v89-auto-contrast .event-meta{opacity:.78;}
.block.v89-auto-contrast{color:inherit !important;}
/* Interaction geometry: freeze the validated V8.8 behavior without changing its look. */
#eventModal .event-actions-v81,#weekModal .modal-validate{position:static !important;}
.week-picker-day,.palette-btn,.tab,.nav button,.smallbtn,.primary{touch-action:manipulation;}
</style>
'''

js=r'''
<script id="v89-stability-intelligence-script">
(function(){
  const FIXED_TYPES_V89=new Set(['Travail','École','Rendez-vous']);
  const FLEX_TYPES_V89=new Set(['Sport','Courses','Temps pour soi','Tâche']);
  const FIXED_WORDS_V89=['travail','ecole','école','rdv','rendez-vous','rendez vous','medecin','médecin','dentiste','kiné','kine','crèche','creche'];

  function minsV89(t){const p=String(t||'00:00').split(':').map(Number);return (p[0]||0)*60+(p[1]||0);}
  function durV89(e){return Math.max(0,minsV89(e?.end)-minsV89(e?.start));}
  function normV89(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function isFixedV89(e){
    if(FIXED_TYPES_V89.has(e?.type))return true;
    const title=normV89(e?.title);return FIXED_WORDS_V89.some(k=>title.includes(normV89(k)));
  }
  function isFlexibleV89(e){return !!e && !isFixedV89(e) && FLEX_TYPES_V89.has(e.type);}
  window.isFixedActivityV89=isFixedV89;
  window.isFlexibleActivityV89=isFlexibleV89;

  function rgbV89(hex){
    let h=String(hex||'').replace('#','').trim();if(h.length===3)h=h.split('').map(x=>x+x).join('');
    if(!/^[0-9a-f]{6}$/i.test(h))return [255,255,255];
    return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];
  }
  function contrastTextV89(hex){
    const [r,g,b]=rgbV89(hex).map(v=>v/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));
    const L=.2126*r+.7152*g+.0722*b;
    return L>.42?'#2D2738':'#FFFFFF';
  }
  window.contrastTextV89=contrastTextV89;
  function eventStyleV89(e){const bg=eventUserColor(e),fg=contrastTextV89(bg);return `background:${bg};--task-color:${eventTaskColor(e)};color:${fg}!important`;}

  /* Day view: preserve the validated V8.7 "around now" behavior and add automatic contrast. */
  function sameDayV89(a,b){return a&&b&&a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();}
  function hhmmV89(d){return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');}
  window.renderDay=function(){
    const now=new Date(),today=sameDayV89(selectedDate,now),allEvents=eventsForDate(selectedDate),currentHour=now.getHours();
    const contextualStart=today?Math.max(0,currentHour-1):0;
    const startHour=(today&&!window.pastHoursExpandedV87)?contextualStart:0;let html='';
    if(today&&contextualStart>0){
      const hiddenCount=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)<contextualStart).length;
      if(window.pastHoursExpandedV87){
        html+=`<button type="button" class="past-hours-toggle-v87" onclick="togglePastHoursV87(event)"><b>⌃ Replier les heures passées</b><span>${hiddenCount?hiddenCount+' activité'+(hiddenCount>1?'s':''):''}</span></button>`;
      }else{
        const lastHidden=contextualStart-1,range=lastHidden===0?'00h':`00h–${String(lastHidden).padStart(2,'0')}h`;
        html+=`<button type="button" class="past-hours-toggle-v87" onclick="togglePastHoursV87(event)"><b>Plus tôt aujourd’hui · ${range}</b><span>${hiddenCount?hiddenCount+' activité'+(hiddenCount>1?'s':'')+' · ':''}Afficher ▾</span></button>`;
      }
    }
    for(let h=startHour;h<24;h++){
      const hs=String(h).padStart(2,'0')+':00',ev=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)===h),current=today&&h===currentHour;
      const marker=current?`<div class="now-marker-v87">Maintenant · ${hhmmV89(now)}</div>`:'';
      html+=`<div class="hour-row ${current?'current-hour-v87':''}"><div class="hour">${hs}</div><div class="hour-content">${marker}${ev.map(e=>`<div class="event-pill v89-auto-contrast" style="${eventStyleV89(e)}" onclick='openDetails(${JSON.stringify(e)})'>${emoji(e.type)} ${e.title}<div class="event-meta">${e.start}-${e.end} · ${e.person}</div></div>`).join('')}</div></div>`;
    }
    calendar.innerHTML=html;
  };

  window.openDetails=function(e){
    const prettyDate=(typeof pretty==='function'&&e.date)?pretty(e.date):(e.date||e.day||'');
    detailContent.innerHTML=`<div class="event-pill v89-auto-contrast" style="${eventStyleV89(e)}">${emoji(e.type)} ${e.title}<div class="event-meta">${prettyDate} · ${e.start}-${e.end} · ${e.person} · ${e.repeat||'Aucune'}</div></div>`;
    detailModal.classList.add('show');if(typeof updateFloatingVisibility==='function')updateFloatingVisibility();
  };

  /* ---- Advice rotation without weather monopolising the banner. ---- */
  function dateKeyV89(d){const x=d||new Date();return `${x.getFullYear()}-${String(x.getMonth()+1).padStart(2,'0')}-${String(x.getDate()).padStart(2,'0')}`;}
  function tomorrowV89(d){const x=new Date(d);x.setDate(x.getDate()+1);return x;}
  function earliestFixedV89(date){
    const ev=(eventsForDate(date)||[]).filter(isFixedV89).sort((a,b)=>minsV89(a.start)-minsV89(b.start));return ev[0]||null;
  }
  function bedtimeSuggestionV89(baseDate){
    const next=tomorrowV89(baseDate),first=earliestFixedV89(next);if(!first||minsV89(first.start)>=11*60)return null;
    const start=minsV89(first.start),wake=Math.max(5*60,start-60),bed=(wake-8*60+24*60)%(24*60),screen=(bed-45+24*60)%(24*60);
    const fmt=m=>`${String(Math.floor(m/60)%24).padStart(2,'0')}h${String(m%60).padStart(2,'0')}`;
    return {id:'sleep',text:`🌙 Demain commence tôt avec « ${first.title} » à ${first.start}. Pour garder une bonne marge de sommeil, vise un coucher autour de ${fmt(bed)} et commence à ralentir vers ${fmt(screen)}.`};
  }
  function tasksForDateV89(date){
    const target=normV89(dayNameFromDate(date));
    return (Array.isArray(floating)?floating:[]).filter(t=>{const ds=Array.isArray(t.days)?t.days:[];return ds.some(d=>normV89(d)===target||normV89(d)==='peu importe');});
  }
  function candidateAdviceV89(){
    const ev=eventsForDate(selectedDate)||[],ft=tasksForDateV89(selectedDate),minutes=ev.reduce((s,e)=>s+durV89(e),0),fixedMins=ev.filter(isFixedV89).reduce((s,e)=>s+durV89(e),0);
    const c=[];
    if(ev.length===0&&ft.length===0)c.push({id:'margin',text:'🌿 Ta journée est encore très libre. Garde volontairement une partie de cette marge au lieu de chercher à tout remplir.'});
    if(minutes>=480)c.push({id:'dense',text:'📆 Ta journée est très remplie. Les contraintes fixes restent en place : évite surtout d’ajouter du facultatif autour.'});
    else if(minutes>=300)c.push({id:'breath',text:'🫧 La journée est déjà bien occupée. Garde au moins 10 minutes de transition sans tâche entre deux gros blocs si tu peux.'});
    if(fixedMins>=360)c.push({id:'fixed',text:'🧱 Une grande partie de ta charge vient de contraintes fixes. L’objectif n’est pas de les déplacer, mais de protéger ce qu’il reste de libre.'});
    if(ft.length)c.push({id:'floating',text:`🧩 ${ft.length} tâche(s) restent à placer aujourd’hui. Évite de les coller toutes au même moment.`});
    if(mood==='fatigue'||mood==='epuisee')c.push({id:'fatigue',text:'😴 Tu as signalé de la fatigue. Aujourd’hui, garde le nécessaire et privilégie une activité douce ou une vraie pause.'});
    const sleep=bedtimeSuggestionV89(selectedDate);if(sleep)c.push(sleep);
    c.push({id:'screen',text:'📵 Ce soir, essaie de garder 30 à 45 minutes sans écran avant de dormir : un petit sas calme aide à vraiment terminer la journée.'});
    c.push({id:'stretch',text:'🧘 Une pause de 3 minutes suffit : épaules, nuque, dos, puis quelques respirations lentes avant de repartir.'});
    c.push({id:'walk',text:'🚶 Si tu as un petit creux dans le planning, 5 à 10 minutes de marche peuvent faire une vraie coupure sans alourdir la journée.'});
    c.push({id:'breathing',text:'🌬️ Mini-pause possible : inspire 4 secondes, expire 6 secondes, pendant 2 minutes. Simple et facile à placer entre deux activités.'});
    if(liveWeather?.rain)c.push({id:'weather-rain',text:'🌧️ La météo est humide aujourd’hui : si tu dois sortir, regrouper les déplacements peut économiser du temps et de l’énergie.'});
    else if(liveWeather&&liveWeather.temperature>=30)c.push({id:'weather-heat',text:`☀️ Il fait environ ${Math.round(liveWeather.temperature)}°C : garde les activités extérieures pour le matin ou la fin de journée.`});
    return c;
  }
  function chooseAdviceV89(cands){
    if(!cands.length)return {id:'default',text:'🌿 Garde une petite marge dans ta journée si tu peux.'};
    const d=isNaN(selectedDate)?new Date():selectedDate, now=new Date();
    const bucket=`${dateKeyV89(d)}:${sameDayV89(d,now)?Math.floor(now.getHours()/6):'date'}`;
    let cache={};try{cache=JSON.parse(localStorage.getItem('esprit_advice_choice_v89')||'{}')||{};}catch(e){}
    if(cache.bucket===bucket){const old=cands.find(x=>x.id===cache.id);if(old)return old;}
    let hist=[];try{hist=JSON.parse(localStorage.getItem('esprit_advice_history_v89')||'[]')||[];}catch(e){}
    const recent=hist.slice(-3);let pool=cands.filter(x=>!recent.includes(x.id));if(!pool.length)pool=cands;
    const seed=Array.from(bucket).reduce((s,ch)=>s+ch.charCodeAt(0),0);const pick=pool[seed%pool.length];
    localStorage.setItem('esprit_advice_choice_v89',JSON.stringify({bucket,id:pick.id}));
    hist.push(pick.id);localStorage.setItem('esprit_advice_history_v89',JSON.stringify(hist.slice(-8)));return pick;
  }
  function dayAdviceV89(){
    const score=(typeof scoreWithTasksV67==='function'?scoreWithTasksV67():computeSerenityScore(eventsForDate(selectedDate)||[]));
    return {score,text:chooseAdviceV89(candidateAdviceV89()).text};
  }
  window.advice=function(){return dayAdviceV89().text;};
  window.refreshDayIntelligenceV67=function(showDetails){
    try{
      const r=dayAdviceV89(),label=r.score>=80?'Très serein':r.score>=65?'Serein':r.score>=50?'Équilibré':r.score>=35?'Chargé':'Sous pression';
      const icon=r.score>=80?'🌿':r.score>=65?'🌱':r.score>=50?'🍃':r.score>=35?'🍂':'🌪';
      const sn=document.getElementById('serenityScoreNum');if(sn)sn.textContent=`${r.score}/100`;
      const se=document.getElementById('serenity');if(se)se.textContent=label;
      const round=document.querySelector('.stable-hero .hero-stat-card .hero-round-icon');if(round)round.textContent=icon;
      const adv=document.getElementById('advice');if(adv)adv.textContent=r.text;
      const out=document.getElementById('freeAdviceResultV67');if(out&&!isPremium){out.innerHTML=`<b>Score actuel : ${r.score}/100</b><br>${r.text}`;out.style.display=showDetails?'block':out.style.display;}
    }catch(e){console.warn('V8.9 adaptive advice',e);}
  };

  /* ---- Premium weekly assistant: never proposes moving fixed obligations. ---- */
  window.runAiWeekLighten=function(){
    if(!isPremium){alert('Cette fonction est disponible en Premium.');return;}
    const card=document.getElementById('aiWeeklyResult'),content=document.getElementById('aiWeeklyContent');if(!card||!content)return;
    if(card.classList.contains('ai-visible')&&getComputedStyle(card).display!=='none'){card.style.display='none';card.classList.remove('ai-visible');return;}
    const startW=weekStart(selectedDate);
    const dd=days.map((name,i)=>{const date=addDays(startW,i),ev=eventsForDate(date)||[];return {name,date,ev,minutes:ev.reduce((s,e)=>s+durV89(e),0),fixed:ev.filter(isFixedV89),flex:ev.filter(isFlexibleV89),score:computeSerenityScore(ev),overlaps:(typeof overlapsV65==='function'?overlapsV65(ev):0)};});
    const weekScore=typeof weekSerenityV65==='function'?weekSerenityV65(dd):Math.round(dd.reduce((s,d)=>s+d.score,0)/7);
    const busiest=[...dd].sort((a,b)=>b.minutes-a.minutes)[0],lightest=[...dd].sort((a,b)=>a.minutes-b.minutes)[0];
    const suggestions=[`🌿 Score de sérénité hebdomadaire estimé : ${weekScore}/100.`];
    if(busiest&&busiest.minutes>=360)suggestions.push(`📆 ${busiest.name} est la journée la plus chargée (${Math.round(busiest.minutes/6)/10} h planifiées).`);
    if(busiest?.overlaps)suggestions.push(`⚠️ ${busiest.name} contient ${busiest.overlaps} chevauchement(s) d’horaires à vérifier.`);
    const movable=busiest?.flex?.slice().sort((a,b)=>durV89(b)-durV89(a))[0];
    if(movable&&lightest&&lightest.name!==busiest.name&&busiest.minutes-lightest.minutes>=90){
      suggestions.push(`↔️ Si tu veux alléger ${busiest.name}, « ${movable.title} » (${movable.type.toLowerCase()}) est un créneau facultatif qui pourrait être déplacé vers ${lightest.name}.`);
    }else if(busiest&&busiest.fixed.reduce((s,e)=>s+durV89(e),0)>=Math.max(300,busiest.minutes*.65)){
      suggestions.push(`🧱 La charge de ${busiest.name} vient surtout de contraintes fixes (travail, école ou rendez-vous). Je ne te propose pas de les déplacer : protège plutôt les créneaux libres autour.`);
    }
    const totalLate=dd.reduce((s,d)=>s+d.ev.filter(e=>minsV89(e.start)>=19*60).length,0);if(totalLate>=2)suggestions.push(`🌙 ${totalLate} activité(s) commencent après 19 h : essaie de garder au moins une fin de soirée sans obligation.`);
    const nextFixed=earliestFixedV89(tomorrowV89(selectedDate));
    if(nextFixed&&minsV89(nextFixed.start)<10*60){const sleep=bedtimeSuggestionV89(selectedDate);if(sleep)suggestions.push(sleep.text);}
    suggestions.push('📵 Une soirée chargée se termine mieux avec 30 à 45 minutes sans écran avant le coucher.');
    suggestions.push('🧘 Si tu enchaînes plusieurs blocs, place 3 minutes d’étirements ou de respiration entre deux activités plutôt qu’une nouvelle tâche.');
    if(mood==='fatigue'||mood==='epuisee')suggestions.push('😴 Ta fatigue est prise en compte : les tâches facultatives sont les premières candidates à reporter ou raccourcir.');
    if(floating.length)suggestions.push(`🧩 ${floating.length} tâche(s) restent à placer : commence par les journées avec le plus de marge, sans toucher aux contraintes fixes.`);
    if(liveWeather?.rain)suggestions.push('🌧️ S’il faut sortir, regroupe les déplacements plutôt que de multiplier les allers-retours.');
    else if(liveWeather&&liveWeather.temperature>=30)suggestions.push(`☀️ Avec environ ${Math.round(liveWeather.temperature)}°C, privilégie les activités extérieures tôt ou tard.`);
    content.innerHTML=`<div class="ai-result"><b>Analyse de ta semaine</b><ul>${suggestions.slice(0,7).map(s=>`<li>${s}</li>`).join('')}</ul></div>`;
    card.classList.add('ai-visible');card.style.display='block';
  };

  /* Final visual/state reconciliation after legacy wrappers have rendered. */
  function stabilizeV89(){
    document.querySelectorAll('.week-picker-day.week-selected').forEach(el=>el.setAttribute('aria-pressed','true'));
    try{if(typeof refreshDayIntelligenceV67==='function')refreshDayIntelligenceV67(false);}catch(e){}
  }
  document.addEventListener('DOMContentLoaded',()=>setTimeout(stabilizeV89,180));
  setTimeout(stabilizeV89,260);
})();
</script>
'''

html += css+js

# Sanity checks before writing.
if 'appNotes.slice(0,2)' in html:
    raise SystemExit('old two-note memo cap still present')
if html.count('id="v89-stability-intelligence-style"')!=1 or html.count('id="v89-stability-intelligence-script"')!=1:
    raise SystemExit('V8.9 blocks missing or duplicated')
if 'id="v86-native-theme-controller"' not in html or 'id="v87-fluid-glance-script"' not in html or 'id="v88-backup-restore"' not in html:
    raise SystemExit('validated V8.6/V8.7/V8.8 baseline unexpectedly missing')
if html.count('function runAiWeekLighten(){') < 1:
    raise SystemExit('Premium assistant baseline missing')
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.9"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,89))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.9 stability and smarter suggestions applied')