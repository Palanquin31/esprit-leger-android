from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.4 — restore the original luminous visual, keep Twilight untouched,
# collapse all week days by default, and lift modal validation buttons above bottom nav.

# 1) All week-template day accordions start collapsed, including Monday.
html=html.replace("${di===0?'open':''}", "")

# 2) Re-assert the original light-mode look that already exists in the base HTML.
# Appended last so V8.3's experimental light palette can no longer override it.
css=r'''
<style id="v84-light-and-modal-fix">
/* Original luminous appearance restored. */
body.light{
  background:#FFFFFF !important;
  color:#2D2738 !important;
  --ink:#2D2738 !important;
  --muted:#7A7284 !important;
  --card:rgba(255,255,255,.92) !important;
}
body.light .phone{
  background:#FFFFFF !important;
}
body.light .modal{
  background:rgba(255,255,255,.72) !important;
}
body.light .card,
body.light .day-col,
body.light .listitem,
body.light .coloritem,
body.light .slot,
body.light .suggestion,
body.light .sheet,
body.light .plan-card,
body.light .dayform,
body.light .slot-choice,
body.light .color-popup,
body.light input,
body.light select,
body.light textarea,
body.light .quick-add-menu,
body.light .mood-floating,
body.light .week-day-accordion{
  background:#FFFFFF !important;
  color:#2D2738 !important;
  border-color:#ECEAF2 !important;
}
body.light .nav{
  background:#FFFFFF !important;
  color:#2D2738 !important;
  border-color:rgba(180,160,230,.18) !important;
  box-shadow:0 10px 30px rgba(67,47,105,.10) !important;
}
body.light .tabs{
  background:#F6F5FA !important;
  color:#2D2738 !important;
}
body.light .mood,
body.light .smallbtn,
body.light .ghost,
body.light .tab,
body.light .chip,
body.light .day-choice{
  background:#F6F5FA !important;
  color:#2D2738 !important;
}
body.light .advice-card{
  background:#FFFFFF !important;
}
body.light .top-bubble{
  background:linear-gradient(135deg,#EDE7FF,#FFE9F0) !important;
  color:#2D2738 !important;
  border-color:rgba(180,160,230,.20) !important;
  box-shadow:0 18px 45px rgba(80,45,120,.12) !important;
}
body.light .top-main p{color:#6F6878 !important;}
body.light .stat{
  background:rgba(255,255,255,.75) !important;
  color:#2D2738 !important;
  border:1px solid rgba(180,160,230,.25) !important;
}
body.light .brand{opacity:.75 !important;}
body.light p,
body.light .note,
body.light .event-meta,
body.light .details-line,
body.light label,
body.light .week-day-summary{color:#7A7284 !important;}
body.light .soft-calendar{background:#FFFFFF !important;}
body.light .soft-advice{background:linear-gradient(135deg,#FFFFFF,#EDFFF7) !important;}
body.light .primary,
body.light .mood.active,
body.light .tab.active,
body.light .nav button.active{
  background:linear-gradient(135deg,var(--lav),var(--pink)) !important;
  color:white !important;
}
body.light .week-day-head{color:#2D2738 !important;}
body.light .week-global-settings-v83{
  background:#FFFFFF !important;
  border-color:#ECEAF2 !important;
}

/* Keep creation/edit validation areas completely above the validated bottom nav. */
#eventModal,
#weekModal{
  padding-bottom:146px !important;
  align-items:flex-end !important;
}
#eventModal .sheet,
#weekModal .sheet{
  max-height:calc(100dvh - 178px) !important;
  overflow-y:auto !important;
  overscroll-behavior:contain !important;
  padding-bottom:18px !important;
}
#weekModal .modal-validate{
  position:sticky !important;
  bottom:0 !important;
  z-index:25 !important;
  margin-top:14px !important;
  box-shadow:0 -10px 24px rgba(255,255,255,.90) !important;
}
body.crepuscule #weekModal .modal-validate{
  box-shadow:0 -10px 24px rgba(42,37,48,.95) !important;
}
</style>
'''
if 'id="v84-light-and-modal-fix"' not in html:
    html += css

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.4"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,84))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.4 light restoration and modal spacing applied')
