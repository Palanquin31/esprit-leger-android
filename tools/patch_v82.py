from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.2 — daily-use fluidity: deterministic themes, softer twilight,
# compact week templates with person/type, and collapsible Premium advice.

# 1) Theme selector calls a dedicated theme controller instead of relying on render().
html=html.replace('onchange="theme=this.value;render()"','onchange="setAppThemeV82(this.value)"',1)

css=r'''
<style id="v82-fluidity-style">
/* Softer, calmer twilight palette. Appended last so old dark rules cannot win. */
body.crepuscule{
  background:linear-gradient(160deg,#1d1a23,#211d28) !important;
  color:#F1EDF3 !important;
  --ink:#F1EDF3 !important;
  --muted:#C6BEC9 !important;
}
body.crepuscule .phone{background:transparent !important;}
body.crepuscule .top-bubble{
  background:linear-gradient(135deg,#51465f,#655064) !important;
  color:#F5F1F6 !important;
  border-color:rgba(255,255,255,.09) !important;
  box-shadow:0 14px 32px rgba(0,0,0,.16) !important;
}
body.crepuscule .card,
body.crepuscule .day-col,
body.crepuscule .listitem,
body.crepuscule .coloritem,
body.crepuscule .slot,
body.crepuscule .suggestion,
body.crepuscule .sheet,
body.crepuscule .plan-card,
body.crepuscule .dayform,
body.crepuscule .slot-choice,
body.crepuscule .color-popup,
body.crepuscule input,
body.crepuscule select,
body.crepuscule textarea,
body.crepuscule .nav,
body.crepuscule .tabs,
body.crepuscule .quick-add-menu,
body.crepuscule .mood-floating{
  background:#2a2530 !important;
  color:#F1EDF3 !important;
  border-color:rgba(255,255,255,.09) !important;
}
body.crepuscule .soft-calendar{background:linear-gradient(135deg,#2c2733,#302a38) !important;}
body.crepuscule .soft-advice{background:linear-gradient(135deg,#29332f,#343027) !important;}
body.crepuscule p,body.crepuscule .note,body.crepuscule .event-meta,
body.crepuscule .details-line,body.crepuscule label{color:#C6BEC9 !important;}
body.crepuscule .smallbtn,body.crepuscule .ghost,body.crepuscule .mood,
body.crepuscule .tab,body.crepuscule .chip,body.crepuscule .day-choice{
  background:#39323f !important;color:#F1EDF3 !important;
}
body.crepuscule .primary,body.crepuscule .mood.active,
body.crepuscule .tab.active,body.crepuscule .nav button.active{
  background:linear-gradient(135deg,#8172aa,#ad718a) !important;color:#fff !important;
}
body.crepuscule .card-title-ribbon{filter:saturate(.72) brightness(.88);}
body.crepuscule .card{box-shadow:0 10px 24px rgba(0,0,0,.13) !important;}

/* Compact accordion week editor. */
#weekForms{display:flex;flex-direction:column;gap:8px;}
.week-day-accordion{border:1px solid #eee4fa;border-radius:20px;overflow:hidden;background:#fff;}
.week-day-head{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:14px 15px;background:transparent;color:var(--ink);font-weight:950;text-align:left;}
.week-day-head .week-day-summary{font-size:12px;color:var(--muted);font-weight:800;margin-left:auto;}
.week-day-head .chevron{transition:transform .18s ease;font-size:18px;}
.week-day-accordion.open .chevron{transform:rotate(180deg);}
.week-day-body{display:none;padding:0 12px 12px;}
.week-day-accordion.open .week-day-body{display:block;}
.week-day-body .slot{margin-top:8px;padding:11px;}
.week-slot-extra{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;}
.week-color-preview{display:flex;gap:8px;align-items:center;margin-top:2px;font-size:12px;color:var(--muted);font-weight:800;}
.week-color-dot{width:12px;height:12px;border-radius:50%;display:inline-block;border:1px solid rgba(0,0,0,.08);}
body.crepuscule .week-day-accordion{background:#2a2530!important;border-color:rgba(255,255,255,.09)!important;}
body.crepuscule .week-day-head{color:#F1EDF3!important;}
@media(max-width:370px){.week-slot-extra{grid-template-columns:1fr;}}
</style>
'''
if 'id="v82-fluidity-style"' not in html:
    html += css

