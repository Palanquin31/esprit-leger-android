from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

v612=r'''
<style id="v612-nav-premium-style">
/* Keep V6.11 swipe stability; only lift fixed controls above Xiaomi system nav. */
.nav{bottom:42px!important;}
.fab{bottom:136px!important;}
.floating-add,.quick-add,.floating-plus{bottom:136px!important;}
body{padding-bottom:106px!important;}

/* AI creation is a Premium-only feature. */
body:not(.premium-active) button[onclick*="openAiCommand"],
body:not(.premium-active) button[onclick*="runAiCommand"]{display:none!important}
body.premium-active button[onclick*="openAiCommand"],
body.premium-active button[onclick*="runAiCommand"]{display:inline-flex!important}
</style>
<script id="v612-premium-ai-restore">
(function(){
  function aiButtons(){
    return Array.from(document.querySelectorAll('button')).filter(b=>{
      const oc=b.getAttribute('onclick')||'';
      return oc.includes('openAiCommand')||oc.includes('runAiCommand');
    });
  }
  function syncPremiumAiV612(){
    try{
      const premium=(typeof isPremium!=='undefined'&&!!isPremium)||document.body.classList.contains('premium-active');
      aiButtons().forEach(b=>{
        if(premium){
          b.style.removeProperty('display');
          b.hidden=false;
          b.disabled=false;
        }else{
          b.style.setProperty('display','none','important');
        }
      });
      // If an old free guard removed only the quick-add AI button, recreate it in Premium.
      if(premium){
        const quick=document.querySelector('.quick-actions,.quick-add-menu,#quickAddMenu,.quick-menu');
        if(quick && !quick.querySelector('button[onclick*="openAiCommand"]')){
          const b=document.createElement('button');
          b.className='smallbtn';
          b.textContent='✨ Demander à l’IA';
          b.setAttribute('onclick','toggleQuickAdd(false);openAiCommand()');
          quick.appendChild(b);
        }
      }
    }catch(e){console.warn('V6.12 premium AI restore',e);}
  }
  window.syncPremiumAiV612=syncPremiumAiV612;
  const mo=new MutationObserver(()=>setTimeout(syncPremiumAiV612,0));
  mo.observe(document.body,{attributes:true,attributeFilter:['class'],childList:true,subtree:true});
  document.addEventListener('DOMContentLoaded',()=>setTimeout(syncPremiumAiV612,120));
  document.addEventListener('click',()=>setTimeout(syncPremiumAiV612,80),true);
  setTimeout(syncPremiumAiV612,250);
})();
</script>
'''
html=html.replace('</body>',v612+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.12"',b)
bp.write_text(b,encoding='utf-8')
print('V6.12 patch applied')
