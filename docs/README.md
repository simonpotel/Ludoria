# Smart Games

Ce projet contient trois jeux de plateau stratégiques : Katarenga, Isolation et Congress.

## Installation

1. Clonez le dépôt :
```bash
cd smart_games
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Les Jeux

### Katarenga

Katarenga est un jeu de stratégie où chaque joueur doit occuper les camps adverses.

#### Règles
- Le plateau est composé de 10x10 cases avec différents types de pièces
- Les pièces se déplacent différemment selon la case sur laquelle elles se trouvent :
  - Tour (0) : déplacement en ligne droite
  - Cavalier (1) : déplacement en L
  - Roi (2) : déplacement d'une case dans toutes les directions
  - Fou (3) : déplacement en diagonale
- Pour gagner, un joueur doit :
  - Soit occuper les deux camps adverses
  - Soit bloquer tous les mouvements possibles de l'adversaire
- Au premier tour, les captures ne sont pas autorisées

### Isolation

Isolation est un jeu où les joueurs doivent isoler les pièces adverses.

#### Règles
- Le plateau est composé de 8x8 cases
- À chaque tour, un joueur place une tour sur une case vide
- Une tour ne peut pas être placée sur une case menacée par une tour adverse
- Le joueur qui n'a plus de coup possible perd la partie

### Congress

Congress est un jeu où les joueurs doivent connecter leurs pièces.

#### Règles
- Le plateau est composé de 8x8 cases
- Les pièces se déplacent selon leur type
- Le but est de connecter toutes ses pièces orthogonalement
- Le premier joueur qui connecte toutes ses pièces gagne la partie

## Mode Solo

Pour jouer en solo contre l'ordinateur :

1. Lancez le jeu :
```bash
python src/main.py
```

2. Sélectionnez le jeu souhaité
3. Choisissez le mode "Solo"
4. Jouez votre tour en cliquant sur les cases du plateau

## Sauvegarde et Chargement

- Une partie peut être sauvegardée à tout moment
- Les sauvegardes sont stockées dans le dossier `saves/`
- Pour charger une partie, sélectionnez-la dans le menu principal

## Interface

- Le plateau de jeu est affiché au centre
- Les informations de la partie sont affichées en haut
- Les messages d'état sont affichés en bas
- Les pièces sont représentées par des symboles colorés :
  - Joueur 1 : bleu
  - Joueur 2 : rouge

