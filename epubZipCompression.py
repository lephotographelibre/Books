# From: https://stackoverflow.com/questions/23717101/add-file-to-zip-archive-without-compression
#
# just in case in order to reduce the size of an Epub fille
# - mimetypes MUST NOT BE COMPRESSED ---> compress_type=zipfile.ZIP_STORED
# - others files can be compressed --> compress_type=zipfile.ZIP_DEFLATED
import zipfile, os

def create_archive(path='/path/to/our/epub/directory'):
    '''Create the ZIP archive.  The mimetype must be the first file in the archive
    and it must not be compressed.'''

    epub_name = '%s.epub' % os.path.basename(path)

    # The EPUB must contain the META-INF and mimetype files at the root, so
    # we'll create the archive in the working directory first and move it later
    os.chdir(path)

    # Open a new zipfile for writing
    epub = zipfile.ZipFile(epub_name, 'w')

    # Add the mimetype file first and set it to be uncompressed
    epub.write(MIMETYPE, compress_type=zipfile.ZIP_STORED)

    # For the remaining paths in the EPUB, add all of their files
    # using normal ZIP compression
    for p in os.listdir('.'):
        for f in os.listdir(p):
            epub.write(os.path.join(p, f)), compress_type=zipfile.ZIP_DEFLATED)
    epub.close()
'''

