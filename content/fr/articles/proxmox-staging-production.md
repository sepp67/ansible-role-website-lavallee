---
title: "Pourquoi j’ai séparé le staging et la production sur deux nœuds Proxmox"
date: 2026-06-02
description: "Comment une plateforme auto-hébergée est passée d’un unique nœud Proxmox à une infrastructure séparée entre staging et production."
---

Lorsque j’ai acheté le nom de domaine **lavallee.tech** en 2021, mon objectif était simple : apprendre, expérimenter et héberger quelques services pour des associations locales. À l’époque, un unique nœud Proxmox installé sur un Dell OptiPlex d’occasion était largement suffisant. J’y ai déployé quelques machines virtuelles YunoHost, hébergé plusieurs sites web et fourni des services cloud et de messagerie à différentes associations.
Cinq ans plus tard, l’infrastructure a beaucoup évolué.
Ce qui avait commencé comme un petit projet d’auto-hébergement est progressivement devenu une plateforme hébergeant des services en production, des environnements de développement, des systèmes de supervision et des applications personnalisées.
Cette croissance m’a finalement obligé à repenser complètement l’architecture.

![Architecture avant et après : passage d’un nœud Proxmox unique à une séparation staging / production](/images/articles/proxmox-staging-production/before-after-proxmox.png)

_L’infrastructure avant et après la séparation des environnements de staging et de production._

## L’architecture d’origine

La plateforme fonctionnait initialement sur un Dell OptiPlex 3040 équipé d’un processeur Intel i5-6500 et de 16 Go de mémoire vive.
Pendant plusieurs années, cette machine a hébergé l’ensemble des services :
* Services cloud et messagerie pour les associations locales
* Déploiements Nextcloud et Matrix
* Sites WordPress
* Systèmes de supervision
* Projets de développement
* Applications en production

La simplicité d’une infrastructure à nœud unique présentait de nombreux avantages. Une seule machine était à administrer et les ressources étaient faciles à gérer.
Tant que le nombre de services restait limité, cette approche fonctionnait étonnamment bien.

## Quand la croissance devient un problème
Le premier changement majeur a été l’introduction d’un véritable cycle de déploiement staging / production.
Au départ, je n’hébergeais que quelques sites WordPress. Les déploiements étaient simples et le risque lié aux modifications en production restait faible.
La situation a changé lorsque j’ai commencé à développer et déployer mes propres applications.
Une infrastructure de supervision a été ajoutée.
Une architecture de reverse proxy a été mise en place.
Le site lavallee.tech est devenu un projet à part entière.
Une application de diffusion vidéo pour caméra IP a été déployée.
Une application française de facturation électronique est entrée en phase de développement.
Chaque nouveau projet nécessitait désormais un environnement de production et un environnement de staging.
Au fil du temps, l’infrastructure a atteint près d’une vingtaine de machines virtuelles.
À ce stade, les limites du matériel d’origine sont devenues impossibles à ignorer.

## Une mémoire devenue insuffisante
Le Dell OptiPlex 3040 est limité à 16 Go de RAM.

Aujourd’hui, ce nœud héberge :
* 1 VM AzuraCast
* 1 VM de supervision Proxmox
* 4 VM YunoHost pour des associations locales
* 2 VM WordPress
* 1 VM de reverse proxy en production
* 1 VM lavallee.tech
* 1 VM Facturier
* 1 VM de streaming vidéo
* L’équivalent de ces applications en environnement de staging
* 2 VM de supervision pour la plateforme applicative
* 1 VM de contrôle Ansible

Le signe le plus évident que l’infrastructure avait atteint ses limites est que l’environnement de staging ne pouvait plus rester allumé en permanence.
Pour garantir la stabilité des services en production, j’étais obligé d’éteindre l’ensemble des machines virtuelles de staging.
Même avec une dizaine de VM arrêtées, l’utilisation mémoire restait proche de 80 %.
À ce stade, il n’était plus possible d’ajouter davantage de mémoire car la machine avait déjà atteint sa capacité maximale.
L’infrastructure avait tout simplement dépassé les capacités du serveur d’origine.

## Pourquoi ajouter un second nœud Proxmox ?
Plutôt que de remplacer la machine existante, j’ai décidé d’ajouter un second nœud Proxmox.
Le nouveau serveur est un Dell OptiPlex 7010 équipé d’un processeur Intel i7-3770 et de 32 Go de RAM.
J’ai volontairement choisi une nouvelle fois une station de travail d’occasion.
De nombreux homelabs s’appuient sur du matériel serveur professionnel, mais dans mon cas la capacité mémoire est souvent plus importante que la puissance brute du processeur.
Les Dell OptiPlex d’occasion sont peu coûteux, fiables, compacts et faciles à trouver.
Surtout, ils offrent un excellent rapport coût / capacité pour une infrastructure auto-hébergée.
L’ajout de ce second nœud fait immédiatement passer la mémoire disponible de 16 Go à 48 Go tout en conservant un budget raisonnable.

