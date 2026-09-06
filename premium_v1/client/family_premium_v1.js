/*
 * L'Esprit Léger Premium V1 — contrat client préparatoire.
 * IMPORTANT : aucune connexion cloud n'est effectuée ici.
 * Le module est volontairement désactivé tant que PREMIUM_FAMILY_V1_ENABLED=false.
 */
(function(global){
  'use strict';

  const CONFIG = Object.freeze({
    name: "L'Esprit Léger Premium V1",
    version: 'premium-v1',
    PREMIUM_FAMILY_V1_ENABLED: false,
    CLOUD_SYNC_ENABLED: false,
    FAMILY_ADVICE_SYNC_ENABLED: false
  });

  const VISIBILITY = Object.freeze({PRIVATE:'private', SHARED:'shared'});
  const ITEM_KIND = Object.freeze({APPOINTMENT:'appointment', TASK:'task', TYPICAL_WEEK:'typical_week'});
  const FIXED_TYPES = new Set(['Travail','École','Rendez-vous']);
  const FLEXIBLE_TYPES = new Set(['Sport','Courses','Temps pour soi','Tâche']);

  function normalizedText(value){
    return String(value||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  }

  function isFixedActivity(item){
    if(!item)return false;
    if(FIXED_TYPES.has(item.type))return true;
    const title=normalizedText(item.title);
    return ['travail','ecole','rdv','rendez-vous','rendez vous','medecin','dentiste','kine','creche']
      .some(word=>title.includes(word));
  }

  function isFlexibleActivity(item){
    return !!item && !isFixedActivity(item) && FLEXIBLE_TYPES.has(item.type);
  }

  function normalizeVisibility(value){
    return value===VISIBILITY.SHARED ? VISIBILITY.SHARED : VISIBILITY.PRIVATE;
  }

  function assertCanMutate(item, currentUserId){
    if(!item || !currentUserId)return false;
    return String(item.owner_id||item.ownerId||'')===String(currentUserId);
  }

  function cloudItemFromLocal(localItem, options){
    const o=options||{};
    const visibility=normalizeVisibility(o.visibility);
    return {
      id:o.id||null,
      owner_id:o.ownerId||null,
      household_id:visibility===VISIBILITY.SHARED ? (o.householdId||null) : null,
      item_kind:o.kind,
      visibility,
      fixed:isFixedActivity(localItem),
      payload:JSON.parse(JSON.stringify(localItem||{})),
      revision:Number(o.revision||1)
    };
  }

  function localItemFromCloud(row){
    if(!row || !row.payload)return null;
    const item=JSON.parse(JSON.stringify(row.payload));
    item._cloud={
      id:row.id,
      ownerId:row.owner_id,
      householdId:row.household_id,
      visibility:normalizeVisibility(row.visibility),
      fixed:!!row.fixed,
      revision:Number(row.revision||1),
      readOnly:false
    };
    return item;
  }

  function localSharedItemForViewer(row, currentUserId){
    const item=localItemFromCloud(row);
    if(!item)return null;
    item._cloud.readOnly=String(row.owner_id)!==String(currentUserId);
    return item;
  }

  // Les conseils familiaux ne doivent recevoir que les éléments explicitement partagés.
  function buildFamilyAdviceSnapshot(rows, members){
    const shared=(Array.isArray(rows)?rows:[])
      .filter(r=>r && r.visibility===VISIBILITY.SHARED && !r.deleted_at)
      .map(r=>({
        id:r.id,
        ownerId:r.owner_id,
        kind:r.item_kind,
        fixed:!!r.fixed,
        payload:JSON.parse(JSON.stringify(r.payload||{}))
      }));

    return {
      engine:'premium-v1',
      createdAt:new Date().toISOString(),
      members:(Array.isArray(members)?members:[]).map(m=>({userId:m.user_id,displayName:m.display_name||''})),
      sharedItems:shared,
      movableItems:shared.filter(x=>!x.fixed && isFlexibleActivity(x.payload)),
      fixedItems:shared.filter(x=>x.fixed || isFixedActivity(x.payload))
    };
  }

  function disabledReason(){
    if(!CONFIG.PREMIUM_FAMILY_V1_ENABLED)return 'premium-family-v1-disabled';
    if(!CONFIG.CLOUD_SYNC_ENABLED)return 'cloud-sync-disabled';
    return null;
  }

  global.ELPremiumV1=Object.freeze({
    config:CONFIG,
    VISIBILITY,
    ITEM_KIND,
    isFixedActivity,
    isFlexibleActivity,
    normalizeVisibility,
    assertCanMutate,
    cloudItemFromLocal,
    localItemFromCloud,
    localSharedItemForViewer,
    buildFamilyAdviceSnapshot,
    disabledReason
  });
})(window);
