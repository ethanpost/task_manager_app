__author__ = 'Ethan Post'

import tkinter as tk
import os
from bin import *
import time
from PIL import ImageTk, Image, ImageOps
from debug import *
from collections import OrderedDict

class StatusBox():

    def __init__(self, *args, **kwargs):

        debug('StatusBox: kwargs={}'.format(kwargs))

        self.root=kwargs['root']
        self.canvas=kwargs['canvas']

        if 'width' in kwargs.keys():
            self.width=kwargs['width']
        else:
            self.width=self.canvas.winfo_reqwidth

        if 'height' in kwargs.keys():
            self.height=kwargs['height']
        else:
            self.height=16

        if 'x' in kwargs.keys():
            self.x=kwargs['x']
        else:
            self.x=0

        if 'y' in kwargs.keys():
            self.y=kwargs['y']
        else:
            self.y=0
        
        self.object_id=None

        self._text=None

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self.clear()
        if text:
            self.object_id=self.canvas.create_text(self.x, self.y, text=text, font=('Arial', 12), fill="black", anchor="nw", justify="left")

    def clear(self):
        debug2('StatusBox.clear')
        self.canvas.delete(self.object_id)
        
