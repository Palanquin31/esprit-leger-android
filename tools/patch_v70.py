from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V7.0 = stable tester baseline. Do not alter validated swipe/nav/premium logic.
# Raise the actual global + button (class is .fab-global, not .fab) and its menu.
final_css='''\n<style id="v70-stable-baseline">\n/* Validated bottom navigation stays at 68px. */\n.nav{bottom:68px !important;}\n/* Actual floating add button used by the UI. */\n.fab-global{bottom:174px !important;}\n/* Open menu must sit immediately above the raised + button. */\n.quick-add-menu{bottom:242px !important;}\n/* Mood floating control uses the same safe vertical zone. */\n.mood-floating{bottom:174px !important;}\n/* Keep enough scroll space behind fixed controls. */\n.phone{padding-bottom:210px !important;}\n</style>\n'''
if 'id="v70-stable-baseline"' not in html:
    html += final_css

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "7.0"',b)
# Increment dev version code when present so Android can distinguish the baseline.
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,70))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V7.0 stable baseline patch applied')
