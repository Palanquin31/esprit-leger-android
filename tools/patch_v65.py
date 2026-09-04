from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Startup stability: render() must not call Premium UI code before it exists.
html=html.replace(' applyPremiumUiState();',' if(typeof applyPremiumUiState==="function") applyPremiumUiState();',1)

# 2) Real family member modal (the previous escaped block could be rendered as text in some builds).
if 'id="familyMemberModalV65"' not in html:
    family_modal='''
<div class="modal" id="familyMemberModalV65"><div class="sheet">
  <button class="close" onclick="document.getElementById('familyMemberModalV65').classList.remove('show')">Fermer</button>
  <h2>Ajouter un membre</h2>
  <p class="note">Ajoute un prénom et choisis sa couleur dans le planning.</p>
  <label>Prénom</label><input id="familyMemberNameV65" placeholder="Ex : Dorian">
  <label>Couleur</label><div class="palette" id="familyMemberPaletteV65"></div>
  <button class="primary modal-validate" onclick="saveFamilyMemberV65()">Ajouter</button>
</div></div>
'''
    html=html.replace('</body>',family_modal+'</body>',1)

# 3) Backup / restore modal and card.
if 'id="backupModalV65"' not in html:
    backup_modal='''
<div class="modal" id="backupModalV65"><div class="sheet">
  <button class="close" onclick="document.getElementById('backupModalV65').classList.remove('show')">Fermer</button>
  <h2>Sauvegarde de mes données</h2>
  <p class="note">Copie ce bloc dans un fichier ou une note avant de désinstaller l'application. Pour restaurer, colle une sauvegarde ici puis appuie sur Importer.</p>
  <textarea id="backupTextV65" rows="12" style="width:100%;box-sizing:border-box;border-radius:16px;padding:12px"></textarea>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">
    <button class="primary" onclick="generateBackupV65()">Générer la sauvegarde</button>
    <button class="smallbtn" onclick="copyBackupV65()">Copier</button>
    <button class="smallbtn" onclick="importBackupV65()">Importer</button>
  </div>
</div></div>
'''
    html=html.replace('</body>',backup_modal+'</body>',1)

