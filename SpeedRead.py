import numpy as np
import cv2
import codecs
import os
from PIL import Image, ImageDraw, ImageFont
from tkinter import Entry, Label, messagebox, Button, Tk, filedialog
from tkinter import filedialog

class SpeedRead:

    def __init__(self, document_path, video_path=None,
                 fps=5, edge=1.2, countdown = 0,
                 font_name='times', font_size=36,
                 color=(0,0,0), background_color=(255,255,255)):
        '''
        Inputs:
        - document_path (str) - valid path to text document
        - video_path (str) - (Optional) path to save video (default same name as document_path)
        - fps (int) - (Optional) number of words per second (default 5)
        - countdown (int) - (Optional) number of seconds to countdown (default 0)
        - font_name (str) - (Optional) name of the font to use (default 'times')
        - font_size (int) - (Optional) size of the font to use (default 36)
        - edge (float) - (Optional) relative size of edging (default 1.2), edge >= 1
        - color (tuple or list) - (Optional) color of the text to use in RGB mode (default (0,0,0) - black)
        '''
        self.document_path = self.set_document_path(document_path)
        self.video_path = self.set_video_path(video_path)
        self.font = self.set_font(font_name,font_size)
        self.fps = self.set_number(fps)
        self.countdown = self.set_number(countdown)
        self.edge = self.set_edge(edge)
        self.color = self.set_color(color)
        self.background_color = self.set_color(background_color)
        self.max_len = self.set_max_length()
        self.max_width = self.set_max_width()
        self.size = self.set_image_size()
        print('To create a video call create_video method')
        
    def set_document_path(self,document_path):
        _, file_extension = os.path.splitext(document_path)
        if os.path.isfile(document_path):
            if file_extension == '.txt':
                return document_path
            else:
                raise TypeError('Document should be of .txt type')
        else:
            raise FileNotFoundError('Desired document does not exist')
    
    def set_video_path(self,video_path):
        if video_path:
            if video_path.endswith('.mp4') or video_path.endswith('.avi'):
                return video_path
            else:
                videoname, _ = os.path.splitext(video_path)
                video_path = videoname + '.mp4'
                print('Desired video format is not supported: reset to mp4')
                print('Path to the video is set to:',video_path)
                return video_path
        filename, _ = os.path.splitext(self.document_path)
        video_path = filename + '.avi'
        print('Default path to the video is set to:',video_path)
        return video_path

    def set_font(self,font_name,font_size):
        try:
            font = ImageFont.truetype(font_name + '.ttf', font_size)
        except:
            font = ImageFont.truetype('times.ttf', font_size)
            print("Desired font not found: font reset to default ('times')")
        return font
    
    def set_edge(self,edge):
        if float(edge) >= 1:
            return float(edge)
        raise ValueError('Edge should be >= 1')
    
    def set_color(self,color):
        if len(color) == 3 and sum([(c >= 0) and (c <= 255) and (type(c) == int) for c in color]) == 3:
            return color
        else:
            raise TypeError('Color should be in RGB mode')

    def set_max_length(self):
        return max([self.font.getbbox(word)[2] for word in self.get_word_list()])

    def set_max_width(self):
        return max([self.font.getbbox(word)[3] for word in self.get_word_list()])

    def set_image_size(self):
        return ([int(self.max_len*self.edge),int(self.max_width*self.edge)])

    def set_number(self,fps):
        # if type(fps) == int or type(fps) == <class 'int'>:
        if int(fps) > 0:
            return int(fps)
        # raise TypeError('number of words per second (fps) should be integer')
    
    def get_word_list(self):
        with codecs.open(self.document_path, encoding='utf-8', mode='r') as f:
            data = f.readlines()
            data = ' '.join(line.rstrip() for line in data)
        return data.split()
    
    def add_text_to_image(self,word,color,background_color):
        image = np.ones([self.size[1],self.size[0],3],dtype=np.uint8)*np.array(background_color,dtype=np.uint8)
        left = int((image.shape[1] - self.font.getbbox(word)[2]) / 2)
        bottom = int((image.shape[0] - self.max_width) / 2)
        image = Image.fromarray(image)
        draw = ImageDraw.Draw(image)
        draw.text((left, bottom), word, color=color, fill=color, font=self.font)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    
    def create_video(self, video_path=None, fps=None, color=None, background_color=None, countdown=None):
        '''
        Inputs:
        - video_path (str) - (Optional) path to save video (default video_path was set during initialization)
        - fps (int) - (Optional) number of words per second (default fps was set during initialization)
        '''

        video_path = self.set_video_path(video_path) if video_path else self.video_path
        fps = self.set_fps(fps) if fps else self.fps
        color = self.set_color(color) if color else self.color
        background_color = self.set_color(background_color) if background_color else self.background_color
        countdown = self.set_number(countdown) if countdown else self.countdown

        out = cv2.VideoWriter(video_path,cv2.VideoWriter_fourcc(*'DIVX'), fps, self.size)
        if countdown:
            for i in range(countdown,0,-1):
                image = self.add_text_to_image(str(i),color,background_color)
                for _ in range(fps):
                    out.write(image)

        for word in self.get_word_list():
            image = self.add_text_to_image(word,color,background_color)
            out.write(image)

        out.release()
        return f'Video was saved to {video_path}'
        

