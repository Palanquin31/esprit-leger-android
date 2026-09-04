from pathlib import Path
from PIL import Image
import sys, re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Planning day view: true 24-hour display, 00:00 -> 23:00.
html=re.sub(
    r'function renderDay\(\)\{let html="";for\(let h=6;h<=24;h\+\+\)\{let hs=String\(h\)\.padStart\(2,"0"\)\+":00";',
    'function renderDay(){let html="";for(let h=0;h<24;h++){let hs=String(h).padStart(2,"0")+":00";',
    html,
    count=1
)

# 2) Consent modal: make sure its validation continues the first-run wizard.
cs=html.find('id="consentModal"')
if cs!=-1:
    ce=html.find('</div>\n</div>',cs)
    if ce==-1: ce=html.find('</div></div>',cs)
    if ce!=-1:
        block=html[cs:ce+12]
        block=block.replace('<input type="checkbox" checked> Localisation météo','<input type="checkbox" id="consentLocation" checked> Localisation météo')
        block=block.replace('<input type="checkbox"> Données santé','<input type="checkbox" id="consentHealth"> Données santé')
        block=block.replace('<input type="checkbox" checked> Notifications','<input type="checkbox" id="consentNotif" checked> Notifications')
        block=re.sub(r'onclick="(?:closeModals\(\)|acceptConsentStep\(\))"', 'onclick="acceptConsentStep()"', block, count=1)
        html=html[:cs]+block+html[ce+12:]

# 3) Live weather: ask native Android bridge for the locality and persist it with weather.
needle='''    const lat=pos.coords.latitude;\n    const lon=pos.coords.longitude;'''
replacement='''    const lat=pos.coords.latitude;\n    const lon=pos.coords.longitude;\n    let resolvedCity="";\n    try{\n      if(window.AndroidBridge && typeof AndroidBridge.getCity==="function") resolvedCity=String(AndroidBridge.getCity(lat,lon)||"");\n    }catch(_e){}'''
if needle in html:
    html=html.replace(needle,replacement,1)

needle2='''        longitude:lon,\n        temperature:data.current?.temperature_2m ?? 24,'''
replacement2='''        longitude:lon,\n        city:resolvedCity,\n        temperature:data.current?.temperature_2m ?? 24,'''
if needle2 in html:
    html=html.replace(needle2,replacement2,1)

# Always show the resolved city in the weather tile subtitle.
html=html.replace(
    'if(wd)wd.textContent=liveWeather ? (liveWeather.rain ? "Pluie possible" : "Météo locale") : "Météo locale";',
    'if(wd)wd.textContent=liveWeather ? (liveWeather.city || "Météo locale") : "Météo locale";',
    1
)

# 4) Family member editor: replace JS prompt() with an in-app modal.
family_modal='''\n<div class="modal" id="familyMemberModal"><div class="sheet">\n  <button class="close" onclick="document.getElementById('familyMemberModal').classList.remove('show')">Fermer</button>\n  <h2>Ajouter un membre</h2>\n  <p class="note">Ajoute un prénom et choisis sa couleur dans le planning.</p>\n  <label>Prénom</label><input id="familyMemberName" placeholder="Ex : Dorian">\n  <label>Couleur</label><div class="palette" id="familyMemberPalette"></div>\n  <button class="primary modal-validate" onclick="saveFamilyMemberV62()">Ajouter</button>\n</div></div>\n'''
if 'id="familyMemberModal"' not in html:
    html += family_modal

