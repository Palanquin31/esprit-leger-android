from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.7 — glance-first daily use polish.
# Keep V8.6 theme/native behavior untouched. Improve palette clarity, free advice folding,
# calmer Twilight Premium teaser, and focus today's calendar around the current time.

# 1) Remove exact duplicate colors from the shared palette while preserving order.
m=re.search(r'const palette=\[(.*?)\];',html,re.S)
if not m: raise SystemExit('palette not found')
vals=re.findall(r'"(#[0-9A-Fa-f]{6})"',m.group(1))
unique=[]
for c in vals:
    if c not in unique: unique.append(c)
new_palette='const palette=[\n '+',\n '.join('"'+c+'"' for c in unique)+'\n];'
html=html[:m.start()]+new_palette+html[m.end():]
if len(unique)!=52: raise SystemExit(f'unexpected unique palette size: {len(unique)}')

css=r'''
<style id="v87-fluid-glance-style">
.palette-btn{position:relative;}
.palette-btn.is-selected-v87{
  outline:3px solid #2D2738 !important;
  outline-offset:2px !important;
  box-shadow:0 0 0 2px rgba(255,255,255,.82),0 5px 14px rgba(40,30,70,.16) !important;
}
.palette-btn.is-selected-v87::after{
  content:"✓";position:absolute;inset:50% auto auto 50%;transform:translate(-50%,-50%);
  width:17px;height:17px;line-height:17px;border-radius:50%;background:rgba(255,255,255,.92);
  color:#2D2738;font-size:11px;font-weight:950;text-align:center;text-shadow:none;
}
body.crepuscule .palette-btn.is-selected-v87{
  outline-color:#F4EFF7 !important;
  box-shadow:0 0 0 2px rgba(129,114,170,.52),0 5px 15px rgba(0,0,0,.28) !important;
}

#freeAdviceCardV67{cursor:pointer;transition:max-height .2s ease,padding .2s ease;}
#freeAdviceCardV67 .ribbon-advice{display:flex;align-items:center;justify-content:center;gap:9px;}
#freeAdviceCardV67 .ribbon-advice::after{content:"⌃";font-size:16px;opacity:.72;transition:transform .18s ease;}
#freeAdviceCardV67.v87-collapsed #advice,
#freeAdviceCardV67.v87-collapsed .free-premium-info{display:none !important;}
#freeAdviceCardV67.v87-collapsed .ribbon-advice{margin-bottom:-2px;}
#freeAdviceCardV67.v87-collapsed .ribbon-advice::after{transform:rotate(180deg);}

body.crepuscule .free-premium-info{
  background:linear-gradient(135deg,#332c3a,#2d2933) !important;
  border-color:rgba(207,190,225,.16) !important;color:#C9C0CE !important;box-shadow:none !important;
}
body.crepuscule .free-premium-info b{color:#CDBBE4 !important;}
body.crepuscule .free-premium-info span{color:#B9B0BF !important;}

.past-hours-toggle-v87{
  width:100%;border:1px solid rgba(138,122,154,.22);background:rgba(244,239,255,.72);color:var(--ink);
  border-radius:16px;padding:10px 12px;margin:2px 0 8px;font-weight:850;font-size:12px;text-align:left;
  display:flex;justify-content:space-between;align-items:center;gap:10px;
}
.past-hours-toggle-v87 span{color:var(--muted);font-weight:750;}
body.crepuscule .past-hours-toggle-v87{background:#342e3b !important;border-color:rgba(255,255,255,.09) !important;color:#F1EDF3 !important;}
body.crepuscule .past-hours-toggle-v87 span{color:#BDB4C3 !important;}
.current-hour-v87{background:linear-gradient(90deg,rgba(185,155,255,.08),rgba(255,158,181,.04));border-radius:14px;padding-left:5px;padding-right:5px;}
body.crepuscule .current-hour-v87{background:linear-gradient(90deg,rgba(129,114,170,.15),rgba(173,113,138,.08));}
.now-marker-v87{display:flex;align-items:center;gap:7px;color:#8B6CA8;font-size:11px;font-weight:950;margin:1px 0 4px;}
.now-marker-v87::before{content:"";width:7px;height:7px;border-radius:50%;background:linear-gradient(135deg,var(--lav),var(--pink));box-shadow:0 0 0 3px rgba(185,155,255,.14);}
.now-marker-v87::after{content:"";height:1px;flex:1;background:linear-gradient(90deg,rgba(185,155,255,.55),transparent);}
body.crepuscule .now-marker-v87{color:#C7B6DA;}
</style>
'''

