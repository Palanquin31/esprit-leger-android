package com.espritlibre.app;

import android.Manifest;
import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
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
        // V8.6: never let WebView auto-darken the carefully designed Light palette.
        if(Build.VERSION.SDK_INT>=33){
            s.setAlgorithmicDarkeningAllowed(false);
        }else if(Build.VERSION.SDK_INT>=29){
            s.setForceDark(WebSettings.FORCE_DARK_OFF);
        }
        webView.addJavascriptInterface(new NotificationBridge(this),"AndroidNotifications");
        webView.addJavascriptInterface(new ThemeBridge(),"AndroidTheme");
        webView.addJavascriptInterface(new CityBridge(),"AndroidBridge");
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

    class CityBridge {
        @JavascriptInterface public String getCity(double lat,double lon){
            try{
                android.location.Geocoder g=new android.location.Geocoder(MainActivity.this,java.util.Locale.getDefault());
                java.util.List<android.location.Address> a=g.getFromLocation(lat,lon,1);
                if(a!=null&&!a.isEmpty()){
                    android.location.Address x=a.get(0);
                    String c=x.getLocality();
                    if(c==null||c.trim().isEmpty())c=x.getSubAdminArea();
                    if(c==null||c.trim().isEmpty())c=x.getAdminArea();
                    return c==null?"":c;
                }
            }catch(Exception ignored){}
            return "";
        }
    }

    private void tryLoadWeather(){if(webView==null)return;boolean g=Build.VERSION.SDK_INT<23||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;if(g)webView.postDelayed(()->webView.evaluateJavascript("if(typeof loadLiveWeather==='function'){loadLiveWeather();}",null),500);}
    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){super.onRequestPermissionsResult(r,p,g);if(r==LOCATION_REQ)tryLoadWeather();if(r==NOTIFICATION_REQ&&webView!=null)webView.postDelayed(()->webView.evaluateJavascript("if(typeof syncNativeNotificationsV66==='function')syncNativeNotificationsV66();",null),250);}
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}

    private void applyResolvedSystemBars(boolean dark){
        int bg=dark?Color.rgb(18,16,24):Color.rgb(250,250,250);
        getWindow().setStatusBarColor(bg);
        getWindow().setNavigationBarColor(bg);
        if(Build.VERSION.SDK_INT>=23){
            int flags=0;
            if(!dark)flags|=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if(Build.VERSION.SDK_INT>=26 && !dark)flags|=View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            getWindow().getDecorView().setSystemUiVisibility(flags);
        }
        if(Build.VERSION.SDK_INT>=30){
            WindowInsetsController c=getWindow().getInsetsController();
            if(c!=null){
                int appearance=dark?0:(WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS);
                int mask=WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(appearance,mask);
                c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());
            }
        }
    }

    public class ThemeBridge {
        @JavascriptInterface public String getSystemMode(){
            int night=getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK;
            return night==Configuration.UI_MODE_NIGHT_YES?"dark":"light";
        }
        @JavascriptInterface public void applyResolvedMode(String mode){
            final boolean dark="dark".equalsIgnoreCase(mode);
            runOnUiThread(()->applyResolvedSystemBars(dark));
        }
    }

    @Override public void onConfigurationChanged(Configuration newConfig){
        super.onConfigurationChanged(newConfig);
        if(webView!=null){
            webView.post(()->webView.evaluateJavascript("if(typeof applySystemThemeV86==='function')applySystemThemeV86();",null));
        }
    }

    public static class NotificationBridge {
        private final Context context;
        NotificationBridge(Context c){context=c.getApplicationContext();}
        @JavascriptInterface public void sync(String stateJson,String settingsJson){
            context.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).edit().putString("state",stateJson).putString("settings",settingsJson).apply();
            NotificationScheduler.reschedule(context,stateJson,settingsJson);
        }
        @JavascriptInterface public String status(){
            try{
                NotificationManager nm=(NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE);
                boolean enabled=Build.VERSION.SDK_INT<24 || nm.areNotificationsEnabled();
                boolean channelEnabled=true;
                if(Build.VERSION.SDK_INT>=26){NotificationChannel ch=nm.getNotificationChannel(NotificationScheduler.CHANNEL_ID);channelEnabled=ch==null || ch.getImportance()!=NotificationManager.IMPORTANCE_NONE;}
                return "{\"enabled\":"+enabled+",\"channelEnabled\":"+channelEnabled+"}";
            }catch(Exception e){return "{\"enabled\":true,\"channelEnabled\":true}";}
        }

    }
}
