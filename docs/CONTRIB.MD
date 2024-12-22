# Contribution Guide

## Branches

### Branche Master
La branche `master` est une branche stable qui contient du code fiable, testé et généralement sans bug.

### Branche Dev
La branche `dev` contient toutes les modifications. Lorsque nous sommes sûrs que tout fonctionne, nous créons une pull request de `dev` vers `master`.

## Flux de Travail

### Créer une Fonctionnalité ou Corriger un Bug
Lorsque vous souhaitez ajouter une fonctionnalité, corriger un bug ou apporter d'autres modifications, créez une nouvelle branche basée sur `dev`. Chaque jour, et avant d'envoyer vos commits ou autres modifications, récupérez les mises à jour de la branche `dev` :

```bash
git merge dev
```

⚠️ **Attention :** S'il y a des conflits, vous devez les résoudre sans causer de problèmes de fonctionnement.

### Pull Requests
Lorsque vous avez créé une nouvelle branche de travail, vous devez créer une pull request (de votre branche vers `dev`) et expliquer ce que vous voulez faire, sans fusionner. Vous ne devez fusionner qu'après que nous trois ayons confirmé.


