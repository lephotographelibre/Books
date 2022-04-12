import ebooklib
import os
from ebooklib import epub
from ebooklib.utils import debug
import zipfile
from lxml import etree
from PIL import Image

# Many ways to explore to detect what's the cover image
# - cover.page -- cover image will always be the first page to be displayed. So get the content of cover image from epub and try to display it
# - Only one image
# - properties properties="cover-image"
# - item id cover
# - <guide> --> cover page --> cover image


## See also docs at http://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#reading-epub
'''
if len(sys.argv) < 2:
    print("Usage: " + sys.argv[0] + " filename.epub")
    exit()

epubfile = sys.argv[1]
if not os.path.isfile(epubfile):
    print("File not found: " + epubfile)
    exit()
'''
epubfile = 'samples/test.epub'

# Let's define the required XML namespaces
namespaces = {
    "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "opf": "http://www.idpf.org/2007/opf",
    "u": "urn:oasis:names:tc:opendocument:xmlns:container",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def get_epub_cover(epub_path):
    ''' Return the cover image file from an epub archive. '''

    # We open the epub archive using zipfile.ZipFile():
    with zipfile.ZipFile(epub_path) as z:
        # We load "META-INF/container.xml" using lxml.etree.fromString():
        t = etree.fromstring(z.read("META-INF/container.xml"))
        # We use xpath() to find the attribute "full-path":
        '''
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="OEBPS/content.opf" ... />
          </rootfiles>
        </container>
        '''
        rootfile_path = t.xpath("/u:container/u:rootfiles/u:rootfile",
                                namespaces=namespaces)[0].get("full-path")
        print("Path of root file found: " + rootfile_path)

        # We load the "root" file, indicated by the "full_path" attribute of "META-INF/container.xml",
        # using lxml.etree.fromString():
        t = etree.fromstring(z.read(rootfile_path))
        # We use xpath() to find the attribute "content":
        '''
        <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
          ...
          <meta content="my-cover-image" name="cover"/>
          ...
        </metadata>
        '''
        cover_id = t.xpath("//opf:metadata/opf:meta[@name='cover']",
                           namespaces=namespaces)[0].get("content")
        print("ID of cover image found: " + cover_id)

        # We use xpath() to find the attribute "href":
        '''
        <manifest>
            ...
            <item id="my-cover-image" href="images/978.jpg" ... />
            ... 
        </manifest>
        '''
        cover_href = t.xpath("//opf:manifest/opf:item[@id='" + cover_id + "']",
                             namespaces=namespaces)[0].get("href")
        a = os.path.dirname(rootfile_path)
        # In order to get the full path for the cover image, we have to join rootfile_path and cover_href:
        cover_path = os.path.join(os.path.dirname(rootfile_path), cover_href)
        print("Path of cover image found: " + cover_path)

        # We return the image
        return z.open(cover_path)


# get cover from Zipping epub file and parsing content.opf in search of name="cover"
cover2 = Image.open(get_epub_cover(epubfile))


#
#  Creates new instance of EpubBook with the content defined in the input file.
book = epub.read_epub(epubfile)

# ====== Are there cover declaration as meta  =====================
# extract metadata  <meta name="cover" content="image.jpeg" /> within content.opf

# debug(book.metadata)

# -- A method to get OPF ou DC Dublin Core metadata (namespace (OPF or DC))
# from Ebooklib docs at http://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#reading-epub
print('*** OPF Metadata cover = ' + str(book.get_metadata('OPF', 'cover')))
cover = book.get_metadata('OPF', 'cover')
# cover est une liste de tuples qui sont des dictionaires (None, {'name': 'cover', 'content': 'image.jpeg'})
print('**** tag cover within opt = ' + str(cover[0]))
print(cover[0][0])
print(cover[0][1])
print("The original dictionary : " + str(cover[0][1]))
key, val = cover[0][1].items()
cover_name = val[1]

# ====== List of Images within the epub fils =====================
booksItems = book.get_items()
for x1 in booksItems:
    print(x1.file_name)

# ====== Are there image files within the ebook =====================
# get  nombre d'images dans le fichiers epub (de type ebooklib.ITEM_IMAGE)
nb_images = 0
for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
    nb_images = nb_images + 1
    print(' *** image file = ' + x.file_name)

if nb_images > 0:
    print('** Image files number ===>' + str(nb_images))
else:
    print('!! Pas d\'images trouvées')

# --  another possible method to detect cover file using cover-image propertie with manifest
# if manifest contains an item with properties="cover-image
# # <item id="image.jpeg" href="Images/image.jpeg" media-type="image/jpeg" properties="cover-image"/>
for x2 in book.get_items_of_type(ebooklib.ITEM_COVER):
    print(' *** cover-image file = ' + x2.file_name)

# Another way to do the same thing
# From EBooklib docs http://docs.sourcefabric.org/projects/ebooklib/en/latest/tutorial.html#items
for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_COVER:
        print('==================================')
        print('NAME : ', item.get_name())
        print('----------------------------------')
        print(item.get_content())
        print('==================================')

# get the cover by id -- <item id="cover".... can be anything
cover_image = book.get_item_with_id('cover')
print('==================================')
print('NAME : ', cover_image.get_name())
print('----------------------------------')
print(cover_image.get_content())
print('==================================')

# list Item by item.id or
for item in book.get_items():
    print('============Item id = ' + item.id)
    print('============Item.media_type = ' + item.media_type)

# identify cover using XML parsing of the epub.fil as a Zipfile
# Let's define the required XML namespaces
namespaces = {
    "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "opf": "http://www.idpf.org/2007/opf",
    "u": "urn:oasis:names:tc:opendocument:xmlns:container",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# remove cover within epub

# swap cover with new image
