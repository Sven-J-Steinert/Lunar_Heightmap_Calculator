from skimage import io, img_as_float
from mpmath import mp
mp.prec = 100   # precision: 32 digits after zero


import math
import numpy as np
from PIL import ImageTk,Image
Image.MAX_IMAGE_PIXELS = 1000000000

from tkinter import *

# pip install pillow
from PIL import Image, ImageTk



class Window(Frame):
    def __init__(self, master=None, planet_diameter=None, pixel_width=None, elevation_range=None):

        print('WARNING   IMAGE_MAP_PROJECTION not implemented')

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

        self.canvas = Canvas(self, width=800, height=800, bg='yellow')
        self.canvas.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)


        print('LOADING   ', end='', flush=True)
        URL = 'LDEM_80S_20M_cut.jpg'
        #URL = 'white.jpg'

        raw = io.imread(URL)
        raw = img_as_float(raw)
        self.data = raw
        print('done. \"' + URL + '\" ' + str(self.data.shape)  + ' min: ' + str(np.min(self.data)) + '  max: ' + str(np.max(self.data)))

        print('CONTRAST  ', end='', flush=True)
        raw = raw - np.min(raw)
        raw = raw / np.max(raw)
        self.display = raw

        io.imsave('display.png', (self.display*255).astype(np.uint8))
        print('done. \"' + URL + '\" ' + str(self.display.shape)  + ' min: ' + str(np.min(self.display)) + '  max: ' + str(np.max(self.display)))


        im = Image.open('display.png')
        self.canvas.image = ImageTk.PhotoImage(im)
        self.display_image = self.canvas.create_image((0,0), image=self.canvas.image, anchor='nw')

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
            self.draw_dot_temp = self.canvas.create_oval(x+5, y+5, x-5, y-5, fill="#e08616", outline="black")
            self.new_dot = False
        else:
            end_x = x - self.offset_x
            end_y = y - self.offset_y
            if ((start_x != end_x ) and (start_y != end_y )):
                # check if its inside the picture dimensions - overflow otherwise
                max_x = self.data.shape[1]
                max_y = self.data.shape[0]
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


        self.draw_line = self.canvas.create_line(start_x+self.offset_x, start_y+self.offset_y, end_x+self.offset_x, end_y+self.offset_y, fill="#f09c35", width=4)
        self.draw_dot_1 = self.canvas.create_oval(start_x+self.offset_x+5, start_y+self.offset_y+5, start_x+self.offset_x-5, start_y+self.offset_y-5, fill="#e08616", outline="black")
        self.draw_dot_2 = self.canvas.create_oval(end_x+self.offset_x+5, end_y+self.offset_y+5, end_x+self.offset_x-5, end_y+self.offset_y-5, fill="#e08616", outline="black")

        print('Inputs: ', end=' ')
        print(tuple((start_x,start_y)) + tuple((end_x,end_y)))

        delta_x = end_x - start_x
        delta_y = end_y - start_y
        print('Delta: ', end=' ')
        print(tuple((delta_x,delta_y)))

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


        print('Step size: ', end=' ')
        print(tuple((x_step_size,y_step_size)))

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
                point_value_list.append(tuple((P_x, P_y, self.data[point_list[i]][0] * self.elevation_range)))
            else:
                # weighted parts
                w_1 = ( ((x_2 - P_x)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_11][0]
                w_2 = ( ((P_x - x_1)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_21][0]
                w_3 = ( ((x_2 - P_x)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_12][0]
                w_4 = ( ((P_x - x_1)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_22][0]

                interpolated_height_value = (w_1 + w_2 + w_3 + w_4) * self.elevation_range

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

        self.draw_result_box = self.canvas.create_rectangle(start_x+self.offset_x+(delta_x*0.5)-40, start_y+self.offset_y+(delta_y*0.5)-12, start_x+self.offset_x+(delta_x*0.5)+40, start_y+self.offset_y+(delta_y*0.5)+12, fill='white')
        self.draw_result = self.canvas.create_text(start_x+self.offset_x+(delta_x*0.5), start_y+self.offset_y+(delta_y*0.5),fill="black",font="Arial 12", text=f'{(meter_count/1000):.3f}'+' m')


custom_input = input('LOAD preset? No [Yes] ')
if custom_input == '':
    custom = False
else:
    custom = True

# HEIGHTMAP PROPERTY SETTINGS
if custom:
    planet_diameter =  int(input('          Insert planet diameter [km]: ')) * 1000
    pixel_width =      int(input('          Insert width of a pixel [m]: '))
    elevation_range =  int(input('          Insert elevation range (lowest to heighest) [km]: ')) * 1000
else:
    planet_diameter =  3474800
    pixel_width =      20
    elevation_range =  16000
    print('LOADED    Moon , resolution=20m, elevation_range=16km')

root = Tk()
app = Window(root, planet_diameter, pixel_width, elevation_range)
root.attributes('-fullscreen', True)
root.wm_title("Tkinter window")
root.mainloop()
