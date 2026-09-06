from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.10 final — one canonical daily score across Home + Family, and explicit day/week labels.
html=html.replace('<p>Score : <span id="serenityScoreNum">','<p>Score de la journée : <span id="serenityScoreNum">',1)

js=r'''
<script id="v810-final-score-coherence">
(function(){
  function normV810Final(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function minsV810Final(t){const p=String(t||'00:00').split(':').map(Number);return (p[0]||0)*60+(p[1]||0);}
  function durV810Final(e){let d=minsV810Final(e?.end)-minsV810Final(e?.start);if(d<0)d+=1440;return Math.max(0,d);}
  function labelV810Final(s){return s>=80?'Très serein':s>=65?'Serein':s>=50?'Équilibré':s>=35?'Chargé':'Sous pression';}
  function iconV810Final(s){return s>=80?'🌿':s>=65?'🌱':s>=50?'🍃':s>=35?'🍂':'🌪';}
  function floatingForDateV810Final(date,member){
    const target=normV810Final(dayNameFromDate(date));
    return (Array.isArray(floating)?floating:[]).filter(t=>{
      if(member&&t.person&&t.person!==member)return false;
      const ds=Array.isArray(t.days)?t.days:[];
      return ds.some(d=>{const n=normV810Final(d);return n===target||n==='peu importe';});
    });
  }
  window.serenitySnapshotV810Final=function(date,options){
    const opt=options||{},ev=Array.isArray(opt.events)?opt.events:(eventsForDate(date)||[]);
    let score=computeSerenityScore(ev);
    const ft=opt.includeFloating===false?[]:floatingForDateV810Final(date,opt.member||null);
    if(ft.length){const taskMins=ft.reduce((s,t)=>s+(parseInt(t.duration||'30',10)||30),0);score-=Math.min(18,ft.length*3+Math.floor(taskMins/90)*2);}
    score=Math.max(0,Math.min(100,Math.round(score)));
    const minutes=ev.reduce((s,e)=>s+durV810Final(e),0);
    return {score,label:labelV810Final(score),icon:iconV810Final(score),events:ev,tasks:ft,minutes,overlaps:typeof overlapsV65==='function'?overlapsV65(ev):0};
  };

  // The Home card and every consumer of scoreWithTasksV67 now resolve through the same snapshot.
  window.scoreWithTasksV67=function(){return window.serenitySnapshotV810Final(selectedDate).score;};

  window.openFamilyScores=function(){
    const modal=document.getElementById('familyScoreModal'),content=document.getElementById('familyScoreContent');if(!modal||!content)return;
    const all=eventsForDate(selectedDate)||[],owner=firstUserName(),names=Object.keys(people).length?Object.keys(people):[owner];
    const rows=names.map(name=>{
      const own=all.filter(e=>!e.person||e.person===name);
      const snap=window.serenitySnapshotV810Final(selectedDate,{events:own,member:name,includeFloating:name===owner||floating.some(t=>t.person===name)});
      return `<div class="score-row"><span>${name}${name===owner?' · personnel':''}</span><strong>${snap.icon} ${snap.score}/100</strong><small>${snap.label} · estimation personnelle</small></div>`;
    }).join('');
    // IMPORTANT: total Family is exactly the same daily score displayed on Home.
    const fam=window.serenitySnapshotV810Final(selectedDate),familyNum=fam.score;
    let familyAdvice='La charge familiale est bien répartie pour cette journée.';
    if(familyNum<80)familyAdvice='La journée commence à se charger : garde des marges et répartis les tâches si possible.';
    if(familyNum<60)familyAdvice='La charge familiale est élevée : déplace une tâche non urgente ou protège un créneau de récupération.';
    if(familyNum<40)familyAdvice='La journée familiale est très chargée : garde uniquement l’essentiel et reporte ce qui peut l’être.';
    content.innerHTML=`${rows}<div class="score-row family-total"><span>Famille · score de la journée</span><strong>${fam.icon} ${fam.score}/100</strong><small>${fam.label} · même calcul que l’accueil</small></div><div class="ai-result"><b>✨ Lecture familiale</b><p>${familyAdvice}</p></div>`;
    modal.classList.add('show');updateFloatingVisibility();
  };

  // Premium weekly assistant clearly separates selected-day score from seven-day score.
  window.runAiWeekLighten=function(){
    if(!isPremium){alert('Cette fonction est disponible en Premium.');return;}
    const card=document.getElementById('aiWeeklyResult'),content=document.getElementById('aiWeeklyContent');if(!card||!content)return;
    if(card.classList.contains('ai-visible')&&getComputedStyle(card).display!=='none'){card.style.display='none';card.classList.remove('ai-visible');return;}
    const startW=weekStart(selectedDate);
    const dd=days.map((name,i)=>{const date=addDays(startW,i),snap=window.serenitySnapshotV810Final(date),ev=snap.events;return {name,date,ev,minutes:snap.minutes,fixed:ev.filter(e=>typeof isFixedActivityV89==='function'&&isFixedActivityV89(e)),flex:ev.filter(e=>typeof isFlexibleActivityV89==='function'&&isFlexibleActivityV89(e)),score:snap.score,overlaps:snap.overlaps};});
    const weekScore=typeof weekSerenityV65==='function'?weekSerenityV65(dd):Math.round(dd.reduce((s,d)=>s+d.score,0)/7),todaySnap=window.serenitySnapshotV810Final(selectedDate);
    const busiest=[...dd].sort((a,b)=>b.minutes-a.minutes)[0],lightest=[...dd].sort((a,b)=>a.minutes-b.minutes)[0];
    const suggestions=[`${todaySnap.icon} Score de la journée (${dayNameFromDate(selectedDate)}) : ${todaySnap.score}/100 · ${todaySnap.label}.`,`📊 Score de la semaine : ${weekScore}/100 · ${labelV810Final(weekScore)} · calculé sur les 7 jours.`];
    if(busiest&&busiest.minutes>=360)suggestions.push(`📆 ${busiest.name} est la journée la plus chargée (${Math.round(busiest.minutes/6)/10} h planifiées, score ${busiest.score}/100).`);
    if(busiest?.overlaps)suggestions.push(`⚠️ ${busiest.name} contient ${busiest.overlaps} chevauchement(s) d’horaires à vérifier.`);
    const movable=busiest?.flex?.slice().sort((a,b)=>durV810Final(b)-durV810Final(a))[0];
    if(movable&&lightest&&lightest.name!==busiest.name&&busiest.minutes-lightest.minutes>=90){
      suggestions.push(`↔️ Si tu veux alléger ${busiest.name}, « ${movable.title} » (${String(movable.type||'activité').toLowerCase()}) est un créneau facultatif qui pourrait être déplacé vers ${lightest.name}.`);
    }else if(busiest&&busiest.fixed.reduce((s,e)=>s+durV810Final(e),0)>=Math.max(300,busiest.minutes*.65)){
      suggestions.push(`🧱 La charge de ${busiest.name} vient surtout de contraintes fixes (travail, école ou rendez-vous). Je ne te propose pas de les déplacer : protège plutôt les créneaux libres autour.`);
    }
    const totalLate=dd.reduce((s,d)=>s+d.ev.filter(e=>minsV810Final(e.start)>=19*60).length,0);if(totalLate>=2)suggestions.push(`🌙 ${totalLate} activité(s) commencent après 19 h : essaie de garder au moins une fin de soirée sans obligation.`);
    if(mood==='fatigue'||mood==='epuisee')suggestions.push('😴 Ta fatigue est prise en compte : les tâches facultatives sont les premières candidates à reporter ou raccourcir.');
    if(floating.length)suggestions.push(`🧩 ${floating.length} tâche(s) restent à placer : commence par les journées avec le plus de marge, sans toucher aux contraintes fixes.`);
    content.innerHTML=`<div class="ai-result"><b>Analyse de ta semaine</b><ul>${suggestions.slice(0,7).map(s=>`<li>${s}</li>`).join('')}</ul></div>`;
    card.classList.add('ai-visible');card.style.display='block';
  };

  function reconcileV810Final(){try{if(typeof refreshDayIntelligenceV67==='function')refreshDayIntelligenceV67(false);}catch(e){}}
  document.addEventListener('DOMContentLoaded',()=>setTimeout(reconcileV810Final,180));setTimeout(reconcileV810Final,260);
})();
</script>
'''
if 'id="v810-final-score-coherence"' not in html: html += js
if html.count('id="v810-final-score-coherence"')!=1: raise SystemExit('V8.10 final score block missing/duplicated')
for frozen in ['id="v86-native-theme-controller"','id="v87-fluid-glance-script"','id="v88-backup-restore"','id="v89-stability-intelligence-script"','id="v810-calendar-intelligence-script"']:
    if frozen not in html: raise SystemExit('frozen baseline missing: '+frozen)
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.10"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1));b=b[:m.start(1)]+str(max(old+1,811))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.10 final score coherence applied')
