from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

v613=r'''
<style id="v613-nav-position-style">
/* V6.13: keep V6.11/V6.12 stability and Premium logic; only raise bottom controls further. */
.nav{bottom:68px!important;}
.fab{bottom:162px!important;}
.floating-add,.quick-add,.floating-plus{bottom:162px!important;}
body{padding-bottom:132px!important;}
</style>
'''
html=html.replace('</body>',v613+'\n</body>',1)
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.13"',b)
bp.write_text(b,encoding='utf-8')
print('V6.13 patch applied')