v65='''
<script id="v65-stability-ai">
/* V6.5 stability + smarter local assistant */
let familyMemberColorV65="#8ED6FF";
function renderFamilyMemberPaletteV65(){
  const el=document.getElementById("familyMemberPaletteV65"); if(!el)return;
  el.innerHTML=palette.map(c=>`<button class="palette-btn" style="background:${c};${familyMemberColorV65===c?'outline:3px solid #2D2738':''}" onclick="familyMemberColorV65='${c}';renderFamilyMemberPaletteV65();return false"></button>`).join("");
}
function addFamilyMember(){
  const m=document.getElementById("familyMemberModalV65"),n=document.getElementById("familyMemberNameV65");
  if(n)n.value=""; familyMemberColorV65="#8ED6FF"; renderFamilyMemberPaletteV65(); if(m)m.classList.add("show");
  if(typeof updateFloatingVisibility==="function")updateFloatingVisibility();
}
function saveFamilyMemberV65(){
  const name=(document.getElementById("familyMemberNameV65")?.value||"").trim();
  if(!name){alert("Ajoute le prénom du membre.");return;}
  people[name]=familyMemberColorV65; document.getElementById("familyMemberModalV65")?.classList.remove("show"); render();
}

function minutesV65(t){const [h,m]=(t||"00:00").split(":").map(Number);return h*60+m;}
function durationV65(e){return Math.max(0,minutesV65(e.end)-minutesV65(e.start));}
function overlapsV65(ev){
  const a=[...ev].sort((x,y)=>minutesV65(x.start)-minutesV65(y.start));let n=0;
  for(let i=1;i<a.length;i++)if(minutesV65(a[i].start)<minutesV65(a[i-1].end))n++;
  return n;
}
function weekSerenityV65(daysData){
  if(!daysData.length)return 100;
  const totalEvents=daysData.reduce((s,d)=>s+d.ev.length,0);
  if(totalEvents===0 && floating.length===0 && mood!=="fatigue" && mood!=="epuisee")return 100;
  const avg=daysData.reduce((s,d)=>s+d.score,0)/daysData.length;
  const min=Math.min(...daysData.map(d=>d.score));
  let s=Math.round(avg*0.55+min*0.45);
  const maxMinutes=Math.max(...daysData.map(d=>d.minutes));
  if(maxMinutes>=600)s-=5; else if(maxMinutes>=480)s-=3;
  return Math.max(0,Math.min(100,s));
}
function runAiWeekLighten(){
  if(!isPremium){alert("Cette fonction est disponible en Premium.");return;}
  const card=document.getElementById("aiWeeklyResult"),content=document.getElementById("aiWeeklyContent"); if(!card||!content)return;
  const startW=weekStart(selectedDate);
  const daysData=days.map((name,i)=>{const date=addDays(startW,i),ev=eventsForDate(date);const minutes=ev.reduce((s,e)=>s+durationV65(e),0);return{name,date,ev,minutes,late:ev.filter(e=>minutesV65(e.start)>=19*60).length,score:computeSerenityScore(ev),overlaps:overlapsV65(ev)};});
  const totalEvents=daysData.reduce((s,d)=>s+d.ev.length,0),weekScore=weekSerenityV65(daysData);
  const busiest=[...daysData].sort((a,b)=>b.minutes-a.minutes)[0],lightest=[...daysData].sort((a,b)=>a.minutes-b.minutes)[0];
  const suggestions=[`🌿 Score de sérénité hebdomadaire estimé : ${weekScore}/100.`];
  if(totalEvents===0){
    suggestions.push("🪶 Aucun rendez-vous ni activité n’est planifié cette semaine : ta marge est maximale.");
    if(floating.length)suggestions.push(`🧩 Tu as cependant ${floating.length} tâche(s) à placer : répartis-les progressivement plutôt que de les concentrer sur une seule journée.`);
  }else{
    if(busiest.minutes>=360)suggestions.push(`📆 ${busiest.name} est la journée la plus chargée (${Math.round(busiest.minutes/6)/10} h planifiées, score ${busiest.score}/100). Évite d’y ajouter une contrainte importante.`);
    if(busiest.overlaps)suggestions.push(`⚠️ ${busiest.name} contient ${busiest.overlaps} chevauchement(s) d’horaires. C’est prioritaire à corriger.`);
    if(lightest && busiest && lightest.name!==busiest.name && busiest.minutes-lightest.minutes>=120){
      const movable=busiest.ev.find(e=>["Tâche","Courses","Sport","Temps pour soi"].includes(e.type))||busiest.ev[busiest.ev.length-1];
      if(movable)suggestions.push(`↔️ ${lightest.name} est nettement plus léger. Si c’est possible, déplacer « ${movable.title} » de ${busiest.name} vers ${lightest.name} équilibrerait mieux la semaine.`);
    }
    const late=daysData.reduce((s,d)=>s+d.late,0);if(late>=2)suggestions.push(`🌙 ${late} activité(s) commencent après 19 h. Essaie de préserver au moins une soirée totalement libre.`);
  }
  if(mood==="fatigue"||mood==="epuisee")suggestions.push("😴 Ton état de fatigue est pris en compte : privilégie les tâches courtes, les pauses et la délégation avant d’ajouter des obligations.");
  if(floating.length>0)suggestions.push(`🧩 ${floating.length} tâche(s) restent à placer. Commence par les journées ayant les meilleurs scores.`);
  if(liveWeather){if(liveWeather.rain)suggestions.push("☂ La météo locale est humide : regroupe les déplacements et privilégie les tâches intérieures.");else if(liveWeather.temperature>=30)suggestions.push(`☀ Il fait environ ${Math.round(liveWeather.temperature)}°C : place les activités extérieures tôt le matin ou en soirée.`);}
  if(weekScore>=85 && totalEvents>0)suggestions.push("✅ La semaine est globalement bien équilibrée : garde volontairement des créneaux vides.");
  else if(weekScore<65)suggestions.push("⚠️ La semaine commence à être chargée : déplace, délègue ou supprime au moins une contrainte non essentielle.");
  content.innerHTML=`<div class="ai-result"><b>Analyse de ta semaine</b><ul>${suggestions.map(s=>`<li>${s}</li>`).join("")}</ul><p class="note">Assistant intelligent local V6.5 : analyse du planning, des chevauchements, de la répartition, des tâches, de la fatigue et de la météo.</p></div>`;
  card.classList.add("ai-visible");card.style.display="block";card.scrollIntoView({behavior:"smooth",block:"start"});
}

function dayNameFromOffsetV65(offset){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()+offset);return d.toLocaleDateString("fr-FR",{weekday:"long"}).replace(/^./,c=>c.toUpperCase());}
function normalizeDayFromText(text){
  const l=(text||"").toLowerCase();
  if(l.includes("après-demain")||l.includes("apres-demain"))return dayNameFromOffsetV65(2);
  if(l.includes("demain"))return dayNameFromOffsetV65(1);
  if(l.includes("aujourd'hui")||l.includes("aujourdhui"))return dayNameFromOffsetV65(0);
  for(const d of days){if(l.includes(d.toLowerCase()))return d;}
  return dayNameFromOffsetV65(0);
}
function extractDurationV65(text,def=30){
  const l=(text||"").toLowerCase();
  let m=l.match(/(\d+)\s*h\s*(\d{1,2})?/);if(m)return Number(m[1])*60+(m[2]?Number(m[2]):0);
  m=l.match(/(\d{1,3})\s*(?:min|minutes)/);if(m)return Number(m[1]);return def;
}
function extractTimeV65(text){
  const l=(text||"").toLowerCase();let t=extractTime(text);if(t)return t;
  if(l.includes("matin"))return "09:00";if(l.includes("midi"))return "12:00";if(l.includes("après-midi")||l.includes("apres-midi"))return "14:00";if(l.includes("soir"))return "19:00";return null;
}
function runAiCommand(){
  const text=(document.getElementById("aiCommandText")?.value||"").trim(),result=document.getElementById("aiCommandResult");if(!text){alert("Écris une demande.");return;}
  const lower=text.toLowerCase(),day=normalizeDayFromText(text),start=extractTimeV65(text),duration=extractDurationV65(text,30);let created="";
  if(lower.includes("tiramisu")||lower.includes("course")||lower.includes("acheter")||lower.includes("ingrédient")){
    let items=lower.includes("tiramisu")?["Mascarpone","Œufs","Sucre","Biscuits cuillère","Café","Cacao en poudre"]:[text.replace(/acheter|courses?|liste/gi,"").trim()||text];
    appNotes.push({id:"note_"+Date.now(),category:"Courses",text:`Liste IA : ${items.join(", ")}`});created="📝 Note de courses créée.";
  }else if(lower.includes("rdv")||lower.includes("rendez")||lower.includes("dentiste")||lower.includes("médecin")||lower.includes("docteur")){
    const st=start||"10:00",title=lower.includes("dentiste")?"Dentiste":(lower.includes("médecin")||lower.includes("docteur"))?"Médecin":"Rendez-vous";
    events.push({type:"Rendez-vous",title,day,start:st,end:addMinutesToTime(st,duration||45),person:firstUserName(),repeat:"Aucune"});created=`📅 ${title} ajouté : ${day} ${st} (${duration||45} min).`;
  }else if(["sport","courir","ménage","lire","appeler","téléphoner"].some(k=>lower.includes(k))){
    const title=lower.includes("courir")?"Courir":lower.includes("sport")?"Sport":lower.includes("ménage")?"Ménage":lower.includes("lire")?"Lire":lower.includes("appeler")||lower.includes("téléphoner")?text.replace(/demain|aujourd'hui|aujourdhui|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|à\s*\d{1,2}(?:h\d{0,2}|:\d{2})?/gi,"").trim():"Tâche";
    if(start){events.push({type:lower.includes("sport")||lower.includes("courir")?"Sport":"Tâche",title,day,start,end:addMinutesToTime(start,duration),person:firstUserName(),repeat:"Aucune"});created=`✅ ${title} planifié : ${day} ${start} pendant ${duration} min.`;}
    else{floating.push({title,duration:String(duration),days:[day]});created=`🧩 Tâche à placer créée : ${title} · ${duration} min · ${day}.`;}
  }else if(start){events.push({type:"Tâche",title:text,day,start,end:addMinutesToTime(start,duration),person:firstUserName(),repeat:"Aucune"});created=`✅ Tâche ajoutée : ${day} ${start} pendant ${duration} min.`;}
  else{appNotes.push({id:"note_"+Date.now(),category:"Idée",text:`Note IA : ${text}`});created="📝 Note créée.";}
  if(result)result.innerHTML=`<div class="ai-result"><b>${created}</b><p class="note">Compréhension locale V6.5 : dates relatives, moments de la journée et durées en heures/minutes sont interprétés automatiquement.</p></div>`;
  const input=document.getElementById("aiCommandText");if(input)input.value="";render();
}

function collectBackupV65(){return {version:"6.5",savedAt:new Date().toISOString(),state:localStorage.getItem("esprit_leger_premiere_connexion"),consents:localStorage.getItem("esprit_consents"),notifications:localStorage.getItem("esprit_notifications"),firstRun:localStorage.getItem("esprit_leger_first_run_v62_complete"),beta:localStorage.getItem("esprit_leger_beta_agreement")};}
function openBackupV65(){const m=document.getElementById("backupModalV65");if(m)m.classList.add("show");generateBackupV65();}
function generateBackupV65(){const t=document.getElementById("backupTextV65");if(t)t.value=JSON.stringify(collectBackupV65(),null,2);}
async function copyBackupV65(){generateBackupV65();const t=document.getElementById("backupTextV65");try{await navigator.clipboard.writeText(t.value);alert("Sauvegarde copiée.");}catch(e){t.select();document.execCommand("copy");alert("Sauvegarde copiée.");}}
function importBackupV65(){const t=document.getElementById("backupTextV65");try{const b=JSON.parse(t.value);if(b.state)localStorage.setItem("esprit_leger_premiere_connexion",b.state);if(b.consents)localStorage.setItem("esprit_consents",b.consents);if(b.notifications)localStorage.setItem("esprit_notifications",b.notifications);if(b.firstRun)localStorage.setItem("esprit_leger_first_run_v62_complete",b.firstRun);if(b.beta)localStorage.setItem("esprit_leger_beta_agreement",b.beta);alert("Sauvegarde importée. L'application va recharger les données.");location.reload();}catch(e){alert("Sauvegarde invalide.");}}
function installBackupCardV65(){const p=document.getElementById("profile");if(!p||document.getElementById("backupCardV65"))return;const c=document.createElement("div");c.className="card";c.id="backupCardV65";c.innerHTML='<div class="card-title-ribbon ribbon-profile">💾 Sauvegarde</div><p>Exporte tes données avant une réinstallation et réimporte-les ensuite.</p><button class="primary" onclick="openBackupV65()">Sauvegarder / Restaurer</button>';p.appendChild(c);}
setTimeout(installBackupCardV65,500);
</script>
'''
html=html.replace('</body>',v65+'</body>',1)
htmlp.write_text(html,encoding='utf-8')

# 4) Stable signing from V6.5 onward.
bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.5"',b)
b=b.replace('''    defaultConfig {''','''    signingConfigs {
        dev {
            storeFile file("esprit-leger-dev.keystore")
            storePassword "espritdev65"
            keyAlias "espritdev"
            keyPassword "espritdev65"
        }
    }

    defaultConfig {''',1)
b=b.replace('''    }
}''','''    }

    buildTypes {
        debug { signingConfig signingConfigs.dev }
    }
}''',1)
bp.write_text(b,encoding='utf-8')
print('V6.5 patch applied')
