import zipfile
import datetime
import pathlib


# List all the content of the Zip file
with zipfile.ZipFile("test.zip", mode="r") as archive:
    archive.printdir()


# List all the content of the Zip file with exception management

try:
    with zipfile.ZipFile("test.epub") as archive:
        print(' -- List all the file : ')
        archive.printdir()
        print(' -- end --')
except zipfile.BadZipFile as error:
    print(error)

# If the target ZIP file doesn’t exist, then ZipFile creates it for you when you close the archive:
with zipfile.ZipFile("hello.zip", mode="w") as archive:
    archive.write("hello.txt")
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    archive.printdir()
# Append a new file test2.epub to the zip
with zipfile.ZipFile("hello.zip", mode="a") as archive:
    archive.write("test2.epub")
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    archive.printdir()

# Reading Metadata From ZIP Files
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    info = archive.getinfo("hello.txt")
    print('-- Metadata hello.txt size = ' + str(info.file_size) + ' .....  compress_size = ' + str(info.compress_size))

# Reading Metadata using infolist()
print('-- Metadata hello.zip ......................')
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    for info in archive.infolist():
        print(f"Filename: {info.filename}")
        print(f"Modified: {datetime.datetime(*info.date_time)}")
        print(f"Normal size: {info.file_size} bytes")
        print(f"Compressed size: {info.compress_size} bytes")
        print("-" * 20)

# Loop and print filename
print('-- Metadata print filename ......................')
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    for filename in archive.namelist():
        print(filename)


# Read the content of hello.txt as bytes. Then you call .decode() to decode the bytes into a string using UTF-8 as
# encoding.
print('-- Read the content of hello.txt as bytes......................')
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    text = archive.read("hello.txt").decode(encoding="utf-8")
    print(text)

# Extracting Member Files From Your ZIP Archives
print('-- Extracting Member Files  hello.txt to output_dir......................')
with zipfile.ZipFile("hello.zip", mode="r") as archive:
    archive.extract("hello.txt", path="output_dir/")
    # Closing ZIP Files After Use - if you open a ZIP file for appending ("a") new member files,
    # then you need to close the archive to write the files.
    archive.close()

# Creating a ZIP File From Multiple Regular Files
filenames = ["hello.txt", "test.zip", "plage.jpg"]
with zipfile.ZipFile("multiple_files.zip", mode="w") as archive:
    for filename in filenames:
        archive.write(filename)
    archive.close()
# List all the content of the multiple_files.zip file
with zipfile.ZipFile("multiple_files.zip", mode="r") as archive:
    archive.printdir()

# Building a ZIP File From the bin Directory
print('-- Building a ZIP File From the bin Directory......................')
directory = pathlib.Path("bin/")
with zipfile.ZipFile("directory.zip", mode="w") as archive:
    # If you don’t pass file_path.name to arcname, then your source directory will be at the root of your ZIP file,
    # which can also be a valid result depending on your needs.
    for file_path in directory.iterdir():
        archive.write(file_path, arcname=file_path.name)
with zipfile.ZipFile("directory.zip", mode="r") as archive:
    archive.printdir()

# Extracting Files and Directories
with zipfile.ZipFile("multiple_files.zip", mode="r") as archive:
    for file in archive.namelist():
        if file.endswith(".jpg"):
            print(' -- Extracting JPEG to output_dir/  ... ' + file)
            archive.extract(file, "output_dir/")