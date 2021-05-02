from skimage import io, img_as_float
import numpy as np
from PIL import ImageTk,Image
Image.MAX_IMAGE_PIXELS = 1000000000

from tkinter import *

# pip install pillow
from PIL import Image, ImageTk



class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self._geom='200x200+0+0'
        master.bind('<Escape>',self.toggle_geom)
        master.bind("<Button 1>",self.left_click)
        master.bind("<Button 3>",self.right_click)

        self.canvas = Canvas(self, width=800, height=800, bg='yellow')
        self.canvas.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)



        URL = 'LDEM_80S_20M_cut.jpg'

        raw = io.imread(URL)
        raw = img_as_float(raw)
        self.data = raw
        print('loaded \"' + URL + '\" ' + str(raw.shape)  + ' min: ' + str(np.min(raw)) + '  max: ' + str(np.max(raw)))
        raw = raw - np.min(raw)
        self.display = raw / np.max(raw)
        io.imsave('display.png', self.display)
        print('display \"' + URL + '\" ' + str(raw.shape)  + ' min: ' + str(np.min(raw)) + '  max: ' + str(np.max(raw)))


        im = Image.open('display.png')
        self.canvas.image = ImageTk.PhotoImage(im)
        self.display_image = self.canvas.create_image((0,0), image=self.canvas.image, anchor='nw')


        self.new_dot = True

    def refresh(self):
        im = Image.open('display.png')
        self.canvas.image = ImageTk.PhotoImage(im)
        self.canvas.itemconfigure(self.display_image, image=self.canvas.image)

    def toggle_geom(self,event):
        print('ESC')
        exit(0)

    def left_click(self, content):
          global x,y
          x = content.x
          y = content.y
          print(str(x) + ' , ' + str(y))
          self.draw_line(x,y)

    def right_click(self,v):
          print('clear')

    def draw_line(self,x,y):

        global start_x, start_y

        if self.new_dot:
            start_x = x
            start_y = y
            self.new_dot = False
        else:
            end_x = x
            end_y = y
            self.get_line(start_x,start_y,end_x,end_y)
            self.new_dot = True

    def get_line(self,start_x,start_y,end_x,end_y):

        self.canvas.create_line(start_x, start_y, end_x, end_y, fill="#f09c35", width=4)
        print(start_x, end=' ')
        print(start_y, end=' ')
        print(end_x, end=' ')
        print(end_y)


        delta_x = end_x - start_x
        delta_y = end_y - start_y
        step_x = delta_x/ abs(min(delta_x,delta_y))
        step_y = delta_y/ abs(min(delta_x,delta_y))
        print('step x: ' + str(step_x))
        print('step y: ' + str(step_y))

        walk_x = start_x
        walk_y = start_y
        print('x: ' + str(walk_x))
        print('y: ' + str(walk_y))
        line = []
        for a in range(100):
            walk_x = walk_x + step_x
            walk_y = walk_y + step_y
            line.append(tuple((int(walk_x), int(walk_y))))
        print(line)

        for i in range(len(line)):
            #self.data[line[i]] = 1
            self.display[line[i]] = tuple((1,0,0))
        io.imsave('display.png', self.display)
        self.refresh()
        #print(self.data[start_x,start_y][0])
        #print(self.data[end_x,end_y][0])



root = Tk()
app = Window(root)
root.attributes('-fullscreen', False)
root.wm_title("Tkinter window")
root.mainloop()
