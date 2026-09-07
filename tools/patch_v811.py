from pathlib import Path
import re, sys
from xml.etree import ElementTree as ET

root=Path(sys.argv[1] if len(sys.argv)>1 else 'extracted/EspritLibreAndroid')
assets=root/'app/src/main/assets'
p=assets/'index.html'
s=p.read_text(encoding='utf-8')
source=Path(__file__).resolve().parent
if 'id="v811PhotoModal"' in s:
    raise SystemExit('V8.11 already applied; refusing duplicate patch')

def replace(old,new):
    global s
    if s.count(old)!=1: raise SystemExit('Expected one source anchor: '+old[:100])
    s=s.replace(old,new,1)

def add_after(anchor,content): replace(anchor,anchor+content)

# Preserve the V8.10 calendar, notification, theme and score logic.
replace('</head>','<style id="v811-photo-polish">\n'+(source/'v811-ui.css').read_text(encoding='utf-8')+'\n</style>\n</head>')
replace('<span id="serenityScoreNum">78/100</span>','<strong id="serenityScoreNum">78/100</strong>')
replace('onclick="toggleQuickAdd(false);openAiCommand()"','onclick="toggleQuickAdd(false);openAiCommandV811()"')

share='<button type="button" class="smallbtn v811-share" disabled aria-disabled="true" title="Partage bientôt disponible">↗ Partager · bientôt</button>'
add_after('<div id="aiCommandResult"></div>','\n<div class="v811-action-row"><button type="button" class="smallbtn" onclick="openPhotoV811()">📷 Photographier une liste <span class="v811-photo-badge">Premium</span></button>'+share+'</div>')
add_after('<textarea id="quickNoteText" placeholder="Ex : penser au cadeau de Victoria"></textarea>','\n<div class="v811-action-row">'+share+'</div>')
for name in ('saveEvent','saveFloating','saveQuickThought'):
    pattern=r'<button\b[^>]*onclick="'+name+r'\(\)"[^>]*>'
    matches=list(re.finditer(pattern,s))
    if len(matches)!=1:raise SystemExit('Expected one save button: '+name)
    pos=matches[0].start()
    s=s[:pos]+share+'\n'+s[pos:]

profile='''<div class="card v811-share-card" id="v811ShareCard"><div class="card-title-ribbon ribbon-profile">↗ Partage familial</div><p class="note">Le partage des données n’est pas encore activé.</p><div class="v811-qr-placeholder" aria-label="Emplacement du futur QR code, non généré"><span>▦</span><small>QR code<br>à venir</small></div><p class="note">Le QR code sera généré ici lorsque le partage sera disponible.</p><button type="button" class="smallbtn v811-share" disabled aria-disabled="true">Partager · bientôt</button></div>'''
replace('<div class="card mode-switch-card">',profile+'\n<div class="card mode-switch-card">')

# Do not advertise unfinished cloud sharing or real subscriptions.
replace('Tu peux aussi lui parler naturellement pour créer un rendez-vous ou une tâche, et ses recommandations deviennent plus précises en tenant compte de ton planning, de la météo, de ta fatigue et de la charge de toute la famille.','Tu peux lui parler naturellement pour créer un rendez-vous ou une tâche, et ses recommandations deviennent plus précises en tenant compte de ton planning, de la météo, de ta fatigue et de la charge de toute la famille. Le mode photo permet de photographier une liste ou un document, de vérifier le texte reconnu et de l’enregistrer en note. Le partage familial et son QR code sont en préparation.')
replace('<span class="ok-pill">Annuel : 39,99 €/an</span>','<span class="ok-pill">Annuel : 39,99 €/an</span><p class="note">Premium de test : aucun paiement n’est effectué dans cette version. Tarifs indicatifs.</p>')

legal_start=s.index('<div class="legal-section">',s.index('id="legalModal"'))
legal_end=s.index('<button class="primary modal-validate"',legal_start)
s=s[:legal_start]+'''<div class="legal-section"><h3>CGU · Version 8.11 de test</h3><p>L'Esprit Léger est une application bêta d'aide à l'organisation personnelle et familiale. Elle propose notamment planning, notes, tâches, semaines types, rappels et suggestions intelligentes. Les fonctions peuvent évoluer et leur disponibilité n'est pas garantie sans interruption.</p><p>Les conseils et le score de sérénité sont des aides à l'organisation. Ils ne constituent pas un diagnostic ni un avis médical, psychologique, juridique ou professionnel. L'utilisateur vérifie les informations avant de les enregistrer et reste responsable de ses décisions.</p><p>Le Premium est simulé pour les tests autorisés : aucun abonnement ni paiement n'est effectué dans cette version. Les tarifs affichés sont indicatifs et pourront évoluer.</p></div>
<div class="legal-section"><h3>Données et confidentialité</h3><p>Les données de planning, notes, profils familiaux et préférences sont conservées localement par l'application sur l'appareil. Les fonctions de sauvegarde et de restauration existantes permettent de gérer une copie de ses données. La désinstallation ou l'effacement des données de l'application peut entraîner leur perte.</p><p>La reconnaissance photo utilise un modèle embarqué sur l'appareil : l'image n'est pas envoyée à un serveur pour la reconnaissance. Le texte reconnu est enregistré uniquement après validation. Les photos prises par cette fonction utilisent des fichiers temporaires privés, supprimés après traitement. Les images choisies dans la galerie ne sont pas supprimées.</p><p>La météo peut contacter un service externe et utiliser la localisation après autorisation. Le partage familial, l'association de comptes et la génération de QR code ne sont pas actifs dans cette version. Aucun QR code de partage réel n'est créé.</p><p>Les futures intégrations de santé et d'objets connectés devront faire l'objet d'un consentement spécifique. Cette bêta ne revendique pas de certification médicale ni de conformité juridique définitive.</p></div>
<div class="legal-section"><h3>Autorisations et sécurité</h3><p>La localisation sert à la météo et les notifications aux rappels activés. L'accès à une image est demandé lors de la sélection ou de la prise d'une photo. L'utilisateur peut refuser ces accès ; les fonctions correspondantes seront alors indisponibles. Il est conseillé de vérifier le texte reconnu et d'éviter les documents sensibles inutiles à l'organisation.</p></div>
<div class="legal-section"><h3>Évolution du service</h3><p>Cette version est destinée aux tests autorisés. Les anomalies peuvent être signalées à l'équipe de développement. Les conditions commerciales, les modalités de traitement des données et les fonctions de partage devront être précisées et faire l'objet d'une validation juridique avant une diffusion publique.</p></div>
''' +s[legal_end:]

