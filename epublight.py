# From https://github.com/jmdigne
#
# Usage
# $ python epub_light.py  test.epub --jpeg-quality=25 --log-level=info
#
# - remove eggs from epub files (image bomb + bullshit content added to increase the file size))
# - reduce images quality (jpg and png) parameter --jpeg_quality
# - resize cover (basewidth = 800px)
# - compute compression ratio
#
# code to locate/identify the cover is from https://github.com/paulocheque/epub-meta
# code to compress images is from https://github.com/murrple-1/epub-shrink

import argparse
import base64
import io
import logging
import mimetypes
import os
import os.path
import sys
import zipfile
from xml.dom import minidom

from PIL import Image

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from urllib import unquote
else:
    from urllib.parse import unquote


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    # parser.add_argument('out_epub_filepath')
    parser.add_argument('-l', '--log-level')
    parser.add_argument('--jpeg-quality', type=int, default=50)
    parser.add_argument('--image-resize-percent', type=int)
    parser.add_argument('--image-resize-resample')
    args = parser.parse_args()

    print('-- epublight args --', str(args))

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if type(log_level_num) is not int:
            raise ValueError('Invalid log level: {}'.format(args.log_level))
        # print('-- Log Level Num = ' + str(log_level_num))
        logging.basicConfig(level=log_level_num)
    else:
        # default is INFO if missing from command line
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.isfile(args.in_epub_filepath):
        raise FileNotFoundError(args.in_epub_filepath)
    # Get the filename from input file abd define output filename adding _light.epub at the end
    logging.info('-- Input filename = ' + args.in_epub_filepath)
    args.out_epub_filepath = args.in_epub_filepath.split('.')[0] + '_light.epub'
    logging.info('-- Output filename = ' + args.out_epub_filepath)

    if os.path.isdir(args.out_epub_filepath):
        args.out_epub_filepath = os.path.join(
            args.out_epub_filepath, os.path.basename(args.in_epub_filepath))

    if args.out_epub_filepath == args.in_epub_filepath:
        raise FileExistsError(args.out_epub_filepath)

    # Variables
    _files_number = 0
    _images_number = 0
    _font_number = 0
    is_cover = False

    # MAIN LOOP - Open epub file as a zip then iterate
    with zipfile.ZipFile(args.in_epub_filepath, 'r') as in_book:
        with zipfile.ZipFile(args.out_epub_filepath, 'w') as out_book:
            for name in in_book.namelist():
                logging.debug('-- file name -- ' + name)
                _files_number = _files_number + 1
                with in_book.open(name, 'r') as in_file:
                    content = in_file.read()
                    type_, encoding = mimetypes.guess_type(name)

                    if type_:
                        type_, subtype = type_.split('/')

                        # Compress jpeg image
                        if type_ == 'image':
                            _images_number = _images_number + 1
                            # cover detection
                            if name == _locate_cover(args.in_epub_filepath) and is_cover == False:
                                is_cover = True
                                logging.debug(
                                    '-- cover found --------------' + name + ' ... isCover = ' + str(is_cover))
                                # cover is resize to basewidth = 800 px
                                content = resize_cover(subtype, content, args, 800)
                            else:
                                # Not a cover
                                content = compress_image(subtype, content, args)
                    # modify content if it's an egg
                    else:
                        content = is_an_egg(name, content, args)

                    # Write current file into destination if not a font file
                    if not is_a_font_file(name):
                        if name == 'mimetype':
                            # Add the mimetype file first and set it to be uncompressed
                            out_book.writestr(name, content)
                        else:
                            # Compress content except for mimetype
                            out_book.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)
                    else:
                        _font_number = _font_number + 1

    in_book.close()
    out_book.close()

    # Display Stats
    logging.info('-- Number of files in the initial file = ' + str(_files_number))
    logging.info('-- Number of images in the initial file = ' + str(_images_number))
    logging.info('-- JPEG Quality % = ' + str(args.jpeg_quality))
    if _font_number > 0:
        logging.info('-- Number of font files removed =  = ' + str(_font_number))
    logging.info('-- Initial size = ' + str(os.path.getsize(args.in_epub_filepath)))
    logging.info('-- Final size = ' + str(os.path.getsize(args.out_epub_filepath)))

    ratio = os.path.getsize(args.out_epub_filepath) / os.path.getsize(args.in_epub_filepath) * 100
    logging.info('-- Compression Ratio = ' + str(100 - round(ratio)) + '%')


