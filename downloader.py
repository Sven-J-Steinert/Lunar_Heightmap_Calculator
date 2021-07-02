from bs4 import BeautifulSoup
import requests
import sys
from prettytable import *

from os import walk
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

import os



url = 'http://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/JP2/'
ext = 'JP2'

print('Select map of interest')
print('Preview: http://imbrium.mit.edu/BROWSE/LOLA_GDR/POLAR/SOUTH_POLE/')
print()

def listFD(url, ext=''):
    page = requests.get(url).text
    #print(page)
    soup = BeautifulSoup(page, 'html.parser')
    # url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)
    return [ node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

table = PrettyTable(['FILE NAMES'])
table.align['FILE NAMES'] = 'l'
table.set_style(DRAWING)

for file in listFD(url, ext):
    if file[0:4] == 'LDEM':
        table.add_row([file])

print(table)
print()
file_name = input('Download File: ')


with open(file_name, "wb") as f:
    print("Downloading %s" % file_name)
    response = requests.get(url+file_name, stream=True)
    total_length = response.headers.get('content-length')

    if total_length is None: # no content length header
        f.write(response.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            f.write(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
            sys.stdout.write(' ' + str(int(dl/1024)) + ' kB' + '/' + str(int(total_length/1024)) + ' kB')
            sys.stdout.flush()


print()

print(file_name, end=' ', flush=True)
im = Image.open(file_name)
print('opened.', end=' ', flush=True)
print('converting to .png', end=' ', flush=True)
im.save(str(file_name)+'.png')
print('saved.')
im.close()

os.remove(file_name)
print('cleanup: ' + file_name + ' deleted.')
print()
print('Dont forget to update config')
