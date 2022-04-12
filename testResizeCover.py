import base64
import os
import io
import os.path
from xml.dom import minidom
import zipfile
import sys
from PIL import Image

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from urllib import unquote
else:
    from urllib.parse import unquote


def main():
    print(' -- cover file name ---- ' + _locate_cover('samples/test3egg.epub'))
    print(' -- End testResizeCover ------------------------------------------------------------------')


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
        # The cover image path is relative to the OPF file
        base_dir = os.path.dirname(opf_filepath)
        # Also, normalize the path (ie opfpath/../cover.jpg -> cover.jpg)
        coverpath = os.path.normpath(os.path.join(base_dir, filepath))
        try:
            content = zf.read(coverpath)
        except KeyError:
            raise EPubException("Cannot read {} from EPub file {}".format(
                coverpath, os.path.basename(zf.filename)))
        content = base64.b64encode(content)

    return content, extension, filepath


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
