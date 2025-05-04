# Contribution Guide

## Branches

### Branche master
La branche `master` est une branche stable qui contient du code fiable, testé et généralement sans bug.

## Flux de Travail

### Créer une Fonctionnalité ou Corriger un Bug
Lorsque vous souhaitez ajouter une fonctionnalité, corriger un bug ou apporter d'autres modifications, créez une nouvelle branche basée sur `master`. Chaque jour, et avant d'envoyer vos commits ou autres modifications, récupérez les mises à jour de la branche `master` :

```bash
git merge master
```

> [!IMPORTANT]  
> **git merge master**


⚠️ **Attention :** S'il y a des conflits, vous devez les résoudre sans causer de problèmes de fonctionnement.

### Pull Requests
Lorsque vous avez créé une nouvelle branche de travail, vous devez créer une pull request (de votre branche vers `master`) et expliquer ce que vous voulez faire, sans fusionner. Vous ne devez fusionner qu'après que nous trois ayons confirmé.

### Issues
Si vous souhaîtez partager un bug ou une idée, merci de faire une issue correctement formulé : Problème / Description / Comment reproduire
Si possible avec contenu ajouté comme des screenshots.