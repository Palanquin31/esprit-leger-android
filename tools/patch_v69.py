from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# Strong free-tier boundaries: no manual AI analysis and no AI creation in free mode.
v69=r'''
<style id="v69-free-tier-boundaries">
body:not(.premium-active) #freeAdviceActionV67,
body:not(.premium-active) #freeAdviceResultV67,
body:not(.premium-active) #freeAdviceCardV67 button,
body:not(.premium-active) button[onclick*="openAiCommand"],
body:not(.premium-active) button[onclick*="runAiCommand"]{display:none!important}
</style>
<script id="v69-free-tier-guard">
(function(){
  function normV69(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim();}
  function cleanFreeAiV69(){
    try{
      if(typeof isPremium!=='undefined' && !isPremium){
        document.querySelectorAll('button').forEach(b=>{
          const t=normV69(b.innerText||b.textContent);
          const oc=b.getAttribute('onclick')||'';
          if(t.includes('analyser ma journee') || t.includes("demander a l'ia") || t.includes('creer avec l\'ia') || oc.includes('openAiCommand') || oc.includes('runAiCommand')) b.style.setProperty('display','none','important');
        });
        document.getElementById('freeAdviceActionV67')?.remove();
        document.getElementById('freeAdviceResultV67')?.remove();
      }
    }catch(e){console.warn('V6.9 free guard',e);}
  }
  const originalOpenAi=window.openAiCommand;
  if(typeof originalOpenAi==='function') window.openAiCommand=function(){if(!isPremium){cleanFreeAiV69();return;}return originalOpenAi.apply(this,arguments);};
  const originalRunAi=window.runAiCommand;
  if(typeof originalRunAi==='function') window.runAiCommand=function(){if(!isPremium){cleanFreeAiV69();return;}return originalRunAi.apply(this,arguments);};
  const mo=new MutationObserver(()=>cleanFreeAiV69());
  mo.observe(document.documentElement,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
  document.addEventListener('DOMContentLoaded',()=>setTimeout(cleanFreeAiV69,80));
  setTimeout(cleanFreeAiV69,180);
  // Keep free intelligence automatic after every save/render.
  document.addEventListener('click',()=>setTimeout(()=>{try{if(typeof refreshDayIntelligenceV67==='function')refreshDayIntelligenceV67(false);cleanFreeAiV69();}catch(e){}},120),true);
})();
</script>
'''
html=html.replace('</body>',v69+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

# Replace MainActivity with a layout that physically constrains the WebView
# between system bars. This fixes fixed-position tabs on OEM gesture/navigation bars.
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
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class MainActivity extends Activity {
    private WebView webView;
    private FrameLayout rootView;
    private static final int LOCATION_REQ=100;
    private static final int NOTIFICATION_REQ=101;

    private int dp(float v){ return Math.round(v*getResources().getDisplayMetrics().density); }

    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        NotificationScheduler.ensureChannel(this);
        final Window w=getWindow();
        w.setStatusBarColor(Color.rgb(250,250,250));
        w.setNavigationBarColor(Color.rgb(250,250,250));
        if(Build.VERSION.SDK_INT>=23){
            int flags=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if(Build.VERSION.SDK_INT>=26) flags|=View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            w.getDecorView().setSystemUiVisibility(flags);
        }
        if(Build.VERSION.SDK_INT>=30){
            WindowInsetsController c=w.getInsetsController();
            if(c!=null){c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_DEFAULT);}
        }

        rootView=new FrameLayout(this);
        rootView.setBackgroundColor(Color.rgb(250,250,250));
        webView=new WebView(this);
        FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.MATCH_PARENT);
        rootView.addView(webView,lp);
        setContentView(rootView);

        final int minTop=dp(32), minBottom=dp(52);
        final int[] safe={minTop,minBottom};
        rootView.setOnApplyWindowInsetsListener((v,i)->{
            int top=Math.max(minTop,i.getSystemWindowInsetTop());
            int bottom=Math.max(minBottom,i.getSystemWindowInsetBottom());
            safe[0]=Math.max(safe[0],top); safe[1]=Math.max(safe[1],bottom);
            FrameLayout.LayoutParams p=(FrameLayout.LayoutParams)webView.getLayoutParams();
            p.topMargin=safe[0]; p.bottomMargin=safe[1]; p.leftMargin=0; p.rightMargin=0;
            webView.setLayoutParams(p);
            return i;
        });
        rootView.requestApplyInsets();

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
        if(hasFocus){
            if(Build.VERSION.SDK_INT>=30){WindowInsetsController c=getWindow().getInsetsController();if(c!=null)c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());}
            if(rootView!=null)rootView.requestApplyInsets();
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

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.9"',b)
bp.write_text(b,encoding='utf-8')
print('V6.9 patch applied')
