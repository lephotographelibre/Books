import epub_meta
import sys


def main():
    try:
        metadata = epub_meta.get_epub_metadata('/ssdhome/jm/PycharmProjects/Books/samples/testidcover.epub',
                                               read_cover_image=True, read_toc=True)
        print_dict(metadata)
    except epub_meta.EPubException as e:
        print(e)

    print('----- Extract Metadata --------------------------------------------')
    print('-- Title  -----' + str(metadata.title))
    print('-- Authors  -----' + str(metadata.authors))
    print('-- epub version  -----' + str(metadata.epub_version))




    # To discover and parse yourself the ePub OPF file, you can get the content of the OPF - XML file:
    #
    print('----- Extract the content of the OPF - XML file --------------------------------------------')
    print(epub_meta.get_epub_opf_xml('/ssdhome/jm/PycharmProjects/Books/samples/testidcover.epub'))


def print_dict(dico):
    print(
        str(dico)
            .replace(', ', '\n')
            .replace(': ', ':\t')
            .replace('{', '')
            .replace('}', '')
    )


if __name__ == "__main__":
    sys.exit(main())
