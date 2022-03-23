import os
import ebooklib
from ebooklib import epub
from ebooklib.utils import debug
from PIL import Image

# Read the epub filename as command line argument
# book = epub.read_epub(sys.argv[1])

# Open test.epub
book = epub.read_epub('test_copy.epub')

#debug(book.metadata)
#debug(book.spine)
#debug(book.toc)
debug(book.title)

print ('*** Titre du Livre : ' + book.title)


# get  nombre d'images dans le fichiers epub (de type ebooklib.ITEM_IMAGE)
nb_images = 0
for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    nb_images = nb_images + 1

print('nb_images ===>' + str(nb_images))


# pour chaque item de type ITEM_IMAGE - extraite les données et créer un fichier correspondant
for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
#    print(x.id)
#    print(x.file_name)
#   extraction du nom de fichier image contenu dans le epub
    file_path = os.path.splitext(x.file_name)[0]
    file_name = file_path.split('/')[-1]
    print(x.media_type)
    extension1 = os.path.splitext(x.media_type)[0]
    extension = extension1.split('/')[-1]
    print(' ****** Nom du fichier à créer = ' + file_name+'.' +extension)
#   creation fichier binaire image  à partir du champ x.content
    f = open(file_name+'.' + extension, 'wb')
    f.write(x.content)
    f.close()
#   extraction de la taille du fichier image contenu dans le epub
    im = Image.open(file_name+'.' +extension, 'r')
    print('*** Taille image ' + file_name+'.' +extension +' = ' + str(im.size))
    im.close()
    debug(x)

for x in book.get_items_of_type(ebooklib.ITEM_COVER):
    debug(x)


# for x in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
#    debug(x)



