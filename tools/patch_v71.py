from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Serenity modal: use the exact live serenity engine instead of legacy fabricated scores.
old_start=html.find('function openFamilyScores(){')
old_end=html.find('\n\nfunction openAddWithType',old_start)
if old_start==-1 or old_end==-1:
    raise SystemExit('openFamilyScores block not found')
new_func=r'''function openFamilyScores(){
  const modal=document.getElementById("familyScoreModal");
  const content=document.getElementById("familyScoreContent");
  if(!modal || !content)return;

  // Always recompute from current live data when the bubble is opened.
  const allToday=eventsForDate(selectedDate);
  const members=Object.keys(people);
  const owner=firstUserName();
  const names=members.length?members:[owner];

  function leafFor(n){return n>=80?"🌱":n>=65?"🌿":n>=50?"🍃":n>=35?"🍂":"🌪️";}
  function labelFor(n){return n>=80?"Très serein":n>=65?"Serein":n>=50?"Équilibré":n>=35?"Chargé":"Sous pression";}

  const rows=names.map(name=>{
    // Personal load = the member's own events, evaluated with the same serenity engine as Home.
    const ownEvents=allToday.filter(e=>!e.person || e.person===name);
    const scoreNum=computeSerenityScore(ownEvents);
    return `<div class="score-row"><span>${name}${name===owner?' · personnel':''}</span><strong>${leafFor(scoreNum)} ${scoreNum}/100</strong><small>${labelFor(scoreNum)}</small></div>`;
  }).join("");

  // Family = exactly the same live engine applied to every family event on the selected day.
  const familyNum=computeSerenityScore(allToday);
  const familyLeaf=leafFor(familyNum);
  let familyAdvice="La charge familiale est bien répartie pour cette journée.";
  if(familyNum<80)familyAdvice="La journée commence à se charger : garde des marges et répartis les tâches si possible.";
  if(familyNum<60)familyAdvice="La charge familiale est élevée : déplace une tâche non urgente ou protège un créneau de récupération.";
  if(familyNum<40)familyAdvice="La journée familiale est très chargée : garde uniquement l’essentiel et reporte ce qui peut l’être.";

  content.innerHTML=`${rows}<div class="score-row family-total"><span>Famille</span><strong>${familyLeaf} ${familyNum}/100</strong><small>${labelFor(familyNum)}</small></div><div class="ai-result"><b>✨ Lecture familiale</b><p>${familyAdvice}</p></div>`;
  modal.classList.add("show");
  updateFloatingVisibility();
}'''
html=html[:old_start]+new_func+html[old_end:]

# 2) Remove development/technical labels from Premium weekly suggestions, old and V6.5 paths.
html=re.sub(r'<p class="note">Assistant intelligent local de développement\s*:\s*analyse automatique de tes données présentes dans l’application\.</p>','',html)
html=re.sub(r'<p class="note">Assistant intelligent local V6\.5\s*:\s*analyse du planning, des chevauchements, de la répartition, des tâches, de la fatigue et de la météo\.</p>','',html)
# Defensive plain text cleanup in case markup changed.
html=html.replace('Assistant intelligent local de développement : analyse automatique de tes données présentes dans l’application.','')
html=html.replace('Assistant intelligent local V6.5 : analyse du planning, des chevauchements, de la répartition, des tâches, de la fatigue et de la météo.','')

# 3) Refresh subscription proposition to reflect the stable V7 feature split.
html=html.replace(
  'Planning, notes, météo, santé/sport connectés, score de sérénité et suggestions simples.',
  'Planning jour/semaine, notes et décharge mentale, profils famille, météo locale réelle, score de sérénité recalculé automatiquement, conseils généraux et rappels Android.',
  1
)
html=html.replace(
  'Assistant IA, Allège ma semaine, création intelligente, suggestions avancées, analyse familiale et recommandations personnalisées.',
  'Tout le mode Gratuit + Allège ma semaine, analyse IA approfondie de la charge, des chevauchements et de la répartition, création de tâches et rendez-vous en langage naturel, recommandations personnalisées selon planning, météo, fatigue et charge familiale.',
  1
)

# Small presentation polish for score rows without changing V7 visual structure.
style=r'''\n<style id="v71-content-polish">\n#familyScoreContent .score-row{display:grid;grid-template-columns:1fr auto;gap:2px 10px;align-items:center}\n#familyScoreContent .score-row small{grid-column:1/-1;color:#81788c;font-size:12px}\n</style>\n'''
if 'id="v71-content-polish"' not in html:
    html += style

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-v7.1"',b)
bp.write_text(b,encoding='utf-8')
print('V7.1 content patch applied')
