__author__ = 'Ethan Post'

import tkinter as tk
import os
import bin
import time
from PIL import ImageTk, Image, ImageOps
from debug import *
import re
import keyboard

class FileBar():
    
    FAIL=0
    SUCCESS=1
    DELETE=2
    EVENT_IMAGE_DROP=10
    DRAG_AND_DROP=9000

    def __init__(self, *args, **kwargs):

        self.root=kwargs['root']
        self.canvas=kwargs['canvas']
        self.height=kwargs['height']

        self.keyboard=keyboard.Keyboard(canvas=self.canvas)

        if 'x' in kwargs.keys():
            self.x=kwargs['x']
        else:
            self.x=0

        self.original_x=self.x

        if 'y' in kwargs.keys():
            self.y=kwargs['y']
        else:
            self.y=0

        if 'statusbox' in kwargs.keys():
            self.statusbox=kwargs['statusbox']
        else:
            self.statusbox=None

        if 'cbfunc' in kwargs.keys():
            self.cbfunc=kwargs['cbfunc']
        else:
            self.cbfunc=None

        # ToDo: This can be removed soon.
        self.files={}

        self.objects={}

        self.filebar=None

        self.bottom=None

        # Used for drag and drop operations.
        self._dragging={}

        # Total real width of the file bar, not what is shown on the screen.
        self.filebar_width=None

        # Pointer to the first thumbnail on the file bar.
        self._object_id_of_first_file=None
                
        self.images_folder=os.path.join(bin.application_root_folder(), 'images')

        # ToDo: Add audio and video types.
        self.extensions={
            '.jpg'  : 'image',
            '.gif'  : 'image',
            '.bmp'  : 'image',
            '.docx' : 'word.jpg',
            '.pptx' : 'ppt.jpg',
            '.txt'  : 'text.jpg'
        }

        self.patterns_to_exclude=[]

        self.canvas.tag_bind("FileBarFile", "<ButtonPress-1>",   self._thumbnail_mouse_down)
        #self.canvas.tag_bind("FileBarFile", "<B1-Motion>",       self._thumbnail_mouse_over)
        self.canvas.tag_bind("FileBarFile", "<Motion>",       self._thumbnail_mouse_over)
        self.canvas.tag_bind("FileBarFile", "<ButtonRelease-1>", self._thumbnail_mouse_up)
        self.canvas.tag_bind("FileBarFile", "<Double-1>",        self._thumbnail_mouse_doubleclick)

        self.real_x=self.x

        self.draw()

    def draw(self):
        debug('FileBar.draw')
        self.thumbnail_size=int(self.height*.8)
        self.bottom=self.y+self.height

    def clear(self):
        debug('FileBar.clear')
        self.canvas.delete('FileBarFile')
        self.objects={}
        self.x=self.original_x
        self._object_id_of_first_file=None

    def add_object(self, object_name, object_type, image_file, drags=False, is_folder=False):
        debug('FileBar.add_object')
        i=bin.get_photoimage_thumbnail(image_file, size=self.thumbnail_size-1, border_color='black', border_size=1)
        object_id=self.canvas.create_image(self.x+int(self.height*.1), self.y+int(self.height*.1), anchor=tk.NW, image=i, state=tk.NORMAL, tags='FileBarFile')

        if not self._object_id_of_first_file:
            self._object_id_of_first_file=object_id

        self.x+=self.height

        self.filebar_width=self.x

        self.objects[object_id]={
            'name':object_name,
            'type':object_type,
            'photoimage': i,
            'drags':drags,
            'is_folder': is_folder,
            'image_file': image_file
        }
        
    def add_folder(self, directory, drags=False):
        debug('FileBar.add_folder')
        self.add_object(
            object_name=directory,
            object_type='directory',
            image_file=os.path.join(self.images_folder, 'folder.jpg'),
            drags=drags,
            is_folder=True)

    def add_files(self, directory, drags=True):
        debug('FileBar.add_files: {}'.format(directory))
        for file in os.listdir(directory):

            skip_file=False

            for pattern in self.patterns_to_exclude:
                r=re.compile(pattern)
                if r.match(file):
                    skip_file=True
                    break

            if skip_file:
                continue
                    
            extension = os.path.splitext(file)[-1].lower()

            if extension in self.extensions.keys():
                if self.extensions[extension]=='image':
                    image_file=os.path.join(directory, file)
                else:
                    image_file=os.path.join(self.images_folder, self.extensions[extension])
            else:
                image_file=os.path.join(self.images_folder, 'default.jpg')

            file_path=os.path.join(directory, file)

            self.add_object(object_name=file_path, object_type='file', image_file=image_file, drags=True)

#            self.files[object_id]={
#                "image-ref":i,
#                "file-type":file_type,
#                "file-name": file_path,
#                "modified-time":time.localtime(os.path.getmtime(file_path))
#            }
        
