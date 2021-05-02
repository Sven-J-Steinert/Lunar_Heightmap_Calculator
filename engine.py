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


        print('LOADING     ', end='', flush=True)
        URL = 'LDEM_80S_20M_cut.jpg'

        raw = io.imread(URL)
        raw = img_as_float(raw)
        self.data = raw
        print('done. \"' + URL + '\" ' + str(self.data.shape)  + ' min: ' + str(np.min(self.data)) + '  max: ' + str(np.max(self.data)))

        print('CONVERTING  ', end='', flush=True)
        raw = raw - np.min(raw)
        raw = raw / np.max(raw)
        self.display = raw

        io.imsave('display.png', (self.display*255).astype(np.uint8))
        print('done. \"' + URL + '\" ' + str(self.display.shape)  + ' min: ' + str(np.min(self.display)) + '  max: ' + str(np.max(self.display)))


        im = Image.open('display.png')
        self.canvas.image = ImageTk.PhotoImage(im)
        self.display_image = self.canvas.create_image((0,0), image=self.canvas.image, anchor='nw')

        self.draw_line = None
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
          self.calc_line(x,y)

    def right_click(self,v):
          print('Right Click')

    def calc_line(self,x,y):

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
        if self.draw_line is not None:
            self.canvas.delete(self.draw_line)
        self.draw_line = self.canvas.create_line(start_x, start_y, end_x, end_y, fill="#f09c35", width=4)


        delta_x = end_x - start_x
        delta_y = end_y - start_y

        calc_res = max(abs(delta_x),abs(delta_y))

        step_x = delta_x/ calc_res
        step_y = delta_y/ calc_res


        walk_x = start_x
        walk_y = start_y

        line = []
        line.append(tuple((int(walk_y), int(walk_x))))
        for a in range(calc_res):
            walk_x = walk_x + step_x
            walk_y = walk_y + step_y
            line.append(tuple((int(walk_y), int(walk_x))))



root = Tk()
app = Window(root)
root.attributes('-fullscreen', False)
root.wm_title("Tkinter window")
root.mainloop()
