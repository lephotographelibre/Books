# From https://github.com/jmdigne
#
# Usage
# $ python FaireMaigrirBook input_file.epub output_file.epub --jpeg-quality=25 --log-level=info
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
remove_fonts = remove all the fonts within book args --remove_fonts=yes
easter_eggs = remove all the existing easter egge with the book (file named content, images files with size > 3 MB;..) 
            --remove_eggs=yes
is_an_egg = retrun True if we can identify this file as an egg (increase the logic based on name , size, mimetype, 
            extension 
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_epub_filepath')
    parser.add_argument('out_epub_filepath')
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

    if os.path.isdir(args.out_epub_filepath):
        args.out_epub_filepath = os.path.join(
            args.out_epub_filepath, os.path.basename(args.in_epub_filepath))

    if args.out_epub_filepath == args.in_epub_filepath:
        raise FileExistsError(args.out_epub_filepath)

    # Variables
    _files_number = 0
    _images_number = 0
    # MAIN LOOP - Open epub file as a zip then iterate
    with zipfile.ZipFile(args.in_epub_filepath, 'r') as in_book:
        with zipfile.ZipFile(args.out_epub_filepath, 'w') as out_book:
            for name in in_book.namelist():
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

                        # Write current file into destination if type not None
                        out_book.writestr(name, content)

    logging.info('-- Number of files in the initial file = ' + str(_files_number))
    logging.info('-- Number of images in the initial file = ' + str(_images_number))
    logging.info('-- Initial size = ' + str(os.path.getsize(args.in_epub_filepath)))
    logging.info('-- Final size = ' + str(os.path.getsize(args.out_epub_filepath)))
    ratio = os.path.getsize(args.out_epub_filepath) / os.path.getsize(args.in_epub_filepath) * 100
    logging.info('-- Ratio = ' + str(round(ratio)) + '%')

'''
def is_an_egg(in_book, name, args):
    with in_book.open(name, 'r') as in_file:
        content = in_file.read()
        type_, encoding = mimetypes.guess_type(name)

        if type_:
            type_, subtype = type_.split('/')
            if type_ == 'image':
                # -- Add new check here
                # TODO Check size > 3 MB
                if os.path.getsize(args.in_epub_filepath)  > 3000000:
                    logging.debug('-- Image file size = ' )
            return False
        # No type it's an egg
        else:
            return True
'''


def compress_image(subtype, old_content, args):
    if subtype not in {'jpeg', 'jpg', 'png'}:
        return old_content

    in_buffer = io.BytesIO(old_content)
    img = Image.open(in_buffer)

    if args.image_resize_percent:
        original_size = img.size
        new_size = (int(original_size[0] * args.image_resize_percent),
                    int(original_size[1] * args.image_resize_percent))
        logging.debug('old size: %s', original_size)
        logging.debug('new size: %s', new_size)

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

    logging.debug('old content length: %s', len(old_content))
    logging.debug('new content length: %s', len(new_content))

    return new_content


if __name__ == "__main__":
    sys.exit(main())