def process():
    try:
        document_path = str(L_document_path.cget('text'))
        video_path = str(Entry.get(E_video_path))
        fps = int(str(Entry.get(E_fps)))
        countdown = int(Entry.get(E_countdown))
        font_name = str(Entry.get(E_font_name))
        font_size = int(Entry.get(E_font_size))
        color = tuple(list(map(int,str(Entry.get(E_color)).split())))
        background_color = tuple(list(map(int,str(Entry.get(E_background_color)).split())))
        edge = float(Entry.get(E_edge))

        SR = SpeedRead(document_path, video_path,
                    fps, edge, countdown,
                    font_name, font_size,
                    color, background_color)

        result = SR.create_video()
        result_label.configure(text=result)

    except Exception as e:
        messagebox.showinfo("Error",str(e))
    
def browse_file():
    document_path = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    L_document_path.configure(text=document_path)
    filename, _ = os.path.splitext(document_path)
    E_video_path.delete(0,'end')
    E_video_path.insert(0, filename+'.mp4')

top = Tk()
top.title("SpeedRead")
top.geometry("1100x500")
top.config(background = "teal")

Label(top, text="",background ='teal').grid(row=0,column=0)

L_document_path = Label(top, text = "Select txt file",width = 50, fg = "white", background ='teal')
L_document_path.grid(row=1, column=0)
B_Browse_file = Button(top, text = "Browse File", command = browse_file,background ='white')
B_Browse_file.grid(row=1, column=1)
Label(top, text="",background ='teal',).grid(row=2,column=0)

L_video_path = Label(top, text=" (Optional) path to save video (default same name as document_path) ",background ='teal',fg = "white")
L_video_path.grid(row=3,column=0)
E_video_path = Entry(top, bd=5, width=50, justify='center',background ='white')
E_video_path.grid(row=3,column=1)
E_video_path.insert(0, 'Select txt file first')
Label(top, text="",background ='teal').grid(row=4,column=0)

L_fps = Label(top, text=" (Optional) number of words per second (default 5) ",background ='teal',fg = "white")
L_fps.grid(row=5,column=0)
E_fps = Entry(top, bd=5, width=50, justify='center',background ='white')
E_fps.grid(row=5,column=1)
E_fps.insert(0, '5')
Label(top, text="",background ='teal').grid(row=6,column=0)

L_countdown = Label(top, text=" (Optional) number of seconds to countdown (default 0) " ,background ='teal',fg = "white")
L_countdown.grid(row=7,column=0)
E_countdown = Entry(top, bd=5, width=50, justify='center',background ='white')
E_countdown.grid(row=7,column=1)
E_countdown.insert(0, '0')
Label(top, text="",background ='teal').grid(row=8,column=0)

L_font_name = Label(top, text=" (Optional) name of the font to use (default 'times')  ",background ='teal',fg = "white")
L_font_name.grid(row=9,column=0)
E_font_name = Entry(top, bd=5, width=50, justify='center',background ='white')
E_font_name.grid(row=9,column=1)
E_font_name.insert(0, 'times')
Label(top, text="",background ='teal').grid(row=10,column=0)

L_font_size = Label(top, text=" (Optional) size of the font to use (default 100) ",background ='teal',fg = "white")
L_font_size.grid(row=11,column=0)
E_font_size = Entry(top, bd=5, width=50, justify='center',background ='white')
E_font_size.grid(row=11,column=1)
E_font_size.insert(0, '100')
Label(top, text="",background ='teal').grid(row=12,column=0)

L_color = Label(top, text=" (Optional) color of the text to use in RGB mode (default (0,0,0) - black) ",background ='teal',fg = "white")
L_color.grid(row=13,column=0)
E_color = Entry(top, bd=5, width=50, justify='center',background ='white')
E_color.grid(row=13,column=1)
E_color.insert(0, '0 0 0')
Label(top, text="",background ='teal').grid(row=14,column=0)

L_background_color = Label(top, text=" (Optional) background color to use in RGB mode (default (255,255,255) - white) ",background ='teal',fg = "white")
L_background_color.grid(row=15,column=0)
E_background_color = Entry(top, bd=5, width=50, justify='center',background ='white')
E_background_color.grid(row=15,column=1)
E_background_color.insert(0, '255 255 255')
Label(top, text="",background ='teal').grid(row=16,column=0)

L_edge = Label(top, text=" (Optional) relative size of edging (default 1.2), edge >= 1 ",background ='teal',fg = "white")
L_edge.grid(row=17,column=0)
E_edge = Entry(top, bd=5, width=50, justify='center',background ='white')
E_edge.grid(row=17,column=1)
E_edge.insert(0, '1.2')
Label(top, text="",background ='teal').grid(row=18,column=0)

B_create_video = Button(top, text = "Create video", command = process,background ='white')
B_create_video.grid(row=19, column=1)

result_label = Label(top, text = "",width = 100, background ='teal', fg = "white")
result_label.grid(row=19, column=0)

top.mainloop()