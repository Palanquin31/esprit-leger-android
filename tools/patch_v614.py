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

# Final audit marker appended after all historical fragments.
audit='''\n<style id="v614-final-nav-lock">\n.nav{bottom:68px !important;}\n.fab{bottom:162px !important;}\n.floating-add,.quick-add,.floating-plus{bottom:162px !important;}\n</style>\n'''
if 'id="v614-final-nav-lock"' not in html:
    html += audit
htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "1.0-beta6.14"',b)
bp.write_text(b,encoding='utf-8')
print('V6.14 stabilization patch applied')