js=r'''
<script id="v82-fluidity-script">
(function(){
  /* --- Deterministic theme controller --- */
  const mediaV82=window.matchMedia?window.matchMedia('(prefers-color-scheme: dark)'):null;
  function resolvedThemeV82(){return theme==='auto'?(mediaV82&&mediaV82.matches?'dark':'light'):theme;}
  window.applyThemeV82=function(){
    const resolved=resolvedThemeV82();
    document.body.classList.remove('light','crepuscule');
    document.body.classList.add(resolved==='dark'?'crepuscule':'light');
    const sel=document.getElementById('themeSelect');
    if(sel && ['light','dark','auto'].includes(theme))sel.value=theme;
  };
  window.setAppThemeV82=function(value){
    theme=['light','dark','auto'].includes(value)?value:'light';
    window.applyThemeV82();
    if(typeof saveState==='function')saveState();
  };
  const oldRenderV82=window.render;
  if(typeof oldRenderV82==='function'){
    window.render=function(){
      const out=oldRenderV82.apply(this,arguments);
      window.applyThemeV82();
      return out;
    };
  }
  const onSystemThemeV82=()=>{if(theme==='auto')window.applyThemeV82();};
  if(mediaV82){
    if(mediaV82.addEventListener)mediaV82.addEventListener('change',onSystemThemeV82);
    else if(mediaV82.addListener)mediaV82.addListener(onSystemThemeV82);
  }
  setTimeout(window.applyThemeV82,0);

  /* --- Compact typical-week editor --- */
  const activityTypesV82=['Travail','École','Rendez-vous','Sport','Courses','Repas','Temps pour soi','Tâche'];
  function safeIdV82(s){return String(s).replace(/[^a-zA-Z0-9_-]/g,'_');}
  function personOptionsV82(selected){
    const names=Object.keys(people);if(!names.length)names.push(firstUserName());
    return names.map(n=>`<option value="${n}" ${n===selected?'selected':''}>${n}</option>`).join('');
  }
  function typeOptionsV82(selected){return activityTypesV82.map(t=>`<option value="${t}" ${t===selected?'selected':''}>${emoji(t)} ${t}</option>`).join('');}
  function defaultTimesV82(key){return key==='matin'?['08:00','12:00']:key==='midi'?['12:00','14:00']:key==='soir'?['17:00','20:00']:['21:00','23:00'];}
  window.toggleWeekDayV82=function(day){
    const el=document.getElementById('weekday_'+safeIdV82(day));if(!el)return;
    el.classList.toggle('open');
  };
  window.updateWeekSlotColorsV82=function(day,key){
    const p=document.getElementById(`wp_${day}_${key}`)?.value||firstUserName();
    const t=document.getElementById(`wt_${day}_${key}`)?.value||'Travail';
    const pd=document.getElementById(`wpdot_${day}_${key}`),td=document.getElementById(`wtdot_${day}_${key}`);
    if(pd)pd.style.background=people[p]||'#B99BFF';if(td)td.style.background=colors[t]||'#B99BFF';
  };
  window.updateWeekDaySummaryV82=function(day){
    const count=slots.filter(([key])=>document.getElementById(`active_${day}_${key}`)?.checked).length;
    const rest=document.getElementById('rest_'+day)?.checked;
    const el=document.getElementById('weeksummary_'+safeIdV82(day));if(el)el.textContent=rest?'Repos':count?`${count} créneau${count>1?'x':''}`:'À compléter';
  };
  window.openWeekTemplate=function(editMode=false){
    if(!editMode){
      editingWeekTemplateId=null;tempSelectedWeeks=[];
      if(document.getElementById('weekName'))weekName.value='Semaine type';
      if(document.getElementById('weekCycle'))weekCycle.value='Semaine A';
    }
    const wf=document.getElementById('weekForms');if(!wf)return alert('Formulaire semaine introuvable.');
    wf.innerHTML=days.map((d,di)=>`<div class="week-day-accordion ${di===0?'open':''}" id="weekday_${safeIdV82(d)}">
      <button type="button" class="week-day-head" onclick="toggleWeekDayV82('${d}')"><span>${d}</span><span class="week-day-summary" id="weeksummary_${safeIdV82(d)}">À compléter</span><span class="chevron">⌄</span></button>
      <div class="week-day-body">
        <label style="display:flex;align-items:center;gap:8px;margin:4px 0 8px"><input type="checkbox" id="rest_${d}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV82('${d}')"> Repos complet</label>
        ${slots.map(([key,label])=>{const [a,b]=defaultTimesV82(key);return `<div class="slot"><div class="slot-title">${label}</div><label style="font-weight:800;display:flex;gap:8px;align-items:center"><input type="checkbox" id="active_${d}_${key}" style="width:auto;margin:0" onchange="updateWeekDaySummaryV82('${d}')"> Ajouter ce créneau</label><div class="grid2"><div><label>Début</label><input type="time" id="s_${d}_${key}" value="${a}"></div><div><label>Fin</label><input type="time" id="e_${d}_${key}" value="${b}"></div></div><div class="week-slot-extra"><div><label>Membre</label><select id="wp_${d}_${key}" onchange="updateWeekSlotColorsV82('${d}','${key}')">${personOptionsV82(firstUserName())}</select></div><div><label>Type d’activité</label><select id="wt_${d}_${key}" onchange="updateWeekSlotColorsV82('${d}','${key}')">${typeOptionsV82('Travail')}</select></div></div><div class="week-color-preview"><span class="week-color-dot" id="wpdot_${d}_${key}" style="background:${people[firstUserName()]||'#B99BFF'}"></span> membre <span class="week-color-dot" id="wtdot_${d}_${key}" style="background:${colors.Travail||'#FF9EB5'}"></span> activité</div></div>`}).join('')}
      </div></div>`).join('');
    if(typeof renderWeekPickCalendar==='function')renderWeekPickCalendar();
    const modal=document.getElementById('weekModal');if(modal){modal.classList.add('show');updateFloatingVisibility();}
  };
  window.saveWeekTemplate=function(){
    const slotsToSave=[];
    days.forEach(d=>{
      const rest=document.getElementById('rest_'+d);if(rest&&rest.checked)return;
      slots.forEach(([key,label])=>{
        const active=document.getElementById(`active_${d}_${key}`);
        if(active&&active.checked)slotsToSave.push({day:d,label,type:document.getElementById(`wt_${d}_${key}`)?.value||'Travail',start:document.getElementById(`s_${d}_${key}`)?.value||'08:00',end:document.getElementById(`e_${d}_${key}`)?.value||'12:00',person:document.getElementById(`wp_${d}_${key}`)?.value||firstUserName()});
      });
    });
    const name=(document.getElementById('weekName')?.value||'').trim();const cycle=document.getElementById('weekCycle')?.value||'Semaine A';const appliedWeeks=[...(tempSelectedWeeks||[])];
    if(!name)return alert('Donne un nom à ta semaine type.');if(!slotsToSave.length)return alert('Ajoute au moins un créneau.');if(!appliedWeeks.length)return alert('Choisis au moins une semaine concernée.');
    const payload={id:editingWeekTemplateId||'week_'+Date.now(),name,cycle,appliedWeeks,slots:slotsToSave};
    if(editingWeekTemplateId)weekTemplates=weekTemplates.map(t=>t.id===editingWeekTemplateId?payload:t);else weekTemplates.push(payload);
    editingWeekTemplateId=null;tempSelectedWeeks=[];closeModals();render();
  };
  window.editWeekTemplate=function(id){
    const t=weekTemplates.find(w=>w.id===id);if(!t)return;
    editingWeekTemplateId=id;window.openWeekTemplate(true);
    weekName.value=t.name;weekCycle.value=t.cycle||'Semaine A';tempSelectedWeeks=[...(t.appliedWeeks||[])];
    days.forEach(d=>{
      const daySlots=(t.slots||[]).filter(s=>s.day===d);
      slots.forEach(([key,label])=>{
        const s=daySlots.find(x=>x.label===label),active=document.getElementById(`active_${d}_${key}`);if(active)active.checked=!!s;
        if(s){
          const st=document.getElementById(`s_${d}_${key}`),en=document.getElementById(`e_${d}_${key}`),ps=document.getElementById(`wp_${d}_${key}`),ts=document.getElementById(`wt_${d}_${key}`);
          if(st)st.value=s.start;if(en)en.value=s.end;if(ps)ps.value=s.person||firstUserName();if(ts)ts.value=s.type||'Travail';window.updateWeekSlotColorsV82(d,key);
        }
      });
      const rest=document.getElementById('rest_'+d);if(rest)rest.checked=daySlots.length===0;
      window.updateWeekDaySummaryV82(d);
      if(daySlots.length){const el=document.getElementById('weekday_'+safeIdV82(d));if(el)el.classList.add('open');}
    });
    renderWeekPickCalendar();
  };

  /* --- Allège ma semaine becomes a true toggle. --- */
  const oldLightenV82=window.runAiWeekLighten;
  if(typeof oldLightenV82==='function'){
    window.runAiWeekLighten=function(){
      const box=document.getElementById('aiWeeklyResult');
      if(box && box.style.display!=='none' && getComputedStyle(box).display!=='none'){
        box.style.display='none';box.classList.remove('ai-visible');return;
      }
      return oldLightenV82.apply(this,arguments);
    };
  }
})();
</script>
'''
if 'id="v82-fluidity-script"' not in html:
    html += js

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.2"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1));b=b[:m.start(1)]+str(max(old+1,82))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.2 fluidity patch applied')
