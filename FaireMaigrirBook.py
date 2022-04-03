# From https://github.com/jmdigne
#
# Usage
# $ python FaireMaigrirBook /ssdhome/jm/PycharmProjects/Books/test_avec_eggs.epub --jpeg-quality=25 --log-level=info
#
# TODO
# add --fonts:
# how to detect an egg ? size > 4 MB, mimetype without extension ? name content ? no reference within opf file
#
import argparse
import logging
import sys
import os
import mimetypes
import zipfile
import io
from PIL import Image

'''
compress_image = compress  images jpeg defined by  args --jpeg-quality=25
is_a_font = test if it's a font file
is_an_egg = remove all the existing easter egge with the book (file named content, images files with size > 3 MB;..)           
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    # parser.add_argument('out_epub_filepath')
    parser.add_argument('-l', '--log-level')
    parser.add_argument('--jpeg-quality', type=int, default=75)
    parser.add_argument('--image-resize-percent', type=int)

    args = parser.parse_args()

    if args.log_level:
        log_level_num = getattr(logging, args.log_level.upper(), None)
        if type(log_level_num) is not int:
            raise ValueError('Invalid log level: {}'.format(args.log_level))
        # print('-- Log Level Num = ' + str(log_level_num))
        logging.basicConfig(level=log_level_num)

    if not os.path.isfile(args.in_epub_filepath):
        raise FileNotFoundError(args.in_epub_filepath)
    # Get the filename from input file abd define output filename adding _light.epub at the end
    logging.info('-- Input filename = ' + args.in_epub_filepath)
    args.out_epub_filepath = args.in_epub_filepath.split('.')[0]+'_light.epub'
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
                            content = compress_image(subtype, content, args)
                    # modify content if it's an egg
                    else:
                        content = is_an_egg(name, content, args)

                    # Write current file into destination if not a font file
                    if not is_a_font_file(name):
                        out_book.writestr(name, content)
                    else:
                        _font_number = _font_number + 1

    logging.info('-- Number of files in the initial file = ' + str(_files_number))
    logging.info('-- Number of images in the initial file = ' + str(_images_number))
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
    img = Image.open(in_buffer)

    if args.image_resize_percent:
        original_size = img.size
        new_size = (int(original_size[0] * args.image_resize_percent),
                    int(original_size[1] * args.image_resize_percent))
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


if __name__ == "__main__":
    sys.exit(main())
