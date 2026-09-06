# L'Esprit Léger Premium V1

Branche de préparation du futur mode Premium familial.

## Statut

**Désactivé par défaut.** Aucun écran Premium familial, aucune connexion Supabase et aucune synchronisation ne doivent être activés tant que la version individuelle n'est pas validée.

Feature flag prévu : `PREMIUM_FAMILY_V1_ENABLED = false`.

## Principes produit figés

1. Le partage familial est réservé au Premium.
2. Chaque élément possède un propriétaire unique.
3. À la création d'un rendez-vous, d'une tâche ou d'une semaine type, la visibilité sera simplement `privé` ou `partagé`.
4. Un élément partagé est lisible par les membres du même foyer.
5. Un autre membre du foyer ne peut jamais modifier ni supprimer un élément appartenant à quelqu'un d'autre. Cette règle doit être imposée côté base, pas seulement dans l'interface.
6. Les contraintes fixes (`Travail`, `École`, `Rendez-vous` et assimilés) ne sont jamais proposées comme éléments à déplacer par l'assistant.
7. L'assistant familial peut utiliser les éléments partagés de tous les membres pour proposer une meilleure répartition des activités flexibles.
8. Les conseils du foyer sont synchronisés et identiques pour les membres du même foyer.
9. Les éléments privés restent invisibles aux autres membres et ne doivent jamais être utilisés pour produire un conseil familial partagé.
10. L'application doit continuer à fonctionner localement si le cloud est indisponible, puis resynchroniser plus tard.

## Architecture visée

- **Application Android/WebView** : interface et copie locale rapide.
- **Supabase Auth** : identité des utilisateurs.
- **PostgreSQL / Supabase** : foyers, membres, éléments partagés et conseils familiaux.
- **Row Level Security** : droits réels de lecture/écriture.
- **Realtime** : propagation des changements entre les téléphones d'un même foyer.

## Étapes prévues

### Phase A — socle invisible
- modèles de données ;
- feature flags ;
- contrats de synchronisation ;
- schéma SQL + RLS ;
- aucune UI active.

### Phase B — comptes et foyer test
- connexion ;
- création/rejoindre un foyer ;
- invitation par code/QR ;
- toujours derrière le flag de développement.

### Phase C — partage
- sélecteur `Privé / Partagé` dans RDV, tâches et semaines types ;
- lecture en temps réel des éléments partagés ;
- écriture réservée au propriétaire.

### Phase D — intelligence familiale
- charge familiale ;
- identification des contraintes fixes et activités flexibles ;
- suggestions de répartition ;
- conseil du foyer synchronisé.

## Sécurité

Aucune clé secrète Supabase, aucun `service_role` et aucune clé privée ne doivent être commit dans le dépôt. Le client n'utilisera qu'une clé publique/anon adaptée au client ; les règles RLS restent la barrière d'autorisation principale.
