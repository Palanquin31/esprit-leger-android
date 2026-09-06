from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.8 — weekly-test stabilization.
# Keep the validated V8.6 theme and V8.7 calendar untouched.
# Fix modal safe height, simplify event/task creation, remove legal beta flash,
# harden backup/restore, and use a leaf-only Android notification icon.

# 1) Event/task creation: direct Start/End time entry is enough.
html,n=re.subn(
    r'\s*<div class="slot-choice">\s*<label>Moment de la journée</label>\s*'
    r'<select id="dayPart" onchange="applyDayPart\(\)">.*?</select>\s*'
    r'<p class="note">Tu peux choisir un moment, puis ajuster l\'heure à la minute près\.</p>\s*</div>\s*',
    '\n',html,count=1,flags=re.S)
if n!=1:
    raise SystemExit('event day-part block not found')

# 2) First-run/legal beta screen must never flash on an already configured installation.
html,n=re.subn(r'<div class="modal show" id="betaNdaModal"',
               '<div class="modal" id="betaNdaModal"',html,count=1)
if n!=1:
    raise SystemExit('beta modal initial show marker not found')
# Remove obsolete unconditional opener. V6.1/V6.2 first-run sequence remains authoritative.
html,n=re.subn(r'\s*setTimeout\(startFirstOpenSequence,\s*50\);', '', html, count=1)
if n!=1:
    raise SystemExit('obsolete 50ms beta opener not found')
# A completed V6.1 onboarding is also a completed onboarding for later versions.
html=html.replace(
    'if(localStorage.getItem("esprit_leger_first_run_v62_complete")==="1"){hideV62FirstRun();return;}',
    'if(localStorage.getItem("esprit_leger_first_run_v62_complete")==="1" || localStorage.getItem("esprit_leger_first_run_complete")==="1"){hideV62FirstRun();return;}',
    1)

# 3) Safe modal geometry: leave the Android status area visible and keep bottom controls above tabs.
css=r'''
<style id="v88-week-test-ui">
#eventModal,#weekModal{
  padding-top:74px !important;
  padding-bottom:146px !important;
  align-items:flex-end !important;
  box-sizing:border-box !important;
}
#eventModal .sheet,#weekModal .sheet{
  max-height:calc(100dvh - 232px) !important;
  overflow-y:auto !important;
  overscroll-behavior:contain !important;
  padding-bottom:26px !important;
  margin-top:0 !important;
}
#eventModal .event-actions-v81,#weekModal .modal-validate{
  position:static !important;
  bottom:auto !important;
  box-shadow:none !important;
}
@media(max-height:720px){
  #eventModal,#weekModal{padding-top:62px !important;padding-bottom:132px !important;}
  #eventModal .sheet,#weekModal .sheet{max-height:calc(100dvh - 202px) !important;}
}
</style>
'''
if 'id="v88-week-test-ui"' not in html:
    html += css

