from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Remove literal escaped-newline text that can be rendered as visible text.
# V7.1 style wrapper.
html=html.replace(r'\n<style id="v71-content-polish">', '<style id="v71-content-polish">')
# Convert literal escaped newlines inside the V7.1 style block to real newlines.
start=html.find('<style id="v71-content-polish">')
if start!=-1:
    end=html.find('</style>',start)
    if end!=-1:
        block=html[start:end+8].replace('\\n','\n')
        html=html[:start]+block+html[end+8:]
# Old V6.2 wrapper remnants sitting outside the script tag.
html=html.replace(r'\n<script id="v62-behaviour-fixes">', '\n<script id="v62-behaviour-fixes">')
start=html.find('<script id="v62-behaviour-fixes">')
if start!=-1:
    end=html.find('</script>',start)
    if end!=-1 and html[end+9:end+11]=='\\n':
        html=html[:end+9]+'\n'+html[end+11:]
# Defensive cleanup of any line made only of literal escaped newline tokens.
html=re.sub(r'(?m)^(?:\\n\s*)+$', '', html)

# 2) Slightly lower the + button while keeping the validated V7 nav position untouched.
finish_css=r'''
<style id="v72-finish-polish">
/* V7.0 validated navigation remains untouched. */
.nav{bottom:68px !important;}
/* + lowered slightly from V7.0, still clearly above the tab bar. */
.fab-global{bottom:158px !important;}
.quick-add-menu{bottom:226px !important;}
/* Mood picker is now anchored beside/below the Etat bubble by JS, not at page bottom. */
.mood-floating{
  bottom:auto !important;
  width:264px !important;
  max-width:calc(100vw - 36px) !important;
  padding:14px !important;
  gap:10px !important;
  border-radius:28px !important;
  z-index:11000 !important;
  box-shadow:0 20px 50px rgba(67,47,105,.24) !important;
}
.mood-floating .mood{
  min-height:54px !important;
  font-size:28px !important;
  padding:8px !important;
}
</style>
'''
if 'id="v72-finish-polish"' not in html:
    html += finish_css

# Anchor mood picker to the Etat card whenever it opens/resizes.
anchor_js=r'''
<script id="v72-mood-anchor">
(function(){
  function positionMoodPickerV72(){
    const menu=document.getElementById('moodFloating');
    const card=document.querySelector('.hero-stat-card[onclick*="toggleMoodMenu"]');
    if(!menu||!card||!menu.classList.contains('show'))return;
    const r=card.getBoundingClientRect();
    const w=Math.min(264,window.innerWidth-36);
    let left=Math.min(window.innerWidth-w-18,Math.max(18,r.right-w));
    let top=r.bottom+10;
    const estimatedH=86;
    if(top+estimatedH>window.innerHeight-18)top=Math.max(18,r.top-estimatedH-10);
    menu.style.left=left+'px';
    menu.style.right='auto';
    menu.style.top=top+'px';
    menu.style.transform='none';
  }
  const oldToggle=window.toggleMoodMenu;
  window.toggleMoodMenu=function(){
    if(typeof oldToggle==='function')oldToggle.apply(this,arguments);
    requestAnimationFrame(positionMoodPickerV72);
  };
  window.addEventListener('resize',positionMoodPickerV72);
  window.addEventListener('scroll',positionMoodPickerV72,{passive:true});
})();
</script>
'''
if 'id="v72-mood-anchor"' not in html:
    html += anchor_js

# 3) Rewrite subscription copy as readable benefits instead of a mechanical feature list.
html=html.replace(
 'Planning jour/semaine, notes et décharge mentale, profils famille, météo locale réelle, score de sérénité recalculé automatiquement, conseils généraux et rappels Android.',
 "La version Gratuite t’aide déjà à organiser simplement le quotidien : tu poses tes rendez-vous et tes tâches, tu gardes tes notes au même endroit, tu suis la charge de ta journée grâce au score de sérénité et tu reçois des conseils simples adaptés à la météo et à ton organisation familiale.",
 1
)
html=html.replace(
 'Tout le mode Gratuit + Allège ma semaine, analyse IA approfondie de la charge, des chevauchements et de la répartition, création de tâches et rendez-vous en langage naturel, recommandations personnalisées selon planning, météo, fatigue et charge familiale.',
 "Avec Premium, L’Esprit Léger ne se contente plus d’afficher ton planning : il t’aide réellement à l’alléger. L’assistant repère les journées trop chargées, les chevauchements et les moments où tu peux déplacer une tâche. Tu peux aussi lui parler naturellement pour créer un rendez-vous ou une tâche, et ses recommandations deviennent plus précises en tenant compte de ton planning, de la météo, de ta fatigue et de la charge de toute la famille.",
 1
)

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-v7.2"',b)
bp.write_text(b,encoding='utf-8')
print('V7.2 finishing patch applied')
