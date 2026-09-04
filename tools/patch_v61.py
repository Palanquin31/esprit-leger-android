from pathlib import Path
from PIL import Image
import sys, re

root=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/data/v6proj/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# 1) Free home: merge Premium teaser + advice into one card.
old='''  <div class="card premium-teaser"><div class="card-title-ribbon ribbon-advice">🍃 Premium</div><p><b>Allège ma semaine</b> est disponible en Premium : l’IA analyse planning, météo, tâches et fatigue pour proposer une semaine plus légère.</p></div>\n  <div class="card" id="aiWeeklyResult" style="display:none"><h3>Suggestions IA</h3><div id="aiWeeklyContent"></div></div>\n  <div class="card advice-card soft-advice"><div class="card-title-ribbon ribbon-advice">✨ Conseil de l’application</div><p id="advice"></p><span class="family-test">✨ ✨ Premium</span></div>'''
new='''  <div class="card" id="aiWeeklyResult" style="display:none"><h3>Suggestions IA</h3><div id="aiWeeklyContent"></div></div>\n  <div class="card advice-card soft-advice unified-advice-card">\n    <div class="card-title-ribbon ribbon-advice">✨ Conseils de l’application</div>\n    <p id="advice"></p>\n    <div class="free-premium-info"><b>🍃 Plus précis en Premium</b><span>En mode gratuit, les conseils restent généraux. En Premium, l’IA affine davantage ses recommandations selon ton planning, la météo, la fatigue et la charge familiale.</span></div>\n  </div>'''
if old not in html:
    raise SystemExit('Home free cards block not found')
html=html.replace(old,new,1)

# 2) Consent screen: give real IDs and make Validate continue the onboarding flow.
html=html.replace('<label><input type="checkbox" checked> Localisation météo</label>', '<label><input type="checkbox" id="consentLocation" checked> Localisation météo</label>',1)
html=html.replace('<label><input type="checkbox"> Données santé</label>', '<label><input type="checkbox" id="consentHealth"> Données santé</label>',1)
html=html.replace('<label><input type="checkbox" checked> Notifications</label>', '<label><input type="checkbox" id="consentNotif" checked> Notifications</label>',1)
html=html.replace('<button class="primary modal-validate" onclick="closeModals()">Valider</button>', '<button class="primary modal-validate" onclick="acceptConsentStep()">Valider et continuer</button>',1)

# 3) Stop render() from fighting the first-launch wizard.
old_render=''' const familyModal=document.getElementById('familyIntroModal');\n if(familyModal)familyModal.classList.toggle('show', !familyIntroSeen);\n const setup=document.getElementById('setupModal');\n if(setup)setup.classList.toggle('show', familyIntroSeen && Object.keys(people).length===0);\n const onboard=document.getElementById('onboardingModal');\n if(onboard)onboard.classList.toggle('show', Object.keys(people).length>0 && !onboardingSeen);'''
new_render=''' const firstRunDone=localStorage.getItem("esprit_leger_first_run_complete")==="1";\n const familyModal=document.getElementById('familyIntroModal');\n const setup=document.getElementById('setupModal');\n const onboard=document.getElementById('onboardingModal');\n if(firstRunDone){\n   if(familyModal)familyModal.classList.toggle('show', !familyIntroSeen);\n   if(setup)setup.classList.toggle('show', familyIntroSeen && Object.keys(people).length===0);\n   if(onboard)onboard.classList.remove('show');\n }'''
if old_render not in html:
    raise SystemExit('render onboarding block not found')
html=html.replace(old_render,new_render,1)

