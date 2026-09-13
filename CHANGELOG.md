# Historique des versions

Ce fichier conserve l'historique visible du projet MDADM Manager. Les anciennes versions ne sont plus conservées comme scripts actifs à la racine, mais leurs changements restent documentés ici et dans l'historique Git.

## v1.75 FULL — 2026-09-13

- consolidation de la version FULL actuelle ;
- gestion RAID complète et protections avant opérations sensibles ;
- réintégration d'anciens membres RAID ;
- suivi des slots, membres absents et identité physique des disques ;
- outils SMART et diagnostic disque ;
- assistant câble/SATA et hot-swap ;
- suivi CRC ;
- progression reconstruction/recovery/resync/reshape ;
- améliorations d'interface et de maintenance ;
- nouvelle série de captures d'écran ;
- remise à niveau de l'architecture modulaire sur la base du moteur v1.75 ;
- métadonnées `uv` synchronisées sur v1.75.

## v1.62 à v1.74 — développements intermédiaires

Ces numéros correspondent à des évolutions intermédiaires ayant mené au script v1.75 FULL. Ils n'ont pas tous été publiés séparément dans le dépôt GitHub avec un commit de release identifiable. Leurs changements sont donc conservés dans la version FULL consolidée plutôt que décrits artificiellement version par version.

Cette section sera complétée si les anciens scripts ou notes de versions correspondants sont ajoutés au dépôt.

## v1.61 — 2026-09-13

- correction de la détection du pourcentage de reconstruction dans `/proc/mdstat` ;
- affichage du pourcentage directement sur le membre en reconstruction ;
- panneau dédié REBUILD / RESYNC ;
- affichage des blocs reconstruits, de la vitesse et du temps restant ;
- détection recovery, resync, reshape, check et repair.

## v1.60 — 2026-09-13

- ajout du suivi temps réel de reconstruction RAID ;
- lecture de `/proc/mdstat` ;
- ajout du panneau de progression rebuild/resync.

## v1.59 — 2026-09-13

- ajout du suivi de tendance CRC ;
- distinction entre une ancienne valeur CRC stable et une hausse active ;
- ajout de l'assistant CRC avant/après ;
- ajout de l'assistant de maintenance et de remplacement.

## v1.58 — 2026-09-13

- réintégration sécurisée d'un ancien membre RAID ;
- validation de l'Array UUID ;
- vérification de l'ancien slot RAID ;
- comparaison du compteur Events ;
- tentative `mdadm --re-add` lorsqu'un ancien membre correspond exactement ;
- détection des candidats de remplacement.

## v1.56 — 2026-09-13

- activation du mécanisme de réintégration RAID ;
- intégration de la réintégration sécurisée des anciens membres ;
- mise à jour du lanceur courant.

## v1.49 — 2026-09-10

- première refactorisation importante vers `mdadm_matrix/` ;
- séparation des composants principaux en modules ;
- amélioration de la détection des limites entre modules ;
- séparation de plusieurs composants GUI ;
- ajout de la configuration `uv` et de la documentation de déploiement.

## v1.48 RC1 — 2026-09-06

- publication de la version RC1 ;
- base de gestion RAID, SMART, informations disque et interface Matrix utilisée pour les versions suivantes.

## v1.29 — 2026-09-05

- première version bêta publique ;
- gestion et surveillance RAID ;
- assistant de création RAID ;
- informations SMART ;
- protections RAID/FSTAB ;
- effacement sécurisé des anciens superblocks avec confirmations.

---

## Politique pour les prochaines versions

À partir de v1.75, chaque nouvelle version publiée doit ajouter une entrée dans ce fichier avant ou pendant le commit de release. Le dépôt peut ne conserver que le script/lanceur courant, mais l'historique des versions ne doit plus être supprimé.
