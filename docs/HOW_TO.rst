Comment re-downloader tous les zips jahia ?
===========================================

1. On se connecte à la machine : ssh team@qa1-web-wordpress -A

2. On active le virtualenv et on se place dans la racine du projet : vjahia

3. On surpprime tous les zips : rm -rf exports/*.zip

4. On lance un screen: screen -S greg

5. On lance la commande de crawl des sites jahia : python src/jahiap.py crawl 3dcamp --number=645 --output-dir=/mnt/export/build-qa1 --debug --export-path=/mnt/export


Remarques :
-----------

- Le téléchargement des zips doit se faire dans une partition NAS qui est partager entre les environnements qa1 et qa2.
Ce chemin c'est :

/mnt/export

- Le script écrit des informations dans un TRACER dans un répertoire propre à l'environnement qa1 ou qa2 :

/mnt/export/build-qa1

- De plus, le script jahiap fonctionne de la manière suivante : On doit passer le 1er site à parser


6. Le script est lancé, il faut fermer la fenetre.


Si on veut reprendre le screen :
--------------------------------

1. On se connecte à la machine : ssh team@qa1-web-wordpress -A

2. On peut voir la liste des screen : screen -ls

3. On se rattache à son screen : screen -r greg
