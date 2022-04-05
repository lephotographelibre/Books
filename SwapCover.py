#!/usr/bin/env python3
# Author: Jean-Marc Digne - https://github.com/jmdigne
'''
**** SwapCover ****
Usage: /ssdhome/jm/PycharmProjects/Books/SwapCover.py in.epub out.epub --log-level=info

Run/Debug as
/ssdhome/jm/PycharmProjects/Books/SwapCover.py /ssdhome/jm/PycharmProjects/Books/test.epub /ssdhome/jm/PycharmProjects/Books/target.epub

Logic to find the cover within an EPUB FILE
- method 1 - aka Dublin Core defined field or EPUB 2 Markup style
    content.opf XML Parsing to find <meta ... name="cover"...>
- method 2 - EPUB 3 Markup style
    using Ebooklib search a manifest item with properties="cover-image" ie. item as ebooklib.ITEM_COVER
    such as <item id="image.jpeg" href="Images/image.jpeg" media-type="image/jpeg" properties="cover-image"/>
-TODO   <manifest>
    <item id="cover" href="Images/cover.jpeg" media-type="image/jpeg"/>

'''

# Imports
from os.path import splitext

import ebooklib
import os
import sys
from ebooklib import epub
from ebooklib.utils import debug
import zipfile
from lxml import etree
from PIL import Image
import sys
import logging
import argparse
import mimetypes
from datetime import datetime
from time import gmtime, strftime

'''

'''

# Variables

