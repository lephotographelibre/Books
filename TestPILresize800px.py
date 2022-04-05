from PIL import Image

img = Image.open("/ssdhome/jm/PycharmProjects/Books/plage.jpg")
print(img.format, img.size, img.mode)
basewidth = 800

wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth, hsize), Image.ANTIALIAS)
img.save('newcoverx800px.jpg')
print(img.format, img.size, img.mode)
img.show()
