from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.1 — daily-use improvements on top of V8.0.
# 1) Add a precise date field to scheduled items while retaining the legacy weekday select hidden for compatibility.
old='<label>Titre</label><input id="title" placeholder="Ex : Running 30 min"><label>Jour</label><select id="day">'
new='<label>Titre</label><input id="title" placeholder="Ex : Running 30 min"><label>Date</label><input type="date" id="eventDate"><div class="v81-legacy-day" aria-hidden="true"><label>Jour</label><select id="day">'
if old in html:
    html=html.replace(old,new,1)
    # Close the wrapper immediately after the weekday select.
    end_select='</select>\n<div class="slot-choice">'
    html=html.replace(end_select,'</select></div>\n<div class="slot-choice">',1)

# 2) Keep event edit actions visible above the fixed bottom navigation.
css=r'''
<style id="v81-daily-use-style">
.v81-legacy-day{display:none!important;}
#eventModal{padding-bottom:118px!important;align-items:flex-end!important;}
#eventModal .sheet{
  max-height:calc(100dvh - 150px)!important;
  overflow-y:auto!important;
  overscroll-behavior:contain!important;
  padding-bottom:14px!important;
}
#eventModal .event-actions-v81{
  position:sticky!important;
  bottom:0!important;
  z-index:20!important;
  padding:12px 0 4px!important;
  margin-top:10px!important;
  background:linear-gradient(to bottom,rgba(255,255,255,.72),#fff 26%)!important;
  border-radius:0 0 22px 22px!important;
}
body.twilight #eventModal .event-actions-v81,
body.dark #eventModal .event-actions-v81{
  background:linear-gradient(to bottom,rgba(37,31,50,.72),rgb(37,31,50) 26%)!important;
}
.soft-calendar{touch-action:pan-y!important;}
</style>
'''
if 'id="v81-daily-use-style"' not in html:
    html += css

# Wrap validate/delete buttons once, so they stick to the bottom of the modal sheet.
buttons='<button class="primary modal-validate" onclick="saveEvent()">Valider</button><button id="deleteBtn" class="danger" style="display:none;margin-top:8px;width:100%" onclick="deleteEditing()">Supprimer cette donnée</button>'
if buttons in html:
    html=html.replace(buttons,'<div class="event-actions-v81">'+buttons+'</div>',1)

# Let the calendar bubble own its horizontal swipes instead of the global tab swipe engine.
html=html.replace("return !!(t?.closest?.('.modal,.nav,.fab,.fab-global,.quick-add-menu,input,textarea,select,button,.tabs,.tab'));",
                  "return !!(t?.closest?.('.modal,.nav,.fab,.fab-global,.quick-add-menu,input,textarea,select,button,.tabs,.tab,.soft-calendar'));",1)

