from pathlib import Path
import sys,re

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

# V8.6 — native theme stabilization.
# Android/WebView must never algorithmically recolor our page: the app owns both palettes.
# Automatic mode reads the phone's real UI mode through a native bridge.

# 1) Remove V8.2's matchMedia-based theme controller while preserving the rest of its
# week-template and Premium fluidity features.
pattern=(r'(\/\* --- Deterministic theme controller --- \*\/).*?'
         r'(\/\* --- Compact typical-week editor --- \*\/)')
html,n=re.subn(pattern, r'\2', html, count=1, flags=re.S)
if n!=1:
    raise SystemExit('V8.2 theme controller block not found')

# 2) Theme selector now calls the single V8.6 controller.
html=html.replace('onchange="setAppThemeV82(this.value)"','onchange="setAppThemeV86(this.value)"',1)

# 3) One explicit JS controller. AndroidTheme is authoritative in the APK; matchMedia is
# only a browser fallback for development preview.
js=r'''
<script id="v86-native-theme-controller">
(function(){
  function systemModeV86(){
    try{
      if(window.AndroidTheme && typeof AndroidTheme.getSystemMode==='function'){
        const m=String(AndroidTheme.getSystemMode()||'').toLowerCase();
        if(m==='dark'||m==='light')return m;
      }
    }catch(e){}
    try{return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}
    catch(e){return 'light';}
  }
  function resolvedModeV86(){
    if(theme==='auto')return systemModeV86();
    return theme==='dark'?'dark':'light';
  }
  window.applyThemeV86=function(){
    const resolved=resolvedModeV86();
    document.body.classList.remove('light','crepuscule');
    document.body.classList.add(resolved==='dark'?'crepuscule':'light');
    document.documentElement.setAttribute('data-app-theme',resolved);
    const sel=document.getElementById('themeSelect');
    if(sel && ['light','dark','auto'].includes(theme))sel.value=theme;
    try{
      if(window.AndroidTheme && typeof AndroidTheme.applyResolvedMode==='function'){
        AndroidTheme.applyResolvedMode(resolved);
      }
    }catch(e){}
    return resolved;
  };
  window.setAppThemeV86=function(value){
    theme=['light','dark','auto'].includes(value)?value:'light';
    window.applyThemeV86();
    if(typeof saveState==='function')saveState();
  };
  // Backward-compatible aliases for any older call sites, but only one implementation.
  window.applyThemeV82=window.applyThemeV86;
  window.setAppThemeV82=window.setAppThemeV86;

  const previousRenderV86=window.render;
  if(typeof previousRenderV86==='function' && !previousRenderV86.__v86ThemeWrapped){
    const wrapped=function(){
      const out=previousRenderV86.apply(this,arguments);
      window.applyThemeV86();
      return out;
    };
    wrapped.__v86ThemeWrapped=true;
    window.render=wrapped;
  }

  // Called natively when Android's system day/night mode changes while the app is open.
  window.applySystemThemeV86=function(){
    if(theme==='auto')window.applyThemeV86();
  };
  document.addEventListener('visibilitychange',()=>{
    if(!document.hidden && theme==='auto')window.applyThemeV86();
  });
  window.addEventListener('focus',()=>{
    if(theme==='auto')window.applyThemeV86();
  });
  setTimeout(window.applyThemeV86,0);
})();
</script>
'''
if 'id="v86-native-theme-controller"' not in html:
    html += js

# 4) Native WebView: turn Android algorithmic darkening OFF permanently.
# We already have a hand-designed Twilight palette; Android must not recolor Light mode.
mainp=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
main=mainp.read_text(encoding='utf-8')

if 'import android.content.res.Configuration;' not in main:
    main=main.replace('import android.content.pm.PackageManager;','import android.content.pm.PackageManager;\nimport android.content.res.Configuration;',1)

settings_anchor='s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);s.setCacheMode(WebSettings.LOAD_DEFAULT);'
settings_new=settings_anchor+'''\n        // V8.6: never let WebView auto-darken the carefully designed Light palette.\n        if(Build.VERSION.SDK_INT>=33){\n            s.setAlgorithmicDarkeningAllowed(false);\n        }else if(Build.VERSION.SDK_INT>=29){\n            s.setForceDark(WebSettings.FORCE_DARK_OFF);\n        }'''
if 'setAlgorithmicDarkeningAllowed(false)' not in main:
    if settings_anchor not in main: raise SystemExit('WebSettings anchor not found')
    main=main.replace(settings_anchor,settings_new,1)