# 4) Backup/restore V8.8: save current state first, export explicit parsed state + storage,
# and accept both the new format and the old V6.5 backup format.
backup_js=r'''
<script id="v88-backup-restore">
(function(){
  const BACKUP_KEYS_V88=[
    'esprit_leger_premiere_connexion',
    'esprit_consents',
    'esprit_notifications',
    'esprit_leger_first_run_complete',
    'esprit_leger_first_run_v62_complete',
    'esprit_leger_beta_agreement'
  ];

  function safeParseV88(v){
    if(v==null||v==='')return null;
    if(typeof v==='object')return v;
    try{return JSON.parse(v);}catch(e){return null;}
  }

  window.collectBackupV65=function(){
    try{if(typeof saveState==='function')saveState();}catch(e){}
    const storage={};
    BACKUP_KEYS_V88.forEach(k=>{const v=localStorage.getItem(k);if(v!==null)storage[k]=v;});
    const appState=safeParseV88(storage.esprit_leger_premiere_connexion);
    return {
      format:'esprit-leger-backup',
      formatVersion:2,
      appVersion:'8.8',
      savedAt:new Date().toISOString(),
      appState:appState||{},
      storage
    };
  };

  window.generateBackupV65=function(){
    const t=document.getElementById('backupTextV65');
    if(t)t.value=JSON.stringify(window.collectBackupV65(),null,2);
  };

  window.importBackupV65=function(){
    const t=document.getElementById('backupTextV65');
    try{
      const b=JSON.parse(t?.value||'');
      const incomingStorage=(b&&b.storage&&typeof b.storage==='object')?b.storage:{};
      let appState=null;
      if(b&&b.appState&&typeof b.appState==='object')appState=b.appState;
      if(!appState && typeof b?.state==='string')appState=safeParseV88(b.state); // V6.5
      if(!appState && typeof incomingStorage.esprit_leger_premiere_connexion==='string')appState=safeParseV88(incomingStorage.esprit_leger_premiere_connexion);
      if(!appState || typeof appState!=='object' || Array.isArray(appState))throw new Error('missing app state');

      // Restore only known application keys.
      BACKUP_KEYS_V88.forEach(k=>{
        const v=incomingStorage[k];
        if(typeof v==='string')localStorage.setItem(k,v);
      });
      localStorage.setItem('esprit_leger_premiere_connexion',JSON.stringify(appState));

      // Old V6.5 backups stored these fields at the root.
      if(typeof b?.consents==='string')localStorage.setItem('esprit_consents',b.consents);
      if(typeof b?.notifications==='string')localStorage.setItem('esprit_notifications',b.notifications);
      if(typeof b?.beta==='string')localStorage.setItem('esprit_leger_beta_agreement',b.beta);
      if(typeof b?.firstRun==='string')localStorage.setItem('esprit_leger_first_run_v62_complete',b.firstRun);

      // A restored real app state must never be overwritten by setup/onboarding on reload.
      localStorage.setItem('esprit_leger_first_run_complete','1');
      localStorage.setItem('esprit_leger_first_run_v62_complete','1');

      alert('Sauvegarde restaurée. L’application va recharger tes données.');
      location.reload();
    }catch(e){
      console.warn('Backup restore V8.8',e);
      alert('Sauvegarde invalide ou incomplète. Aucune donnée n’a été modifiée.');
    }
  };
})();
</script>
'''
if 'id="v88-backup-restore"' not in html:
    html += backup_js

# 5) Leaf-only Android notification small icon.
drawable=root/'app/src/main/res/drawable'
drawable.mkdir(parents=True,exist_ok=True)
(drawable/'ic_notification_leaf.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M20.7,3.3C15.2,3.5 9.8,5.5 6.5,8.7C3.2,11.9 3.2,16.7 6.2,19.1C9.1,21.4 13.6,20.7 16.4,17.8C19.4,14.7 20.7,9.5 20.7,3.3ZM7.2,18.1C9.5,14.1 12.6,10.9 17.3,7.9C13.8,11.2 11.1,14.8 9.3,18.9C8.5,18.7 7.8,18.5 7.2,18.1Z" />
</vector>
''',encoding='utf-8')

receiver=root/'app/src/main/java/com/espritlibre/app/NotificationReceiver.java'
r=receiver.read_text(encoding='utf-8')
old='b.setSmallIcon(android.R.drawable.ic_dialog_info)'
if old not in r:
    raise SystemExit('old notification info icon not found')
r=r.replace(old,'b.setSmallIcon(R.drawable.ic_notification_leaf)',1)
receiver.write_text(r,encoding='utf-8')

# 6) Sanity checks before writing.
if 'Moment de la journée' in html or 'Horaire personnalisé' in html:
    raise SystemExit('obsolete day-part UI still present')
if '<div class="modal show" id="betaNdaModal"' in html:
    raise SystemExit('beta modal still initially visible')
if 'setTimeout(startFirstOpenSequence, 50)' in html:
    raise SystemExit('obsolete beta flash timer still present')
if html.count('id="v88-backup-restore"')!=1:
    raise SystemExit('V8.8 backup controller missing or duplicated')
if 'id="v86-native-theme-controller"' not in html or 'id="v87-fluid-glance-script"' not in html:
    raise SystemExit('validated V8.6/V8.7 baseline unexpectedly missing')

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.8"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,88))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.8 weekly-test stabilization applied')
