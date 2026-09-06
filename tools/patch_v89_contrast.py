from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
p=root/'app/src/main/assets/index.html'
h=p.read_text(encoding='utf-8')
old="""  function contrastTextV89(hex){
    const [r,g,b]=rgbV89(hex).map(v=>v/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));
    const L=.2126*r+.7152*g+.0722*b;
    return L>.42?'#2D2738':'#FFFFFF';
  }
"""
new="""  function contrastTextV89(hex){
    const [r,g,b]=rgbV89(hex).map(v=>v/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));
    const L=.2126*r+.7152*g+.0722*b;
    const whiteRatio=1.05/(L+.05);
    const darkL=.005605391624202723; /* relative luminance of #111111 */
    const darkRatio=(L+.05)/(darkL+.05);
    return darkRatio>=whiteRatio?'#111111':'#FFFFFF';
  }
"""
if old not in h: raise SystemExit('V8.9 contrast function not found')
h=h.replace(old,new,1)
p.write_text(h,encoding='utf-8')
print('V8.9 WCAG contrast selection hardened')
