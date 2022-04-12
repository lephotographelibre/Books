from PIL import Image
import sys


def main():
    img = Image.open("plage.jpg")
    print(img.format, img.size, img.mode)

    img2 = resize_image(img, 800)

    img2.save('newcoverx800px.jpg', 'JPEG')
    print(img2.format, img2.size, img2.mode)
    img2.show()


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


if __name__ == "__main__":
    sys.exit(main())
