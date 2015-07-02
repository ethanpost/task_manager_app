__author__ = 'Ethan Post'

from debug import *
import copy


class Keyboard():
    KEYPRESS = 8000

    def __init__(self, *args, **kwargs):

        debug2('Keyboard: kwargs={}'.format(kwargs))

        if 'cbfunc' in kwargs.keys():
            self.cbfunc = kwargs['cbfunc']
        else:
            self.cbfunc = None

        self.shift_key_down = False
        self.escape_key_down = False
        self.control_key_down = False
        self.f1_key_down = False
        self.f2_key_down = False
        self.f3_key_down = False
        self.f4_key_down = False
        self.f5_key_down = False
        self.f6_key_down = False

        # A reference to the canvas (required)
        self.canvas = kwargs['canvas']

        self.canvas.bind("<Key>", self._keypress)
        self.canvas.bind("<KeyRelease>", self._keyrelease)

    def _keypress(self, event):
        debug('Keyboard._keypress: state={0} keycode={1} keysym={2}'.format(event.state, event.keycode, event.keysym))

        # StateS: 9=Shift Key Down, 10=Caps-Lock
        if event.state in (8, 9, 11, 10):
            if event.keycode == 16:
                self.shift_key_down = True
                debug('Shift key is down!')
            elif event.keycode == 17:
                self.control_key_down = True
            elif event.keycode == 27:
                self.escape_key_down = True
            elif event.keycode == 112:
                self.f1_key_down = True
            elif event.keycode == 113:
                self.f2_key_down = True
            elif event.keycode == 114:
                self.f3_key_down = True
            elif event.keycode == 115:
                self.f4_key_down = True
            elif event.keycode == 116:
                self.f5_key_down = True
            elif event.keycode == 117:
                self.f6_key_down = True

        if self.cbfunc:
            self.cbfunc({'cbkey': self.KEYPRESS, 'state': event.state, 'keycode': event.keycode, 'key': event.keysym})

    def _keyrelease(self, event):
        #debug('Keyboard._keyrelease: state={0} keycode={1}'.format(event.state, event.keycode))
        if event.keycode == 16:
            self.shift_key_down = False
            debug('Shift key is up!')
        elif event.keycode == 17:
            self.control_key_down = False
        elif event.keycode == 27:
            self.escape_key_down = False
        elif event.keycode == 112:
            self.f1_key_down = False
        elif event.keycode == 113:
            self.f2_key_down = False
        elif event.keycode == 114:
            self.f3_key_down = False
        elif event.keycode == 115:
            self.f4_key_down = False
        elif event.keycode == 116:
            self.f5_key_down = False
        elif event.keycode == 117:
            self.f6_key_down = False