#    self.files[object_id]={
#        "image-ref":i,
#        "file-type":'folder',
#        "file-name": 'folder',
#        "modified-time":None
#        }
        
    def _thumbnail_mouse_down(self, event):
        debug('FileBar._thumbnail_mouse_down')
        object_id=self.canvas.find_closest(event.x, event.y)[0]
        self._dragging['coords']=self.canvas.coords(object_id)
        self._dragging['object_id']=object_id
        self._dragging['axis']='?'
        self.canvas.tag_raise(object_id)
        # Store the original position in case we need to abort the drag and drop.
        self._dragging['x']=self._dragging['x0']=event.x
        self._dragging['y']=self._dragging['y0']=event.y
        self.canvas.focus_force()
        #self.canvas.focus_set()

    def _thumbnail_mouse_over(self, event):
        debug("FileBar._thumbnail_mouse_over")

        self.canvas.focus_set()

        if len(self._dragging)==0:
            return

        if not self._dragging['object_id']:
            return

        # How far have we moved since the initial drag operation?
        delta_x0 = event.x - self._dragging['x0']
        delta_y0 = event.y - self._dragging['y0']

        # If we don't know which way we are dragging yet, figure it out.
        if self._dragging['axis'] == '?':
            if abs(delta_x0) > 10 and abs(delta_x0) > abs(delta_y0):
                self._dragging['axis']='x'
            elif abs(delta_y0) > 10 and abs(delta_y0) > abs(delta_x0):
                self._dragging['axis']='y'
            else:
                # Mouse pointer has not moved far enough to determine the dragging axis.
                return

        # How far have we moved since the last time the event was detected.
        delta_x = event.x - self._dragging["x"]
        delta_y = event.y - self._dragging["y"]
        # Save the current location.
        self._dragging["x"] = event.x
        self._dragging["y"] = event.y

        object_id=self._dragging['object_id']

        if self._dragging['axis']=='x':
            delta_y=0
            delta_x=self._get_valid_delta(delta_x)
            for object_id in self.objects.keys():
                self.canvas.move(object_id, delta_x, delta_y)
        else:
            drags=self.objects[object_id]['drags']
            if drags:
                self.canvas.move(object_id, delta_x, delta_y)

    def _thumbnail_drag_abort(self, x, y):
        debug('Filebar._thumbnail_drag_abort: x={0} y={1} coords={2}'.format(x, y, self._dragging['coords']))
        object_id=self._dragging['object_id']
        self.canvas.coords(object_id, x, y)

    def _thumbnail_mouse_up(self, event):
        debug("Filebar._thumbnail_mouse_up")

        if len(self._dragging)==0:
            return

        if self._dragging['axis']!='?':
            object_id=self._dragging['object_id']
            if self.cbfunc:
                coords=self.canvas.coords(object_id)
                self.cbfunc({'cbkey':self.DRAG_AND_DROP, 'object':self.objects[object_id], 'x':int(coords[0]), 'y':int(coords[1])})
            self._thumbnail_drag_abort(int(self._dragging['coords'][0]), int(self._dragging['coords'][1]))

        self._dragging={}
        
    def _thumbnail_mouse_doubleclick(self, event):
        object_id=self.canvas.find_closest(event.x, event.y, start=0)[0]
        if object_id:
            object=self.objects[object_id]

            if object['type']=='upfolder':
                directory=object['name']
                self.filebar=None
                self.clear()
                self.add_folder(directory=directory, drags=False)
                self.draw()
                
            elif object['is_folder']:
                if self.keyboard.shift_key_down:
                    bin.open_file_using_default_program(object['name'])
                    self.keyboard.shift_key_down=False
                else:
                    self.clear()
                    self.add_object(
                        object_name=object['name'],
                        object_type='upfolder',
                        image_file=os.path.join(self.images_folder, 'left_arrow.jpg'),
                        drags=True,
                        is_folder=True)
                    self.add_files(directory=object['name'], drags=True)
            else:
                bin.open_file_using_default_program(self.objects[object_id]['name'])
                # sublime(self.files[object_id]['file-name'])

    def _get_valid_delta(self, x):
        left,y=self.canvas.coords(self._object_id_of_first_file)
        if x > 0:
            if left > 0:
                return 0
            elif left+x > 0:
                return -left+10
            else:
                return x
        elif x < 0:
            if left <= -self.filebar_width+self.canvas.winfo_width():
                return 0
            elif left+x <= -self.filebar_width+self.canvas.winfo_width():
                return (-self.filebar_width+self.canvas.winfo_width())-left
            else:
                return x
        else:
            return x

    def right_arrow(self):
        delta_y=0
        delta_x=-self.thumbnail_size
        delta_x=self._get_valid_delta(delta_x)
        for object_id in self.thumbnails.keys():
            self.canvas.move(object_id, delta_x, delta_y)

    def left_arrow(self):
        delta_y=0
        delta_x=self.thumbnail_size
        delta_x=self._get_valid_delta(delta_x)
        for object_id in self.thumbnails.keys():
            self.canvas.move(object_id, delta_x, delta_y)