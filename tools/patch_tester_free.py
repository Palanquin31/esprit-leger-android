from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# Free-only tester UI/behaviour. Keep informative Premium teaser, remove activation paths.
html += r'''
<style id="tester-free-lock-css">
/* Distribution testeurs : gratuit uniquement */
.ai-action,.logo-premium-badge,.premium-badge-info,.plan-card.premium{display:none!important}
#premiumModeStatus{display:none!important}
.tester-free-banner{margin:12px 0;padding:10px 14px;border-radius:16px;background:#f5efff;color:#65557a;font-size:13px;text-align:center}
</style>
<script id="tester-free-lock-js">
(function(){
  function lockFree(){
    try{isPremium=false;}catch(_e){}
    document.body.classList.remove('premium-active');
    const status=document.getElementById('premiumModeStatus');if(status)status.textContent='Version d’essai gratuite';
    document.querySelectorAll('button').forEach(b=>{const t=(b.textContent||'').trim().toLowerCase();if(t==='mode premium'||t==='mode gratuit'){const card=b.closest('.card');if(card)card.style.display='none';else b.style.display='none';}});
    const ai=document.getElementById('aiWeeklyResult');if(ai){ai.classList.remove('ai-visible');ai.style.display='none';}
    const p=document.getElementById('profile');
    if(p&&!document.getElementById('testerFreeBanner')){const d=document.createElement('div');d.id='testerFreeBanner';d.className='tester-free-banner';d.textContent='Version d’essai gratuite • Programme de test L’Esprit Léger';p.prepend(d);}
  }
  try{setPremiumMode=function(){lockFree();alert('Cette version d’essai fonctionne uniquement en mode gratuit.');};}catch(_e){}
  try{togglePremium=function(){lockFree();};}catch(_e){}
  try{runAiWeekLighten=function(){alert('L’assistant IA avancé sera disponible dans la version Premium.');};}catch(_e){}
  const oldRender=typeof render==='function'?render:null;
  if(oldRender){render=function(){isPremium=false;const r=oldRender.apply(this,arguments);setTimeout(lockFree,0);return r;};}
  setInterval(lockFree,1200);setTimeout(lockFree,50);
})();
</script>
'''
htmlp.write_text(html,encoding='utf-8')

# Dedicated package / version + hardened release build.
bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r"applicationId\s+['\"][^'\"]+['\"]","applicationId 'com.espritlibre.app.testfree'",b,1)
b=re.sub(r'versionCode\s+\d+','versionCode 6501',b,1)
b=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '0.9-test-gratuit'",b,1)
# Remove any prior signingConfigs/buildTypes appended by experimental patches.
b=re.sub(r'\n\s*signingConfigs\s*\{.*?\n\s*\}\s*\n\s*buildTypes\s*\{.*?\n\s*\}\s*', '\n', b, flags=re.S)
insert=r'''

    signingConfigs {
        testerRelease {
            storeFile file('tester-release.keystore')
            storePassword 'EspritTester2026!'
            keyAlias 'esprit-tester'
            keyPassword 'EspritTester2026!'
        }
    }
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            debuggable false
            signingConfig signingConfigs.testerRelease
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
'''
pos=b.rfind('}')
b=b[:pos]+insert+b[pos:]
bp.write_text(b,encoding='utf-8')

(root/'app/proguard-rules.pro').write_text(r'''
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}
''',encoding='utf-8')

# Manifest hardening.
manifest=root/'app/src/main/AndroidManifest.xml'
m=manifest.read_text(encoding='utf-8')
if 'android:allowBackup=' not in m:
    m=m.replace('<application','<application\n        android:allowBackup="false"\n        android:fullBackupContent="false"\n        android:usesCleartextTraffic="false"',1)
manifest.write_text(m,encoding='utf-8')

