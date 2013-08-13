__author__ = 'Ethan Post'

from debug import *
import copy

class Keyboard():

    KEYPRESS=8000
    
    def __init__(self, *args, **kwargs):

        debug('Keyboard: kwargs={}'.format(kwargs))

        if 'cbfunc' in kwargs.keys():
            self.cbfunc=kwargs['cbfunc']
        else:
            self.cbfunc=None
        
        self.shift_key_down=False
        self.escape_key_down=False
        self.control_key_down=False
        self.f1_key_down=False

        # A reference to the canvas (required)
        self.canvas=kwargs['canvas']

        self.canvas.bind("<Key>", self._keypress)
        self.canvas.bind("<KeyRelease>", self._keyrelease)

    def _keypress(self, event):
        debug('Keyboard._keypress: state={0} keycode={1}'.format(event.state, event.keycode))

        if event.state==8:
            if event.keycode==16:
                self.shift_key_down=True
            elif event.keycode==17:
                self.control_key_down=True
            elif event.keycode==27:
                self.escape_key_down=True
            elif event.keycode==112:
                self.f1_key_down=True

        if self.cbfunc:
            self.cbfunc({'cbkey': self.KEYPRESS, 'state': event.state, 'keycode':event.keycode})

    def _keyrelease(self, event):
        debug('Keyboard._keyrelease: state={0} keycode={1}'.format(event.state, event.keycode))
        if event.keycode==16:
            self.shift_key_down=False
        elif event.keycode==17:
            self.control_key_down=False
        elif event.keycode==27:
            self.escape_key_down=False
        elif event.keycode==112:
            self.f1_key_down=False

