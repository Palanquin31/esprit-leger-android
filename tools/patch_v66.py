from pathlib import Path
from PIL import Image
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# ---------- Web -> native notifications bridge ----------
bridge=r'''
<script id="v66-native-notifications">
function nativeNotificationSettingsV66(){
  try{return localStorage.getItem("esprit_notifications") || JSON.stringify(typeof prepareNotificationPayload==='function'?prepareNotificationPayload():{appointments:true,tasks:true,bestMoment:true,busyDay:true,success:false,frequency:"Équilibré"});}
  catch(e){return JSON.stringify({appointments:true,tasks:true,bestMoment:true,busyDay:true,success:false,frequency:"Équilibré"});}
}
function syncNativeNotificationsV66(){
  try{
    if(window.AndroidNotifications && typeof window.AndroidNotifications.sync==='function'){
      const state=localStorage.getItem("esprit_leger_premiere_connexion") || "{}";
      window.AndroidNotifications.sync(state,nativeNotificationSettingsV66());
    }
  }catch(e){console.warn("Native notification sync",e);}
}
const saveStateBeforeV66=saveState;
saveState=function(){saveStateBeforeV66();setTimeout(syncNativeNotificationsV66,80);};
const saveNotificationSettingsBeforeV66=saveNotificationSettings;
saveNotificationSettings=function(){saveNotificationSettingsBeforeV66();setTimeout(syncNativeNotificationsV66,80);};
document.addEventListener("change",e=>{if(e.target && /^notif/.test(e.target.id||""))setTimeout(syncNativeNotificationsV66,100);});
setTimeout(syncNativeNotificationsV66,1200);
</script>
'''
if 'id="v66-native-notifications"' not in html:
    html=html.replace('</body>',bridge+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

# ---------- Manifest ----------
manifest=root/'app/src/main/AndroidManifest.xml'
ms=manifest.read_text(encoding='utf-8')
for perm in ['android.permission.POST_NOTIFICATIONS','android.permission.RECEIVE_BOOT_COMPLETED']:
    tag=f'<uses-permission android:name="{perm}" />'
    if tag not in ms:
        ms=ms.replace('<application',tag+'\n<application',1)
receivers='''
        <receiver android:name=".NotificationReceiver" android:exported="false" />
        <receiver android:name=".BootReceiver" android:enabled="true" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
            </intent-filter>
        </receiver>
'''
if '.NotificationReceiver' not in ms:
    ms=ms.replace('</application>',receivers+'\n    </application>',1)
manifest.write_text(ms,encoding='utf-8')

java_dir=root/'app/src/main/java/com/espritlibre/app'
java_dir.mkdir(parents=True,exist_ok=True)

# ---------- MainActivity with native JS bridge ----------
main=java_dir/'MainActivity.java'
main.write_text(r'''package com.espritlibre.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
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
        webView=new WebView(this);
        setContentView(webView);
        webView.setOnApplyWindowInsetsListener((v,i)->{v.setPadding(0,i.getSystemWindowInsetTop(),0,i.getSystemWindowInsetBottom());return i;});
        webView.requestApplyInsets();
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

# ---------- Notification receiver ----------
(java_dir/'NotificationReceiver.java').write_text(r'''package com.espritlibre.app;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class NotificationReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent){
        NotificationScheduler.ensureChannel(context);
        String title=intent.getStringExtra("title");
        String text=intent.getStringExtra("text");
        int id=intent.getIntExtra("id",(int)(System.currentTimeMillis()%100000));
        Intent open=new Intent(context,MainActivity.class);open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi=PendingIntent.getActivity(context,id,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(context,NotificationScheduler.CHANNEL_ID):new Notification.Builder(context);
        b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle(title==null?"L'Esprit Léger":title).setContentText(text==null?"Un rappel t'attend.":text).setContentIntent(pi).setAutoCancel(true).setStyle(new Notification.BigTextStyle().bigText(text));
        ((NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE)).notify(id,b.build());
    }
}
''',encoding='utf-8')

# ---------- Boot receiver ----------
(java_dir/'BootReceiver.java').write_text(r'''package com.espritlibre.app;
import android.content.BroadcastReceiver;import android.content.Context;import android.content.Intent;
public class BootReceiver extends BroadcastReceiver{
 @Override public void onReceive(Context c,Intent i){String s=c.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).getString("state","{}");String n=c.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).getString("settings","{}");NotificationScheduler.reschedule(c,s,n);}
}
''',encoding='utf-8')

# ---------- Scheduler ----------
(java_dir/'NotificationScheduler.java').write_text(r'''package com.espritlibre.app;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

