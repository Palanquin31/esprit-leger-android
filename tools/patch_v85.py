from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.5 — clean stabilization.
# Goal: restore the untouched V6/V7 Light appearance, keep the validated V8 Twilight,
# consolidate automatic theme switching, and return modal validation buttons to normal flow.

# 1) Remove the two experimental Light-mode style layers introduced in V8.3/V8.4.
# The original V6/V7 Light CSS is still present unchanged in the base stylesheet.
for sid in ('v83-corrective-style','v84-light-and-modal-fix'):
    html,n=re.subn(r'\n?<style id="'+re.escape(sid)+r'">.*?</style>\n?', '\n', html, count=1, flags=re.S)
    if n!=1:
        raise SystemExit(f'{sid} style block not found')

# 2) Remove the first automatic-theme listener from V8.0. V8.2 already owns the single
# matchMedia listener and updates the UI immediately when Automatic is selected.
html,n=re.subn(r'\n?<script id="v80-auto-theme">.*?</script>\n?', '\n', html, count=1, flags=re.S)
if n!=1:
    raise SystemExit('v80 auto-theme script not found')

# 3) Original render() must no longer manipulate theme classes itself.
# V8.2's applyThemeV82 is the sole class controller and is called after every render.
old_theme_block=''' const resolvedThemeV8=(theme==="auto" ? (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : theme);\n document.body.classList.toggle("light", resolvedThemeV8==="light");\n document.body.classList.toggle("crepuscule", resolvedThemeV8==="dark");'''
if old_theme_block not in html:
    raise SystemExit('legacy render theme block not found')
html=html.replace(old_theme_block,'',1)

# 4) V8.3 wrapped applyThemeV82 a second time. Remove that wrapper so there is one controller.
html,n=re.subn(
    r'\n\s*/\* Re-apply the explicit palette after startup/render so Light is always truly light\. \*/\s*'
    r'const oldApplyV83=window\.applyThemeV82;\s*'
    r'if\(typeof oldApplyV83===\'function\'\)\{\s*'
    r'window\.applyThemeV82=function\(\)\{.*?\};\s*\}\s*'
    r'setTimeout\(\(\)=>\{if\(typeof window\.applyThemeV82===\'function\'\)window\.applyThemeV82\(\);\},20\);',
    '', html, count=1, flags=re.S)
if n!=1:
    raise SystemExit('V8.3 theme wrapper not found')

# 5) Re-add only the non-Light structural rules that V8.3 supplied:
# stronger Twilight navigation, global week settings, and safe modal height.
# Validation buttons are explicitly static: visible at the end of the scroll, never floating.
css=r'''
<style id="v85-clean-stable-style">
/* Validated Twilight navigation: slightly more visible without changing the palette. */
body.crepuscule .nav{
  background:#37303f !important;
  border:1px solid rgba(255,255,255,.13) !important;
  box-shadow:0 10px 28px rgba(0,0,0,.30),0 0 0 1px rgba(255,255,255,.025) inset !important;
}
body.crepuscule .nav button{color:#cfc6d6 !important;}
body.crepuscule .nav button.active{
  color:#fff !important;
  box-shadow:0 5px 14px rgba(129,114,170,.24) !important;
}

/* One person and one activity type for the whole typical week. */
.week-global-settings-v83{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
  margin:10px 0 14px;
  padding:12px;
  border:1px solid #ece4f2;
  border-radius:18px;
  background:rgba(255,255,255,.72);
}
.week-global-settings-v83 .week-global-preview{
  grid-column:1/-1;
  display:flex;
  gap:14px;
  align-items:center;
  font-size:12px;
  color:var(--muted);
  font-weight:850;
}
.week-global-settings-v83 .preview-item{display:flex;align-items:center;gap:6px;}
body.crepuscule .week-global-settings-v83{
  background:#2a2530 !important;
  border-color:rgba(255,255,255,.09) !important;
}
body.light .week-global-settings-v83{
  background:#fff !important;
  border-color:#ece4f2 !important;
}
@media(max-width:370px){
  .week-global-settings-v83{grid-template-columns:1fr;}
  .week-global-settings-v83 .week-global-preview{grid-column:1;}
}

/* Keep the modal height validated in V8.4 but return action buttons to document flow. */
#eventModal,#weekModal{
  padding-bottom:146px !important;
  align-items:flex-end !important;
}
#eventModal .sheet,#weekModal .sheet{
  max-height:calc(100dvh - 178px) !important;
  overflow-y:auto !important;
  overscroll-behavior:contain !important;
  padding-bottom:24px !important;
}
#eventModal .event-actions-v81{
  position:static !important;
  bottom:auto !important;
  z-index:auto !important;
  margin-top:14px !important;
  padding:10px 0 0 !important;
  background:transparent !important;
  box-shadow:none !important;
}
#weekModal .modal-validate{
  position:static !important;
  bottom:auto !important;
  z-index:auto !important;
  margin-top:14px !important;
  box-shadow:none !important;
}
</style>
'''
if 'id="v85-clean-stable-style"' not in html:
    html += css

# 6) Sanity checks before writing the asset.
if 'id="v83-corrective-style"' in html or 'id="v84-light-and-modal-fix"' in html:
    raise SystemExit('obsolete Light style layer still present')
if 'id="v80-auto-theme"' in html:
    raise SystemExit('duplicate V8.0 auto-theme listener still present')
if html.count('window.applyThemeV82=function') != 1:
    raise SystemExit(f'expected one applyThemeV82 controller, found {html.count("window.applyThemeV82=function")}')
if html.count("matchMedia('(prefers-color-scheme: dark)')") != 1:
    raise SystemExit('automatic theme listener/controller is not unique')

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.5"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,85))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.5 clean theme stabilization and modal-flow fix applied')
