# OCR-developpement-interface

Vous travaillez en tant que développeur⸱se en IA pour le compte d’une ESN.
Un client exprime un besoin d’évolution pour sa procédure de pré-traitement des factures fournisseurs.
Le client souhaite étendre les fonctionnalités de pré-traitement au-delà avec des fonctionnalités d’OCR (ou “reconnaissance optique de caractères”) afin d’obtenir un reporting automatisé de sa comptabilité fournisseurs.
Le client en question vous donne accès aux sources de sa procédure de traitement : API d'accès aux factures numérisées.

Contexte du projet

Votre mission (si vous l'acceptez) est la suivante :

En tant que développeur⸱se en IA pour le compte d’une ESN, vous devez développer l'application OCR et :

● Intégrer la connexion à un ou plusieurs services OCR (open source, cloud based, etc)

● Intégrer les appels aux fonctions d’OCR

● Paramétrer les services OCR afin d'obtenir une qualité de traitement optimale

● Extraire les informations pertinentes

● Calculer les métriques attendues à partir des résultats de l’API

● Identifier un seuil de qualité minimum pour l'OCR

● Stocker les résultats en base de données

● Automatiser le processus complet, depuis le traitement d'une facture jusqu'au stockage en base de données

● Intégrer les résultats dans une interface web simple

● Documenter, versionner, livrer

​

Ce projet s'inscrit dans un cadre global consistant à exploiter des services d’IA externes dans le développement d’applications d’IA, avec pour missions de :

● Préconiser un service d’IA en fonction du besoin et des paramètres du projet,

● Intégrer dans une application existante l’API du modèle ou du service d’intelligence artificielle,

● Appliquer les bonnes pratiques de sécurité et d’accessibilité dans le développement d’application web,

● Développer des tests d’intégration sur le périmètre de l’API exploité,

● Rédiger une documentation technique.


Livrables

● Application web fonctionnelle et conforme aux attentes :
- Maquettes figma
- Authentification de l'utilisateur
- Technologie : au choix
- 3 vues (mini) :
      - Traitement OCR pour une facture (démo)
      - Dashboard sur les données de facturation : reporting
      - Dashboard sur les données de monitoring : reporting

● Backend :
- Flask ou FastAPI
- Modules de traitement OCR
- Swagger
- Tests automatisés : intégrer les concepts TDD, gestion des exceptions, assertions, etc.
- CI/CD
- Déploiement Docker

● Base de données :
- Table(s) pour le stockage des données facturation
- Table(s) pour les données de monitoring

● IA :
- Clustering : [à développer]

● Projet :
- Schéma fonctionnel de l’application avec les services nécessaires les technologies utilisées
- Trello
- GitHub : .gitignore, requirements.txt, readme, et tous les autres scripts
- Rapport de 5 pages mini : présentation du projet, présentation de l'OCR (principe, méthode et fonctionnement, limites, etc.), fonctionnement de l'application
- Slides de présentation : identification des services d'IA existants et utilisés. Savoir expliquer leur fonctionnement. Lister les spécifications fonctionnelles de l’application
Critères de performance

L'application finale doit :
- Correspondre aux objectifs énoncés
- Intégrer tous les services nécessaires à son bon fonctionnement

Bonus :
- La procédure en cas de résultat en dessous d’un seuil de qualité minimum est définie.
- La procédure en cas de résultat en dessous d’un seuil de qualité minimum est appliquée
- L'application intègre les modalités du "Human Feedback loop".
- L'application intègre un template "user friendly"
- L'application est sécurisée selon le top 10 OWASP
- L'application offre le choix d'utiliser différents services OCR