# 4) Complete first launch in strict sequence NDA -> consent -> tutorial -> profile -> family.
# Replace the later locked sequence so it wins over duplicate earlier functions.
start=html.index('/* Séquence d\'ouverture verrouillée */')
end=html.index('</script>', start)
block='''/* Séquence d'ouverture V6.1 : NDA -> autorisations -> tutoriel -> profil -> famille */\nlet onboardingStepLock = "done";\n\nfunction hideOnboardingStack(){\n  ["betaNdaModal","consentModal","onboardingModal","setupModal","familyIntroModal"].forEach(id=>{\n    const el=document.getElementById(id);\n    if(el)el.classList.remove("show");\n  });\n}\nfunction showOnlyOnboarding(id){\n  hideOnboardingStack();\n  const el=document.getElementById(id);\n  if(el)el.classList.add("show");\n  onboardingStepLock = id==="betaNdaModal" ? "nda" : id==="consentModal" ? "consent" : id==="onboardingModal" ? "tutorial" : id==="setupModal" ? "profile" : id==="familyIntroModal" ? "family" : "done";\n}\nfunction acceptBetaAgreement(){\n  const cb=document.getElementById("ndaAccept");\n  if(cb && !cb.checked){ alert("Veuillez accepter les conditions pour continuer."); return; }\n  localStorage.setItem("esprit_leger_beta_agreement", JSON.stringify({agreement:"Conditions bêta v1.0",acceptedAt:new Date().toISOString(),appVersion:"V6.1 DEV"}));\n  showOnlyOnboarding("consentModal");\n}\nfunction acceptConsentStep(){\n  localStorage.setItem("esprit_consents", JSON.stringify({\n    location:document.getElementById("consentLocation")?.checked ?? true,\n    health:document.getElementById("consentHealth")?.checked ?? false,\n    devices:false, notifications:document.getElementById("consentNotif")?.checked ?? true, ai:false\n  }));\n  showOnlyOnboarding("onboardingModal");\n}\nfunction finishOnboarding(){\n  onboardingSeen=true;\n  showOnlyOnboarding("setupModal");\n}\nfunction completeSetup(){\n  const name=document.getElementById("setupName")?.value?.trim();\n  if(!name){ alert("Ajoute ton prénom pour commencer."); return; }\n  Object.keys(people).forEach(k=>delete people[k]);\n  people[name]=setupColor || "#B99BFF";\n  onboardingSeen=true;\n  showOnlyOnboarding("familyIntroModal");\n}\nconst _finishFamilyIntroV61 = finishFamilyIntro;\nfinishFamilyIntro=function(){\n  _finishFamilyIntroV61();\n  localStorage.setItem("esprit_leger_first_run_complete","1");\n  onboardingStepLock="done";\n  hideOnboardingStack();\n  render();\n};\nfunction enforceOnboardingSequence(){\n  if(onboardingStepLock==="nda")showOnlyOnboarding("betaNdaModal");\n  else if(onboardingStepLock==="consent")showOnlyOnboarding("consentModal");\n  else if(onboardingStepLock==="tutorial")showOnlyOnboarding("onboardingModal");\n  else if(onboardingStepLock==="profile")showOnlyOnboarding("setupModal");\n  else if(onboardingStepLock==="family")showOnlyOnboarding("familyIntroModal");\n}\nfunction startV61FirstRun(){\n  if(localStorage.getItem("esprit_leger_first_run_complete")==="1"){\n    onboardingStepLock="done"; hideOnboardingStack(); return;\n  }\n  onboardingStepLock="nda"; showOnlyOnboarding("betaNdaModal");\n}\nsetTimeout(startV61FirstRun,120);\n'''
html=html[:start]+block+html[end:]

# 5) Final CSS overrides: free card + real safe spacing inside the WebView as a second line of defence.
css='''\n<style id="v61-final-fixes">\n/* V6.1 final UI fixes */\n.premium-teaser{display:none !important;}\n.family-test{display:none !important;}\n.free-premium-info{\n  display:flex;flex-direction:column;gap:5px;margin-top:14px;padding:12px 14px;border-radius:18px;\n  background:linear-gradient(135deg,#F5EEFF,#FFF1F6);border:1px solid #E7DBFA;color:#5C4A72;font-size:13px;line-height:1.35;\n}\n.free-premium-info b{font-size:13px;color:#6A4C93;}\n.free-premium-info span{color:#776C82;}\nbody.premium-active .free-premium-info{display:none !important;}\n.unified-advice-card{overflow:hidden;}\n/* Fixed navigation must never sit on Android system controls. Native insets resize the WebView; this adds breathing room. */\n.phone{padding-top:18px !important;padding-bottom:150px !important;}\n.nav{bottom:22px !important;}\n.stable-hero{margin-top:0 !important;}\n/* Visual logo in the hero: centered in its grid cell */\n.hello-logo-wrap{margin-left:0 !important;justify-self:center !important;}\n@media(max-width:430px){.phone{padding-top:16px !important;padding-bottom:148px !important}.nav{bottom:20px !important}}\n</style>\n'''
html += css
htmlp.write_text(html,encoding='utf-8')

