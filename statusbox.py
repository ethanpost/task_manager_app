__author__ = 'Ethan Post'

import tkinter as tk
import os
from bin import *
import time
from PIL import ImageTk, Image, ImageOps
from debug import *
import theme

from collections import OrderedDict

class StatusBox():

    def __init__(self, *args, **kwargs):

        debug('StatusBox: kwargs={}'.format(kwargs))

        self.root=kwargs['root']
        self.canvas=kwargs['canvas']

        if 'theme' in kwargs.keys():
            self.theme=kwargs['theme']
        else:
            self.theme=theme.Theme()

        # The font_size can be a number which is a specific font size of it can be one or more "<" or ">"'s which are
        # used to adjust the size from the base font size using the theme class.
        if 'font_size' in kwargs.keys():
            self.font_size=kwargs['font_size']
        else:
            self.font_size=None

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

        debug('Statusbox.__init__: x={0} y={1}'.format(self.x, self.y))

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self.clear()
        if text:
            self.object_id=self.canvas.create_text(self.x, self.y, text=text, font=self.theme.font(size=self.font_size), fill="black", anchor="nw", justify="left")

    def clear(self):
        debug2('StatusBox.clear')
        self.canvas.delete(self.object_id)
        
