from skimage import io, img_as_float
from mpmath import mp
mp.prec = 200   # precision: 32 digits after zero

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
        master.bind('<Key>', self.key_press)

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

    def key_press(self,event):
        print(event)

    def right_click_drag(self,event):
        delta_x = self.old_drag_x - event.x
        delta_y = self.old_drag_y - event.y
        self.move_image(-delta_x,-delta_y)
        self.old_drag_x = event.x
        self.old_drag_y = event.y

    def go_left(self,event):
        print('left')
        self.offset_x = self.offset_x + 200
        self.move_image(200,0)

    def go_right(self,event):
        print('right')
        self.offset_x = self.offset_x - 200
        self.move_image(-200,0)

    def go_top(self,event):
        print('top')
        self.offset_y = self.offset_y + 200
        self.move_image(0,200)

    def go_bottom(self,event):
        print('bottom')
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

        delta_x = end_x - start_x
        delta_y = end_y - start_y

        calc_res = max(abs(delta_x),abs(delta_y))

        step_x = delta_x/ calc_res
        step_y = delta_y/ calc_res

        walk_x = start_x
        walk_y = start_y

        point_list = []
        point_list.append(tuple((int(walk_y) * self.pixel_width, int(walk_x) * self.pixel_width, self.data[tuple((int(walk_y), int(walk_x)))][0] * self.elevation_range)))
        for a in range(calc_res):
            walk_x = walk_x + step_x
            walk_y = walk_y + step_y
            point_list.append(tuple((int(walk_y) * self.pixel_width, int(walk_x) * self.pixel_width, self.data[tuple((int(walk_y), int(walk_x)))][0] * self.elevation_range)))

        #print(point_list)

        vector_list = []
        for i in range(1,len(point_list)):
            previous = np.array([point_list[i-1]])
            current = np.array([point_list[i]])
            delta = current-previous
            vector_list.append(delta[0])

        flat_vector_list = []
        for i in range(len(vector_list)):
            flat_vector_list.append(np.array((vector_list[i][0],vector_list[i][1])))

        meter_count = 0
        flat_meter_count = 0
        for x in range(0,len(vector_list)):
            meter_count = meter_count + np.linalg.norm(vector_list[x])
            flat_meter_count = flat_meter_count + np.linalg.norm(flat_vector_list[x])

        flat_length = mp.sqrt(delta_x**2 + delta_y**2) * self.pixel_width
        circle_segment = self.planet_diameter * mp.asin(flat_length/self.planet_diameter)
        distortion = mp.mpf((1 - (flat_length/circle_segment)) * 100)


        # CORRECTING EDGE DISTORTION
        alpha = mp.mpf(mp.atan(delta_y/delta_x))
        x_calc = mp.mpf(1 - abs(0.0773*mp.sin(-4*alpha))) # curve fitted error correction
        meter_count = float(mp.mpf(x_calc * meter_count))
        flat_meter_count = float(mp.mpf(x_calc * flat_meter_count))

        # INFO OUTPUT
        print(f'{meter_count:.2f}' + ' m')
        print('             with ~' + f'{float(distortion):.4f}' + '% curvature distortion (' + f'{float(flat_length):.4f}' + ' m flat vs. ' + f'{float(circle_segment):.4f}' + ' m curved)')
        edge_distortion = abs((1 - (flat_length/flat_meter_count)) *100)
        print('             with ~' + f'{float(edge_distortion):.4f}' + '% edge distortion left (' + f'{float(flat_length):.4f}' + ' m flat vs. ' + f'{float(flat_meter_count):.4f}' + ' m calculated flat)')

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
