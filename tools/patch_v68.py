from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# Remove the free manual analysis button/result introduced in V6.7.
v68=r'''
<style id="v68-free-auto-style">
#freeAdviceActionV67,#freeAdviceResultV67{display:none!important}
</style>
<script id="v68-free-auto-intelligence">
(function(){
  function removeFreeManualUiV68(){
    document.getElementById('freeAdviceActionV67')?.remove();
    document.getElementById('freeAdviceResultV67')?.remove();
  }
  // Free mode remains fully automatic: every render refreshes score and advice.
  const refreshAutoV68=function(){
    try{
      removeFreeManualUiV68();
      if(typeof refreshDayIntelligenceV67==='function') refreshDayIntelligenceV67(false);
      removeFreeManualUiV68();
    }catch(e){console.warn('V6.8 automatic free analysis',e);}
  };
  document.addEventListener('DOMContentLoaded',()=>setTimeout(refreshAutoV68,120));
  setTimeout(refreshAutoV68,220);

  // Extra hooks for legacy flows that save without immediately rendering.
  if(typeof saveState==='function'&&!saveState.__v68wrapped){
    const old=saveState;
    window.saveState=function(){const x=old.apply(this,arguments);setTimeout(refreshAutoV68,0);return x;};
    window.saveState.__v68wrapped=true;
  }

  // Keep premium manual analysis only. If UI state changes, ensure free button stays absent.
  const mo=new MutationObserver(()=>removeFreeManualUiV68());
  mo.observe(document.body,{childList:true,subtree:true});
})();
</script>
'''
html=html.replace('</body>',v68+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

# Android system-bar stability: cache the largest observed insets so transient gesture
# states can never collapse the safe area. Also keep bars visible and opaque.
main=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
s=main.read_text(encoding='utf-8')
s=s.replace('import android.os.Bundle;','import android.os.Bundle;\nimport android.graphics.Color;\nimport android.view.View;\nimport android.view.Window;\nimport android.view.WindowInsets;\nimport android.view.WindowInsetsController;')

old='''        webView=new WebView(this);\n        setContentView(webView);\n        webView.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(0,i.getSystemWindowInsetTop(),0,i.getSystemWindowInsetBottom());return i;});\n        webView.requestApplyInsets();'''
new='''        webView=new WebView(this);\n        final Window w=getWindow();\n        w.setStatusBarColor(Color.rgb(250,250,250));\n        w.setNavigationBarColor(Color.rgb(250,250,250));\n        if(Build.VERSION.SDK_INT>=23) w.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | (Build.VERSION.SDK_INT>=26?View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR:0));\n        if(Build.VERSION.SDK_INT>=30){\n            WindowInsetsController c=w.getInsetsController();\n            if(c!=null){c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_DEFAULT);}\n        }\n        setContentView(webView);\n        final int[] safe={0,0};\n        webView.setOnApplyWindowInsetsListener((v,i)->{\n            int top=i.getSystemWindowInsetTop(), bottom=i.getSystemWindowInsetBottom();\n            if(top>safe[0])safe[0]=top; if(bottom>safe[1])safe[1]=bottom;\n            v.setPadding(0,safe[0],0,safe[1]);\n            return i;\n        });\n        webView.requestApplyInsets();'''
if old not in s:
    raise SystemExit('V6.8 MainActivity inset block not found')
s=s.replace(old,new,1)

# Re-show bars whenever activity regains focus, useful after horizontal gestures on OEM launchers.
insert='''\n    @Override public void onWindowFocusChanged(boolean hasFocus){\n        super.onWindowFocusChanged(hasFocus);\n        if(hasFocus && Build.VERSION.SDK_INT>=30){\n            WindowInsetsController c=getWindow().getInsetsController();\n            if(c!=null)c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());\n        }\n        if(hasFocus && webView!=null)webView.requestApplyInsets();\n    }\n'''
marker='    private void tryLoadWeather()'
s=s.replace(marker,insert+'\n'+marker,1)
main.write_text(s,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.8"',b)
bp.write_text(b,encoding='utf-8')
print('V6.8 patch applied')
