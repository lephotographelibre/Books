from PIL import Image
import sys


def main():
    img = Image.open("plage.jpg")
    print(img.format, img.size, img.mode)
    img.save('newcoverx800px.jpg')

    img = resize_image(img,800)
    print(img.format, img.size, img.mode)
    img.show()


'''This script will resize an image (somepic.jpg) using PIL (Python Imaging Library) to a width of 300 pixels and a 
height proportional to the new width. It does this by determining what percentage 300 pixels is of the original width 
(img.size[0]) and then multiplying the original height (img.size[1]) by that percentage. 
Change "basewidth" to any other number to change the default width of your images.
'''


def resize_image(img_input, basewidth):
    wpercent = (basewidth / float(img_input.size[0]))
    hsize = int((float(img_input.size[1]) * float(wpercent)))
    img = img_input.resize((basewidth, hsize), Image.ANTIALIAS)
    return img


if __name__ == "__main__":
    sys.exit(main())