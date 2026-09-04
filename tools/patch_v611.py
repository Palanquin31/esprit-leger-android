from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

v611=r'''
<style id="v611-swipe-stability-style">
/* Keep the navigation bar completely outside swipe animations/compositing. */
.nav{
  transform:translateX(-50%)!important;
  will-change:auto!important;
  backface-visibility:visible!important;
  contain:layout paint style!important;
}
/* Screen changes no longer translate horizontally; this removes the small vertical jump
   seen on Xiaomi when switching around the second tab. */
.screen.slide-left,.screen.slide-right,.slide-left,.slide-right{
  animation:none!important;
  transform:none!important;
}
.screen{transform:none!important;backface-visibility:visible!important;will-change:auto!important;}
</style>
<script id="v611-unified-swipe-engine">
(function(){
  const order=['planning','data','notes','profile'];
  let sx=0,sy=0,startTarget=null;

  function activeIndex(){
    const a=document.querySelector('.screen.active');
    const i=order.indexOf(a?.id||'planning');
    return i<0?0:i;
  }
  function modalOpen(){return !!document.querySelector('.modal.show');}
  function isExcluded(t){
    return !!(t?.closest?.('.modal,.nav,.fab,.fab-global,.quick-add-menu,input,textarea,select,button,.tabs,.tab'));
  }
  function changeTab(delta){
    const current=activeIndex();
    const next=Math.max(0,Math.min(order.length-1,current+delta));
    if(next===current)return;
    const btn=Array.from(document.querySelectorAll('.nav button'))[next];
    if(btn && typeof go==='function'){
      go(order[next],btn);
      // Absolutely no legacy slide classes after the tab change.
      document.querySelectorAll('.screen').forEach(s=>s.classList.remove('slide-left','slide-right'));
    }
  }

  // Capture phase + stopImmediatePropagation means the two old swipe engines
  // (global tabs + planning day/week) never receive the same gesture anymore.
  document.addEventListener('touchstart',function(e){
    if(e.touches.length!==1 || modalOpen() || isExcluded(e.target)){sx=sy=0;startTarget=null;return;}
    sx=e.touches[0].clientX; sy=e.touches[0].clientY; startTarget=e.target;
  },true);

  document.addEventListener('touchend',function(e){
    if(!sx)return;
    const dx=e.changedTouches[0].clientX-sx;
    const dy=e.changedTouches[0].clientY-sy;
    const valid=Math.abs(dx)>70 && Math.abs(dx)>Math.abs(dy)*1.5;
    sx=sy=0;startTarget=null;
    if(!valid)return;
    e.stopImmediatePropagation();
    // Finger left -> next tab. Finger right -> previous tab.
    changeTab(dx<0?1:-1);
  },true);

  // Also neutralise the legacy helper so even programmatic use cannot add slide transforms.
  window.goByIndex=function(idx){
    const current=activeIndex();
    const safe=Math.max(0,Math.min(order.length-1,idx));
    if(safe===current)return;
    const btn=Array.from(document.querySelectorAll('.nav button'))[safe];
    if(btn && typeof go==='function')go(order[safe],btn);
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('slide-left','slide-right'));
  };
})();
</script>
'''
html=html.replace('</body>',v611+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.11"',b)
bp.write_text(b,encoding='utf-8')
print('V6.11 patch applied')
