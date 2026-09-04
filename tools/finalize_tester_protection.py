from pathlib import Path
import sys
if len(sys.argv)!=6: raise SystemExit('usage: finalize <root> <html_sha> <cert_sha> <aes_key> <aes_iv>')
root=Path(sys.argv[1]); html_sha,cert_sha,key,iv=sys.argv[2:]
p=root/'app/src/main/java/com/espritlibre/app/MainActivity.java'
s=p.read_text(encoding='utf-8')
s=s.replace('__HTML_SHA__',html_sha).replace('__CERT_SHA__',cert_sha).replace('__AES_KEY__',key).replace('__AES_IV__',iv)
if '__' in s: raise SystemExit('protection placeholders remain')
p.write_text(s,encoding='utf-8')
print('Tester protection finalized')