photo='''<div class="modal" id="v811PhotoModal" data-noswipe="true" onclick="backdropClose(event)"><div class="sheet"><button class="close" onclick="closeModals()">Fermer</button><h2>📷 Photo vers note</h2><p class="note">Photographie une liste ou choisis une image. Le texte est reconnu sur ton appareil, puis tu peux le corriger avant l'enregistrement.</p><div class="v811-photo-actions"><button type="button" class="smallbtn" onclick="startPhotoV811(true)">📷 Prendre une photo</button><button type="button" class="smallbtn" onclick="startPhotoV811(false)">▧ Choisir une image</button></div><p class="v811-photo-status" id="v811PhotoStatus" role="status" aria-live="polite">Choisis une image pour commencer.</p><label for="v811PhotoCategory">Catégorie</label><select id="v811PhotoCategory"><option>Courses</option><option>Repas</option><option>Maison</option><option>Administratif</option><option>Vacances</option><option>Idée</option></select><label for="v811PhotoText">Texte reconnu à vérifier</label><textarea id="v811PhotoText" class="v811-photo-preview" placeholder="Le texte reconnu apparaîtra ici. Tu peux aussi le compléter."></textarea><button type="button" id="v811PhotoSave" class="primary modal-validate" onclick="savePhotoNoteV811()">Enregistrer la note</button></div></div>'''
replace('<div class="modal" id="quickNoteModal"',photo+'\n<div class="modal" id="quickNoteModal"')
s=re.sub(r'(?i)(version\s*)8\.10\b',r'\g<1>8.11',s)
replace('</body>','<script id="v811-photo-polish-script">\n'+(source/'v811-ui.js').read_text(encoding='utf-8')+'\n</script>\n</body>')
p.write_text(s,encoding='utf-8')

# Keep the same application ID and increase the version code for an update.
gradle=root/'app/build.gradle';g=gradle.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 812',g)
g=re.sub(r'versionName\s+["\'][^"\']+["\']','versionName "8.11"',g)
g+='\n// Bundled on-device Latin text recognition and private camera URI support.\ndependencies {\n    implementation "com.google.mlkit:text-recognition:16.0.1"\n    implementation "androidx.core:core:1.13.1"\n}\n'
gradle.write_text(g,encoding='utf-8')
manifest=root/'app/src/main/AndroidManifest.xml';m=manifest.read_text(encoding='utf-8')
m=m.replace('<application','<uses-feature android:name="android.hardware.camera" android:required="false" />\n<application',1)
m=m.replace('</application>','''    <provider android:name="androidx.core.content.FileProvider" android:authorities="${applicationId}.photo" android:exported="false" android:grantUriPermissions="true"><meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/v811_photo_paths" /></provider>
    </application>''',1)
ET.fromstring(m);manifest.write_text(m,encoding='utf-8')
xml=root/'app/src/main/res/xml';xml.mkdir(parents=True,exist_ok=True)
(xml/'v811_photo_paths.xml').write_text('<?xml version="1.0" encoding="utf-8"?><paths xmlns:android="http://schemas.android.com/apk/res/android"><cache-path name="photo" path="." /></paths>\n',encoding='utf-8')
java=root/'app/src/main/java/com/espritlibre/app';main=java/'MainActivity.java';j=main.read_text(encoding='utf-8')
if j.count('private WebView webView;')!=1:raise SystemExit('WebView anchor missing')
j=j.replace('private WebView webView;','private WebView webView;\n    private PhotoBridge photoBridge;',1)
if j.count('webView.addJavascriptInterface(new NotificationBridge')!=1:raise SystemExit('Notification bridge anchor missing')
j=j.replace('webView.addJavascriptInterface(new NotificationBridge','photoBridge=new PhotoBridge(this,webView);\n        webView.addJavascriptInterface(photoBridge,"AndroidPhoto");\n        webView.addJavascriptInterface(new NotificationBridge',1)
if j.count('    @Override public void onWindowFocusChanged')!=1:raise SystemExit('Lifecycle anchor missing')
j=j.replace('    @Override public void onWindowFocusChanged','    @Override protected void onActivityResult(int request,int result,android.content.Intent data){super.onActivityResult(request,result,data);if(photoBridge!=null)photoBridge.onResult(request,result,data);}\n\n    @Override public void onWindowFocusChanged',1)
main.write_text(j,encoding='utf-8')
(java/'PhotoBridge.java').write_text((source/'PhotoBridgeV811.java').read_text(encoding='utf-8'),encoding='utf-8')
print('V8.11 source updated: photo, layout, legal text and inactive sharing')