def is_an_egg(name, old_content, args):
    # TODO To Be improved
    if name == 'mimetype':
        return old_content

    (head, tail) = os.path.split(name)
    if tail == 'toc.ncx':
        return old_content
    else:
        if len(old_content) == 0:
            # github Issue 1: don't remove empty directories  (content size=0)
            logging.debug('!!! NOT AN EGG -- DIRECTORY -----> Name = ' + name + ' Size = ' + str(len(old_content)))
            return old_content
        else:
            # Egg detected
            logging.info('!!! EGG REMOVED  -----> Name = ' + name + ' Size = ' + str(len(old_content)))
            # modify content with a dummy binary object
            new_content = b"Bytes objects are immutable sequences of single bytes"
            return new_content


def is_a_font_file(name):
    (head, tail) = os.path.split(name)
    ext = name.split('.')[-1]
    # logging.info('!!! is_a_font_file -----> Name = ' + name + ' extension = ' + ext)
    if ext == 'ttf':
        # logging.info('!!! FONTS DETECTED  -----> Name = ' + name + ' extension = ' + ext)
        return True
    else:
        return False


def compress_image(subtype, old_content, args):
    logging.debug('-- compress_image -- ' + subtype)
    if subtype not in {'jpeg', 'jpg', 'png'}:
        return old_content

    in_buffer = io.BytesIO(old_content)
    try:
        img = Image.open(in_buffer)
    except:
        # Decompression bomb protection see https://github.com/python-pillow/Pillow/issues/515
        print("!!! WARNING !!!! Egg ---> DecompressionBombError")
        new_content = b"Bytes objects are immutable sequences of single bytes"
        return new_content

    if args.image_resize_percent:
        original_size = img.size
        new_size = (int(original_size[0] * args.image_resize_percent / 100),
                    int(original_size[1] * args.image_resize_percent / 100))
        logging.debug('-- image_resize_percent -- old size: %s', original_size)
        logging.debug('-- image_resize_percent -- new size: %s', new_size)

        resample = None
        if args.image_resize_resample:
            resample_attr = args.image_resize_resample.upper()
            if not hasattr(Image, resample_attr):
                raise ValueError('unknown resample mode: {}'.format(
                    args.image_resize_resample))

            resample = getattr(Image, resample_attr)

        img = img.resize(new_size, resample)

    format_ = None
    params = {}
    if subtype == 'jpeg' or subtype == 'jpg':
        format_ = 'JPEG'
        params['quality'] = args.jpeg_quality
        params['optimize'] = True
    elif subtype == 'png':
        format_ = 'PNG'
        params['optimize'] = True

    out_buffer = io.BytesIO()
    img.save(out_buffer, format_, **params)

    new_content = out_buffer.getvalue()

    logging.debug('-- compress_image -- old content length: %s', len(old_content))
    logging.debug('-- compress_image -- new content length: %s', len(new_content))

    return new_content


def resize_cover(subtype, old_content, args, base_width):
    logging.info('-- Resize_cover to basewidth = 800px --')
    if subtype not in {'jpeg', 'jpg', 'png'}:
        return old_content

    in_buffer = io.BytesIO(old_content)
    try:
        img = Image.open(in_buffer)
    except:
        # Decompression bomb protection see https://github.com/python-pillow/Pillow/issues/515
        print("!!! WARNING !!!! Egg ---> DecompressionBombError")
        new_content = b"Bytes objects are immutable sequences of single bytes"
        return new_content

    original_size = img.size
    wpercent = (base_width / float(img.size[0]))
    logging.debug('-- cover wpercent = ' + str(float(wpercent)))
    hsize = int((float(img.size[1]) * float(wpercent)))
    new_size = (800, hsize)

    logging.debug('-- cover old size: %s', original_size)
    logging.debug('-- cover new size: %s', new_size)

    if float(wpercent) > 1.0:
        # do not Resize
        logging.debug('-- cover old size: < 800px -- Skip resize')
        return old_content
    else:
        # Resize
        img = img.resize((base_width, hsize), Image.LANCZOS)

    format_ = None
    params = {}
    if subtype == 'jpeg' or subtype == 'jpg':
        format_ = 'JPEG'
        params['quality'] = args.jpeg_quality
        params['optimize'] = True
    elif subtype == 'png':
        format_ = 'PNG'
        params['optimize'] = True

    out_buffer = io.BytesIO()
    img.save(out_buffer, format_, **params)

    new_content = out_buffer.getvalue()

    logging.debug('-- resize_cover -- old content length: %s', len(old_content))
    logging.debug('-- resize_cover -- new content length: %s', len(new_content))

    return new_content


class EPubException(Exception):
    pass


