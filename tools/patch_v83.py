from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

css=r'''
<style id="v83-corrective-style">
/* V8.3 — explicit luminous palette, appended last so legacy dark rules cannot leak into Light mode. */
body.light{
  background:linear-gradient(160deg,#fbf8fc,#f5f1f8) !important;
  color:#433a49 !important;
  --ink:#433a49 !important;
  --muted:#84798b !important;
}
body.light .phone{background:transparent !important;}
body.light .top-bubble{
  background:linear-gradient(135deg,#f0e7ff,#fbe8ef) !important;
  color:#433a49 !important;
  border-color:rgba(105,82,135,.10) !important;
  box-shadow:0 14px 30px rgba(97,78,121,.10) !important;
}
body.light .card,
body.light .day-col,
body.light .listitem,
body.light .coloritem,
body.light .slot,
body.light .suggestion,
body.light .sheet,
body.light .plan-card,
body.light .dayform,
body.light .slot-choice,
body.light .color-popup,
body.light input,
body.light select,
body.light textarea,
body.light .nav,
body.light .tabs,
body.light .quick-add-menu,
body.light .mood-floating,
body.light .week-day-accordion{
  background:rgba(255,255,255,.96) !important;
  color:#433a49 !important;
  border-color:#ece4f2 !important;
}
body.light .soft-calendar{background:linear-gradient(135deg,#ffffff,#faf6ff) !important;}
body.light .soft-advice{background:linear-gradient(135deg,#f5fbf7,#fff9ee) !important;}
body.light p,body.light .note,body.light .event-meta,
body.light .details-line,body.light label,body.light .week-day-summary{color:#84798b !important;}
body.light .smallbtn,body.light .ghost,body.light .mood,
body.light .tab,body.light .chip,body.light .day-choice{
  background:#f5effa !important;color:#51465a !important;
}
body.light .primary,body.light .mood.active,
body.light .tab.active,body.light .nav button.active{
  background:linear-gradient(135deg,#9c86c8,#cf829f) !important;color:#fff !important;
}
body.light .card{box-shadow:0 10px 24px rgba(85,66,105,.08) !important;}
body.light .week-day-head{color:#433a49 !important;}

/* Make the bottom navigation easier to perceive in Twilight while keeping it calm. */
body.crepuscule .nav{
  background:#37303f !important;
  border:1px solid rgba(255,255,255,.13) !important;
  box-shadow:0 10px 28px rgba(0,0,0,.30),0 0 0 1px rgba(255,255,255,.025) inset !important;
}
body.crepuscule .nav button{color:#cfc6d6 !important;}
body.crepuscule .nav button.active{
  color:#fff !important;
  box-shadow:0 5px 14px rgba(129,114,170,.24) !important;
}

/* One global person/activity choice for the whole typical week. */
.week-global-settings-v83{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
  margin:10px 0 14px;
  padding:12px;
  border:1px solid #ece4f2;
  border-radius:18px;
  background:rgba(255,255,255,.72);
}
.week-global-settings-v83 .week-global-preview{
  grid-column:1/-1;
  display:flex;
  gap:14px;
  align-items:center;
  font-size:12px;
  color:var(--muted);
  font-weight:850;
}
.week-global-settings-v83 .preview-item{display:flex;align-items:center;gap:6px;}
body.crepuscule .week-global-settings-v83{
  background:#2a2530 !important;
  border-color:rgba(255,255,255,.09) !important;
}
body.light .week-global-settings-v83{
  background:rgba(255,255,255,.78) !important;
  border-color:#ece4f2 !important;
}
@media(max-width:370px){.week-global-settings-v83{grid-template-columns:1fr;}.week-global-settings-v83 .week-global-preview{grid-column:1;}}
</style>
'''
if 'id="v83-corrective-style"' not in html:
    html += css

