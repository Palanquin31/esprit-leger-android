package com.espritlibre.app;

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
        String title=intent.getStringExtra("title"),text=intent.getStringExtra("text");
        int id=intent.getIntExtra("id",(int)(System.currentTimeMillis()%100000));
        Intent open=new Intent(context,MainActivity.class);open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi=PendingIntent.getActivity(context,id,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(context,NotificationScheduler.CHANNEL_ID):new Notification.Builder(context);
        String safeTitle=(title==null||title.trim().isEmpty())?"L'Esprit Léger":title;
        String safeText=(text==null||text.trim().isEmpty())?"Un rappel t'attend.":text;
        b.setSmallIcon(R.drawable.ic_notification_leaf).setContentTitle(safeTitle).setContentText(safeText).setContentIntent(pi).setAutoCancel(true).setStyle(new Notification.BigTextStyle().bigText(safeText));
        ((NotificationManager)context.getSystemService(Context.NOTIFICATION_SERVICE)).notify(id,b.build());
    }
}
