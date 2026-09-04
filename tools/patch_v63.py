from pathlib import Path
from PIL import Image, ImageStat
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Re-enable the current local assistant. It does not send data to an external AI service,
# so the cloud-AI consent must not block it.
html=html.replace('''  if(!aiConsentAllowed()){ alert("L’assistant IA n’est pas activé dans les consentements."); return; }\n''','',1)

# Keep consent storage coherent for this local development assistant.
html=html.replace('ai:false','ai:true')

# 2) Launcher icon: keep the artwork comfortably inside the adaptive-icon safe zone,
# while filling the surrounding area with a matching pink/purple background (no white rim).
drawable=root/'app/src/main/res/drawable'
source=Image.open(drawable/'app_icon.png').convert('RGBA')

# Estimate a background tone from visible corner pixels, with a safe fallback.
corner_pts=[(8,8),(source.width-9,8),(8,source.height-9),(source.width-9,source.height-9)]
vals=[]
for x,y in corner_pts:
    r,g,b,a=source.getpixel((x,y))
    if a>20: vals.append((r,g,b))
if vals:
    bg_rgb=tuple(sum(v[i] for v in vals)//len(vals) for i in range(3))
else:
    bg_rgb=(231,157,210)

canvas=Image.new('RGBA',(512,512),bg_rgb+(255,))
# 430 px gives the full logo breathing room on Xiaomi/Android adaptive masks.
art=source.resize((430,430),Image.Resampling.LANCZOS)
canvas.alpha_composite(art,((512-430)//2,(512-430)//2))
canvas.convert('RGB').save(drawable/'app_icon_full.png',quality=96)

# Keep the full artwork in the adaptive background and a transparent foreground.
(drawable/'app_icon_adaptive_bg.xml').write_text('''<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n  <item><bitmap android:src="@drawable/app_icon_full" android:gravity="fill"/></item>\n</layer-list>\n''',encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.3"',b)
bp.write_text(b,encoding='utf-8')

htmlp.write_text(html,encoding='utf-8')
print('V6.3 patch applied')
