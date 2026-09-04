from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# --- 1) Navigation/modal behaviour -------------------------------------------------
old_go="function go(id,btn){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));btn.classList.add('active')}"
new_go="function go(id,btn){if(typeof closeModals==='function')closeModals();document.body.classList.remove('modal-open-v67');document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');if(typeof refreshDayIntelligenceV67==='function')setTimeout(refreshDayIntelligenceV67,0)}"
if old_go in html:
    html=html.replace(old_go,new_go,1)

# Add a stable ID to the unified advice card if not already present.
html=html.replace('<div class="card advice-card soft-advice unified-advice-card">','<div class="card advice-card soft-advice unified-advice-card" id="freeAdviceCardV67">',1)

# Add styles and logic late so it wins over legacy CSS/JS.
v67=r'''
<style id="v67-fluid-navigation-style">
body.modal-open-v67{overflow:hidden!important;overscroll-behavior:none!important;touch-action:none!important}
body.modal-open-v67 .phone{overflow:hidden!important}
.modal.show{overscroll-behavior:contain!important;touch-action:none!important}
.modal.show .sheet{touch-action:pan-y!important;overscroll-behavior:contain!important;max-height:calc(100vh - 32px);overflow-y:auto;-webkit-overflow-scrolling:touch}
#freeAdviceActionV67{margin-top:14px;width:100%;border:0;border-radius:18px;padding:13px 16px;font-weight:800;font-size:15px;background:linear-gradient(135deg,#f3e8ff,#ffe6f1);color:#3b3144;box-shadow:0 6px 18px rgba(110,80,140,.12)}
#freeAdviceResultV67{margin-top:12px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.66);font-size:14px;line-height:1.42}
.premium-active #freeAdviceActionV67,.premium-active #freeAdviceResultV67{display:none!important}
</style>
<script id="v67-fluid-navigation-ai">
(function(){
  const navTexts=new Set(['Planning','Données','Notes','Profil']);
  function modalIsOpenV67(){return !!document.querySelector('.modal.show');}
  function syncModalLockV67(){document.body.classList.toggle('modal-open-v67',modalIsOpenV67());}
  window.syncModalLockV67=syncModalLockV67;

  // Any tab click closes every open modal before navigation can affect the background.
  document.addEventListener('click',function(e){
    const b=e.target.closest('button');
    if(b){const txt=(b.innerText||b.textContent||'').trim();if(navTexts.has(txt)||b.closest('.nav')){if(typeof closeModals==='function')closeModals();syncModalLockV67();}}
    const m=e.target.classList&&e.target.classList.contains('modal')?e.target:null;
    if(m&&m.classList.contains('show')){if(typeof closeModals==='function')closeModals();syncModalLockV67();}
  },true);

  // Watch legacy code that opens/closes modals and lock the document automatically.
  const mo=new MutationObserver(syncModalLockV67);
  document.querySelectorAll('.modal').forEach(m=>mo.observe(m,{attributes:true,attributeFilter:['class']}));

  // Prevent swipe page navigation while a modal is visible.
  document.addEventListener('touchstart',function(e){if(modalIsOpenV67())e.stopImmediatePropagation();},true);
  document.addEventListener('touchmove',function(e){if(modalIsOpenV67()&&!e.target.closest('.sheet'))e.preventDefault();},{capture:true,passive:false});

  function dayKeyV67(d){return (d||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
  function selectedDayNameV67(){return selectedDate.toLocaleDateString('fr-FR',{weekday:'long'}).replace(/^./,c=>c.toUpperCase());}
  function tasksForSelectedDayV67(){
    const target=dayKeyV67(selectedDayNameV67());
    return (Array.isArray(floating)?floating:[]).filter(t=>{
      const ds=Array.isArray(t.days)?t.days:[];
      return ds.some(d=>dayKeyV67(d)===target);
    });
  }
  function scoreWithTasksV67(){
    const ev=eventsForDate(selectedDate)||[];
    let s=computeSerenityScore(ev);
    const ft=tasksForSelectedDayV67();
    if(ft.length){
      const mins=ft.reduce((a,t)=>a+(parseInt(t.duration||'30',10)||30),0);
      s-=Math.min(18,ft.length*3+Math.floor(mins/90)*2);
    }
    return Math.max(0,Math.min(100,Math.round(s)));
  }
  window.scoreWithTasksV67=scoreWithTasksV67;

  function labelForScoreV67(s){if(s>=80)return 'Très serein';if(s>=65)return 'Serein';if(s>=50)return 'Équilibré';if(s>=35)return 'Chargé';return 'Sous pression';}
  function iconForScoreV67(s){if(s>=80)return '🌿';if(s>=65)return '🌱';if(s>=50)return '🍃';if(s>=35)return '🍂';return '🌪';}

  function freeDayAdviceV67(){
    const ev=eventsForDate(selectedDate)||[],ft=tasksForSelectedDayV67(),s=scoreWithTasksV67();
    let minutes=0,late=0;
    ev.forEach(e=>{const a=(e.start||'00:00').split(':').map(Number),b=(e.end||'00:00').split(':').map(Number);minutes+=Math.max(0,b[0]*60+b[1]-a[0]*60-a[1]);if(a[0]>=19)late++;});
    const msgs=[];
    if(ev.length===0&&ft.length===0)msgs.push('Ta journée est encore complètement libre : garde cette marge si tu peux.');
    else{
      if(minutes>=480)msgs.push('Ta journée est déjà très remplie. Évite d’ajouter une contrainte importante.');
      else if(minutes>=300)msgs.push('La journée commence à être bien chargée : conserve au moins un vrai temps de respiration.');
      else msgs.push('La charge planifiée reste raisonnable pour le moment.');
      if(ft.length)msgs.push(`${ft.length} tâche(s) restent à placer aujourd’hui : répartis-les plutôt que de les enchaîner.`);
      if(late>=2)msgs.push('Plusieurs activités sont prévues le soir : essaie de protéger la fin de journée.');
    }
    if(mood==='fatigue'||mood==='epuisee')msgs.push('Ton niveau de fatigue est pris en compte : privilégie le nécessaire et reporte le reste.');
    if(liveWeather){if(liveWeather.rain)msgs.push('La météo est humide : regrouper les déplacements peut alléger la journée.');else if(liveWeather.temperature>=30)msgs.push('Avec la chaleur, place les activités extérieures tôt ou tard dans la journée.');}
    return {score:s,text:msgs.join(' ')};
  }

  function ensureFreeAdviceUiV67(){
    const card=document.getElementById('freeAdviceCardV67');if(!card)return;
    let btn=document.getElementById('freeAdviceActionV67');
    if(!btn){
      btn=document.createElement('button');btn.id='freeAdviceActionV67';btn.type='button';btn.textContent='✨ Analyser ma journée';btn.onclick=function(){refreshDayIntelligenceV67(true);};card.appendChild(btn);
      const out=document.createElement('div');out.id='freeAdviceResultV67';out.style.display='none';card.appendChild(out);
    }
  }

  window.refreshDayIntelligenceV67=function(showDetails){
    try{
      const r=freeDayAdviceV67();
      const sn=document.getElementById('serenityScoreNum');if(sn)sn.textContent=`${r.score}/100`;
      const se=document.getElementById('serenity');if(se)se.textContent=labelForScoreV67(r.score);
      const round=document.querySelector('.stable-hero .hero-stat-card .hero-round-icon');if(round)round.textContent=iconForScoreV67(r.score);
      const adv=document.getElementById('advice');if(adv&&!isPremium)adv.textContent=r.text;
      ensureFreeAdviceUiV67();
      const out=document.getElementById('freeAdviceResultV67');if(out&&!isPremium){out.innerHTML=`<b>Score actuel : ${r.score}/100</b><br>${r.text}`;out.style.display=showDetails?'block':out.style.display;}
    }catch(e){console.warn('V6.7 day intelligence',e);}
  };

  // Wrap render once so every create/edit/delete immediately refreshes free score + advice.
  if(typeof render==='function'&&!render.__v67wrapped){
    const oldRender=render;
    window.render=function(){const x=oldRender.apply(this,arguments);setTimeout(()=>refreshDayIntelligenceV67(false),0);return x;};
    window.render.__v67wrapped=true;
  }
  ensureFreeAdviceUiV67();
  setTimeout(()=>refreshDayIntelligenceV67(false),150);
})();
</script>
'''
html=html.replace('</body>',v67+'\n</body>',1)

# Version bump
bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.7"',b)
bp.write_text(b,encoding='utf-8')

htmlp.write_text(html,encoding='utf-8')
print('V6.7 patch applied')
