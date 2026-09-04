from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# Add Automatic option to the existing appearance selector without changing the validated V7.2 layout.
old_select='<label>Ambiance de l’application</label><select id="themeSelect" onchange="theme=this.value;render()"><option value="light">☀️ Mode Lumière</option><option value="dark">🌙 Mode Crépuscule</option></select>'
new_select='<label>Ambiance de l’application</label><select id="themeSelect" onchange="theme=this.value;render()"><option value="light">☀️ Mode Lumière</option><option value="dark">🌙 Mode Crépuscule</option><option value="auto">🌓 Automatique</option></select>'
if old_select not in html:
    raise SystemExit('theme selector not found')
html=html.replace(old_select,new_select,1)

# In Automatic mode, resolve the visual theme from Android/WebView prefers-color-scheme.
old_theme=''' document.body.classList.toggle("light", theme==="light");\n document.body.classList.toggle("crepuscule", theme==="dark");'''
new_theme=''' const resolvedThemeV8=(theme==="auto" ? (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : theme);\n document.body.classList.toggle("light", resolvedThemeV8==="light");\n document.body.classList.toggle("crepuscule", resolvedThemeV8==="dark");'''
if old_theme not in html:
    raise SystemExit('theme render block not found')
html=html.replace(old_theme,new_theme,1)

# React immediately when Android changes between light and dark while Automatic is selected.
auto_js='''\n<script id="v80-auto-theme">\n(function(){\n  const mq=window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;\n  function refreshAutomaticThemeV8(){\n    if(typeof theme!=='undefined' && theme==='auto' && typeof render==='function') render();\n  }\n  if(mq){\n    if(typeof mq.addEventListener==='function') mq.addEventListener('change',refreshAutomaticThemeV8);\n    else if(typeof mq.addListener==='function') mq.addListener(refreshAutomaticThemeV8);\n  }\n  window.applyAutomaticThemeV8=refreshAutomaticThemeV8;\n})();\n</script>\n'''
if 'id="v80-auto-theme"' not in html:
    html += auto_js

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\\s+["\\\'].*?["\\\']','versionName "8.0"',b)
m=re.search(r'versionCode\\s+(\\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,80))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.0 automatic appearance mode applied')