def _locate_cover(epub_filepath):
    '''
    References: http://idpf.org/epub/201 and http://idpf.org/epub/301
    1. Parse META-INF/container.xml file and find the .OPF file path.
    2. In the .OPF file, find the metadata
    return cover_image_filepath
    '''
    if not zipfile.is_zipfile(epub_filepath):
        raise EPubException('Unknown file')

    try:
        # print('Reading ePub file: {}'.format(filepath))
        zf = zipfile.ZipFile(epub_filepath, 'r', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
        container = zf.read('META-INF/container.xml')
        container_xmldoc = minidom.parseString(container)
        # e.g.: <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
        opf_filepath = container_xmldoc.getElementsByTagName('rootfile')[0].attributes['full-path'].value

        opf = zf.read(os.path.normpath(opf_filepath))
        opf_xmldoc = minidom.parseString(opf)
    except IndexError:
        raise EPubException("Cannot parse raw metadata from {}".format(
            os.path.basename(epub_filepath)))

    cover_image_content, cover_image_extension, cover_image_filepath = _discover_cover_image(zf, opf_xmldoc,
                                                                                             opf_filepath)

    logging.debug(' -- locate cover - file path = ' + cover_image_filepath)
    return cover_image_filepath

    # print("-- cover_image_content = " + str(cover_image_content))
    # print("-- cover_image_extension = " + cover_image_extension)
    # print("-- cover_image__filepath = " + cover_image_filepath)

    # in_buffer = io.BytesIO(cover_image_content)
    # img = Image.open(in_buffer)


def resize_image(img_input, basewidth):
    """
    This script will resize an image (some-pic.jpg) using PIL to a width   and a height proportional to the new width
    Param: img_input IMAGE, basewidth int
    Return: IMAGE
    """
    wpercent = (basewidth / float(img_input.size[0]))
    hsize = int((float(img_input.size[1]) * float(wpercent)))
    img = img_input.resize((basewidth, hsize), Image.LANCZOS)
    return img


def _discover_cover_image(zf, opf_xmldoc, opf_filepath):
    '''
    Find the cover image path in the OPF file.
    Returns a tuple: (image content in base64, file extension)
    '''
    content = None
    filepath = None
    extension = None

    # Strategies to discover the cover-image path:

    # e.g.: <meta name="cover" content="cover"/>
    tag = find_tag(opf_xmldoc, 'meta', 'name', 'cover')
    if tag and 'content' in tag.attributes.keys():
        item_id = tag.attributes['content'].value
        if item_id:
            # e.g.: <item href="cover.jpg" id="cover" media-type="image/jpeg"/>
            filepath, extension = find_img_tag(opf_xmldoc, 'item', 'id', item_id)
    if not filepath:
        filepath, extension = find_img_tag(opf_xmldoc, 'item', 'id', 'cover-image')
    if not filepath:
        filepath, extension = find_img_tag(opf_xmldoc, 'item', 'id', 'cover')

    # If we have found the cover image path:
    if filepath:
        logging.debug('-- _discover_cover_image file path before normalization = ' + filepath)
        # The cover image path is relative to the OPF file
        base_dir = os.path.dirname(opf_filepath)
        # Also, normalize the path (ie opfpath/../cover.jpg -> cover.jpg)
        coverpath = os.path.normpath(os.path.join(base_dir, filepath))
        logging.debug('-- _discover_cover_image file path after normalization = ' + coverpath)
        try:
            content = zf.read(coverpath)
        except KeyError:
            raise EPubException("Cannot read {} from EPub file {}".format(
                coverpath, os.path.basename(zf.filename)))
        content = base64.b64encode(content)

    # return content, extension, filepath
    # Change to correct issue #3 (cover path doesn't match)
    return content, extension, coverpath


def find_img_tag(xmldoc, tag_name, attr, value):
    # print('Finding img tag: <{} {}="{}">'.format(tag_name, attr, value))
    for tag in xmldoc.getElementsByTagName(tag_name):
        if attr in tag.attributes.keys() and tag.attributes[attr].value == value:
            if 'href' in tag.attributes.keys():
                filepath = unquote(tag.attributes['href'].value)
                filename, file_extension = os.path.splitext(filepath)
                if file_extension in ('.gif', '.jpg', '.jpeg', '.png', '.svg'):
                    return filepath, file_extension
    return None, None


def find_tag(xmldoc, tag_name, attr, value):
    # print('Finding tag: <{} {}="{}">'.format(tag_name, attr, value))
    for tag in xmldoc.getElementsByTagName(tag_name):
        if attr in tag.attributes.keys() and tag.attributes[attr].value == value:
            return tag


if __name__ == "__main__":
    sys.exit(main())