## Séparer le staging et la production
L’objectif principal du nouveau nœud est de séparer physiquement les charges de travail de production et de staging.
Auparavant, les deux environnements partageaient le même matériel.
Cette organisation était acceptable au début du projet mais devenait de plus en plus difficile à maintenir à mesure que le nombre d’applications augmentait.
La nouvelle architecture est beaucoup plus simple :

![Centre de données Proxmox montrant l’architecture à deux nœuds](/images/articles/proxmox-staging-production/proxmox-two-nodes.png)

_Le centre de données Proxmox actuel. Les charges de travail de production et de staging sont désormais réparties sur deux serveurs physiques distincts._

| Nœud | CPU | RAM | Rôle |
|-------|-------|-------|-------|
| Dell OptiPlex 3040 | Intel i5-6500 | 16 Go | Production |
| Dell OptiPlex 7010 | Intel i7-3770 | 32 Go | Staging |

### Nœud de production

* Services pour les associations
* Nextcloud
* Matrix
* Sites WordPress
* Applications accessibles au public
* Services de reverse proxy

### Nœud de staging

* Développement applicatif
* Validation des déploiements
* Tests d’infrastructure
* Projets expérimentaux

Cette séparation offre une meilleure isolation des ressources et permet de maintenir les environnements de staging disponibles en permanence.
Plus important encore, elle rapproche l’organisation de l’infrastructure de ce que l’on rencontre dans des environnements professionnels.

## Réduire la dépendance à certaines instances YunoHost
YunoHost a joué un rôle important dans la croissance de la plateforme.
Il m’a permis de déployer rapidement des services comme Nextcloud ou Matrix et a constitué une excellente porte d’entrée vers l’auto-hébergement.
Cependant, avec l’augmentation du nombre de services, certaines limites sont apparues.
Chaque instance YunoHost nécessite une machine virtuelle dédiée et consomme significativement plus de mémoire qu’un déploiement conteneurisé.
La supervision de plusieurs instances YunoHost devient également plus complexe à mesure que l’infrastructure grandit.
Pour ces raisons, j’ai choisi de profiter de cette restructuration pour migrer progressivement certains services collaboratifs vers des déploiements Docker gérés par Ansible.
L’objectif n’est pas de remplacer totalement YunoHost, mais d’utiliser un modèle plus flexible lorsque cela est pertinent.

## Construire une supervision centralisée
Une autre motivation importante derrière cette restructuration est l’observabilité.
À mesure que de nouvelles applications et machines virtuelles ont été ajoutées, la supervision s’est fragmentée.
Plusieurs solutions de monitoring ont été déployées au fil du temps, notamment une plateforme dédiée à Proxmox ainsi que des environnements de supervision séparés pour les applications.
L’objectif à long terme est de centraliser la supervision autour d’une plateforme basée sur Prometheus, Grafana et Loki.
Au lieu de surveiller chaque environnement séparément, l’ensemble de l’infrastructure sera visible depuis un point unique.
Cela simplifiera le diagnostic des incidents, améliorera la visibilité globale et permettra de mieux comprendre la consommation des ressources sur tous les nœuds.

## Préparer les projets futurs
L’infrastructure est également préparée pour accueillir de nouvelles applications.
L’un des projets les plus importants actuellement en développement est une plateforme française de facturation électronique capable de générer des factures Factur-X à partir de documents PDF.
Cette application nécessite un véritable environnement de staging permettant de tester les nouvelles fonctionnalités avant leur mise en production.
Disposer d’une infrastructure dédiée au staging supprime un obstacle important au développement et permet aux projets d’évoluer plus rapidement.

## Et maintenant ?
L’objectif de cette restructuration n’est pas simplement d’ajouter davantage de mémoire.
C’est l’occasion de repenser une infrastructure qui a considérablement évolué depuis 2021.
Ce qui avait commencé comme un petit environnement auto-hébergé destiné à quelques associations est devenu une plateforme hébergeant des services en production, des environnements de développement, des systèmes de supervision et des applications personnalisées.
En séparant le staging de la production, en migrant certaines charges vers Docker et en construisant une plateforme de supervision centralisée, l’infrastructure devient plus simple à maintenir, plus facile à faire évoluer et mieux préparée pour les projets futurs.
Le Dell OptiPlex 3040 a rempli son rôle de manière remarquable.
L’ajout d’un second nœud Proxmox n’est finalement qu’une nouvelle étape dans l’évolution de la plateforme.
