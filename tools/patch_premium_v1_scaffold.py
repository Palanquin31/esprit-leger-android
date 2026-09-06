from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
htmlp=root/'app/src/main/assets/index.html'
html=htmlp.read_text(encoding='utf-8')

repo_root=Path(__file__).resolve().parent.parent
contract=(repo_root/'premium_v1/client/family_premium_v1.js').read_text(encoding='utf-8')

marker='id="premium-v1-family-scaffold"'
if marker in html:
    raise SystemExit('Premium V1 scaffold already injected')

# La branche Premium part de la base visuelle/fonctionnelle stable V8.9.
for required in ['id="v86-native-theme-controller"','id="v87-fluid-glance-script"','id="v89-stability-intelligence-script"']:
    if required not in html:
        raise SystemExit(f'validated baseline missing: {required}')

# Le scaffold est chargé mais toutes les fonctions réseau/UI restent OFF.
block='\n<script id="premium-v1-family-scaffold">\n'+contract+'\n</script>\n'
html=html.replace('</body>',block+'</body>',1)

# Garde-fous : cette étape ne doit jamais activer le cloud par accident.
if "PREMIUM_FAMILY_V1_ENABLED: false" not in html:
    raise SystemExit('Premium V1 feature flag is not safely disabled')
if "CLOUD_SYNC_ENABLED: false" not in html:
    raise SystemExit('Cloud sync flag is not safely disabled')
if "FAMILY_ADVICE_SYNC_ENABLED: false" not in html:
    raise SystemExit('Family advice sync flag is not safely disabled')

htmlp.write_text(html,encoding='utf-8')
print("L'Esprit Léger Premium V1 scaffold injected — features remain disabled")
