from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
p=root/'app/build.gradle'
s=p.read_text(encoding='utf-8')
s=re.sub(r'\n\s*signingConfigs \{.*?\n\s*\}\n\n\s*defaultConfig \{','\n\n    defaultConfig {',s,count=1,flags=re.S)
s=re.sub(r'\n\s*buildTypes \{\s*debug \{ signingConfig signingConfigs\.dev \}\s*\}\n','\n',s,count=1,flags=re.S)
p.write_text(s,encoding='utf-8')
print('V6.5 signing cleanup applied')
