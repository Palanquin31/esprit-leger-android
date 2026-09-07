package com.espritlibre.app;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;
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
    private static final String TAG="EspritNotifications";
    private NotificationScheduler(){}

    public static void ensureChannel(Context c){if(Build.VERSION.SDK_INT>=26){NotificationManager nm=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);NotificationChannel ch=new NotificationChannel(CHANNEL_ID,"Rappels L'Esprit Léger",NotificationManager.IMPORTANCE_DEFAULT);ch.setDescription("Rendez-vous, tâches et conseils d'organisation");nm.createNotificationChannel(ch);}}
    private static Calendar dayStart(Calendar in){Calendar c=(Calendar)in.clone();c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);return c;}
    private static Calendar parseDate(String iso){try{String[] p=iso.split("-");Calendar c=Calendar.getInstance();c.set(Integer.parseInt(p[0]),Integer.parseInt(p[1])-1,Integer.parseInt(p[2]),0,0,0);c.set(Calendar.MILLISECOND,0);return c;}catch(Exception e){return null;}}
    private static void setTime(Calendar c,String hhmm){String[] p=(hhmm==null?"09:00":hhmm).split(":");int h=9,m=0;try{h=Integer.parseInt(p[0]);m=p.length>1?Integer.parseInt(p[1]):0;}catch(Exception ignored){}c.set(Calendar.HOUR_OF_DAY,h);c.set(Calendar.MINUTE,m);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);}
    private static String iso(Calendar c){return String.format(Locale.ROOT,"%04d-%02d-%02d",c.get(Calendar.YEAR),c.get(Calendar.MONTH)+1,c.get(Calendar.DAY_OF_MONTH));}
    private static String frDay(Calendar c){String[] d={"","Dimanche","Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"};return d[c.get(Calendar.DAY_OF_WEEK)];}
    private static Calendar weekMonday(Calendar c){Calendar x=dayStart(c);int delta=(x.get(Calendar.DAY_OF_WEEK)+5)%7;x.add(Calendar.DAY_OF_YEAR,-delta);return x;}
    private static boolean eventOccurs(JSONObject e,Calendar date){
        String dateS=e.optString("date","");String rep=e.optString("repeat","Aucune");
        if(!dateS.isEmpty()){
            Calendar target=parseDate(dateS);if(target==null)return false;Calendar d=dayStart(date),t=dayStart(target);if(d.before(t))return false;
            if("Aucune".equals(rep))return iso(d).equals(iso(t));
            if("Chaque semaine".equals(rep)||"Semaine A".equals(rep)||"Semaine B".equals(rep))return d.get(Calendar.DAY_OF_WEEK)==t.get(Calendar.DAY_OF_WEEK);
            if("Tous les jours d'école".equals(rep))return d.get(Calendar.DAY_OF_WEEK)>=Calendar.MONDAY&&d.get(Calendar.DAY_OF_WEEK)<=Calendar.FRIDAY;
            if("Chaque mois".equals(rep))return d.get(Calendar.DAY_OF_MONTH)==t.get(Calendar.DAY_OF_MONTH);
            return iso(d).equals(iso(t));
        }
        String day=e.optString("day","");if("Aujourd'hui".equals(day))return iso(date).equals(iso(Calendar.getInstance()));return frDay(date).equals(day);
    }
    private static int duration(String a,String b){try{String[] x=a.split(":"),y=b.split(":");int aa=Integer.parseInt(x[0])*60+Integer.parseInt(x[1]),bb=Integer.parseInt(y[0])*60+Integer.parseInt(y[1]);int d=bb-aa;if(d<0)d+=1440;return Math.max(0,d);}catch(Exception e){return 0;}}
    private static boolean isTaskReminderType(String type){return "Tâche".equals(type)||"Courses".equals(type)||"Sport".equals(type)||"Temps pour soi".equals(type)||"Repas".equals(type);}
    private static void cancelOld(Context c){AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Set<String> ids=c.getSharedPreferences(PREF,Context.MODE_PRIVATE).getStringSet("ids",Collections.emptySet());for(String x:ids){try{int id=Integer.parseInt(x);PendingIntent pi=PendingIntent.getBroadcast(c,id,new Intent(c,NotificationReceiver.class),PendingIntent.FLAG_NO_CREATE|PendingIntent.FLAG_IMMUTABLE);if(pi!=null){am.cancel(pi);pi.cancel();}}catch(Exception ignored){}}c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().remove("ids").apply();}
    private static void schedule(Context c,int id,long when,String title,String text,Set<String> ids){if(when<=System.currentTimeMillis()+30000)return;AlarmManager am=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);Intent in=new Intent(c,NotificationReceiver.class);in.putExtra("id",id);in.putExtra("title",title);in.putExtra("text",text);PendingIntent pi=PendingIntent.getBroadcast(c,id,in,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);if(Build.VERSION.SDK_INT>=23)am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,when,pi);else am.set(AlarmManager.RTC_WAKEUP,when,pi);ids.add(String.valueOf(id));}
    private static ArrayList<JSONObject> eventsForDate(JSONObject st,Calendar date){
        ArrayList<JSONObject> out=new ArrayList<>();JSONArray ev=st.optJSONArray("events");if(ev!=null)for(int i=0;i<ev.length();i++){JSONObject e=ev.optJSONObject(i);if(e!=null&&eventOccurs(e,date))out.add(e);}
        JSONArray templates=st.optJSONArray("weekTemplates");if(templates!=null){String wk=iso(weekMonday(date)),day=frDay(date);for(int i=0;i<templates.length();i++){JSONObject t=templates.optJSONObject(i);if(t==null)continue;JSONArray weeks=t.optJSONArray("appliedWeeks");boolean active=false;if(weeks!=null)for(int j=0;j<weeks.length();j++)if(wk.equals(weeks.optString(j))){active=true;break;}if(!active)continue;JSONArray slots=t.optJSONArray("slots");if(slots==null)continue;for(int j=0;j<slots.length();j++){JSONObject s=slots.optJSONObject(j);if(s==null||!day.equals(s.optString("day")))continue;JSONObject x=new JSONObject();try{x.put("type",s.optString("type","Travail"));x.put("title",t.optString("name","Semaine type")+" · "+s.optString("label","Créneau"));x.put("start",s.optString("start","09:00"));x.put("end",s.optString("end","10:00"));x.put("person",s.optString("person",""));}catch(Exception ignored){}out.add(x);}}}
        Collections.sort(out,new Comparator<JSONObject>(){public int compare(JSONObject a,JSONObject b){return a.optString("start","09:00").compareTo(b.optString("start","09:00"));}});return out;
    }

    public static synchronized void reschedule(Context c,String stateJson,String settingsJson){
        ensureChannel(c);cancelOld(c);Set<String> ids=new HashSet<>();
        try{
            JSONObject st=new JSONObject(stateJson==null?"{}":stateJson),set=new JSONObject(settingsJson==null?"{}":settingsJson);
            boolean appointments=set.optBoolean("appointments",true),tasks=set.optBoolean("tasks",true),best=set.optBoolean("bestMoment",true),busy=set.optBoolean("busyDay",true),success=set.optBoolean("success",false);
            String freq=set.optString("frequency","Équilibré");int cap=freq.contains("Peu")?1:(freq.contains("Plus")?4:2);
            Calendar today=dayStart(Calendar.getInstance());HashMap<String,Integer> perDay=new HashMap<>(),minutesByDate=new HashMap<>();
            for(int off=0;off<21;off++){
                Calendar date=(Calendar)today.clone();date.add(Calendar.DAY_OF_YEAR,off);String dateKey=iso(date);ArrayList<JSONObject> list=eventsForDate(st,date);int minutes=0;for(JSONObject e:list)minutes+=duration(e.optString("start","09:00"),e.optString("end","10:00"));minutesByDate.put(dateKey,minutes);
                for(JSONObject e:list){int n=perDay.getOrDefault(dateKey,0);if(n>=cap)break;String type=e.optString("type","Tâche");boolean rdv="Rendez-vous".equals(type),taskLike=isTaskReminderType(type);if(!((rdv&&appointments)||(taskLike&&tasks)))continue;Calendar at=(Calendar)date.clone();setTime(at,e.optString("start","09:00"));at.add(Calendar.MINUTE,rdv?-30:-15);String title=e.optString("title","Activité"),start=e.optString("start","09:00");int id=Math.abs((dateKey+start+title+type).hashCode());String text=rdv?("« "+title+" » est prévu à "+start+"."):("« "+title+" » est prévu à "+start+" dans ton planning.");schedule(c,id,at.getTimeInMillis(),rdv?"Rendez-vous bientôt":"Rappel du planning",text,ids);perDay.put(dateKey,n+1);}
                if(busy&&(list.size()>=4||minutes>=360)&&perDay.getOrDefault(dateKey,0)<cap){Calendar at=(Calendar)date.clone();setTime(at,"08:00");int id=Math.abs(("busy"+dateKey).hashCode());schedule(c,id,at.getTimeInMillis(),"Journée chargée","Ton planning est dense aujourd'hui. Garde une marge et évite d'ajouter une activité facultative.",ids);perDay.put(dateKey,perDay.getOrDefault(dateKey,0)+1);}
            }
            JSONArray floating=st.optJSONArray("floating");int floatingCount=floating==null?0:floating.length();
            if(best&&floatingCount>0){String bestDate=null;int min=Integer.MAX_VALUE;for(int off=0;off<7;off++){Calendar d=(Calendar)today.clone();d.add(Calendar.DAY_OF_YEAR,off);String k=iso(d),m=minutesByDate.getOrDefault(k,0)<min?k:null;if(m!=null){min=minutesByDate.getOrDefault(k,0);bestDate=k;}}if(bestDate!=null&&perDay.getOrDefault(bestDate,0)<cap){Calendar at=parseDate(bestDate);setTime(at,"09:30");int id=Math.abs(("best"+bestDate).hashCode());schedule(c,id,at.getTimeInMillis(),"Bon moment pour alléger ta liste",floatingCount+" tâche(s) restent à placer. Cette journée possède actuellement davantage de marge.",ids);}}
            if(success){Calendar sun=(Calendar)today.clone();int delta=(Calendar.SUNDAY-sun.get(Calendar.DAY_OF_WEEK)+7)%7;sun.add(Calendar.DAY_OF_YEAR,delta);setTime(sun,"19:00");String k=iso(sun);if(perDay.getOrDefault(k,0)<cap){schedule(c,Math.abs(("success"+k).hashCode()),sun.getTimeInMillis(),"Décharge réussie 🌿","Prends une minute pour regarder ce que tu as terminé, déplacé ou réussi à alléger cette semaine.",ids);}}
        }catch(Exception e){Log.w(TAG,"Notification reschedule failed",e);}
        c.getSharedPreferences(PREF,Context.MODE_PRIVATE).edit().putStringSet("ids",ids).apply();
    }
}