# 6) Native safe-area handling: replace compact V6 Activity with a safe-area root container.
mainp=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main=mainp.read_text(encoding='utf-8')
# V6 generated Java is minified on GitHub, so patch the imports and onCreate prefix with regex.
main=main.replace('import android.os.Bundle;import android.webkit', 'import android.os.Bundle;import android.view.View;import android.widget.FrameLayout;import android.graphics.Color;import android.webkit')
pattern=r'@SuppressLint\("SetJavaScriptEnabled"\) @Override public void onCreate\(Bundle b\)\{super\.onCreate\(b\);webView=new WebView\(this\);setContentView\(webView\);\s*webView\.setOnApplyWindowInsetsListener\(\(v,i\)->\{v\.setPadding\(0,i\.getSystemWindowInsetTop\(\),0,i\.getSystemWindowInsetBottom\(\)\);return i;\}\);webView\.requestApplyInsets\(\);'
replacement='@SuppressLint("SetJavaScriptEnabled") @Override public void onCreate(Bundle b){super.onCreate(b);\n  getWindow().setStatusBarColor(Color.WHITE);getWindow().setNavigationBarColor(Color.WHITE);getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);\n  FrameLayout root=new FrameLayout(this);webView=new WebView(this);root.addView(webView,new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT,FrameLayout.LayoutParams.MATCH_PARENT));setContentView(root);\n  root.setOnApplyWindowInsetsListener((v,i)->{int top=i.getSystemWindowInsetTop(),bottom=i.getSystemWindowInsetBottom(),left=i.getSystemWindowInsetLeft(),right=i.getSystemWindowInsetRight();FrameLayout.LayoutParams lp=(FrameLayout.LayoutParams)webView.getLayoutParams();lp.setMargins(left,top,right,bottom);webView.setLayoutParams(lp);return i;});root.requestApplyInsets();'
main2,n=re.subn(pattern,replacement,main,count=1)
if n!=1:
    raise SystemExit('MainActivity compact inset block not found')
mainp.write_text(main2,encoding='utf-8')

# 7) Adaptive + centered launcher icon.
drawable=root/'app/src/main/res/drawable'
source=Image.open(drawable/'app_icon.png').convert('RGBA')
canvas=Image.new('RGBA',(512,512),(0,0,0,0))
# Slightly smaller than full canvas so Android masks have balanced safe margins.
img=source.resize((440,440),Image.Resampling.LANCZOS)
canvas.alpha_composite(img,((512-440)//2,(512-440)//2))
canvas.save(drawable/'app_icon_foreground.png')
values=root/'app/src/main/res/values'; values.mkdir(parents=True,exist_ok=True)
colors=values/'colors.xml'
colors.write_text('<resources><color name="icon_background">#F7D6E7</color></resources>\n',encoding='utf-8')
mipmap=root/'app/src/main/res/mipmap-anydpi-v26'; mipmap.mkdir(parents=True,exist_ok=True)
icon_xml='''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/icon_background"/>\n    <foreground android:drawable="@drawable/app_icon_foreground"/>\n</adaptive-icon>\n'''
(mipmap/'ic_launcher.xml').write_text(icon_xml,encoding='utf-8')
(mipmap/'ic_launcher_round.xml').write_text(icon_xml,encoding='utf-8')
manifest=root/'app/src/main/AndroidManifest.xml'
mt=manifest.read_text(encoding='utf-8')
mt=mt.replace('android:icon="@drawable/app_icon"','android:icon="@mipmap/ic_launcher"')
mt=mt.replace('android:roundIcon="@drawable/app_icon"','android:roundIcon="@mipmap/ic_launcher_round"')
manifest.write_text(mt,encoding='utf-8')

# Version name
bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']', 'versionName "1.0-beta6.1"', b)
bp.write_text(b,encoding='utf-8')

print('V6.1 patch applied')
