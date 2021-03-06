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
    object_type = 'statusbox'

    def __init__(self, root):
        # debug('StatusBox')

        self.root = root
        self.canvas = root.canvas
        self.palette = root.palette
        self._y = 0
        self._height = 18
        self.bottom = None
        self.width = None
        self.x = None
        self.font_size = None
        self.object_id = None
        self._text = None
        self._update_bottom()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        self._update_bottom()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height
        self._update_bottom()

    def _update_bottom(self):
        self.bottom = self.y + self._height

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        # debug('text={}'.format(text))
        self.clear()
        if text:
            self.object_id = self.canvas.create_text(
                self.x,
                self.y,
                text=text,
                font=self.palette.get_font(),
                fill="black",
                anchor="nw",
                justify="left")

    def clear(self):
        # debug2('StatusBox.clear')
        self.canvas.delete(self.object_id)

    def draw(self, x, y, width=None):
        """
        Updates x and y position of statusbox.

        Width is here to comply with drawable object rules in TaskManager class.
        """
        self.x = x
        self.y = y
        
