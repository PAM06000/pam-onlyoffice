# pam — catalogue ONLYOFFICE

Catalogue personnalisé contenant uniquement le plugin officiel **AI 3.2.2**.
Le plugin et son archive d'installation restent inchangés.

## Publication gratuite avec GitHub Pages

Dans les paramètres du dépôt, sélectionner **Pages → Source → GitHub Actions**.
Le workflow fourni construit et publie le catalogue à chaque modification de `main`.
L'adresse finale est fournie par l'étape de déploiement GitHub Pages ; ajouter
`store/index.html` à la racine du site.

Dans ONLYOFFICE : **Plugins → Gestionnaire de plugins → Developer Mode**,
coller cette adresse complète de marketplace, puis confirmer.

Le catalogue est accessible à toute personne disposant du lien. Il ne comporte
pas d'authentification ; `noindex` et `robots.txt` découragent uniquement
l'indexation. GitHub Pages gratuit nécessite ici un dépôt public.

## Sources et construction

Exécuter `python3 build_store.py` avec Python 3 pour générer `_site/`.
Le manifeste verrouille chaque fichier au commit officiel
`4d02c4fde76dd98b94129881a0d68366ae0e56e5` et vérifie son empreinte Git.
Le paquet AI est également vérifié par SHA-256.
Les chemins relatifs conviennent à un site hébergé dans un sous-dossier.
Voir [PAM-SOURCE.md](PAM-SOURCE.md) pour les sources, modifications et licences.

Le protocole d'installation et les fichiers ont été vérifiés ; l'installation
dans votre instance ONLYOFFICE reste à confirmer.
