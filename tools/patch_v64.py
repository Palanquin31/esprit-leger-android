from pathlib import Path
from PIL import Image
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Always open the planner on the real current day.
# Keep the saved date in storage for compatibility, but don't restore it on launch.
html=html.replace('if(d.selectedDate){const dt=new Date(d.selectedDate);if(!isNaN(dt))selectedDate=dt;}','selectedDate=new Date();')
# Final safeguard after all legacy scripts have initialized.
html += '''\n<script id="v64-date-fix">\n(function(){\n  selectedDate=new Date();\n  calendarMonth=new Date(selectedDate.getFullYear(),selectedDate.getMonth(),1);\n  setTimeout(()=>{selectedDate=new Date();calendarMonth=new Date(selectedDate.getFullYear(),selectedDate.getMonth(),1);render();},120);\n})();\n</script>\n'''

# 2) Serenity score: an empty scheduled day is always 100/100.
# Keep the existing score logic once there is at least one planned event.
html += '''\n<script id="v64-score-fix">\nconst computeSerenityScoreBeforeV64=computeSerenityScore;\ncomputeSerenityScore=function(today){\n  const ev=Array.isArray(today)?today:[];\n  if(ev.length===0)return 100;\n  return computeSerenityScoreBeforeV64(ev);\n};\nscore=function(today){\n  const s=computeSerenityScore(today);\n  if(s>=80)return "🌱 Très serein";\n  if(s>=65)return "🌿 Serein";\n  if(s>=50)return "🍃 Équilibré";\n  if(s>=35)return "🍂 Chargé";\n  return "Sous pression";\n};\n</script>\n'''

# 3) Weather icons: use robust BMP weather symbols based on WMO/Open-Meteo codes.
# This avoids the replacement-character issue seen with some emoji fonts/WebViews.
html += '''\n<script id="v64-weather-icons">\nfunction weatherSymbolV64(){\n  if(!liveWeather)return "☁";\n  const c=Number(liveWeather.code||0);\n  if(c===0 || c===1)return "☀";\n  if(c===2)return "⛅";\n  if(c===3 || c===45 || c===48)return "☁";\n  if([51,53,55,56,57,61,63,65,66,67,80,81,82].includes(c))return "☂";\n  if([71,73,75,77,85,86].includes(c))return "❄";\n  if([95,96,99].includes(c))return "⛈";\n  return liveWeather.rain ? "☂" : "☀";\n}\nconst weatherLabelBeforeV64=weatherLabel;\nweatherLabel=function(){\n  if(liveWeather)return `${weatherSymbolV64()} ${Math.round(liveWeather.temperature)}°C`;\n  return "☁ météo";\n};\nconst updateStableHeroBeforeV64=updateStableHero;\nupdateStableHero=function(){\n  updateStableHeroBeforeV64();\n  try{\n    const wi=document.getElementById("weatherIcon");\n    const w=document.getElementById("weather");\n    const wd=document.getElementById("weatherDesc");\n    if(wi)wi.textContent=weatherSymbolV64();\n    if(w)w.textContent=liveWeather ? `${Math.round(liveWeather.temperature)}°C` : "météo";\n    if(wd)wd.textContent=liveWeather ? (liveWeather.city || "Météo locale") : "Météo locale";\n  }catch(_e){}\n};\n</script>\n'''

htmlp.write_text(html,encoding='utf-8')

# 4) Launcher icon: intermediate size between V6.2 (too large) and V6.3 (too small).
drawable=root/'app/src/main/res/drawable'
source=Image.open(drawable/'app_icon.png').convert('RGBA')
# Match the existing app artwork background with a stable pink-purple tone.
bg_rgb=(231,157,210)
canvas=Image.new('RGBA',(512,512),bg_rgb+(255,))
# 480 px is deliberately between the previous 430 px and the V6.2 full-bleed crop.
art=source.resize((480,480),Image.Resampling.LANCZOS)
canvas.alpha_composite(art,((512-480)//2,(512-480)//2))
canvas.convert('RGB').save(drawable/'app_icon_full.png',quality=96)

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.4"',b)
bp.write_text(b,encoding='utf-8')

print('V6.4 patch applied')