# Replace MainActivity with encrypted-asset + integrity/signature verification loader.
java=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
java.write_text(r'''package com.espritlibre.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.graphics.Color;
import android.location.Address;
import android.location.Geocoder;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.TextView;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;
import java.util.Locale;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class MainActivity extends Activity {
    private static final int LOCATION_REQ=100;
    private static final String EXPECTED_HTML_SHA="__HTML_SHA__";
    private static final String EXPECTED_CERT_SHA="__CERT_SHA__";
    private static final String AES_KEY_HEX="__AES_KEY__";
    private static final String AES_IV_HEX="__AES_IV__";
    private WebView webView;

    @SuppressLint({"SetJavaScriptEnabled","AddJavascriptInterface"})
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        if(!verifySignature()){block("Signature de l’application invalide.");return;}
        byte[] clear;
        try{clear=decryptAsset();}catch(Exception e){block("Application endommagée.");return;}
        if(!EXPECTED_HTML_SHA.equalsIgnoreCase(sha256(clear))){block("Intégrité de l’application invalide.");return;}

        getWindow().setStatusBarColor(Color.WHITE);getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        FrameLayout root=new FrameLayout(this);webView=new WebView(this);
        root.addView(webView,new FrameLayout.LayoutParams(-1,-1));setContentView(root);
        root.setOnApplyWindowInsetsListener((v,insets)->{FrameLayout.LayoutParams lp=(FrameLayout.LayoutParams)webView.getLayoutParams();lp.setMargins(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());webView.setLayoutParams(lp);return insets;});root.requestApplyInsets();

        WebSettings s=webView.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setDatabaseEnabled(true);s.setGeolocationEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);s.setCacheMode(WebSettings.LOAD_DEFAULT);
        webView.addJavascriptInterface(new CityBridge(),"AndroidBridge");
        webView.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView v,String u){super.onPageFinished(v,u);tryLoadWeather();}});
        webView.setWebChromeClient(new WebChromeClient(){@Override public void onGeolocationPermissionsShowPrompt(String origin,GeolocationPermissions.Callback cb){boolean g=Build.VERSION.SDK_INT<23||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;cb.invoke(origin,g,false);}@Override public void onPermissionRequest(PermissionRequest r){r.deny();}});
        webView.loadDataWithBaseURL("https://appassets.androidplatform.net/",new String(clear,StandardCharsets.UTF_8),"text/html","UTF-8",null);
        if(Build.VERSION.SDK_INT>=23&&checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},LOCATION_REQ);
    }

    private byte[] decryptAsset() throws Exception{
        InputStream in=getAssets().open("index.dat");ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[8192];int n;while((n=in.read(buf))>0)out.write(buf,0,n);in.close();
        Cipher c=Cipher.getInstance("AES/CBC/PKCS5Padding");c.init(Cipher.DECRYPT_MODE,new SecretKeySpec(hex(AES_KEY_HEX),"AES"),new IvParameterSpec(hex(AES_IV_HEX)));return c.doFinal(out.toByteArray());
    }
    private boolean verifySignature(){try{Signature sig;if(Build.VERSION.SDK_INT>=28){PackageInfo p=getPackageManager().getPackageInfo(getPackageName(),PackageManager.GET_SIGNING_CERTIFICATES);sig=p.signingInfo.getApkContentsSigners()[0];}else{PackageInfo p=getPackageManager().getPackageInfo(getPackageName(),PackageManager.GET_SIGNATURES);sig=p.signatures[0];}return EXPECTED_CERT_SHA.equalsIgnoreCase(sha256(sig.toByteArray()));}catch(Exception e){return false;}}
    private static byte[] hex(String s){int len=s.length();byte[] d=new byte[len/2];for(int i=0;i<len;i+=2)d[i/2]=(byte)((Character.digit(s.charAt(i),16)<<4)+Character.digit(s.charAt(i+1),16));return d;}
    private static String sha256(byte[] b){try{byte[] h=MessageDigest.getInstance("SHA-256").digest(b);StringBuilder x=new StringBuilder();for(byte q:h)x.append(String.format(Locale.US,"%02x",q));return x.toString();}catch(Exception e){return "";}}
    private void block(String msg){TextView t=new TextView(this);t.setText(msg);t.setTextSize(18);t.setPadding(40,80,40,40);setContentView(t);}
    private void tryLoadWeather(){if(webView==null)return;boolean g=Build.VERSION.SDK_INT<23||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;if(g)webView.postDelayed(()->webView.evaluateJavascript("if(typeof loadLiveWeather==='function'){loadLiveWeather();}",null),500);}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==LOCATION_REQ)tryLoadWeather();}
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}
    class CityBridge{@JavascriptInterface public String getCity(double lat,double lon){try{Geocoder g=new Geocoder(MainActivity.this,Locale.getDefault());List<Address>a=g.getFromLocation(lat,lon,1);if(a!=null&&!a.isEmpty()){Address x=a.get(0);String c=x.getLocality();if(c==null||c.trim().isEmpty())c=x.getSubAdminArea();if(c==null||c.trim().isEmpty())c=x.getAdminArea();return c==null?"":c;}}catch(Exception ignored){}return "";}}
}
''',encoding='utf-8')

print('Protected free tester patch applied')