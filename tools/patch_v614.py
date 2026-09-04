from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# Fix the real override source: V6.1 CSS is appended later than V6.12/V6.13.
html=html.replace('.nav{bottom:22px !important;}','.nav{bottom:68px !important;}',1)
html=html.replace('.nav{bottom:20px !important}','.nav{bottom:68px !important}',1)
html=html.replace('.phone{padding-top:18px !important;padding-bottom:150px !important;}', '.phone{padding-top:18px !important;padding-bottom:198px !important;}',1)
html=html.replace('.phone{padding-top:16px !important;padding-bottom:148px !important}', '.phone{padding-top:16px !important;padding-bottom:198px !important}',1)

# Repair the V6.2 behaviour script: an old patch inserted literal \\n sequences
# inside the <script>, which makes that whole script invalid JavaScript.
start=html.find('<script id="v62-behaviour-fixes">')
if start!=-1:
    end=html.find('</script>',start)
    if end!=-1:
        block=html[start:end+9].replace('\\n','\n')
        html=html[:start]+block+html[end+9:]

# Restore native city bridge lost when MainActivity was rewritten in V6.10.
mainp=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main=mainp.read_text(encoding='utf-8')
anchor='webView.addJavascriptInterface(new NotificationBridge(this),"AndroidNotifications");'
if '"AndroidBridge"' not in main and anchor in main:
    main=main.replace(anchor,anchor+'\n        webView.addJavascriptInterface(new CityBridge(),"AndroidBridge");',1)
marker='    private void tryLoadWeather()'
if 'class CityBridge' not in main and marker in main:
    bridge='''    class CityBridge {\n        @JavascriptInterface public String getCity(double lat,double lon){\n            try{\n                android.location.Geocoder g=new android.location.Geocoder(MainActivity.this,java.util.Locale.getDefault());\n                java.util.List<android.location.Address> a=g.getFromLocation(lat,lon,1);\n                if(a!=null&&!a.isEmpty()){\n                    android.location.Address x=a.get(0);\n                    String c=x.getLocality();\n                    if(c==null||c.trim().isEmpty())c=x.getSubAdminArea();\n                    if(c==null||c.trim().isEmpty())c=x.getAdminArea();\n                    return c==null?"":c;\n                }\n            }catch(Exception ignored){}\n            return "";\n        }\n    }\n\n'''
    main=main.replace(marker,bridge+marker,1)
mainp.write_text(main,encoding='utf-8')

# Premium IA: distinguish clock time (18h) from a duration (pendant 1h).
ai_fix='''\n<script id="v614-ai-duration-fix">\n(function(){\n  window.extractDurationV65=function(text,def=30){\n    const l=(text||'').toLowerCase();\n    let m=l.match(/(?:pendant|durant|pour|durée(?:\\s+de)?|duree(?:\\s+de)?)\\s*(\\d+)\\s*h\\s*(\\d{1,2})?/);\n    if(m)return Number(m[1])*60+(m[2]?Number(m[2]):0);\n    m=l.match(/(?:pendant|durant|pour|durée(?:\\s+de)?|duree(?:\\s+de)?)\\s*(\\d{1,3})\\s*(?:min|minutes)/);\n    if(m)return Number(m[1]);\n    const hm=[...l.matchAll(/(\\d+)\\s*h\\s*(\\d{1,2})?/g)];\n    if(hm.length>1){const x=hm[hm.length-1];return Number(x[1])*60+(x[2]?Number(x[2]):0);}\n    const mm=[...l.matchAll(/(\\d{1,3})\\s*(?:min|minutes)/g)];\n    if(mm.length)return Number(mm[mm.length-1][1]);\n    return def;\n  };\n})();\n</script>\n'''
if 'id="v614-ai-duration-fix"' not in html:
    html += ai_fix

# Final override appended after every historical style block.
audit='''\n<style id="v614-final-nav-lock">\n.nav{bottom:68px !important;}\n.fab{bottom:162px !important;}\n.floating-add,.quick-add,.floating-plus{bottom:162px !important;}\n</style>\n'''
if 'id="v614-final-nav-lock"' not in html:
    html += audit
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.14"',b)
bp.write_text(b,encoding='utf-8')
print('V6.14 stabilization patch applied')
