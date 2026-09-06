from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
mainp=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main=mainp.read_text(encoding='utf-8')

# V8.10 compilation hardening: notification status bridge introduced references
# to these Android notification classes. Keep this as a tiny post-patch so the
# consolidated V8.10 feature patch stays untouched.
if 'import android.app.NotificationManager;' not in main:
    anchor='import android.Manifest;'
    if anchor not in main:
        raise SystemExit('MainActivity import anchor not found')
    main=main.replace(anchor, anchor+'\nimport android.app.NotificationManager;\nimport android.app.NotificationChannel;', 1)

if 'import android.app.NotificationManager;' not in main or 'import android.app.NotificationChannel;' not in main:
    raise SystemExit('V8.10 notification imports missing after compile fix')

mainp.write_text(main,encoding='utf-8')
print('V8.10 notification compile imports fixed')
