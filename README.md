# Ludoria - Board games

<div style="display: flex; flex-wrap: wrap; justify-content: center;">
<img src="assets/japon/joueur1.png" style="width: 100px; margin: 5px;">
<img src="assets/japon/joueur2.png" style="width: 100px; margin: 5px;">
<img src="assets/tropique/joueur1.png" style="width: 100px; margin: 5px;">
<img src="assets/tropique/joueur2.png" style="width: 100px; margin: 5px;">
<img src="assets/grec/joueur1.png" style="width: 100px; margin: 5px;">
<img src="assets/grec/joueur2.png" style="width: 100px; margin: 5px;">
<img src="assets/sahara/joueur1.png" style="width: 100px; margin: 5px;">
<img src="assets/sahara/joueur2.png" style="width: 100px; margin: 5px;">
<img src="assets/nordique/joueur1.png" style="width: 100px; margin: 5px;">
<img src="assets/nordique/joueur2.png" style="width: 100px; margin: 5px;">
</div>


## Table des matières

- [Ludoria - Board games](#ludoria---board-games)
  - [Table des matières](#table-des-matières)
  - [Installation](#installation)
  - [Lancement des jeux](#lancement-des-jeux)
  - [Documentations](#documentations)

## Installation

Pour installer Ludoria, suivez ces étapes :

1. Assurez-vous d'avoir Python 3.10 ou supérieur installé sur votre système.
2. Clonez le dépôt GitHub ou téléchargez le code source.
3. Ouvrez un terminal à la racine du projet.
4. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## Lancement des jeux

Pour lancer l'application et choisir un jeu :

```bash
python client.py
```

Pour démarrer un serveur multijoueur (nécessaire uniquement pour le mode réseau) :

```bash
python start_server.py
```

L'écran de sélection vous permettra de choisir :
- Le jeu que vous souhaitez jouer (Katarenga, Congress ou Isolation)
- Le mode de jeu (Solo, contre IA, ou Multijoueur en réseau)
- Charger une partie sauvegardée

## Documentations
| Fichier                                                  | Description                                                                                             |
| :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| [`CONTRIBUTIONS.MD`](docs/CONTRIBUTIONS.MD)               | Guide pour les contributeurs expliquant le flux de travail, les branches, les pull requests et le signalement des problèmes. |
| [`TECHNICAL.md`](docs/TECHNICAL.md) | Détails techniques sur l'architecture, les technologies, les structures de données, les algorithmes et le réseau. |
| [`USER_MANUAL.md`](docs/USER_MANUAL.md)                   | Instructions pour les utilisateurs sur l'installation, le lancement des jeux, les règles, les modes de jeu et l'interface. |
| [`CONVENTIONS.md`](docs/CONVENTIONS.md)                   | Définit le style de code, les conventions de nommage et les normes de documentation pour le projet.   |
