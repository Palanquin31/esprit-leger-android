(function(){
  'use strict';
  const byId=id=>document.getElementById(id);
  let scanning=false;
  function premium(){return typeof isPremium!=='undefined'&&!!isPremium;}
  function status(message){const el=byId('v811PhotoStatus');if(el)el.textContent=message;}
  function busy(value){scanning=value;document.querySelectorAll('.v811-photo-actions button').forEach(b=>b.disabled=value);const save=byId('v811PhotoSave');if(save)save.disabled=value;}
  window.openPhotoV811=function(){
    if(!premium()){alert('La reconnaissance de photo est réservée au Premium. Active le mode Premium de test dans Profil.');return;}
    if(typeof closeModals==='function')closeModals();
    byId('v811PhotoText').value='';byId('v811PhotoCategory').value='Courses';
    status('Choisis une photo ou prends une nouvelle image.');busy(false);
    byId('v811PhotoModal').classList.add('show');
    if(typeof updateFloatingVisibility==='function')updateFloatingVisibility();
  };
  window.startPhotoV811=function(camera){
    if(!premium()){alert('Cette fonction est réservée au Premium.');return;}
    if(scanning)return;
    const bridge=window.AndroidPhoto;
    if(!bridge){status('Reconnaissance photo disponible dans la version Android.');return;}
    busy(true);status('Ouverture de la photo…');
    try{camera?bridge.takePhoto():bridge.chooseImage();}
    catch(e){busy(false);status('Impossible d’ouvrir la photo.');}
  };
  window.espritPhotoResultV811=function(result){
    if(!result||typeof result!=='object')return;
    if(result.status==='processing'){busy(true);status('Reconnaissance du texte en cours…');return;}
    busy(false);
    if(result.status==='cancel'){status('Photo annulée.');return;}
    if(result.status==='empty'){status('Aucun texte reconnu. Réessaie avec une photo plus nette.');return;}
    if(result.status==='error'){status(result.text||'La reconnaissance a échoué.');return;}
    if(result.status==='success'){
      if(!premium()){status('Le mode Premium est nécessaire pour utiliser cette fonction.');return;}
      byId('v811PhotoText').value=String(result.text||'').slice(0,20000);
      status('Texte reconnu. Vérifie et corrige la note avant de l’enregistrer.');
    }
  };
  window.savePhotoNoteV811=function(){
    if(!premium()){alert('Cette fonction est réservée au Premium.');return;}
    if(scanning)return;
    const text=byId('v811PhotoText').value.trim();
    if(!text){status('Aucun texte à enregistrer.');return;}
    // Use the existing note model and persistence, not a second data store.
    appNotes.push({id:'note_'+Date.now(),category:byId('v811PhotoCategory').value,text});
    if(typeof saveState==='function')saveState();
    byId('v811PhotoText').value='';
    closeModals();render();
  };
  window.openAiCommandV811=function(){
    if(!premium()){alert('L’assistant et le mode photo sont réservés au Premium.');return;}
    if(typeof openAiCommand==='function')openAiCommand();
  };
  // Share buttons have no handlers. No QR payload, account link or network request.
  function setup(){
    document.querySelectorAll('.hero-stat-card[onclick]').forEach(el=>{
      el.setAttribute('role','button');el.tabIndex=0;
      el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.click();}});
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
})();