# Let's define the required XML namespaces
namespaces = {
    "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "opf": "http://www.idpf.org/2007/opf",
    "u": "urn:oasis:names:tc:opendocument:xmlns:container",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def swap_cover(epubfile_source, epubfile_target, new_cover):
    logging.info('**** SwapCover ****')
    cover_before = None
    cover_after = new_cover

    # Get epub filename
    epubfile_source = args.in_epub_filepath
    date = datetime.today().strftime('_%H_%M_%S')
    epubfile_target = args.out_epub_filepath

    # Is there at least 1 image file within this epub file
    if get_image_number(epubfile_source) < 1:
        print('**** SwapCover **** No cover in this epub file -- nothing to swap')
        exit()

    # Extracting existing cover (Methode 1)
    try:
        cover_before = get_cover_methode_1(epubfile_source)
    except BaseException as err:
        logging.debug('* get_cover_methode_1 -- cover not found')
        # print(f"Unexpected {err=}, {type(err)=}")
        # raise

    if cover_before is None:
        logging.debug('**** continuer extraction cover')
        # Extracting existing cover (Methode 2)
        try:
            cover_before = Image.open(get_cover_methode_2(epubfile_source))
        except BaseException as err:
            logging.debug('* get_cover_methode_2 -- cover not found')
            # print(f"Unexpected {err=}, {type(err)=}")
            # raise

    if cover_before is None:
        logging.info('**** No cover found, Sorry !')
        exit()

    # A cover has been found
    logging.debug('**** Cover Image is : ' + cover_before)

    # Browse source epub
    with zipfile.ZipFile(args.in_epub_filepath, 'r') as in_book:
        with zipfile.ZipFile(args.out_epub_filepath, 'w') as out_book:
            for name in in_book.namelist():
                with in_book.open(name, 'r') as in_file:
                    content = in_file.read()
                    # identify cover file within the epub as zip container
                    if name == cover_before:
                        logging.debug(' filename = ' + name)
                        with in_book.open(name, 'r') as in_file:
                            content = in_file.read()
                            # Guess the MIME type of a file.
                            mimetype_, encoding = mimetypes.guess_type(name)

                            if mimetype_:
                                type_, subtype = mimetype_.split('/')
                                logging.debug(' old cover type = ' + type_)
                                logging.debug(' old cover subtype = ' + subtype)

                            # Open new cover and identify mime type and check if a conversion is needed
                            mimetypenew_, encodingnew = mimetypes.guess_type(new_cover)
                            if mimetypenew_:
                                typenew_, subtypenew = mimetypenew_.split('/')
                                logging.debug(' new cover type = ' + typenew_)
                                logging.debug(' new cover subtype = ' + subtypenew)

                            if mimetype_ == mimetypenew_:
                                logging.debug(
                                    ' Image cover subtype  match --> existing = ' + mimetype_ + ' new = ' + mimetypenew_)
                                logging.debug(' So no conversion is needed !')

                                # Replace the old content readed from existing cover by the newcover
                                # TODO with new_cover.open(name, 'r') as new_cover_file:
                                # TODO content = new_cover_file.read()

                            # if mimetype btw existing cover and new cover doesn't match --> convertion is need to
                            # the old mimetype
                            if mimetype_ != mimetypenew_:
                                logging.debug(
                                    ' Image cover subtypenew does not match  old = ' + mimetype_ + ' new = ' + mimetypenew_)
                                logging.debug(
                                    ' --> convertion iof the new cover is needed to the old mimetype  -> ' + mimetype_)

                                # Open new cover / convert to the initial mimetype /
                                filename, extension = splitext(new_cover)
                                try:
                                    im = Image.open(filename + extension)
                                    output_filemane = filename + '.' + subtype
                                    # Save the new cover file with the correct extension
                                    im.save(filename + '.' + subtype)
                                except OSError:
                                    print('Cannot convert %s' % file)

                                # Verify Image
                                im.show()

                                # Replace the old content readed from existing cover by the new converted content
                                # TODO with output_filemane.open(name, 'r') as new_cover_file:
                                # TODO content = new_cover_file.read()

                    # Write file as result  into target epub
                    out_book.writestr(name, content)


# TODO
# open an nested loop for out book        with zipfile.ZipFile(args.out_epub_filepath, 'w') as out_book:
# convert image if needed
# insert the new image into the epub out

# ======== End of Main ==============================================================

def get_image_number(epub_path):
    ''' Return the number of image files from an epub archive. '''

    image_number = 0
    # We open the epub archive using Ebooklib
    # Open book with Ebooklib
    book = epub.read_epub(epub_path)

    for x in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        image_number = image_number + 1
    logging.info('* get_image_number - number of images found = ' + str(image_number))
    return image_number


def get_cover_methode_1(epub_path):
    ''' Return the cover image file path from an epub archive. '''

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
        # print("Path of root file found: " + rootfile_path)

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
        # print("ID of cover image found: " + cover_id)

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
        # In order to get the full path for the cover image, we have to join rootfile_path and cover_href:
        cover_path = os.path.join(os.path.dirname(rootfile_path), cover_href)

        logging.info('* get_cover_methode_1 - cover found = ' + cover_path)
        # We return the image
        # z.open(cover_path)
        # We return the cover path within zip
        return cover_path


def get_cover_methode_2(epub_path):
    cover = None
    # We open the epub archive using Ebooklib
    book = epub.read_epub(epub_path)

    # if manifest contains an item with properties="cover-image"
    # # <item id="image.jpeg" href="Images/image.jpeg" media-type="image/jpeg" properties="cover-image"/>
    for x2 in book.get_items_of_type(ebooklib.ITEM_COVER):
        cover = x2
        print('* get_cover_methode_2 - cover found = ' + x2.file_name)

    # We return the image
    return cover


# main ==========================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    parser.add_argument('out_epub_filepath')
    parser.add_argument('new_cover_filepath')
    parser.add_argument('-l', '--log-level')

    args = parser.parse_args()

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if type(log_level_num) is not int:
            raise ValueError('Invalid log level: {}'.format(args.log_level))

        logging.basicConfig(level=log_level_num)

    if not os.path.isfile(args.in_epub_filepath):
        raise FileNotFoundError(args.in_epub_filepath)

    if os.path.isdir(args.out_epub_filepath):
        args.out_epub_filepath = os.path.join(
            args.out_epub_filepath, os.path.basename(args.in_epub_filepath))

    if args.out_epub_filepath == args.in_epub_filepath:
        raise FileExistsError(args.out_epub_filepath)

    if not os.path.isfile(args.new_cover_filepath):
        raise FileNotFoundError(args.new_cover_filepath)

    sys.exit(swap_cover(args.in_epub_filepath, args.out_epub_filepath, args.new_cover_filepath))
