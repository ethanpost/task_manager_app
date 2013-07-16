
import tkinter as tk
from datetime import *
import time
import os
import shelve
import math
import subprocess
import copy
from collections import OrderedDict
import tkinter.colorchooser as colorchooser
from PIL import Image, ImageTk
from debug import debug as debug, critical as error
# from debug import dump as dump_debug
import timeline
from bin import *

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        timeline_height=(100,90,80)
        statusbox_height=0
        canvas_height=sum(timeline_height)+statusbox_height

        self.geometry('1000x{}+100+100'.format(canvas_height))

        self.canvas=tk.Canvas(self, background="white", bd=0, height=canvas_height, width=1000, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=False)

        self.timeline=timeline.Timeline(
            root=self,
            canvas=self.canvas,
            default_item_type='task',
            height=timeline_height
        )

    def cbfunc(self, dict):
        debug('cbfunc: {}'.format(dict))
        
if __name__ == "__main__":
    app = App()
    app.mainloop()