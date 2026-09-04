from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
p=root/'app/build.gradle'
s=p.read_text(encoding='utf-8')
s=s.replace("storePassword 'EspritTester2026!'","storePassword System.getenv('TESTER_STORE_PASS')")
s=s.replace("keyPassword 'EspritTester2026!'","keyPassword System.getenv('TESTER_STORE_PASS')")
p.write_text(s,encoding='utf-8')
print('Runtime signing credentials configured')