Comment re-downloader tous les zips jahia ?
===========================================

1. On se connecte à la machine : ssh team@qa1-web-wordpress -A

2. On active le virtualenv et on se place dans la racine du projet : vjahia

3. On supprime tous les zips : rm -rf exports/*.zip

4. On lance un screen: screen -S greg

5. On lance la commande de crawl des sites jahia : python src/jahiap.py crawl 3dcamp --number=645 --output-dir=/mnt/export/build-qa1 --debug --export-path=/mnt/export


Remarques :
-----------

- Le téléchargement des zips doit se faire dans la partition NAS qui est partagée entre tous les environnements qa1, qa2, etc.

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


Comment regénérer X sites wordpress ?
=====================================

Reconstruire le tout :

0. Faire un "git pull" des 2 repos avec les sources
cd /home/team/git-repos/jahiap/
git pull
cd /home/team/git-repos/template-web-wordpress
git pull
git submodule update


1. Lancer un rebuild pour clean la totalité des containers et recréer les helpers
cd /home/team/git-repos/wp-utils/
./rebuild.sh

Note: si le script bloque, c'est peut-être parce que le service docker est un poil aux fraises. Dans ce cas-là, il faut le restart avec :
sudo service docker restart


2. Faire un CTRL-C à la fin du script quand il affiche "Apache FOREGROUND" ou un truc du style


3. Effacer le contenu du dossier "build" qui va être utilisé
cd /home/team/git-repos/jahiap/build/
rm -rf *


4. Lancer l'environnement virtuel (pas trop loin sinon faut marcher pour aller le chercher)
vjahia


5. Exécuter la ligne de commande suivante en adaptant les paramètres si besoin (fichier CSV, nombre de process)
python src/jahiap.py generate csv-data/10-sites.csv --processes=4
