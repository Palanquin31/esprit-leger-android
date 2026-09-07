package com.espritlibre.app;
import android.content.BroadcastReceiver;import android.content.Context;import android.content.Intent;
public class BootReceiver extends BroadcastReceiver{
 @Override public void onReceive(Context c,Intent i){String s=c.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).getString("state","{}");String n=c.getSharedPreferences("esprit_native_notifications",Context.MODE_PRIVATE).getString("settings","{}");NotificationScheduler.reschedule(c,s,n);}
}