bridge_anchor='webView.addJavascriptInterface(new NotificationBridge(this),"AndroidNotifications");'
if '"AndroidTheme"' not in main:
    if bridge_anchor not in main: raise SystemExit('notification bridge anchor not found')
    main=main.replace(bridge_anchor,bridge_anchor+'\n        webView.addJavascriptInterface(new ThemeBridge(),"AndroidTheme");',1)

# Native bar colors follow the resolved app palette as well, so Light looks fully light.
back_anchor='    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}\n\n'
bridge_code=r'''    private void applyResolvedSystemBars(boolean dark){
        int bg=dark?Color.rgb(18,16,24):Color.rgb(250,250,250);
        getWindow().setStatusBarColor(bg);
        getWindow().setNavigationBarColor(bg);
        if(Build.VERSION.SDK_INT>=23){
            int flags=0;
            if(!dark)flags|=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if(Build.VERSION.SDK_INT>=26 && !dark)flags|=View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            getWindow().getDecorView().setSystemUiVisibility(flags);
        }
        if(Build.VERSION.SDK_INT>=30){
            WindowInsetsController c=getWindow().getInsetsController();
            if(c!=null){
                int appearance=dark?0:(WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS);
                int mask=WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(appearance,mask);
                c.show(WindowInsets.Type.statusBars()|WindowInsets.Type.navigationBars());
            }
        }
    }

    public class ThemeBridge {
        @JavascriptInterface public String getSystemMode(){
            int night=getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK;
            return night==Configuration.UI_MODE_NIGHT_YES?"dark":"light";
        }
        @JavascriptInterface public void applyResolvedMode(String mode){
            final boolean dark="dark".equalsIgnoreCase(mode);
            runOnUiThread(()->applyResolvedSystemBars(dark));
        }
    }

    @Override public void onConfigurationChanged(Configuration newConfig){
        super.onConfigurationChanged(newConfig);
        if(webView!=null){
            webView.post(()->webView.evaluateJavascript("if(typeof applySystemThemeV86==='function')applySystemThemeV86();",null));
        }
    }

'''
if 'class ThemeBridge' not in main:
    if back_anchor not in main: raise SystemExit('back handler anchor not found')
    main=main.replace(back_anchor,back_anchor+bridge_code,1)

mainp.write_text(main,encoding='utf-8')

# 5) Receive uiMode changes without destroying the WebView. Automatic mode then updates live.
manifestp=root/'app/src/main/AndroidManifest.xml'
manifest=manifestp.read_text(encoding='utf-8')
if 'android:configChanges=' not in manifest:
    manifest=manifest.replace('android:screenOrientation="portrait">','android:screenOrientation="portrait"\n            android:configChanges="uiMode">',1)
manifestp.write_text(manifest,encoding='utf-8')

# 6) Explicitly forbid Android Force Dark at theme level too.
themesp=root/'app/src/main/res/values/themes.xml'
themes=themesp.read_text(encoding='utf-8')
if 'android:forceDarkAllowed' not in themes:
    themes=themes.replace('<item name="android:windowActionModeOverlay">true</item>',
                          '<item name="android:windowActionModeOverlay">true</item>\n        <item name="android:forceDarkAllowed">false</item>',1)
themesp.write_text(themes,encoding='utf-8')

# Sanity checks: one JS controller, no obsolete V8.2 matchMedia listener, native darkening disabled.
if html.count('id="v86-native-theme-controller"')!=1:
    raise SystemExit('V8.6 theme controller count is not one')
if 'const mediaV82=' in html or 'onSystemThemeV82' in html:
    raise SystemExit('old V8.2 theme listener still present')
if html.count('window.applyThemeV86=function')!=1:
    raise SystemExit('applyThemeV86 controller count is not one')
if 'setAlgorithmicDarkeningAllowed(false)' not in main:
    raise SystemExit('native WebView darkening disable missing')
if 'class ThemeBridge' not in main:
    raise SystemExit('native ThemeBridge missing')

htmlp.write_text(html,encoding='utf-8')

bp=root/'app/build.gradle'
b=bp.read_text(encoding='utf-8')
b=re.sub(r'versionName\s+["\'].*?["\']','versionName "8.6"',b)
m=re.search(r'versionCode\s+(\d+)',b)
if m:
    old=int(m.group(1)); b=b[:m.start(1)]+str(max(old+1,86))+b[m.end(1):]
bp.write_text(b,encoding='utf-8')
print('V8.6 native WebView theme control applied')