js=r'''
<script id="v83-corrective-script">
(function(){
  const activityTypesV83=['Travail','École','Rendez-vous','Sport','Courses','Repas','Temps pour soi','Tâche'];
  function personOptionsV83(selected){
    const names=Object.keys(people);if(!names.length)names.push(firstUserName());
    return names.map(n=>`<option value="${n}" ${n===selected?'selected':''}>${n}</option>`).join('');
  }
  function typeOptionsV83(selected){return activityTypesV83.map(t=>`<option value="${t}" ${t===selected?'selected':''}>${emoji(t)} ${t}</option>`).join('');}
  function defaultTimesV83(key){return key==='matin'?['08:00','12:00']:key==='midi'?['12:00','14:00']:key==='soir'?['17:00','20:00']:['21:00','23:00'];}
  function safeIdV83(s){return String(s).replace(/[^a-zA-Z0-9_-]/g,'_');}

  function ensureWeekGlobalV83(person,type){
    const wf=document.getElementById('weekForms');if(!wf)return;
    let box=document.getElementById('weekGlobalSettingsV83');
    if(!box){
      box=document.createElement('div');box.id='weekGlobalSettingsV83';box.className='week-global-settings-v83';
      wf.parentNode.insertBefore(box,wf);
    }
    const p=person||firstUserName(),t=type||'Travail';
    box.innerHTML=`<div><label>Personne concernée</label><select id="weekPersonV83" onchange="updateWeekGlobalPreviewV83()">${personOptionsV83(p)}</select></div><div><label>Type d’activité</label><select id="weekTypeV83" onchange="updateWeekGlobalPreviewV83()">${typeOptionsV83(t)}</select></div><div class="week-global-preview"><span class="preview-item"><span class="week-color-dot" id="weekPersonDotV83"></span> couleur du membre</span><span class="preview-item"><span class="week-color-dot" id="weekTypeDotV83"></span> couleur de l’activité</span></div>`;
    window.updateWeekGlobalPreviewV83();
  }
  window.updateWeekGlobalPreviewV83=function(){
    const p=document.getElementById('weekPersonV83')?.value||firstUserName();
    const t=document.getElementById('weekTypeV83')?.value||'Travail';
    const pd=document.getElementById('weekPersonDotV83'),td=document.getElementById('weekTypeDotV83');
    if(pd)pd.style.background=people[p]||'#B99BFF';if(td)td.style.background=colors[t]||'#FF9EB5';
  };
  window.toggleWeekDayV83=function(day){
    const el=document.getElementById('weekday_'+safeIdV83(day));if(el)el.classList.toggle('open');
  };
  window.updateWeekDaySummaryV83=function(day){
    const count=slots.filter(([key])=>document.getElementById(`active_${day}_${key}`)?.checked).length;
    const rest=document.getElementById('rest_'+day)?.checked;
    const el=document.getElementById('weeksummary_'+safeIdV83(day));if(el)el.textContent=rest?'Repos':count?`${count} créneau${count>1?'x':''}`:'À compléter';
  };

  window.openWeekTemplate=function(editMode=false){
    if(!editMode){
      editingWeekTemplateId=null;tempSelectedWeeks=[];
      if(document.getElementById('weekName'))weekName.value='Semaine type';
      if(document.getElementById('weekCycle'))weekCycle.value='Semaine A';
    }
    const wf=document.getElementById('weekForms');if(!wf)return alert('Formulaire semaine introuvable.');
    ensureWeekGlobalV83(firstUserName(),'Travail');
    wf.innerHTML=days.map((d,di)=>`<div class="week-day-accordion ${di===0?'open':''}" id="weekday_${safeIdV83(d)}"><button type="button" class="week-day-head" onclick="toggleWeekDayV83('${d}')"><span>${d}</span><span class="week-day-summary" id="weeksummary_${safeIdV83(d)}">À compléter</span><span class="chevron">⌄</span></button><div class="week-day-body"><label style="display:flex;align-items:center;gap:8px;margin:4px 0 8px"><input type="checkbox" id="rest_${d}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV83('${d}')"> Repos complet</label>${slots.map(([key,label])=>{const [a,b]=defaultTimesV83(key);return `<div class="slot"><div class="slot-title">${label}</div><label style="font-weight:800;display:flex;gap:8px;align-items:center"><input type="checkbox" id="active_${d}_${key}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV83('${d}')"> Ajouter ce créneau</label><div class="grid2"><div><label>Début</label><input type="time" id="s_${d}_${key}" value="${a}"></div><div><label>Fin</label><input type="time" id="e_${d}_${key}" value="${b}"></div></div></div>`}).join('')}</div></div>`).join('');
    if(typeof renderWeekPickCalendar==='function')renderWeekPickCalendar();
    const modal=document.getElementById('weekModal');if(modal){modal.classList.add('show');updateFloatingVisibility();}
  };

  window.saveWeekTemplate=function(){
    const globalPerson=document.getElementById('weekPersonV83')?.value||firstUserName();
    const globalType=document.getElementById('weekTypeV83')?.value||'Travail';
    const slotsToSave=[];
    days.forEach(d=>{
      const rest=document.getElementById('rest_'+d);if(rest&&rest.checked)return;
      slots.forEach(([key,label])=>{
        const active=document.getElementById(`active_${d}_${key}`);
        if(active&&active.checked)slotsToSave.push({day:d,label,type:globalType,start:document.getElementById(`s_${d}_${key}`)?.value||'08:00',end:document.getElementById(`e_${d}_${key}`)?.value||'12:00',person:globalPerson});
      });
    });
    const name=(document.getElementById('weekName')?.value||'').trim();
    const cycle=document.getElementById('weekCycle')?.value||'Semaine A';
    const appliedWeeks=[...(tempSelectedWeeks||[])];
    if(!name)return alert('Donne un nom à ta semaine type.');
    if(!slotsToSave.length)return alert('Ajoute au moins un créneau.');
    if(!appliedWeeks.length)return alert('Choisis au moins une semaine concernée.');
    const payload={id:editingWeekTemplateId||'week_'+Date.now(),name,cycle,person:globalPerson,type:globalType,appliedWeeks,slots:slotsToSave};
    if(editingWeekTemplateId)weekTemplates=weekTemplates.map(t=>t.id===editingWeekTemplateId?payload:t);else weekTemplates.push(payload);
    editingWeekTemplateId=null;tempSelectedWeeks=[];closeModals();render();
  };

  window.editWeekTemplate=function(id){
    const t=weekTemplates.find(w=>w.id===id);if(!t)return;
    editingWeekTemplateId=id;window.openWeekTemplate(true);
    weekName.value=t.name;weekCycle.value=t.cycle||'Semaine A';tempSelectedWeeks=[...(t.appliedWeeks||[])];
    const inferredPerson=t.person||(t.slots&&t.slots[0]?.person)||firstUserName();
    const inferredType=t.type||(t.slots&&t.slots[0]?.type)||'Travail';
    ensureWeekGlobalV83(inferredPerson,inferredType);
    days.forEach(d=>{
      const daySlots=(t.slots||[]).filter(s=>s.day===d);
      slots.forEach(([key,label])=>{
        const s=daySlots.find(x=>x.label===label),active=document.getElementById(`active_${d}_${key}`);if(active)active.checked=!!s;
        if(s){const st=document.getElementById(`s_${d}_${key}`),en=document.getElementById(`e_${d}_${key}`);if(st)st.value=s.start;if(en)en.value=s.end;}
      });
      const rest=document.getElementById('rest_'+d);if(rest)rest.checked=daySlots.length===0;
      window.updateWeekDaySummaryV83(d);
      if(daySlots.length){const el=document.getElementById('weekday_'+safeIdV83(d));if(el)el.classList.add('open');}
    });
    if(typeof renderWeekPickCalendar==='function')renderWeekPickCalendar();
  };

  /* Re-apply the explicit palette after startup/render so Light is always truly light. */
  const oldApplyV83=window.applyThemeV82;
  if(typeof oldApplyV83==='function'){
    window.applyThemeV82=function(){oldApplyV83.apply(this,arguments);const resolved=(theme==='auto'?(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'):theme);document.body.classList.toggle('light',resolved==='light');document.body.classList.toggle('crepuscule',resolved==='dark');};
  }
  setTimeout(()=>{if(typeof window.applyThemeV82==='function')window.applyThemeV82();},20);
})();
</script>
'''
if 'id="v83-corrective-script"' not in html:
    html += js

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.3"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1));b=b[:m.start(1)]+str(max(old+1,83))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.3 corrective patch applied')
