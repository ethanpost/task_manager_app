
from debug import *

class Theme():
    def __init__(self, name='default'):
        self.font_name=None
        self.font_size=None
        self.font_color=None
        self.background_color=None
        self.line_color=None
        self._enabled=True
        self._name=name
        self._set_attributes()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, tf):
        if type(tf)==bool:
            self._enabled=tf
            self._set_attributes()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name=name
        self._set_attributes()


    def _set_attributes(self):
        if self._name=='foo':
            if self._enabled:
                None
            else:
                None
        else:
            if self._enabled:
                self.font_name='Arial'
                self.font_size=11
                self.font_color='black'
                self.background_color='white'
                self.outline_color='black'
            else:
                self.font_color='gray'
                self.background_color='light gray'
                self.outline_color='dark gray'

    def font(self, size=None):
        if isinstance(size, int):
            font_size=self.font_size+size
        elif size is not None:
            font_size=self.font_size
            font_size-=size.count('<')
            font_size+=size.count('>')
        else:
            font_size=self.font_size

        if font_size < 0:
            font_size=self.font_size

        return (self.font_name, font_size)