js=r'''
<script id="v87-fluid-glance-script">
(function(){
  window.colorPicker=function(obj,key){
    const current=obj==='people'?people[key]:colors[key];
    return `<div class="palette">${palette.map(c=>`<button type="button" aria-label="Couleur ${c}" class="palette-btn ${current===c?'is-selected-v87':''}" style="background:${c}" onclick="setColor('${obj}','${key}','${c}')"></button>`).join("")}</div>`;
  };
  window.renderSetupPalette=function(){
    const el=document.getElementById("setupPalette");if(!el)return;
    el.innerHTML=palette.map(c=>`<button type="button" class="palette-btn ${setupColor===c?'is-selected-v87':''}" style="background:${c}" onclick="setupColor='${c}';renderSetupPalette();return false"></button>`).join("");
  };
  if(typeof familyMemberColorV62!=='undefined'){
    window.renderFamilyMemberPaletteV62=function(){
      const el=document.getElementById("familyMemberPalette");if(!el)return;
      el.innerHTML=palette.map(c=>`<button type="button" class="palette-btn ${familyMemberColorV62===c?'is-selected-v87':''}" style="background:${c}" onclick="familyMemberColorV62='${c}';renderFamilyMemberPaletteV62();return false"></button>`).join("");
    };
  }
  if(typeof familyMemberColorV65!=='undefined'){
    window.renderFamilyMemberPaletteV65=function(){
      const el=document.getElementById("familyMemberPaletteV65");if(!el)return;
      el.innerHTML=palette.map(c=>`<button type="button" class="palette-btn ${familyMemberColorV65===c?'is-selected-v87':''}" style="background:${c}" onclick="familyMemberColorV65='${c}';renderFamilyMemberPaletteV65();return false"></button>`).join("");
    };
  }

  const adviceCard=document.getElementById('freeAdviceCardV67');
  if(adviceCard && !adviceCard.dataset.v87FoldReady){
    adviceCard.dataset.v87FoldReady='1';adviceCard.setAttribute('role','button');adviceCard.setAttribute('aria-expanded','true');
    adviceCard.addEventListener('click',function(e){
      if(e.target.closest('button,input,select,textarea,a'))return;
      const collapsed=this.classList.toggle('v87-collapsed');
      this.setAttribute('aria-expanded',collapsed?'false':'true');
    });
  }

  window.pastHoursExpandedV87=false;
  function sameDayV87(a,b){return a&&b&&a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();}
  function hhmmV87(d){return String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');}
  window.togglePastHoursV87=function(e){
    if(e){e.preventDefault();e.stopPropagation();}
    window.pastHoursExpandedV87=!window.pastHoursExpandedV87;
    if(typeof renderDay==='function')renderDay();
  };
  window.renderDay=function(){
    const now=new Date();const today=sameDayV87(selectedDate,now);const allEvents=eventsForDate(selectedDate);
    const currentHour=now.getHours();const contextualStart=today?Math.max(0,currentHour-1):0;
    const startHour=(today&&!window.pastHoursExpandedV87)?contextualStart:0;let html="";
    if(today && contextualStart>0){
      const hiddenCount=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)<contextualStart).length;
      if(window.pastHoursExpandedV87){
        html+=`<button type="button" class="past-hours-toggle-v87" onclick="togglePastHoursV87(event)"><b>⌃ Replier les heures passées</b><span>${hiddenCount?hiddenCount+' activité'+(hiddenCount>1?'s':''):''}</span></button>`;
      }else{
        const lastHidden=contextualStart-1;const range=lastHidden===0?'00h':`00h–${String(lastHidden).padStart(2,'0')}h`;
        html+=`<button type="button" class="past-hours-toggle-v87" onclick="togglePastHoursV87(event)"><b>Plus tôt aujourd’hui · ${range}</b><span>${hiddenCount?hiddenCount+' activité'+(hiddenCount>1?'s':'')+' · ':''}Afficher ▾</span></button>`;
      }
    }
    for(let h=startHour;h<24;h++){
      const hs=String(h).padStart(2,"0")+":00";const ev=allEvents.filter(e=>parseInt((e.start||'00:00').slice(0,2),10)===h);
      const current=today&&h===currentHour;const marker=current?`<div class="now-marker-v87">Maintenant · ${hhmmV87(now)}</div>`:'';
      html+=`<div class="hour-row ${current?'current-hour-v87':''}"><div class="hour">${hs}</div><div class="hour-content">${marker}${ev.map(e=>`<div class="event-pill" style="background:${eventUserColor(e)}; --task-color:${eventTaskColor(e)}" onclick='openDetails(${JSON.stringify(e)})'>${emoji(e.type)} ${e.title}<div class="event-meta">${e.start}-${e.end} · ${e.person}</div></div>`).join("")}</div></div>`;
    }
    calendar.innerHTML=html;
  };

  function refocusTodayV87(){
    if(document.hidden)return;
    if(typeof view!=='undefined'&&view==='jour'&&document.getElementById('planning')?.classList.contains('active')){
      window.pastHoursExpandedV87=false;if(typeof renderDay==='function')renderDay();
    }
  }
  document.addEventListener('visibilitychange',refocusTodayV87);
  window.addEventListener('focus',refocusTodayV87);
  setTimeout(()=>{try{if(typeof renderDay==='function'&&view==='jour')renderDay();}catch(e){}},80);
})();
</script>
'''

if 'id="v87-fluid-glance-style"' not in html: html += css
if 'id="v87-fluid-glance-script"' not in html: html += js

# Sanity checks.
mp=re.search(r'const palette=\[(.*?)\];',html,re.S)
final_vals=re.findall(r'"(#[0-9A-Fa-f]{6})"',mp.group(1))
if len(final_vals)!=len(set(final_vals)): raise SystemExit('palette duplicates remain')
if html.count('id="v87-fluid-glance-style"')!=1 or html.count('id="v87-fluid-glance-script"')!=1:
    raise SystemExit('V8.7 blocks missing or duplicated')
if 'id="v86-native-theme-controller"' not in html: raise SystemExit('V8.6 theme controller unexpectedly missing')

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.7"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,87))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.7 glance-first calendar and palette polish applied')