public final class NotificationScheduler {
    public static final String CHANNEL_ID="esprit_leger_rappels";
    private static final String PREF="esprit_native_notifications";
    private NotificationScheduler(){}

    public static void ensureChannel(Context c){
        if(Build.VERSION.SDK_INT>=26){NotificationManager nm=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);NotificationChannel ch=new NotificationChannel(CHANNEL_ID,"Rappels L'Esprit Léger",NotificationManager.IMPORTANCE_DEFAULT);ch.setDescription("Rendez-vous, tâches et conseils d'organisation");nm.createNotificationChannel(ch);}
    }
    private static int dayIndex(String fr){String s=fr==null?"":fr.toLowerCase(Locale.ROOT);if(s.startsWith("lundi"))return Calendar.MONDAY;if(s.startsWith("mardi"))return Calendar.TUESDAY;if(s.startsWith("mercredi"))return Calendar.WEDNESDAY;if(s.startsWith("jeudi"))return Calendar.THURSDAY;if(s.startsWith("vendredi"))return Calendar.FRIDAY;if(s.startsWith("samedi"))return Calendar.SATURDAY;if(s.startsWith("dimanche"))return Calendar.SUNDAY;return -1;}
    private static Calendar nextOccurrence(String day,String hhmm){
        Calendar now=Calendar.getInstance(),c=Calendar.getInstance();int dow=dayIndex(day);if(dow<0)dow=now.get(Calendar.DAY_OF_WEEK);String[] p=(hhmm==null?"09:00":hhmm).split(":");int h=9,m=0;try{h=Integer.parseInt(p[0]);m=p.length>1?Integer.parseInt(p[1]):0;}catch(Exception ignored){}
        c.set(Calendar.HOUR_OF_DAY,h);c.set(Calendar.MINUTE,m);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);int delta=(dow-now.get(Calendar.DAY_OF_WEEK)+7)%7;c.add(Calendar.DAY_OF_YEAR,delta);if(c.getTimeInMillis()<=now.getTimeInMillis()+60000)c.add(Calendar.DAY_OF_YEAR,7);return c;
    }
    private static void cancelOld(Context c){AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Set<String> ids=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getStringSet("ids",Collections.emptySet());for(String x:ids){try{int id=Integer.parseInt(x);PendingIntent pi=PendingIntent.getBroadcast(c,id,new Intent(c,NotificationReceiver.class),PendingIntent.FLAG_NO_CREATE|PendingIntent.FLAG_IMMUTABLE);if(pi!=null){am.cancel(pi);pi.cancel();}}catch(Exception ignored){}}c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().remove("ids").apply();}
    private static void schedule(Context c,int id,long when,String title,String text,Set<String> ids){if(when<=System.currentTimeMillis()+30000)return;AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Intent in=new Intent(c,NotificationReceiver.class);in.putExtra("id",id);in.putExtra("title",title);in.putExtra("text",text);PendingIntent pi=PendingIntent.getBroadcast(c,id,in,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);if(Build.VERSION.SDK_INT>=23)am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,pi);else am.set(AlarmManager.RTC_WAKEUP,when,pi);ids.add(String.valueOf(id));}

    public static synchronized void reschedule(Context c,String stateJson,String settingsJson){
        ensureChannel(c);cancelOld(c);Set<String> ids=new HashSet<>();
        try{
            JSONObject st=new JSONObject(stateJson==null?"{}":stateJson),set=new JSONObject(settingsJson==null?"{}":settingsJson);
            boolean appointments=set.optBoolean("appointments",true),tasks=set.optBoolean("tasks",true),best=set.optBoolean("bestMoment",true),busy=set.optBoolean("busyDay",true),success=set.optBoolean("success",false);
            String freq=set.optString("frequency","Équilibré");int cap=freq.contains("Peu")?1:(freq.contains("Plus")?4:2);
            JSONArray ev=st.optJSONArray("events");if(ev==null)ev=new JSONArray();
            HashMap<String,Integer> dayCount=new HashMap<>(),dayMinutes=new HashMap<>();ArrayList<JSONObject> candidates=new ArrayList<>();
            for(int i=0;i<ev.length();i++){JSONObject e=ev.optJSONObject(i);if(e==null)continue;String day=e.optString("day",""),type=e.optString("type","Tâche"),title=e.optString("title","Activité"),start=e.optString("start","09:00"),end=e.optString("end",start);dayCount.put(day,dayCount.getOrDefault(day,0)+1);dayMinutes.put(day,dayMinutes.getOrDefault(day,0)+duration(start,end));boolean isAppointment="Rendez-vous".equals(type);if((isAppointment&&appointments)||(!isAppointment&&tasks)){e.put("_reminder",isAppointment?30:15);candidates.add(e);}}
            Collections.sort(candidates,new Comparator<JSONObject>(){public int compare(JSONObject a,JSONObject b){return nextOccurrence(a.optString("day"),a.optString("start")).compareTo(nextOccurrence(b.optString("day"),b.optString("start")));}});
            HashMap<String,Integer> scheduledPerDay=new HashMap<>();
            for(JSONObject e:candidates){String day=e.optString("day",""),key=day.toLowerCase(Locale.ROOT);int n=scheduledPerDay.getOrDefault(key,0);if(n>=cap)continue;Calendar at=nextOccurrence(day,e.optString("start","09:00"));at.add(Calendar.MINUTE,-e.optInt("_reminder",15));String type=e.optString("type","Tâche"),title=e.optString("title","Activité");int id=Math.abs((day+e.optString("start")+title+type).hashCode());schedule(c,id,at.getTimeInMillis(),"Rappel · "+title,("Rendez-vous".equals(type)?"Ton rendez-vous commence bientôt.":"Cette tâche arrive dans ton planning."),ids);scheduledPerDay.put(key,n+1);}
            if(busy){for(String day:dayCount.keySet()){if(dayCount.get(day)>=4||dayMinutes.getOrDefault(day,0)>=360){Calendar at=nextOccurrence(day,"08:00");int id=Math.abs(("busy"+day).hashCode());schedule(c,id,at.getTimeInMillis(),"Journée chargée","Ton planning est dense aujourd'hui. Garde une marge et évite d'ajouter une contrainte non essentielle.",ids);}}}
            JSONArray floating=st.optJSONArray("floating");int floatingCount=floating==null?0:floating.length();
            if(best&&floatingCount>0){String lightest="Lundi";int min=Integer.MAX_VALUE;String[] ds={"Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"};for(String d:ds){int m=dayMinutes.getOrDefault(d,0);if(m<min){min=m;lightest=d;}}Calendar at=nextOccurrence(lightest,"09:30");schedule(c,77123,at.getTimeInMillis(),"Bon moment pour alléger ta liste",floatingCount+" tâche(s) restent à placer. "+lightest+" est actuellement l'une des journées les plus légères.",ids);}
            if(success&&ev.length()>0){Calendar at=nextOccurrence("Dimanche","19:00");schedule(c,77124,at.getTimeInMillis(),"Bilan de la semaine","Prends une minute pour regarder ce que tu as allégé ou terminé cette semaine.",ids);}
        }catch(Exception ignored){}
        c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putStringSet("ids",ids).apply();
    }
    private static int duration(String a,String b){try{String[] x=a.split(":"),y=b.split(":");int aa=Integer.parseInt(x[0])*60+Integer.parseInt(x[1]),bb=Integer.parseInt(y[0])*60+Integer.parseInt(y[1]);return Math.max(0,bb-aa);}catch(Exception e){return 0;}}
}
''',encoding='utf-8')

# ---------- Icon: crop the actual rounded-square artwork, then recenter it ----------
drawable=root/'app/src/main/res/drawable'
source=Image.open(drawable/'app_icon.png').convert('RGBA')
# The original 512 artwork contains a large asymmetric vignette around the actual logo.
# Crop around the real rounded square first; this recentres the visual mass instead of just scaling it.
crop=source.crop((92,92,488,488)).resize((472,472),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(512,512),(231,157,210,255))
canvas.alpha_composite(crop,((512-472)//2,(512-472)//2-2))
canvas.convert('RGB').save(drawable/'app_icon_full.png',quality=96)
(drawable/'app_icon_adaptive_bg.xml').write_text('''<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n  <item><bitmap android:src="@drawable/app_icon_full" android:gravity="fill"/></item>\n</layer-list>\n''',encoding='utf-8')

# Version bump
bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.6"',b)
bp.write_text(b,encoding='utf-8')
print('V6.6 native notifications + icon centering applied')
