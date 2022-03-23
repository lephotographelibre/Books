import os
from os import listdir
from os.path import isfile, join


# 1 - récupérer le chemin du répertoire courant
path = os.getcwd()
print("Le répertoire courant est : " + path)

# 2 - récupérer le chemin du script
path = os.path.realpath(__file__)
print("Le chemin du script est : " + path)

# 3 - Parcourir un répertoire
print("*** Afficher les fichiers dans le répertoire " + os.getcwd())
for filename in os.listdir(os.getcwd()):
       print("...." + filename)

# 4 - Afficher uniquement les fichiers du répertoire
dirPath = r"/home/jm"
result = [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]
print("*** Afficher uniquement les fichiers du répertoire ...." + dirPath)
print(result)

# 5 - Parcourir une arborescence
# Walking a directory tree and printing the names of the directories and files
print("*** Afficher Arbre /ssd/Work")
# for dirpath, dirnames, files in os.walk('.'):
for dirpath, dirnames, files in os.walk('/ssd/Work'):
    print('---  Found directory: {'+dirpath+'}')
    for file_name in files:
        print(file_name)