js=r'''
<script id="v81-dated-events-calendar-swipe">
(function(){
  const iso=d=>{const x=new Date(d);x.setMinutes(x.getMinutes()-x.getTimezoneOffset());return x.toISOString().slice(0,10)};
  const fromIso=s=>{if(!s)return null;const p=s.split('-').map(Number);if(p.length!==3||!p[0])return null;return new Date(p[0],p[1]-1,p[2],12,0,0,0)};
  const pretty=s=>{const d=fromIso(s);return d?d.toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}):''};
  function nearestDateForLegacy(day){
    if(day==="Aujourd'hui")return new Date();
    const names=['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'];
    const target=names.indexOf(day);const d=new Date(selectedDate||new Date());
    if(target<0)return d;
    let diff=(target-d.getDay()+7)%7;
    d.setDate(d.getDate()+diff);return d;
  }
  function repeatMatch(e,date){
    const target=fromIso(e.date); if(!target)return false;
    const same=iso(target)===iso(date); const rep=e.repeat||'Aucune';
    if(rep==='Aucune')return same;
    if(date < new Date(target.getFullYear(),target.getMonth(),target.getDate()))return false;
    if(rep==='Chaque semaine'||rep==='Semaine A'||rep==='Semaine B')return date.getDay()===target.getDay();
    if(rep==="Tous les jours d'école")return date.getDay()>=1&&date.getDay()<=5;
    if(rep==='Chaque mois')return date.getDate()===target.getDate();
    return same;
  }
  window.eventMatchesDateV81=function(e,date){
    if(e&&e.date)return repeatMatch(e,date);
    const dayName=dayNameFromDate(date);const isToday=date.toDateString()===new Date().toDateString();
    return e?.day===dayName || (isToday&&e?.day==="Aujourd'hui");
  };
  window.eventsForDate=function(date){
    const normal=events.filter(e=>window.eventMatchesDateV81(e,date));
    return normal.concat(typeof buildTemplateEventsForDate==='function'?buildTemplateEventsForDate(date):[]);
  };
  window.eventMatchesSelectedDay=function(e){return window.eventMatchesDateV81(e,selectedDate);};

  const oldOpenAdd=window.openAdd;
  window.openAdd=function(){
    if(typeof oldOpenAdd==='function')oldOpenAdd.apply(this,arguments);
    const d=document.getElementById('eventDate');if(d)d.value=iso(selectedDate||new Date());
  };
  window.editEvent=function(i){
    editingIndex=i;const e=events[i];
    eventTitle.textContent='Modifier';deleteBtn.style.display='block';
    type.value=e.type;title.value=e.title;day.value=e.day||dayNameFromDate(selectedDate);
    const df=document.getElementById('eventDate');if(df)df.value=e.date||iso(nearestDateForLegacy(e.day));
    start.value=e.start;end.value=e.end;person.value=e.person;repeat.value=e.repeat;
    if(document.getElementById('dayPart'))dayPart.value='custom';
    eventModal.classList.add('show');updateFloatingVisibility();
  };
  window.saveEvent=function(){
    const df=document.getElementById('eventDate');
    if(!df?.value){alert('Choisis une date');return;}
    const chosen=fromIso(df.value);if(!chosen){alert('Date invalide');return;}
    const e={type:type.value,title:title.value.trim(),date:df.value,day:dayNameFromDate(chosen),start:start.value,end:end.value,person:(person.value||firstUserName()),repeat:repeat.value};
    if(!e.title){alert('Ajoute un titre');return;}
    if(editingIndex===null)events.push(e);else events[editingIndex]=e;
    closeModals();render();
  };
  window.openDetails=function(e){
    const when=e.date?pretty(e.date):(e.day||'');
    detailContent.innerHTML=`<div class="event-pill" style="background:${eventUserColor(e)}; --task-color:${eventTaskColor(e)}">${emoji(e.type)} ${e.title}<div class="event-meta">${when} · ${e.start}-${e.end} · ${e.person} · ${e.repeat}</div></div>`;
    detailModal.classList.add('show');
  };

  // Dedicated swipe only inside the calendar card: left = next period, right = previous.
  let sx=0,sy=0,swiped=false;
  function card(){return document.querySelector('#planning.active .soft-calendar');}
  document.addEventListener('touchstart',function(e){
    const c=card();if(!c||!c.contains(e.target)||e.touches.length!==1||e.target.closest('button,input,select,textarea')){sx=sy=0;return;}
    sx=e.touches[0].clientX;sy=e.touches[0].clientY;swiped=false;
  },true);
  document.addEventListener('touchend',function(e){
    if(!sx)return;const c=card();if(!c){sx=sy=0;return;}
    const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;sx=sy=0;
    if(Math.abs(dx)>55&&Math.abs(dx)>Math.abs(dy)*1.4){
      swiped=true;e.preventDefault();e.stopImmediatePropagation();
      if(typeof navigatePlanningPeriod==='function')navigatePlanningPeriod(dx<0?1:-1);
    }
  },true);
  document.addEventListener('click',function(e){
    if(swiped&&e.target.closest('.soft-calendar')){e.preventDefault();e.stopImmediatePropagation();swiped=false;}
  },true);
})();
</script>
'''
if 'id="v81-dated-events-calendar-swipe"' not in html:
    html += js

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.1"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1));b=b[:m.start(1)]+str(max(old+1,81))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.1 dated events, safe edit actions and calendar swipe applied')
