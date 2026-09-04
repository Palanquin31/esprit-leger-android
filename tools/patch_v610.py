from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V6.10: undo the destructive native viewport shrink from V6.9.
# Keep V6.9 free-tier AI restrictions, but restore a full-size WebView.
main=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main.write_text(r'''package com.espritlibre.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class MainActivity extends Activity {
    private WebView webView;
    private static final int LOCATION_REQ=100;
    private static final int NOTIFICATION_REQ=101;

    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        NotificationScheduler.ensureChannel(this);

        getWindow().setStatusBarColor(Color.rgb(250,250,250));
        getWindow().setNavigationBarColor(Color.rgb(250,250,250));
        if(Build.VERSION.SDK_INT>=23){
            int flags=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if(Build.VERSION.SDK_INT>=26)flags|=View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            getWindow().getDecorView().setSystemUiVisibility(flags);
        }
        if(Build.VERSION.SDK_INT>=30){
            WindowInsetsController c=getWindow().getInsetsController();
            if(c!=null){
                c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());
                c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_DEFAULT);
            }
        }

        webView=new WebView(this);
        setContentView(webView);
        // Deliberately do NOT resize/shrink the WebView. V6.10 keeps it full size.
        webView.setPadding(0,0,0,0);

        WebSettings s=webView.getSettings();
        s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setDatabaseEnabled(true);s.setGeolocationEnabled(true);
        s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);s.setCacheMode(WebSettings.LOAD_DEFAULT);
        webView.addJavascriptInterface(new NotificationBridge(this),"AndroidNotifications");
        webView.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView v,String u){super.onPageFinished(v,u);tryLoadWeather();v.postDelayed(()->v.evaluateJavascript("if(typeof syncNativeNotificationsV66==='function')syncNativeNotificationsV66();",null),900);}});
        webView.setWebChromeClient(new WebChromeClient(){
            @Override public void onGeolocationPermissionsShowPrompt(String o,GeolocationPermissions.Callback c){boolean g=checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;c.invoke(o,g,false);}
            @Override public void onPermissionRequest(PermissionRequest r){r.grant(r.getResources());}
        });
        try{
            BufferedReader r=new BufferedReader(new InputStreamReader(getAssets().open("index.html"),"UTF-8"));StringBuilder x=new StringBuilder();String l;while((l=r.readLine())!=null)x.append(l).append('\n');r.close();
            webView.loadDataWithBaseURL("https://appassets.androidplatform.net/",x.toString(),"text/html","UTF-8",null);
        }catch(Exception e){webView.loadUrl("file:///android_asset/index.html");}
        if(Build.VERSION.SDK_INT>=23 && checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},LOCATION_REQ);
        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},NOTIFICATION_REQ);
    }

    @Override public void onWindowFocusChanged(boolean hasFocus){
        super.onWindowFocusChanged(hasFocus);
        if(hasFocus && Build.VERSION.SDK_INT>=30){
            WindowInsetsController c=getWindow().getInsetsController();
            if(c!=null)c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());
        }
    }

    private void tryLoadWeather(){if(webView==null)return;boolean g=Build.VERSION.SDK_INT<23||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;if(g)webView.postDelayed(()->webView.evaluateJavascript("if(typeof loadLiveWeather==='function'){loadLiveWeather();}",null),500);}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==LOCATION_REQ)tryLoadWeather();if(r==NOTIFICATION_REQ&&webView!=null)webView.postDelayed(()->webView.evaluateJavascript("if(typeof syncNativeNotificationsV66==='function')syncNativeNotificationsV66();",null),250);}
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}

    public static class NotificationBridge {
        private final Context context;
        NotificationBridge(Context c){context=c.getApplicationContext();}
        @JavascriptInterface public void sync(String stateJson,String settingsJson){
            context.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).edit().putString("state",stateJson).putString("settings",settingsJson).apply();
            NotificationScheduler.reschedule(context,stateJson,settingsJson);
        }
    }
}
''',encoding='utf-8')

# Safe-area handled inside the web UI only, without shrinking the native viewport.
v610=r'''
<style id="v610-safe-area-style">
/* Xiaomi/Android safe spacing: do not alter viewport height. */
html,body{min-height:100%;}
body{padding-top:24px!important;padding-bottom:88px!important;box-sizing:border-box!important;}
.phone{padding-top:0!important;padding-bottom:0!important;}
/* Bottom tabs stay visually attached to the app but above Android navigation keys. */
.nav{bottom:24px!important;z-index:9990!important;}
/* Floating + remains above the tab bar rather than over it. */
.fab{bottom:118px!important;z-index:9991!important;}
/* Some legacy variants use fixed-position quick-add classes. */
.floating-add,.quick-add,.floating-plus{bottom:118px!important;}
/* Keep modals above tabs and system-safe spacing. */
.modal{z-index:12000!important;}
.modal .sheet{max-height:calc(100vh - 72px)!important;}
</style>
<script id="v610-free-tier-cleanup">
(function(){
  function norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();}
  function clean(){
    try{
      if(typeof isPremium!=='undefined' && !isPremium){
        document.getElementById('freeAdviceActionV67')?.remove();
        document.getElementById('freeAdviceResultV67')?.remove();
        document.querySelectorAll('button').forEach(b=>{
          const t=norm(b.innerText||b.textContent);
          const oc=b.getAttribute('onclick')||'';
          if(t.includes('analyser ma journee') || t.includes("demander a l'ia") || t.includes('creer avec ia') || t.includes("creer avec l'ia") || t.includes('ajouter par ia') || oc.includes('openAiCommand') || oc.includes('runAiCommand')){
            b.style.setProperty('display','none','important');
          }
        });
      }
    }catch(e){console.warn('V6.10 free cleanup',e);}
  }
  const oldOpen=window.openAiCommand;
  if(typeof oldOpen==='function')window.openAiCommand=function(){if(typeof isPremium!=='undefined'&&!isPremium){clean();return;}return oldOpen.apply(this,arguments);};
  const oldRun=window.runAiCommand;
  if(typeof oldRun==='function')window.runAiCommand=function(){if(typeof isPremium!=='undefined'&&!isPremium){clean();return;}return oldRun.apply(this,arguments);};
  const observer=new MutationObserver(clean);observer.observe(document.documentElement,{childList:true,subtree:true});
  document.addEventListener('DOMContentLoaded',()=>setTimeout(clean,80));
  setTimeout(clean,180);
  // Free score/advice remain automatic after every render/save.
  if(typeof render==='function'&&!render.__v610wrapped){
    const oldRender=render;
    window.render=function(){const x=oldRender.apply(this,arguments);setTimeout(()=>{try{if(typeof refreshDayIntelligenceV67==='function')refreshDayIntelligenceV67(false);clean();}catch(e){}},0);return x;};
    window.render.__v610wrapped=true;
  }
})();
</script>
'''
html=html.replace('</body>',v610+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.10"',b)
bp.write_text(b,encoding='utf-8')
print('V6.10 patch applied')