v62_script=r'''\n<script id="v62-behaviour-fixes">\n/* V6.2 first-run + family member fixes */\nlet familyMemberColorV62 = "#8ED6FF";\nfunction renderFamilyMemberPaletteV62(){\n  const el=document.getElementById("familyMemberPalette"); if(!el)return;\n  el.innerHTML=palette.map(c=>`<button class="palette-btn" style="background:${c};${familyMemberColorV62===c?'outline:3px solid #2D2738':''}" onclick="familyMemberColorV62='${c}';renderFamilyMemberPaletteV62();return false"></button>`).join("");\n}\nfunction addFamilyMember(){\n  const m=document.getElementById("familyMemberModal");\n  const n=document.getElementById("familyMemberName");\n  if(n)n.value=""; familyMemberColorV62="#8ED6FF"; renderFamilyMemberPaletteV62();\n  if(m)m.classList.add("show"); updateFloatingVisibility();\n}\nfunction saveFamilyMemberV62(){\n  const n=document.getElementById("familyMemberName"); const name=(n?.value||"").trim();\n  if(!name){alert("Ajoute le prénom du membre.");return;}\n  people[name]=familyMemberColorV62;\n  document.getElementById("familyMemberModal")?.classList.remove("show");\n  render();\n}\n\nfunction hideV62FirstRun(){\n  ["betaNdaModal","consentModal","onboardingModal","setupModal","familyIntroModal"].forEach(id=>document.getElementById(id)?.classList.remove("show"));\n}\nfunction showV62FirstRun(id){\n  hideV62FirstRun(); document.getElementById(id)?.classList.add("show"); updateFloatingVisibility();\n}\nfunction acceptBetaAgreement(){\n  const cb=document.getElementById("ndaAccept");\n  if(cb&&!cb.checked){alert("Veuillez accepter les conditions pour continuer.");return;}\n  localStorage.setItem("esprit_leger_beta_agreement",JSON.stringify({agreement:"Conditions bêta v1.0",acceptedAt:new Date().toISOString(),appVersion:"V6.2 DEV"}));\n  showV62FirstRun("consentModal");\n}\nfunction acceptConsentStep(){\n  localStorage.setItem("esprit_consents",JSON.stringify({location:document.getElementById("consentLocation")?.checked??true,health:document.getElementById("consentHealth")?.checked??false,devices:false,notifications:document.getElementById("consentNotif")?.checked??true,ai:false}));\n  showV62FirstRun("onboardingModal");\n}\nfunction finishOnboarding(){\n  onboardingSeen=true; showV62FirstRun("setupModal");\n}\nfunction completeSetup(){\n  const name=(document.getElementById("setupName")?.value||"").trim();\n  if(!name){alert("Ajoute ton prénom pour commencer.");return;}\n  Object.keys(people).forEach(k=>delete people[k]); people[name]=setupColor||"#B99BFF"; onboardingSeen=true;\n  showV62FirstRun("familyIntroModal"); render();\n}\nconst finishFamilyIntroBeforeV62=finishFamilyIntro;\nfinishFamilyIntro=function(){\n  finishFamilyIntroBeforeV62(); localStorage.setItem("esprit_leger_first_run_v62_complete","1"); hideV62FirstRun(); render();\n};\nfunction startV62FirstRun(){\n  if(localStorage.getItem("esprit_leger_first_run_v62_complete")==="1"){hideV62FirstRun();return;}\n  // V6.2 uses its own test flag so this sequence can be verified once even over a V6.1 installation.\n  showV62FirstRun("betaNdaModal");\n}\nsetTimeout(startV62FirstRun,350);\n</script>\n'''
html += v62_script
htmlp.write_text(html,encoding='utf-8')

# 5) Native Android reverse geocoding bridge for city name.
mainp=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main=mainp.read_text(encoding='utf-8')
# Add JS bridge after web settings are configured, before loading the page.
anchor='s.setCacheMode(WebSettings.LOAD_DEFAULT);'
if anchor in main and 'addJavascriptInterface(new CityBridge' not in main:
    main=main.replace(anchor,anchor+'webView.addJavascriptInterface(new CityBridge(),"AndroidBridge");',1)
# Insert inner bridge class before tryLoadWeather.
marker='private void tryLoadWeather()'
if marker in main and 'class CityBridge' not in main:
    bridge='''class CityBridge{\n @android.webkit.JavascriptInterface public String getCity(double lat,double lon){\n  try{\n   android.location.Geocoder g=new android.location.Geocoder(MainActivity.this,java.util.Locale.getDefault());\n   java.util.List<android.location.Address> a=g.getFromLocation(lat,lon,1);\n   if(a!=null&&!a.isEmpty()){android.location.Address x=a.get(0);String c=x.getLocality();if(c==null||c.trim().isEmpty())c=x.getSubAdminArea();if(c==null||c.trim().isEmpty())c=x.getAdminArea();return c==null?"":c;}\n  }catch(Exception ignored){}\n  return "";\n }\n}\n '''
    main=main.replace(marker,bridge+marker,1)
mainp.write_text(main,encoding='utf-8')

# 6) Launcher icon: zoom the artwork to full bleed and use it as adaptive-icon background.
drawable=root/'app/src/main/res/drawable'
source=Image.open(drawable/'app_icon.png').convert('RGBA')
bbox=source.getbbox() or (0,0,source.width,source.height)
crop=source.crop(bbox)
# Zoom past the transparent/glow perimeter so launchers no longer create a visible white rim.
scale=max(620/crop.width,620/crop.height)
zoom=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
left=max(0,(zoom.width-512)//2); top=max(0,(zoom.height-512)//2)
full=zoom.crop((left,top,left+512,top+512))
# Remove alpha entirely: Xiaomi/other launchers cannot expose a white backing through the corners.
bg=Image.new('RGBA',(512,512),(228,145,203,255)); bg.alpha_composite(full); bg=bg.convert('RGB')
bg.save(drawable/'app_icon_full.png',quality=96)
(drawable/'app_icon_adaptive_bg.xml').write_text('''<layer-list xmlns:android="http://schemas.android.com/apk/res/android"><item><bitmap android:src="@drawable/app_icon_full" android:gravity="fill"/></item></layer-list>\n''',encoding='utf-8')
(drawable/'app_icon_transparent.xml').write_text('''<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#00000000"/></shape>\n''',encoding='utf-8')
for name in ('ic_launcher.xml','ic_launcher_round.xml'):
    p=root/'app/src/main/res/mipmap-anydpi-v26'/name
    p.write_text('''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n <background android:drawable="@drawable/app_icon_adaptive_bg"/>\n <foreground android:drawable="@drawable/app_icon_transparent"/>\n</adaptive-icon>\n''',encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.2"',b)
bp.write_text(b,encoding='utf-8')
print('V6.2 patch applied')
