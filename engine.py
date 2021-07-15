from bs4 import BeautifulSoup
import requests
import sys
from prettytable import *
import os
from os import walk

from skimage import io, img_as_float32
from mpmath import mp
mp.prec = 100   # precision: 32 digits after zero

import math
import numpy as np

from tkinter import *
import json
# pip install pillow
from PIL import Image, ImageTk, ImageMath
Image.MAX_IMAGE_PIXELS = 1000000000


import matplotlib.pyplot as plt
import matplotlib as mpl



class Window(Frame):
    def __init__(self, master=None, map=None, planet_diameter=None, pixel_width=None, elevation_range=None):

        self.planet_diameter = planet_diameter
        self.pixel_width = pixel_width
        self.elevation_range =  elevation_range

        self.offset_x = 0
        self.offset_y = 0

        Frame.__init__(self, master)
        self.master = master
        self._geom='200x200+0+0'
        master.bind('<Escape>',self.toggle_geom)
        master.bind("<Button 1>",self.left_click)
        master.bind('<B3-Motion>', self.right_click_drag)
        master.bind("<Button 3>",self.right_click)

        master.bind("w",self.go_top)
        master.bind("a",self.go_left)
        master.bind("s",self.go_bottom)
        master.bind("d",self.go_right)

        self.canvas = Canvas(self, width=800, height=800, bg='grey')
        self.canvas.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)


        print('LOADING   \"' + map + '\" ', end='', flush=True)
        self.im = Image.open(map)
        self.data = self.im.load()
        print('done.')


        print('CONTRAST  \"helper/display.png\" ', end='', flush=True)
        im2 = ImageMath.eval('im/256', {'im':self.im}).convert('L')
        self.zoom = 2
        #self.zoom = 10
        display = im2.resize(tuple([int(x/self.zoom)  for x in self.im.size]))#.convert('RGB')
        display_edit = display.load()
        display_edit_min, display_edit_max = display.getextrema()
        for y in range(0,display.size[1]):
            for x in range(0,display.size[0]):
                display_edit[x,y] = int(((display_edit[x,y] - display_edit_min) / (display_edit_max - display_edit_min))*255)
        cm_hot = mpl.cm.get_cmap('magma')
        #cm_hot = mpl.cm.get_cmap('plasma')
        #cm_hot = mpl.cm.get_cmap('inferno')
        im_edit = np.array(display)
        im_edit = cm_hot(im_edit)
        im_edit = np.uint8(im_edit * 255)
        im_edit = Image.fromarray(im_edit)
        im_edit.save('helper/display.png')
        print('done.')

        self.canvas.image = ImageTk.PhotoImage(Image.open('helper/display.png'))
        self.display_image = self.canvas.create_image((0,0), image=self.canvas.image, anchor='nw')

        legend_array = [range(0,255)]*20
        im_legend = cm_hot(legend_array)
        im_legend = np.uint8(im_legend * 255)
        im_legend = Image.fromarray(im_legend)
        im_legend.save('helper/legend.png')

        self.font = 'Arial 12'

        self.canvas.legend = ImageTk.PhotoImage(Image.open('helper/legend.png'))
        self.canvas.create_image(root.winfo_screenwidth()-20,root.winfo_screenheight()-20, image=self.canvas.legend, anchor='se')

        self.canvas.create_line(root.winfo_screenwidth()-19,root.winfo_screenheight()-67, root.winfo_screenwidth()-19,root.winfo_screenheight()-20, fill="white",  width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-20,root.winfo_screenheight()-47, root.winfo_screenwidth()-70,root.winfo_screenheight()-67, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-45,root.winfo_screenheight()-57,fill="black", font=self.font,
                        text=str(int(self.elevation_range/1000))+' km', anchor='center')

        self.canvas.create_line(root.winfo_screenwidth()-275,root.winfo_screenheight()-67, root.winfo_screenwidth()-275,root.winfo_screenheight()-20, fill="white",  width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-259,root.winfo_screenheight()-47, root.winfo_screenwidth()-275,root.winfo_screenheight()-67, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-267,root.winfo_screenheight()-57,fill="black", font=self.font,
                        text='0', anchor='center')

        self.canvas.create_line(root.winfo_screenwidth()-20,root.winfo_screenheight()-95, root.winfo_screenwidth()-120, root.winfo_screenheight()-95, fill="white",  width=2)
        self.canvas.create_line(root.winfo_screenwidth()-20,root.winfo_screenheight()-90, root.winfo_screenwidth()-20, root.winfo_screenheight()-100, fill="white",  width=2)
        self.canvas.create_line(root.winfo_screenwidth()-120,root.winfo_screenheight()-90, root.winfo_screenwidth()-120, root.winfo_screenheight()-100, fill="white", width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-35,root.winfo_screenheight()-100, root.winfo_screenwidth()-105,root.winfo_screenheight()-120, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-70,root.winfo_screenheight()-110,fill="black", font=self.font,
                        text=str('{0:.4g}'.format((self.pixel_width*100*self.zoom)/1000))+' km', anchor='center')




        self.draw_line = None
        self.draw_result_box = None
        self.draw_result = None
        self.draw_dot_1 = None
        self.draw_dot_2 = None
        self.draw_dot_temp = None

        self.new_dot = True

    def right_click_drag(self,event):
        delta_x = self.old_drag_x - event.x
        delta_y = self.old_drag_y - event.y
        self.move_image(-delta_x,-delta_y)
        self.old_drag_x = event.x
        self.old_drag_y = event.y

    def go_left(self,event):
        self.offset_x = self.offset_x + 200
        self.move_image(200,0)

    def go_right(self,event):
        self.offset_x = self.offset_x - 200
        self.move_image(-200,0)

    def go_top(self,event):
        self.offset_y = self.offset_y + 200
        self.move_image(0,200)

    def go_bottom(self,event):
        self.offset_y = self.offset_y - 200
        self.move_image(0,-200)


    def move_image(self,x,y):
        self.canvas.move(self.display_image, x, y)
        if self.draw_dot_temp:
            self.canvas.move(self.draw_dot_temp, x, y)
        if self.draw_line:
            self.canvas.move(self.draw_line, x, y)
            self.canvas.move(self.draw_dot_1, x, y)
            self.canvas.move(self.draw_dot_2, x, y)
            self.canvas.move(self.draw_result, x, y)
            self.canvas.move(self.draw_result_box, x, y)


    def toggle_geom(self,event):
        print('ESC')
        exit(0)

    def left_click(self, content):
          global x,y
          x = content.x
          y = content.y
          self.calc_line(x,y)


    def right_click(self,event):
          self.old_drag_x = event.x
          self.old_drag_y = event.y

    def calc_line(self,x,y):

        global start_x, start_y

        if self.new_dot:
            start_x = x - self.offset_x
            start_y = y - self.offset_y
            self.draw_dot_temp = self.canvas.create_oval(x+5, y+5, x-5, y-5, fill="white", outline="black")
            self.new_dot = False
        else:
            end_x = x - self.offset_x
            end_y = y - self.offset_y
            if ((start_x != end_x ) and (start_y != end_y )):
                # check if its inside the picture dimensions - overflow otherwise
                max_y, max_x = self.im.size

                if (start_x < 0) or (start_y < 0) or (end_x < 0) or (end_y < 0) or (start_x > max_x) or (start_y > max_y) or (end_x > max_x) or (end_y > max_y):
                    print('ERROR: OUTSIDE OF PICTURE DIMENSIONS')
                    self.canvas.delete(self.draw_dot_temp)
                else:
                    self.get_line(start_x,start_y,end_x,end_y)
                self.new_dot = True

    def get_line(self,start_x,start_y,end_x,end_y):



        if self.draw_line is not None:
            self.canvas.delete(self.draw_line)
        if self.draw_result_box  is not None:
            self.canvas.delete(self.draw_result_box)
        if self.draw_result is not None:
            self.canvas.delete(self.draw_result)
        if self.draw_dot_1 is not None:
            self.canvas.delete(self.draw_dot_1)
        if self.draw_dot_2 is not None:
            self.canvas.delete(self.draw_dot_2)
        if self.draw_dot_temp is not None:
            self.canvas.delete(self.draw_dot_temp)


        self.draw_line = self.canvas.create_line(start_x+self.offset_x, start_y+self.offset_y, end_x+self.offset_x, end_y+self.offset_y, fill="#000", width=3)

        self.draw_dot_1 = self.canvas.create_oval(start_x+self.offset_x+5, start_y+self.offset_y+5, start_x+self.offset_x-5, start_y+self.offset_y-5, fill="white", outline="black")
        self.draw_dot_2 = self.canvas.create_oval(end_x+self.offset_x+5, end_y+self.offset_y+5, end_x+self.offset_x-5, end_y+self.offset_y-5, fill="white", outline="black")

        start_x_display = start_x
        start_y_display = start_y
        end_x_display = end_x
        end_y_display = end_y
        delta_x_display = end_x_display - start_x_display
        delta_y_display = end_y_display - start_y_display

        # adjust for zoom
        start_x = start_x_display * self.zoom
        start_y = start_y_display * self.zoom
        end_x = end_x_display * self.zoom
        end_y = end_y_display * self.zoom

        delta_x = end_x - start_x
        delta_y = end_y - start_y

        # NEW CALCULATION METHOD

        self.sample_length = 1 # in pixel

        alpha = mp.atan(delta_x/delta_y)

        x_step_size = math.sin(alpha) * self.sample_length
        y_step_size = math.cos(alpha) * self.sample_length

        # recover correct direction
        if delta_x > 0:
            x_step_size = abs(x_step_size)
        else:
            x_step_size = abs(x_step_size) * (-1)

        if delta_y > 0:
            y_step_size = abs(y_step_size)
        else:
            y_step_size = abs(y_step_size) * (-1)


        flat_length = math.sqrt(delta_x**2 + delta_y**2)
        flat_length_meter = math.sqrt((delta_x * self.pixel_width)**2 + (delta_y * self.pixel_width)**2)

        steps = int(flat_length / self.sample_length)

        walk_x = start_x
        walk_y = start_y

        point_list = []
        # picture data features (y,x)
        point_list.append(tuple((start_y, start_x)))
        for i in range(0,steps):
            walk_x = walk_x + x_step_size
            walk_y = walk_y + y_step_size
            point_list.append(tuple((walk_y, walk_x)))

        point_list.append(tuple((end_y, end_x)))

        # TROUBLESHOOT - CHECKING PATH by writing red line in image data
        #for i in range(len(point_list)):
        #    self.display[tuple((int(point_list[i][0]),int(point_list[i][1])))] = tuple((1,0,0))
        #io.imsave('validate.png', self.display)


        # BILINEAR INTERPOLATION
        #        x_1          x_2
        # y_1   P_11          P_21
        #
        #                  P
        #
        # y_2   P_12          P_22

        point_value_list = []

        for i in range(0,len(point_list)):

            P_x = point_list[i][0]
            P_y = point_list[i][1]

            P_11 = tuple((math.floor(point_list[i][0]),math.floor(point_list[i][1])))
            P_21 = tuple((math.ceil(point_list[i][0]),math.floor(point_list[i][1])))
            P_12 = tuple((math.floor(point_list[i][0]),math.ceil(point_list[i][1])))
            P_22 = tuple((math.ceil(point_list[i][0]),math.ceil(point_list[i][1])))

            x_1 = math.floor(point_list[i][0])
            x_2 = math.ceil(point_list[i][0])
            y_1 = math.floor(point_list[i][1])
            y_2 = math.ceil(point_list[i][1])

            if ((x_2 - x_1)*(y_2 - y_1)) == 0:
                point_value_list.append(tuple((P_x, P_y, (self.data[point_list[i]] / 65535)  * self.elevation_range)))
            else:
                # weighted parts
                w_1 = ( ((x_2 - P_x)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_11]
                w_2 = ( ((P_x - x_1)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_21]
                w_3 = ( ((x_2 - P_x)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_12]
                w_4 = ( ((P_x - x_1)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_22]

                interpolated_height_value = ((w_1 + w_2 + w_3 + w_4)/65535 ) * self.elevation_range

                point_value_list.append(tuple((P_x, P_y, interpolated_height_value)))

        vector_list = []

        for i in range(1,len(point_value_list)):
            previous = np.array([point_value_list[i-1]])
            current = np.array([point_value_list[i]])
            delta = current-previous
            delta[0][0] = delta[0][0] * self.pixel_width
            delta[0][1] = delta[0][1] * self.pixel_width
            vector_list.append(delta[0])

        #print(vector_list)

        flat_vector_list = []

        for i in range(len(vector_list)):
            flat_vector_list.append(np.array((vector_list[i][0],vector_list[i][1])))


        # VECTOR NORM
        meter_count = 0
        flat_meter_count = 0

        for i in range(0,len(vector_list)):
            meter_count = meter_count + np.linalg.norm(vector_list[i])
            flat_meter_count = flat_meter_count + np.linalg.norm(flat_vector_list[i])


        # CURVATURE DISTORTION
        circle_segment = self.planet_diameter * mp.asin(flat_length_meter/self.planet_diameter)
        distortion = mp.mpf((1 - (flat_length_meter/circle_segment)) * 100)


        # INFO OUTPUT
        print(f'{meter_count:.2f}' + ' m')
        print('             with ~' + f'{float(distortion):.4f}' + '% curvature distortion (' + f'{float(flat_length_meter):.4f}' + ' m flat vs. ' + f'{float(circle_segment):.4f}' + ' m curved)')
        edge_distortion = abs((1 - (flat_length_meter/flat_meter_count)) *100)
        print('             with ~' + f'{float(edge_distortion):.4f}' + '% edge distortion left (' + f'{float(flat_length_meter):.4f}' + ' m flat vs. ' + f'{float(flat_meter_count):.4f}' + ' m calculated flat)')

        self.draw_result_box = self.canvas.create_rectangle(start_x_display+self.offset_x+(delta_x_display*0.5)-40, start_y_display+self.offset_y+(delta_y_display*0.5)-12, start_x_display+self.offset_x+(delta_x_display*0.5)+40, start_y_display+self.offset_y+(delta_y_display*0.5)+12, fill='white')
        self.draw_result = self.canvas.create_text(start_x_display+self.offset_x+(delta_x_display*0.5), start_y_display+self.offset_y+(delta_y_display*0.5),fill="black",font=self.font, text=f'{(meter_count/1000):.3f}'+' m')



print('┌────────────────────────────────────────────┐')
print('│                                            │               Controls')
print('│      ██╗  ██╗███████╗██████╗  ██████╗      │                       ')
print('│      ██║  ██║██╔════╝██╔══██╗██╔════╝      │                       ┌───┬───┐')
print('│      ███████║███████╗██║  ██║██║           │                       │ L │ R │')
print('│      ██╔══██║╚════██║██║  ██║██║           │       ┌───┐           ├───┴───┤')
print('│      ██║  ██║███████║██████╔╝╚██████╗      │       │ W │           │       │')
print('│      ╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝      │   ┌───┼───┼───┐       │       │')
print('│                                            │   │ A │ S │ D │       │       │')
print('│    Heightmap Surface Distance Calculator   │   └───┴───┴───┘       └───────┘')
print('└────────────────────────────────────────────┘      move map        select points')
print()


# diameter in [m]  source: https://nssdc.gsfc.nasa.gov/planetary/factsheet/
planet_database =  {'Sun':   1392700000,
                    'Mercury':  4879000,
                    'Venus':   12104000,
                    'Earth':   12756000,
                    'Moon':     3475000,
                    'Mars':     6792000,
                    'Jupiter':142984000,
                    'Saturn': 120536000,
                    'Uranus':  51118000,
                    'Neptune': 49528000,
                    'Pluto':    2370000,
                    }
def download():
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


    with open('maps/' + file_name, "wb") as f:
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
                sys.stdout.write(' ' + "{:.2f}".format(dl/(1024*1024)) + ' MB' + ' / ' + "{:.2f}".format(total_length/(1024*1024)) + ' MB')
                sys.stdout.flush()


    print()

    print('maps/' + file_name, end=' ', flush=True)
    im = Image.open('maps/' + file_name)
    print('opened.', end=' ', flush=True)
    print('converting to .png', end=' ', flush=True)
    file_name_new = str(file_name[:len(file_name)-4])+'.png'
    im.save('maps/' + file_name_new)
    print('saved.')
    im.close()

    os.remove('maps/' + file_name)
    print('cleanup: ' + 'maps/' + file_name + ' deleted.')
    print()

    return file_name_new

# HEIGHTMAP PROPERTY SETTINGS
with open('helper/config.json', 'r') as f:
    config = json.load(f)

print('LOADED preset: ' + str(config))

edit_input = input('EDIT preset? [n]/y: ')
if edit_input == '' or edit_input == 'n':
    map = config['map']
    planet_diameter = planet_database[config['planet']]
    pixel_width = config['pixel_width']
    elevation_range = config['elevation_range']
else:
    print()
    map_table = PrettyTable(['AVAILABLE MAPS'])
    map_table.align['AVAILABLE MAPS'] = 'l'
    map_table.set_style(DRAWING)
    f = []
    for (dirpath, dirnames, filenames) in walk('./maps'):
        f.extend(filenames)
        break

    for file in f:
        if file[len(file)-4:len(file)] == '.png':
            map_table.add_row([file])
    map_table.add_row(['DOWNLOAD MORE'])
    print(map_table)
    select =  str(input('          Select map: '))
    if select == 'DOWNLOAD MORE':
        map = download()
    else:
        map = select

    print(tuple(planet_database))
    planet =  str(input('          Type planet to select: '))
    planet_diameter = planet_database[planet]
    pixel_width =      int(input('          Insert width of a pixel [m]: '))
    elevation_range =  int(input('          Insert elevation range (lowest to heighest) [km]: ')) * 1000

    config['map'] = map
    config['planet'] = planet
    config['pixel_width'] = pixel_width
    config['elevation_range'] = elevation_range

    with open('helper/config.json', 'w') as f:
        json.dump(config, f)
    print('SAVED preset into helper/config.json')


root = Tk()
app = Window(root, 'maps/'+map, planet_diameter, pixel_width, elevation_range)
root.attributes('-fullscreen', True)
root.wm_title("Tkinter window")
root.mainloop()
