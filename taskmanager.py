

import tkinter as tk
import re
from debug import *
import bin
import os
import keyboard
import statusbox
import modalinputbox
import filebar
import taskbar
import datetime
import theme
import copy
from profilehooks import coverage, profile, timecall


class ItemForm():
    CLOSE_FORM = 23750

    def __init__(self, root, theme, item, cbfunc=None):
        self.form = tk.Toplevel(root)
        self.form.protocol("WM_DELETE_WINDOW", self._close_form)
        self.form.bind_class("Text", "<Control-a>", self.select_all)
        self.form.bind_class("Entry", "<Control-a>", self.select_all)
        self.keyboard = keyboard
        self.theme = theme
        self.cbfunc = cbfunc
        self._status_doc = '<Enter Status or #Milestone>'
        self._description_doc = '<Description/Notes>'
        self.widget_width = 75
        self.item = item
        self.copy_of_item = copy.deepcopy(item)
        self.title_var = tk.StringVar()
        self._draw()

    def _update_status_history(self):
        self.history_box.configure(state=tk.NORMAL)
        self.history_box.delete(1.0, tk.END)
        for status in self.item.all_statuses():
            self.history_box.insert(tk.END, status)
        self.history_box.configure(state=tk.DISABLED)

    def _close_form(self):
        debug('ItemForm._close_form')
        self.item.title = self.title_var.get()
        self.item.description = self._get_description()
        self.item.tags = self.tags_var.get().split(',')
        self.item.save()
        if self.cbfunc:
            self.cbfunc({'cbkey': self.CLOSE_FORM})
        self.form.destroy()

    def _draw(self):

        item = self.item
        self.form.title(item.title)

        # Title
        title_frame = tk.Frame(self.form)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_label = tk.Label(title_frame, text='Title', font=self.theme.font(size='>'), anchor="w", relief=tk.FLAT,
                               fg='black')
        title_label.pack(fill=tk.X)
        self.title_box = tk.Entry(title_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT,
                                  width=self.widget_width,
                                  textvariable=self.title_var)
        self.title_box.pack(fill=tk.X)
        self.title_box.bind('<Key>', self._keypress_title)
        self.title_box.bind('<FocusIn>', self.select_all)
        self.title_var.set(item.title)

        line = tk.Frame(self.form, bd=2, relief=tk.RAISED, padx=10, pady=2)
        line.pack(fill=tk.X)

        self._draw_description()

        # Status
        status_frame = tk.Frame(self.form)
        status_frame.pack(fill=tk.X, padx=2, pady=2)
        self.status_var = tk.StringVar()
        status_label = tk.Label(status_frame, text='Status', font=self.theme.font(size='>'), anchor="w", relief=tk.FLAT,
                                fg='black')
        status_label.pack(fill=tk.X)
        self.status_box = tk.Entry(status_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT,
                                   width=self.widget_width, textvariable=self.status_var)
        self.status_box.pack(fill=tk.X)
        self.status_box.bind('<Key>', self._keypress_status)
        self.status_box.bind('<FocusIn>', self._focus_in_status)
        self.status_var.set(self._status_doc)
        self.status_box.focus_set()
        self._focus_in_status()

        line = tk.Frame(status_frame, bd=2, relief=tk.RAISED, bg='dark gray', padx=10, pady=2)
        line.pack(fill=tk.X)

        # Status history.
        history_bar = tk.Scrollbar(status_frame)
        history_bar.pack(side=tk.RIGHT, fill=tk.Y)
        history_box_height = 5
        self.history_box = tk.Text(status_frame, height=history_box_height, borderwidth=1,
                                   font=self.theme.font(size='>'),
                                   relief=tk.FLAT, width=self.widget_width, fg='dark grey')
        self.history_box.pack(side=tk.TOP, fill=tk.X)
        self.history_box.configure(yscrollcommand=history_bar.set)
        history_bar.configure(command=self.history_box.yview)
        self._update_status_history()

        # Tags
        debug('item.tags={}'.format(item.tags))
        tags_frame = tk.Frame(self.form)
        tags_frame.pack(fill=tk.X, padx=2, pady=2)
        tags_label = tk.Label(tags_frame, text='Tags', font=self.theme.font(size=">"), anchor="w", width="10",
                              relief=tk.FLAT, fg='black')
        tags_label.pack(fill=tk.X)
        self.tags_var = tk.StringVar()
        self.tags_box = tk.Entry(tags_frame, borderwidth=2, font=self.theme.font(size='>'), relief=tk.FLAT,
                                 width=self.widget_width,
                                 textvariable=self.tags_var)
        self.tags_box.pack(fill=tk.X)
        self.tags_box.bind('<Key>', self._keypress_tags)
        self.tags_box.bind('<FocusIn>', self._focus_in_tags)
        self.tags_var.set(','.join(item.tags))

        files_frame = tk.Frame(self.form)
        files_frame.pack(fill=tk.X, padx=2, pady=2)
        files_label = tk.Label(files_frame, text='Files', font=self.theme.font(size=">"), anchor="w", width="10",
                               relief=tk.FLAT, fg='black')
        files_label.pack(fill=tk.X)

        canvas_frame = tk.Frame(self.form)
        canvas_frame.pack(fill=tk.X, padx=2, pady=2)
        canvas = tk.Canvas(canvas_frame, width=self.widget_width, height=60, bg='white')
        canvas.pack(fill=tk.X)

        self.filebar = filebar.FileBar(root=self.form, canvas=canvas, height=60)
        self.filebar.patterns_to_exclude = ['_data_']
        self.filebar.add_folder(directory=item.storage_folder)
        self.filebar.draw()


    def _draw_description(self):
        description_frame = tk.Frame(self.form)
        description_frame.pack(fill=tk.X, padx=2, pady=2)
        self.description_bar = tk.Scrollbar(description_frame)
        self.description_bar.pack(side=tk.RIGHT, fill=tk.Y)
        description_label = tk.Label(description_frame, text='More', font=self.theme.font(size='>'), anchor="w",
                                     relief=tk.FLAT,
                                     fg='black')
        description_label.pack(fill=tk.X)
        description_box_height = 6
        self.description_box = tk.Text(description_frame, height=description_box_height, borderwidth=1,
                                       font=self.theme.font(size='>'), relief=tk.FLAT, width=self.widget_width)
        self.description_box.pack(side=tk.TOP, fill=tk.X)
        self.description_box.configure(yscrollcommand=self.description_bar.set)
        self.description_bar.configure(command=self.description_box.yview)
        self._set_description_box_text(self.item.description)

        self.description_box.bind('<Tab>', self._focus_set_status_box)
        self.description_box.bind('<Shift-Tab>', self._focus_set_title_box)
        # self.description_box.bind('<FocusOut>', self._focus_out_description)
        #self.description_box.bind('<Control-a>', self._select_all_description)
        self.description_box.bind('<Key>', self._keypress_description)

    def _enable_description(self):
        self.description_box.configure(state=tk.NORMAL)

    def _focus_in_tags(self, event):
        self.tags_box.select_range(tk.END, tk.END)

    def _focus_out_description(self, event):
        """
        Save description to item object on focus out event.
        """
        if self._get_description() != self._description_doc or self._get_description() == '':
            self.item.description = self._get_description()
            self._description_doc = ''
            debug('ItemForm._focus_out_description')

    def _focus_set_status_box(self, event):
        self.status_box.focus_set()
        return "break"

    def _focus_set_title_box(self, event):
        self.title_box.focus_set()
        return "break"

    def _focus_in_status(self, event=None):
        if self.status_var.get() == self._status_doc:
            self.status_box.select_range(0, tk.END)

    def _get_description(self):
        debug('ItemForm._get_description: {}'.format(self.description_box.get('1.0', tk.END)))
        return self.description_box.get('1.0', tk.END).rstrip()

    def _keypress_status(self, event):
        #debug('ItemForm._keypress_status: {0} {1}'.format(event.state, event.keycode))
        if event.state == 8 and event.keycode == 13:
            # Enter
            if self.status_var.get() not in ('', self._status_doc):
                self.item.status = self.status_var.get()
                self.status_var.set(self._status_doc)
                self._focus_in_status()
            self._update_status_history()
        elif event.state == 8 and event.keycode == 27:
            # Escape
            self.status_var.set(self._status_doc)
            self._focus_in_status()

    def _keypress_title(self, event):
        #debug('ItemForm._keypress_title: state={0} keycode={1}'.format(event.state, event.keycode))
        if event.state == 8 and event.keycode == 27:
            # Escape
            self.title_var.set(self.copy_of_item.title)
            self._select_all_title()

        self.item.title = self.title_var.get()

    def _keypress_description(self, event):
        if event.state == 8 and event.keycode == 27:
            # Escape
            self._set_description_box_text(self.copy_of_item.description)
        if self._get_description().startswith(self._description_doc):
            self.item.description = None
        else:
            self.item.description = self._get_description()

    def _keypress_tags(self, event):
        if event.state == 8 and event.keycode == 27:
            # Escape
            self.tags_var.set(','.join(self.copy_of_item.tags))

    def _pack_description(self):
        self.description_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_box.pack(side=tk.TOP, fill=tk.X)

    def select_all(self, event):
        if event.widget.widgetName == 'entry':
            event.widget.select_range(0, tk.END)
        else:
            event.widget.tag_add("sel", "1.0", "end")

    def _select_all_title(self):
        debug('ItemForm._select_all_title')
        self.title_box.select_range(0, tk.END)

    def _select_all_description(self, event=None):
        self.description_box.tag_add("sel", "1.0", "end")

    def _set_description_box_text(self, text=None):
        debug('ItemForm: _set_description_box_text')
        text = bin.nvl(text, self._description_doc)
        self.description_box.delete('1.0', tk.END)
        self.description_box.insert('1.0', text)
        self._select_all_description()

    def test(self, event):
        debug('TEST')

    def _update_tags(self, event):
        """
        http://stackoverflow.com/questions/6687108/tab-order-in-tkinter
        """
        debug('ItemForm._update_tags')
        if event.state == 8 and event.keycode == 13:
            debug('update_tags')
            self.item.tags = self.tags_var.get().split(',')


class Drawers():
    def __init__(self):
        self.key = bin.random_string(20)
        self.name = name
        self._height = height
        self.theme = theme
        self.type = type
        self._y = y
        self._x = None
        self._database_path = os.path.join(bin.application_root_path(), 'data', 'drawers_{}.cfg'.format(self.name))

    def load(self):
        d = bin.open_database2(self._database_path)
        if d:
            self.height = d['height']
            self.key = d['key']


class TagBox():
    def __init__(self, canvas, theme, x=0, y=0):
        self.canvas = canvas
        self.theme = theme
        self.x = x
        self.y = y
        self.object_id = None
        self.right = None
        self.bottom = None
        self.next_tag_x = None
        self.next_tag_y = None
        self.colors_index = ['gray', 'green', 'yellow', 'powder blue', 'orange', 'purple', 'white', 'gray50']
        self.tags = []

    def add_tag(self, name):
        if name not in self.tags:
            self.tags.append(name)

    def remove_tag(self):
        None

    def draw(self):

        self.canvas.delete('tagbox')

        self.next_tag_x = self.x + 6
        self.next_tag_y = self.y + 14
        self.right = self.x
        self.bottom = self.y

        color_index_pointer = 0

        for tag in self.tags:


            text_id = self.canvas.create_text(self.next_tag_x, self.next_tag_y, font=self.theme.font(size='<'),
                                              text=tag, anchor='w', fill=self.theme.font_color,
                                              tags=('tagbox', 'tagbox_{}'.format(tag)))

            # Get the coordinates of the corners of the text box.
            bbox_tuple = self.canvas.bbox(text_id)

            # Create a rectangle to contain the text we want to write with some margins.
            rect_id = self.canvas.create_rectangle(bbox_tuple[0] - 2, bbox_tuple[1] - 2, bbox_tuple[2] + 2,
                                                   bbox_tuple[3] + 2,
                                                   fill=self.colors_index[color_index_pointer], outline='black',
                                                   tags=('tagbox', 'tagbox_{}'.format(tag)))

            # Lift the text so it is not covered by the rectangle we just created.
            self.canvas.lift(text_id)

            self.next_tag_x = bbox_tuple[2] + 10

            color_index_pointer += 1
            if color_index_pointer == len(self.colors_index) - 1:
                color_index_pointer = 0

                # self.next_tag_y = bbox_tuple[1]

    def draw_rect(self):
        self.object_id = self.canvas.create_rectangle(self.x, self.y, self.next_tag_x + 3, self.bottom, fill='green',
                                                      outline='black', tags='TagBox')


class Colors():
    def __init__(self, color):
        self.colors_list = ['white', 'snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
                            'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
                            'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
                            'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
                            'light slate gray', 'gray', 'light grey', 'midnight blue', 'navy', 'cornflower blue',
                            'dark slate blue', 'slate blue', 'medium slate blue', 'light slate blue', 'medium blue',
                            'royal blue', 'blue', 'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue',
                            'steel blue', 'light steel blue', 'light blue', 'powder blue', 'pale turquoise',
                            'dark turquoise','medium turquoise', 'turquoise', 'cyan', 'light cyan', 'cadet blue',
                            'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
                            'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green',
                            'spring green',
                            'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
                            'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod',
                            'light goldenrod yellow',
                            'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod',
                            'rosy brown',
                            'indian red', 'saddle brown', 'sandy brown',
                            'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
                            'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink',
                            'light pink',
                            'pale violet red', 'maroon', 'medium violet red', 'violet red',
                            'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
                            'thistle', 'snow2', 'snow3',
                            'snow4', 'seashell2', 'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2',
                            'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
                            'PeachPuff3', 'PeachPuff4', 'NavajoWhite2', 'NavajoWhite3', 'NavajoWhite4',
                            'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
                            'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
                            'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
                            'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
                            'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
                            'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
                            'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
                            'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
                            'LightSkyBlue3', 'LightSkyBlue4', 'SlateGray1', 'SlateGray2', 'SlateGray3',
                            'SlateGray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
                            'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
                            'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
                            'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
                            'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
                            'cyan4', 'DarkSlateGray1', 'DarkSlateGray2', 'DarkSlateGray3', 'DarkSlateGray4',
                            'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
                            'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
                            'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
                            'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
                            'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
                            'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
                            'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
                            'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
                            'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
                            'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
                            'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
                            'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
                            'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
                            'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
                            'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
                            'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
                            'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
                            'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
                            'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
                            'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
                            'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
                            'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
                            'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
                            'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
                            'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
                            'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
                            'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
                            'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
                            'gray1', 'gray2', 'gray3', 'gray4', 'gray5', 'gray6', 'gray7', 'gray8', 'gray9', 'gray10',
                            'gray11', 'gray12', 'gray13', 'gray14', 'gray15', 'gray16', 'gray17', 'gray18', 'gray19',
                            'gray20', 'gray21', 'gray22', 'gray23', 'gray24', 'gray25', 'gray26', 'gray27', 'gray28',
                            'gray29', 'gray30', 'gray31', 'gray32', 'gray33', 'gray34', 'gray35', 'gray36', 'gray37',
                            'gray38', 'gray39', 'gray40', 'gray42', 'gray43', 'gray44', 'gray45', 'gray46', 'gray47',
                            'gray48', 'gray49', 'gray50', 'gray51', 'gray52', 'gray53', 'gray54', 'gray55', 'gray56',
                            'gray57', 'gray58', 'gray59', 'gray60', 'gray61', 'gray62', 'gray63', 'gray64', 'gray65',
                            'gray66', 'gray67', 'gray68', 'gray69', 'gray70', 'gray71', 'gray72', 'gray73', 'gray74',
                            'gray75', 'gray76', 'gray77', 'gray78', 'gray79', 'gray80', 'gray81', 'gray82', 'gray83',
                            'gray84', 'gray85', 'gray86', 'gray87', 'gray88', 'gray89', 'gray90', 'gray91', 'gray92',
                            'gray93', 'gray94', 'gray95', 'gray97', 'gray98', 'gray99', 'black']

        self.i = 0
        self.max_i = len(self.colors_list)-1
        self.set_color(color)

    def set_color(self, color):
        self.i = self.colors_list.index(color)

    def next_color(self):
        self.i += 1
        if self.i > self.max_i:
            self.i = 0
        return self.colors_list[self.i]

    def last_color(self):
        self.i -= 1
        if self.i < 0:
            self.i = self.max_i
        return self.colors_list[self.i]

    def get_color(self):
        debug('get_color i={}, {}'.format(self.i, self.colors_list[self.i]))
        return self.colors_list[self.i]

    def get_color_info(self):
        return '{} [{}/{}]'.format(self.colors_list[self.i], str(self.i+1), str(self.max_i+1))


class ColorPalette():
    def __init__(self):
        self._bgcolor_obj = Colors('white')
        self._lncolor_obj = Colors('black')
        self._bgcolor = self._bgcolor_obj.get_color()
        self._lncolor = self._lncolor_obj.get_color()

    @property
    def bgcolor(self):
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, color):
        self._bgcolor_obj.set_color(color)
        self._bgcolor = color

    def next_bgcolor(self):
        self._bgcolor = self._bgcolor_obj.next_color()

    def last_bgcolor(self):
        self._bgcolor = self._bgcolor_obj.last_color()

    def get_bgcolor_info(self):
        return self._bgcolor_obj.get_color_info()

    @property
    def lncolor(self):
        return self._lncolor

    @lncolor.setter
    def lncolor(self, color):
        self._lncolor_obj.set_color(color)
        self._lncolor = color

    def next_lncolor(self):
        self._lncolor = self._lncolor_obj.next_color()

    def last_lncolor(self):
        self._lncolor = self._lncolor_obj.last_color()

    def get_lncolor_info(self):
        return self._lncolor_obj.get_color_info()


class LableState():
    def __init__(self):
        self.states = ['none', 'title', 'tag@title', 'status']
        self.i = 0

    def set_state(self, state):
        self.i = self.states.index(state)

    def next_state(self):
        self.i += 1
        if self.i > len(self.states)-1:
            self.i = 0

    def last_state(self):
        self.i -= 1
        if self.i < 0:
            self.i = len(self.states)-1

    @property
    def state(self):
        return self.states[self.i]


class Timeline():
    _timeline_types = ['hourly', 'daily', 'monthly']
    object_type = 'timeline'

    def __init__(self, key, group, theme, statusbox, keyboard, canvas, timeline_type,
                 time=datetime.datetime.now(), draw_labels=True):

        self.key = key

        self._is_original = True
        self._type = None
        self._time = time
        self.total_days = None
        self.tags = []
        self.x_moved_since_last_draw = 0
        self.label_state = LableState()
        self.hidden = False
        self.sync_time = True

        # Local color palette.
        self.colorpalette = ColorPalette()
        # Default color palette pointer to group color palette.
        self.colors = group.colorpalette
        # Keep colors here in sync with the colors of the group.
        self._sync_colors = True

        self.types = {}

        self.types['hourly'] = {
            'label_format': '%I%p',
            'days_displayed': .5,
            'min_days_displayed': .1,
            'max_days_displayed': 1,
            'move_days': 15 / 1440,
            'anchor_time_to': 'middle'
        }

        self.types['daily'] = {
            'label_format': '%d%a',
            'days_displayed': 5,
            'min_days_displayed': 2,
            'max_days_displayed': 15,
            'move_days': 8 / 24,
            'anchor_time_to': 'middle'
        }

        self.types['monthly'] = {
            'label_format': '%B %y',
            'days_displayed': 90,
            'min_days_displayed': 60,
            'max_days_displayed': 180,
            'move_days': 4,
            'anchor_time_to': 'middle'
        }

        self.types['monthly2'] = {
            'label_format': '%B %y',
            'days_displayed': 15,
            'min_days_displayed': 15,
            'max_days_displayed': 60,
            'move_days': 4,
            'anchor_time_to': 'right'
        }

        self.draw_tag = 'draw{}'.format(self.key)
        self.draw_details_tag = 'draw_details{}'.format(self.key)

        self.canvas = canvas
        self.theme = theme

        self.group = group
        self.group_name = group.group_name

        self.items = group.items

        self.statusbox = statusbox
        # Initializes a pointer to the timeline type so we can rotate through the various types if required.
        self.timeline_types = self.iter_timeline_types()
        self.type = timeline_type
        self.bottom = 100
        self._height = 100
        self._y = 0
        # X always 0 for now.
        self.x = 0
        self.width = None
        self.left = None
        self.right = None
        self.top = None
        self.middle = None
        self.begin_time = None
        self.end_time = None
        self.object_id = None
        self.draw_labels = draw_labels
        self._highlight_selected = False
        self.load()

    @property
    def sync_colors(self):
        """
        Return the value of _sync_colors.

        :return: Return True or False
        """
        return self._sync_colors

    @sync_colors.setter
    def sync_colors(self, sync_colors_tf):
        """
        Do you want to keep this timelines colors in sync with the groups colors?

        When True set the color palette to the group and when False set the color palette to local timeline.

        :param bool_sync_colors: Set _sync_colors to True or False.
        :return:
        """
        self._sync_colors = sync_colors_tf
        if sync_colors_tf:
            self.colors = self.group.colorpalette
            self.draw()
        else:
            self.colorpalette.bgcolor = self.colors.bgcolor
            self.colorpalette.lncolor = self.colors.lncolor
            self.colors = self.colorpalette

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        self.bottom = self._y + self._height

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height
        self.bottom = self._y + self._height

    def load(self):
        config = bin.open_dict(dict_name='timeline_{}'.format(self.key), directory=self.group.directory)
        if len(config):
            for key in config.keys():
                if hasattr(self, key):
                    setattr(self, key, config[key])
            self.colors.bgcolor = config['bgcolor']
            self.colors.lncolor = config['lncolor']
            self.label_state.set_state(state=config['_label_state'])

    def save(self):
        config = {'draw_labels': self.draw_labels,
                  # Use _ to make sure we don't cause a conflict in the load hasattr setattr loop.
                  '_label_state': self.label_state.state,
                  'height': self.height,
                  'type': self._type,
                  'bgcolor': self.colors.bgcolor,
                  'lncolor': self.colors.lncolor,
                  'hidden': self.hidden,
                  'sync_time': self.sync_time,
                  'sync_colors': self.sync_colors}

        bin.save_dict(dict_name='timeline_{}'.format(self.key), dict_object=config, directory=self.group.directory)

    @property
    def days_displayed(self):
        return self.types[self.type]['days_displayed']

    @days_displayed.setter
    def days_displayed(self, days_displayed):
        if days_displayed >= self.types[self.type]['min_days_displayed'] and days_displayed <= self.types[self.type][
            'max_days_displayed']:
            self.types[self.type]['days_displayed'] = days_displayed

    def draw(self, y=None):

        debug('Timeline.draw')

        self.x_moved_since_last_draw = 0

        if y is not None:
            self.y = y

        self.canvas.delete(self.draw_tag)

        self.top = self.y
        self.bottom = self.y + self.height
        self.width = self.canvas.winfo_reqwidth() * 5
        self.left = self.x - self.canvas.winfo_reqwidth() * 2
        self.right = self.x + self.canvas.winfo_reqwidth() * 3
        self.middle = self.x + self.canvas.winfo_reqwidth() / 2

        self.object_id = self.canvas.create_rectangle(self.left - 1000,
                                                      self.top,
                                                      self.right + 1000,
                                                      self.bottom,
                                                      fill=self.colors.bgcolor,
                                                      outline=self.colors.lncolor,
                                                      tags=(self.draw_tag, 'timelines'))

        self.canvas.tag_lower(self.object_id)

        #self.canvas.delete('timeline_label_{}'.format(self.key))

        # # Draw the text on timeline which shows which tags this timeline shows.
        # text_id = self.canvas.create_text(self.x+10, self.y+15, font=self.theme.font(size='<'), text='@work, @foo',
        # anchor='w', fill=self.theme.font_color,
        #                                   tags=('timeline_label_{}'.format(self.key), 'timelines'))
        #
        # # Get the coordinates of the corners of the text box.
        # bbox_tuple = self.canvas.bbox(text_id)
        #
        # # Create a rectangle to contain the text we want to write with some margins.
        # self.canvas.create_rectangle(bbox_tuple[0], bbox_tuple[1], bbox_tuple[2], bbox_tuple[3], fill='gray',
        #                              outline='black', tags=('timeline_label_box_{}'.format(self.key), 'timelines'))
        #
        # # Lift the text so it is not covered by the rectangle we just created.
        # self.canvas.lift('timeline_label_{}'.format(self.key))

        self.draw_details(delete=True)

    def draw_details(self, delete=True):
        """
        Draw the lines and labels for the given timeline.
        """

        debug('Timeline.draw_details')

        if delete:
            self.canvas.delete(self.draw_details_tag)

        # The red line needs to be redrawn every time.
        self.canvas.delete('red' + self.draw_details_tag)

        font_size = '<<'

        self.total_days = self.days_displayed * 5

        if self.type == 'hourly':
            self.begin_time = self.time - datetime.timedelta(days=self.days_displayed / 2 + self.days_displayed * 2)
            label_time = self.begin_time.replace(minute=0, second=0, microsecond=0)
        elif self.type == 'daily':
            self.begin_time = self.time - datetime.timedelta(days=self.days_displayed / 2 + self.days_displayed * 2)
            label_time = self.begin_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.type == 'monthly':
            self.begin_time = self.time - datetime.timedelta(days=self.days_displayed / 2 + self.days_displayed * 2)
            label_time = self.begin_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.type == 'monthly2':
            self.begin_time = self.time - datetime.timedelta(days=self.days_displayed * 3)
            label_time = self.begin_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        self.end_time = self.begin_time + datetime.timedelta(days=self.days_displayed * 5)

        x = self._get_x_from_time(label_time)
        first_x = x

        span = 999
        for i in range(1, 500):

            label_text = bin.to_char(label_time, self.types[self.type]['label_format'])
            self.canvas.create_line(x, self.top, x, self.bottom, fill=self.colors.lncolor, tags=(self.draw_details_tag))
            self.canvas.create_text(x + 3, self.bottom - 8, font=self.theme.font(size=font_size), text=label_text,
                                    anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))

            if i == 2:
                span = x - first_x

            if self.type == 'hourly':
                if span > 100:
                    for i in range(1, 4):
                        minute_time = label_time + datetime.timedelta(days=i * 15 / 1440)
                        x = self._get_x_from_time(minute_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill=self.colors.lncolor, tags=(self.draw_details_tag))
                        self.canvas.create_text(x + 3, self.top + 8, font=self.theme.font(size=font_size),
                                                text=str(i * 15), anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))
                label_time = label_time + datetime.timedelta(hours=1)
            elif self.type == 'daily':
                if span > 400:
                    for i in range(1, 24):
                        hourly_time = label_time + datetime.timedelta(hours=i)
                        x = self._get_x_from_time(hourly_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill=self.colors.lncolor, tags=(self.draw_details_tag))
                        self.canvas.create_text(x + 3, self.top + 8, font=self.theme.font(size=font_size), text=str(i),
                                                anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))
                label_time = label_time + datetime.timedelta(hours=24)
            elif self.type == 'monthly':
                if span > 500:
                    for i in range(1, bin.get_number_of_days_in_month_from_datetime(label_time)):
                        daily_time = label_time + datetime.timedelta(hours=i * 24)
                        x = self._get_x_from_time(daily_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill=self.colors.lncolor, tags=(self.draw_details_tag))
                        self.canvas.create_text(x + 3, self.top + 8, font=self.theme.font(size=font_size),
                                                text=str(i + 1), anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))
                label_time = self._get_next_month(label_time)
            elif self.type == 'monthly2':
                if span > 500:
                    for i in range(0, bin.get_number_of_days_in_month_from_datetime(label_time)):
                        t = label_time + datetime.timedelta(days=i)
                        x = self._get_x_from_time(t)
                        # delta=datetime.datetime.now()-t
                        l = bin.to_char(t, '%d')
                        l2 = bin.to_char(t, '%a')
                        self.canvas.create_line(x, self.top, x, self.bottom, fill=self.colors.lncolor, tags=(self.draw_details_tag))
                        self.canvas.create_text(x + 3, self.top + 8, font=self.theme.font(size=font_size), text=str(l),
                                                anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))
                        self.canvas.create_text(x + 3, self.top + 20, font=self.theme.font(size=font_size), text=l2,
                                                anchor='w', fill=self.colors.lncolor, tags=(self.draw_details_tag))
                label_time = self._get_next_month(label_time)

            x = self._get_x_from_time(label_time)

            if label_time > self.end_time:
                break

            # Draw red line @ anchor point.
            if self.type == 'monthly2':
                self.canvas.create_line(self.right, self.top, self.right, self.bottom, fill='red',
                                        tags=('red' + self.draw_details_tag))
            else:
                self.canvas.create_line(self.middle, self.top, self.middle, self.bottom, fill='red',
                                        tags=('red' + self.draw_details_tag))

            # Draw blue line at current time.
            self.draw_line_for_current_time()

        debug(self.items)
        self.draw_items()

    def draw_items(self):

        debug('Timeline.draw_items')
        for item in self.items.iter_items_to_draw():
            if item.group_name == self.group.group_name:
                self.draw_item(item)

    # ToDo: Change display_label to include_lab fsel
    def draw_item(self, item, x=None, y=None, tag=None):

        debug('Timeline.draw_item')

        # Only draw item if the item.tags contains all of timeline.tags
        # if not set(self.tags).issubset(item.tags):
        #    return

        if self.types[self.type]['move_days'] == 0:
            if item.datetime > self.end_time:
                item.datetime = self.end_time - datetime.timedelta(days=self.total_days * .01)
            elif item.datetime < self.begin_time:
                item.datetime = self.begin_time

        if x is not None:
            item.x = x
        else:
            item.x = self._get_x_from_time(item.datetime)

        if y is not None:
            item.y = y
        else:
            item.y = self.y + (self.height * item.y_as_pct_of_height)

        unique_id = '{0}_{1}'.format(self.key, item.key)
        key = 'key={}'.format(item.key)
        tags = '{0} {1} {2} {3} {4} {5}'.format(key, 'BaseItem', item.key, unique_id, self.key, self.draw_details_tag)

        #debug('x={0} y={1}'.format(item.x, item.y))

        self.canvas.delete(unique_id)

        label_tags = tags
        #if item.selected and self.highlight_selected:
        if item.selected and self.items.selected_timeline and self.items.selected_timeline.key == self.key:
            border_width = 2
            outline_color = 'black'
            dash = (1, 2)
            tags += ' TAG_SELECTED'
            label_tags += ' LABEL_SELECTED'
        else:
            border_width = 1
            outline_color = 'black'
            dash = None


        object_id = self.canvas.create_rectangle(item.x, item.y, item.x + item.size, item.y + item.size,
                                                 fill=item.color, outline=outline_color, tags=tags, stipple=None,
                                                 width=border_width, dash=dash)

        label_tags += ' {}_LABEL_TAG'.format(object_id)
        # label_tags = tags
        # Labels are not drawn on every timeline.
        if self.draw_labels:
            if self.label_state.state == 'none':
                label = None
            elif self.label_state.state == 'title':
                label = item.title
            elif self.label_state.state == 'tag@title':
                if len(item.tags) > 0:
                    label = '{0}@{1}'.format(item.tags[0], item.title)
                else:
                    label = item.title
            elif self.label_state.state == 'status':
                if item.status is not None:
                    label = item.status
                else:
                    label = item.title
            x, y, right, bottom = self.canvas.coords(object_id)
            self.canvas.create_text(right + 5, y - 2, text=label, font=self.theme.font(size='<<'), fill="black",
                                    tags=label_tags, anchor="nw", justify="left")

        return object_id

    def draw_line_for_current_time(self):
        # Draw blue line at current time.
        x = self._get_x_from_time(datetime.datetime.now())
        self.canvas.create_line(x, self.top, x, self.bottom, fill='blue', tags=(self.key, self.draw_tag, self.draw_details_tag))

    def _get_x_from_time(self, time):
        r = self.left + (bin.days_between_two_dates(time, self.begin_time) / self.total_days * self.width)
        return r

    def get_time_from_x(self, x):
        x_as_days_from_begin_time = self.total_days * ((abs(self.left) + x) / self.width)
        # ToDo: I don't understand why the +1 is needed here! WHY???? And only works when total days not .5!
        r = self.begin_time + datetime.timedelta(days=x_as_days_from_begin_time)
        return r

    def _get_pct_of_height_from_y(self, y):
        debug2('Timeline._get_pct_of_height_from_y')
        y_as_pct_of_height = abs(y - self.y) / self.height
        return y_as_pct_of_height

    def _get_next_month(self, datetime_object):
        r = datetime_object.replace(day=28) + datetime.timedelta(days=4)
        r = r.replace(day=1)
        return r

    @property
    def highlight_selected(self):
        return self._highlight_selected

    @highlight_selected.setter
    def highlight_selected(self, tf):
        if tf != self._highlight_selected:
            self._highlight_selected = tf
            # ToDo: not sure if I need this or not.
            #self.unselect_all(draw=False)

    def _items_align(self, direction):
        debug('Timeline._items_align: direction={}'.format(direction))
        times = []
        all_selected_items = []

        for item in self.items.all_selected_items():
            all_selected_items.append([item.y, item, item.x])
            times.append(item.datetime)

        number_of_items = len(all_selected_items)

        if direction in ('right', 'left'):
            if direction == 'right':
                time = max(times)
            elif direction == 'left':
                time = min(times)
            for item in self.items.all_selected_items():
                item.datetime = time
        elif direction == 'top':
            sorted_items = bin.sort_lists_in_list(all_selected_items, 0)
            for item in self.items.all_selected_items():
                item.y = sorted_items[0][1].y
                item.y_as_pct_of_height = sorted_items[0][1].y_as_pct_of_height
        elif direction == 'bottom':
            sorted_items = bin.sort_lists_in_list(all_selected_items, 0)
            for item in self.items.all_selected_items():
                item.y = sorted_items[-1][1].y
                item.y_as_pct_of_height = sorted_items[-1][1].y_as_pct_of_height
        elif direction in ('increase_vertical', 'decrease_vertical') and number_of_items > 1:

            rollback = False
            items_modified = []
            distance_between_items = []

            items_sorted_from_top_down = bin.sort_lists_in_list(all_selected_items, 0)
            top_of_first_item = int(items_sorted_from_top_down[0][0])

            for i in range(1, number_of_items):
                distance_between_items.append(items_sorted_from_top_down[i][0] - items_sorted_from_top_down[i - 1][0])

            distance_between_items = min(distance_between_items)

            if distance_between_items > 10:
                multiplier = {'increase_vertical': 1.2, 'decrease_vertical': .8}[direction]
            else:
                multiplier = {'increase_vertical': 2, 'decrease_vertical': .2}[direction]

            distance_between_items = int(distance_between_items * multiplier)

            # Vertical distance can't be less than 0.
            if distance_between_items <= 0:
                distance_between_items = {'increase_vertical': 5, 'decrease_vertical': 0}[direction]

            debug2('distance_between_items={}'.format(distance_between_items))
            # Get the y position of the first item as our starting point.
            y = top_of_first_item
            for item in items_sorted_from_top_down:
                rollback = (y + item[1].size > self.bottom)
                pct_of_height = self._get_pct_of_height_from_y(y)
                rollback = pct_of_height is None or rollback
                if rollback:
                    break
                item[1].y = y
                item[1].y_as_pct_of_height = pct_of_height
                items_modified.append(item[1])
                y += distance_between_items

            if rollback:
                debug('rollback!')
                for item in items_modified:
                    item.restore()

        elif direction in ('increase_horizontal', 'decrease_horizontal'):

            items_sorted_from_left_to_right = bin.sort_lists_in_list(all_selected_items, 2)
            minutes_between_items = []

            for i in range(1, number_of_items):
                minutes_between_items.append(
                    bin.minutes_between_two_dates(items_sorted_from_left_to_right[i][1].datetime,
                                                  items_sorted_from_left_to_right[i - 1][1].datetime))

            minutes_between_items = int(min(minutes_between_items))

            if minutes_between_items > 10:
                multiplier = {'increase_horizontal': 1.2, 'decrease_horizontal': .8}[direction]
            else:
                multiplier = {'increase_horizontal': 2, 'decrease_horizontal': .2}[direction]

            minutes_between_items = int(minutes_between_items * multiplier)

            # Horizontal distance can't be less than 0.
            if minutes_between_items <= 0:
                minutes_between_items = {'increase_horizontal': 5, 'decrease_horizontal': 0}[direction]

            debug('minutes_between_items={}'.format(minutes_between_items))
            t = items_sorted_from_left_to_right[0][1].datetime
            for item in items_sorted_from_left_to_right:
                item[1].datetime = t
                t = t + datetime.timedelta(minutes=minutes_between_items)

        self.draw_items()

    def move2(self, days):
        time_to_move_to = self.time + datetime.timedelta(days=days)
        x_to = self._get_x_from_time(time_to_move_to)
        x_from = self._get_x_from_time(self.time)
        x = x_from - x_to
        # x_to_move_to=self._get_x_from_time(time)
        #x_now=self._get_x_from_time(self.time)
        #x=x_now-x_to_move_to
        #debug('Timeline.move: x={}'.format(x))
        self.canvas.move('moves', x, 0)
        self.time = time_to_move_to

    def move(self, time):

        #debug('Timeline.move: time={}'.format(time))

        if self.type == 'monthly2' and time > datetime.datetime.now():
            time = datetime.datetime.now()

        if self.types[self.type]['move_days'] > 0:
            # coords=self.canvas.coords(self.object_id)
            x_to_move_to = self._get_x_from_time(time)
            x_now = self._get_x_from_time(self.time)
            x = x_now - x_to_move_to

            self.canvas.move(self.draw_details_tag, x, 0)
            self.time = time
            self.x_moved_since_last_draw -= x
            if self.x_moved_since_last_draw / self.left > .85 or self.x_moved_since_last_draw / self.right > .85:
                self.draw()

    def redraw(self):
        self.draw()

    def iter_timeline_types(self):
        for t in self._timeline_types:
            yield t

    def switch_type(self):
        debug('Timeline: switch_type')
        try:
            self.type = next(self.timeline_types)
        except StopIteration:
            self.timeline_types = self.iter_timeline_types()
            self.type = next(self.timeline_types)
        self.draw()

    def label_modes(self):
        debug('Timeline.label_modes')
        for l in self._label_modes:
            yield l

    def next_label_mode(self):
        debug('Timeline.next_label_mode')
        try:
            self.label_mode = next(self.foo)
        except StopIteration:
            self.foo = self.label_modes()
            self.label_mode = next(self.foo)
        self.draw_items()

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        if self.types[self.type]['move_days'] > 0:
            self._time = time

    @property
    def total_selected(self):
        return self.items.total_selected

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def unselect_items_that_are_selected(self, redraw_affected_items=True):
        debug('Timeline.unselect_items_that_are_selected')
        # Set selected attribute to false for all items.
        for item in self.items.all_items():
            if item.selected:
                item.selected = False
                if redraw_affected_items:
                    self.draw_item(item)
        self.items.total_selected = 0


class BaseItem():
    COLORS = ['white', 'grey', 'black', 'green', 'blue', 'yellow', 'red']

    def __init__(self, group_name, root_folder, text, x=None, datetime=None, y=None, y_pct=None, primary_tag=None):
        self.group_name = group_name
        # Root folder for other files and folders.
        self._root_folder = root_folder
        # Unique 20 character key generated automatically.
        self.key = bin.random_string(20)
        # Title of item, does not need to be unique.
        self.title = None
        # Used to store x/y position within the app at various points.
        self.x = x
        self._y = y
        # Used to position the item on the hourly, daily and monthly timeline.
        self._y_as_pct_of_height = y_pct
        self._backup = {}
        # Path to image to display instead of a shape.
        self.image_path = None
        # Size of image or shape.
        self.size = 8
        self.type = None
        self.datetime = datetime
        self.color = 'blue'
        self._selected = False
        self.folder = None
        self.description = None
        self._text = text
        # ToDo: Sort of conflicts with the method get_primary_tag. Make clearer.
        self.primary_tag = primary_tag
        self._tags = []
        # There is a getter/setter for this property. When an item is deleted it is moved to a _deleted_ folder.
        # Will add a purge process which removes deleted items. Also needs to be some sort of automatic purge
        # which takes place.
        self._deleted = False
        self._purged = False
        self.hidden = False
        # Stores entire status history including a datetime stamp.
        self._status = []
        # Stores only the text of the last status.
        self.status_text_only = None
        self.label_int = 0
        # self.display_format='none'
        self._parse_text(text)

        # At a minimum title must be set, if not we just assign text to it, but this should already be done.
        if not self.title:
            self.title = text

        #self.storage_folder = '{0}_{1}'.format(bin.date_to_string(), bin.get_valid_path_name_from_string(self.title))
        self.storage_folder = os.path.join(
            self._root_folder,
            '{}_{}'.format(bin.date_to_string(), bin.get_valid_path_name_from_string(self.title)))

        self.storage_folder = bin.add_backslash_to_backslash(self.storage_folder)
        bin.mkdir(self.storage_folder)

    def add_tag(self, tag):
        if tag not in self._tags:
            self._tags.append(tag)

    @property
    def y_as_pct_of_height(self):
        return self._y_as_pct_of_height

    @y_as_pct_of_height.setter
    def y_as_pct_of_height(self, pct):
        self._backup['y_as_pct_of_height'] = self._y_as_pct_of_height
        self._y_as_pct_of_height = pct

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._backup['y'] = self._y
        self._y = y

    def restore(self):
        if 'y_as_pct_of_height' in self._backup.keys():
            self._y_as_pct_of_height = self._backup['y_as_pct_of_height']
        if 'y' in self._backup.keys():
            self._y = self._backup['y']

    def patch(self):
        """
        Some housekeeping when we initially load the item from the .dat file.
        """
        self._selected = False
        if not hasattr(self, '_y_as_pct_of_height'):
            self._y_as_pct_of_height = None
        if not hasattr(self, '_backup'):
            self._backup = {}
        if not hasattr(self, '_y'):
            self._y = self.y
            # if self.y is None:
            # self.y=10

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._parse_text(text)

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags_list):
        tags_list = bin.remove_duplicates_from_list(tags_list)
        tags_list = [x.lower() for x in tags_list]
        self._tags = tags_list

    def get_primary_tag(self):
        if self.has_tags():
            return self._tags[0]
        else:
            return None

    def has_tags(self):
        if len(self._tags) > 0:
            return True
        else:
            return False

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, tf):
        if tf == True:
            self._selected = True
        else:
            self._selected = False

    @property
    def status(self):
        return self.status_text_only

    @status.setter
    def status(self, text):
        # Status history is stored in a list, with most recent status first, we also add a timestamp.
        self._status.insert(0, bin.to_char(datetime.datetime.now(), '%a %b %d %I:%M %p') + ' ' + text + '\n')
        self.status_text_only = text
        # If label display is using status, we need to force it to update.
        # Todo: This is ugly.
        self.label_int = self.label_int

    def all_statuses(self):
        for status in self._status:
            yield status

    @property
    def purged(self):
        return self._purged

    @purged.setter
    def purged(self, purged_true_false):
        if purged_true_false == True:
            self._purged = True
            # Save must occur before the move or it recreates the original directory defined by folder_path.
            # self.save()
            # debug('BaseItem: *** Moving {} to _deleted_'.format(self.folder_path))
            #bin.mv(self.folder_path, os.path.join(self.folder_path, '..', '_deleted_'))
        else:
            # Todo: This can never happen
            self._purged = False

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, deleted_true_false):
        if deleted_true_false == True:
            self._deleted = True
            # Save must occur before the move or it recreates the original directory defined by folder_path.
            # self.save()
            # debug('BaseItem: *** Moving {} to _deleted_'.format(self.folder_path))
            #bin.mv(self.folder_path, os.path.join(self.folder_path, '..', '_deleted_'))
        else:
            # Todo: Need to add un-delete feature.
            self._deleted = False

    def move(self, app_folder):
        None

    def save(self):
        debug('BaseItem.save')
        data_folder = os.path.join(self.storage_folder, '_data_')
        bin.mkdir(data_folder)
        bin.save_database2(os.path.join(data_folder, self.key), object=self)

        # def load(self, dict):

    # for key in dict.keys():
    #            setattr(self, key, dict[key])

    def _parse_text(self, text):
        None


class Link(BaseItem):
    COLORS = ['light sky blue']

    def __init__(self, group_name, root_folder, text, x=None, datetime=None, y=None, y_pct=None, primary_tag=None):
        super().__init__(group_name, root_folder, text, x, datetime, y, y_pct, primary_tag=None)
        self.color = 'light sky blue'
        self.type = 'link'
        # self._parse_text(self.text)

    def _parse_text(self, text):
        """
        Links are created in this fashion.

        http://google.com <Google> [tag,tag]
        """

        debug('Link._parse_text: text={}'.format(text))
        # Grab http link
        if text.find('http') > 0:
            link = text.split(' ')[0].strip()
            text = text.split(' ', 1)[1]
            self.title = link

        # Alternative text is in last set of angle brackets if it exist.
        if text.rfind('<') > 0:
            b = text.rfind('<')
            e = text.rfind('>')
            if b < e:
                self.title = text[b + 1:e]
                text = text[0:b] + text[e + 1:]

        # Everything in last set of brackets are tags.
        are_tags = []
        if text.rfind('['):
            b = text.rfind('[')
            e = text.rfind(']')
            if b < e:
                are_tags = text[b + 1:e].split(',')
                are_tags = [t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags = []

        self.tags = are_tags


class Remark(BaseItem):
    COLORS = ['yellow']

    def __init__(self, group_name, root_folder, text, x=None, datetime=None, y=None, y_pct=None, primary_tag=None):
        super().__init__(group_name, root_folder, text, x, datetime, y, y_pct, primary_tag=None)
        self.color = 'yellow'
        self.type = 'remark'
        #self._text=text
        #self._parse_text(self._text)

    def _parse_text(self, text):
        """
        Remarks are created in this fashion.
        
        >Remark [tag,tag]
        """
        debug('Remark._parse_text: {}'.format(text))
        if self._text.rfind('>') == 0:
            self._text = self._text.split('>')[1]

        are_tags = []
        if self._text.rfind('['):
            b = self._text.rfind('[')
            e = self._text.rfind(']')
            if b < e:
                are_tags = self._text[b + 1:e].split(',')
                are_tags = [t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags = []

        self.tags = are_tags
        if len(are_tags) > 0:
            self.title = self._text[0:b] + self._text[e + 1:]
        else:
            self.title = self._text


class Task(BaseItem):
    COLORS = ['green', 'blue', 'red']

    def __init__(self, group_name, root_folder, text, x=None, datetime=None, y=None, y_pct=None, primary_tag=None):
        super().__init__(group_name, root_folder, text, x, datetime, y, y_pct, primary_tag=None)
        self.type = 'task'
        #self._parse_text(text)
        self.color = 'green'

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self._parse_text(text)

    def _parse_text(self, text):
        """
        Take the input text and parse out tags, title and current status.

        Title <status> [tag, tag]
        tag@Title <status> [tag,tag]

        """
        debug('Task._parse_input_text: {}'.format(text))

        # Values before the first '@' are tags and should be in a comma separated list
        # Some tags are special, like colors, only the first color will apply.

        at_tag = None
        if text.find('@') > 0:
            tag = text.split('@')[0].strip()
            if ' ' not in tag:
                at_tag = tag
                text = text.split('@')[1]

        debug('! tags={0} text={1}'.format(self.tags, text))

        # Status is in last set of angle brackets if it exist.
        if text.rfind('<') > 0:
            b = text.rfind('<')
            e = text.rfind('>')
            if b < e:
                self._status = text[b + 1:e]
                text = text[0:b] + text[e + 1:]

        # Everything in last set of brackets are tags.
        are_tags = []
        if text.rfind('['):
            b = text.rfind('[')
            e = text.rfind(']')
            if b < e:
                are_tags = text[b + 1:e].split(',')
                are_tags = [t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags = []
                if len(are_tags) > 0:
                    text = text[0:b] + text[e + 1:]

        if at_tag:
            are_tags.append(at_tag)
        self.tags = are_tags

        debug('! tags={0} text={1}'.format(self.tags, text))

        self.title = text


class Items():
    # List of groups of items which can be drawn, either hidden, delete or not hidden/deleted items.
    _display_modes = ['default', 'hidden', 'deleted']

    def __init__(self, directory):

        self.items = {}
        self.folder_path = directory
        self.display_modes = self.get_next_display_mode()
        self.display_mode = next(self.display_modes)
        self.tags = []
        self.selected_timeline = None

        deleted = re.compile('.*_deleted_.*')
        # Find all items. Each item has a _data_ directory.
        for data_dir in bin.find(root=directory, type='d', name='_data_'):
            # Ignore anything with _deleted_ in the path.
            if not re.match(deleted, data_dir):
                # The item is stored in the .dat file.
                for file in bin.find(root=data_dir, type='f', name='.*\.dat'):
                    key = os.path.basename(file).replace('.dat', '')
                    d = bin.open_database2(file.replace('.dat', ''))
                    debug('Adding item to Items.items, {}'.format(d.title))
                    self.items[key] = d
                    d.patch()

        # if the item is not shared and not the same version, patch it and save
        # if the item is shared and the version does not match mark it as read only
        # items should have a save all and each item should also have a save

        # should add a load for above with a directory name, then we can add
        # directories to the timeline and use the same items class.

        self._total_selected = 0

        self.patch()

    def add_item(self, group_name, item_type, text, y_pct, datetime, primary_tag):

        debug('Items.add_item')

        """ Create a new item associated with the given timeline group. """

        # Note, we can't pass group here because we won't be able to pickle the item object easily. So we use
        # group_name instead.

        if item_type == 'link':
            item = Link(group_name=group_name, root_folder=self.folder_path, text=text, datetime=datetime, y_pct=y_pct)
        elif item_type == 'remark':
            item = Remark(group_name=group_name, root_folder=self.folder_path, text=text, datetime=datetime, y_pct=y_pct)
        else:
            item = Task(group_name=group_name, root_folder=self.folder_path, text=text, datetime=datetime, y_pct=y_pct,
                        primary_tag=primary_tag)

        # Store a reference in Items.items.
        self.items[item.key] = item
        item.save()

        # Rebuild the list of unique tags for self.tags.
        if primary_tag:
            if primary_tag not in self.tags:
                self.tags.append(primary_tag)

    def delete_selected_items(self):
        debug('Items.delete_selected_items')
        for item in self.iter_selected_items():
            item.deleted = True
        self.save()
        # Some tags may no longer be used, therefore rebuild the tags list.
        self.tags = []
        for item in self.items:
            # ToDo: hasattr is for patching only.
            if hasattr(item, 'primary_tag') and item.primary_tag and item.primary_tag not in self.tags:
                self.tags.append(item.primary_tag)

    def hide_selected_items(self):
        debug('Items.hide_selected_items')
        for item in self.iter_selected_items():
            item.hidden = True

    def get_next_display_mode(self):
        debug('Items.get_next_display_mode')
        for g in self._display_modes:
            yield g

    def next_display_group(self):
        try:
            self.display_mode = next(self.display_modes)
        except StopIteration:
            self.display_modes = self.get_next_display_mode()
            self.display_mode = next(self.display_modes)
        debug('Items.next_display_group: {}'.format(self.display_mode))

    def patch(self):
        None
        #for item in self.all_items():
        #    None

    @property
    def total_selected(self):
        return self._total_selected

    @total_selected.setter
    def total_selected(self, total_selected):
        self._total_selected = total_selected

    def iter_items_to_draw(self):
        debug('Items.iter_items_to_draw')
        for item in self.items.values():
            if item.deleted and self.display_mode == 'deleted':
                yield item
            elif item.hidden and self.display_mode == 'hidden':
                yield item
            elif not item.deleted and not item.hidden and self.display_mode == 'default':
                yield item

    def all_items(self):
        return self.items.values()

    def iter_selected_items(self):
        for item in self.all_items():
            if item.selected:
                yield item

    def all_selected_items(self):
        for item in self.all_items():
            if item.selected:
                yield item

    def get_by_key(self, key):
        try:
            item = self.items[key]
        except:
            item = None
        return item

    def delete_by_key(self, key, save=True):
        """
        Delete an item.
        """
        self.items[key].deleted = True
        del self.items[key]

    def save(self):
        for item in self.all_items():
            item.save_groups()

    def select(self, item):
        """
        Mark an item as selected.
        """
        if item and not item.selected:
            item.selected = True
            self._total_selected += 1
            debug('*** total_selected={}'.format(self._total_selected))

    def unselect(self, item):
        """
        Mark an item as unselected.
        """
        if item.selected:
            item.selected = False
            self._total_selected -= 1
            debug('*** total_selected={}'.format(self._total_selected))

    def _update_count(self):
        self.group_count = len(self.groups)


class Group():
    def __init__(self, group_directory, group_theme, group_statusbox, group_keyboard, group_canvas):
        self.key = bin.random_string(20)
        self.colorpalette = ColorPalette()
        self.directory = group_directory
        self.theme = group_theme
        self.statusbox = group_statusbox
        self.keyboard = group_keyboard
        self.canvas = group_canvas
        self.group_name = 'default'
        self.timelines = []
        self.items = Items(directory=group_directory)
        self.bottom = 0
        self.load()
        debug('Group {} loaded'.format(self.key))


    def delete_timeline(self, timeline):
        debug('Group.delete_timeline')
        if self.timeline_count > 1:
            self.timelines.remove(timeline)
            timeline = None
        else:
            debug('You must keep at least one timeline.')
            self.statusbox.text = 'You must keep at least one timeline.'

    def add_timeline(self, key=None):
        if not key:
            key = bin.random_string(20)
        t = Timeline(key=key, group=self, theme=self.theme, statusbox=self.statusbox,
                     keyboard=self.keyboard, timeline_type='daily', canvas=self.canvas)
        self.timelines.append(t)
        return t

    def copy_timeline(self, timeline):
        attributes = [
            'height',
            'time',
            'type',
        ]

        t = self.add_timeline()
        t.y = timeline.bottom
        t.sync_colors = timeline.sync_colors
        if not t.sync_colors:
            t.colors = t.colorpalette
            t.colors.bgcolor = timeline.colors.bgcolor
            t.colors.lncolor = timeline.colors.lncolor

        for a in attributes:
            setattr(t, a, getattr(timeline, a))

        self.bottom = t.bottom

    def load(self):
        config = bin.open_dict(dict_name='group', directory=self.directory)
        if len(config) > 0:
            debug('Applying config to group.')
            for key in config.keys():
                if hasattr(self, key):
                    setattr(self, key, config[key])
            self.colorpalette.bgcolor = config['bgcolor']
            self.colorpalette.lncolor = config['lncolor']

        timeline_keys = bin.open_list(list_name='timelines', directory=self.directory)
        if len(timeline_keys) > 0:
            debug('timeline_keys={}'.format(timeline_keys))
            for key in timeline_keys:
                debug('Loading timeline from disk.')
                self.add_timeline(key=key)
        else:
            debug('Loading default timeline.')
            self.add_timeline()

    def save(self):
        debug('*** Saving Group ***')
        config = {'key': self.key,
                  'group_name': self.group_name,
                  'bgcolor': self.colorpalette.bgcolor,
                  'lncolor': self.colorpalette.lncolor}
        bin.save_dict(dict_name='group', dict_object=config, directory=self.directory)
        timeline_keys = []
        for t in self.timelines:
            t.save()
            timeline_keys.append(t.key)
        bin.save_list(list_name='timelines', list_object=timeline_keys, directory=self.directory)

    def set_background_color(self, color):
        for t in self.timelines:
            if t.sync_colors:
                t.background_color = color

    @property
    def timeline_count(self):
        return len(self.timelines)

    @property
    def visible_timeline_count(self):
        i = 0
        for t in self.timelines:
            if not t.hidden:
                i += 1
        return i

    #@timeline_count.setter
    #def timeline_count(self, None):
    #    None

class Dragging():
    def __init__(self):
        self.dragging = False
        self.item = None
        self.object_id = None
        self.coords = None
        self.time = None
        self.x = None
        self.y = None
        self.timeline = None
        self.x0 = None
        self.y0 = None
        self.selectbox_object_id = None
        self.dragging_timeline = False

    def is_dragging_selectbox(self):
        if self.selectbox_object_id is not None:
            return True
        else:
            return False

    def is_dragging_item(self):
        if self.item is not None:
            return True
        else:
            return False

    def is_dragging_timeline(self):
        if self.dragging_timeline:
            return True
        else:
            return False



class TaskManager():
    def __init__(self, root, canvas, theme, **kwargs):
        debug('TaskManager.__init__')
        self.root = root
        self.canvas = canvas
        self.theme = theme
        # Stores a reference to each timeline object.
        self.timelines = []
        self.colors = Colors('white')

        self.statusbox = statusbox.StatusBox(root=self.root, canvas=self.canvas, theme=self.theme)

        self.drawers = []
        self.bottom = 0

        # Just a temporary dict which we can use for this and that.
        self.temp = {}

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.keyboard = keyboard.Keyboard(canvas=self.canvas, cbfunc=(lambda dict: self.keypress(dict)))
        self.x = 0
        self.y = 0
        # Stores information during drag and drop operations.
        self.dragging = Dragging()
        self.mouse = (0, 0)

        self._build_menus()

        # Reference to application root_path.
        self.app_folder = bin.application_root_path()

        self.default_deleted_items_path = None
        # ToDo: look at this
        self.set_default_deleted_items_path()

        self.all_groups_root_directory = os.path.join(self.app_folder, 'taskrx')
        self.default_group_root_folder = os.path.join(self.all_groups_root_directory, 'default')
        bin.mkdir(self.default_group_root_folder)
        # Points to other directories on local or shared file system which contain items and timelines.
        self.other_group_root_folders = bin.open_list(list_name='other_group_root_folders', directory=self.app_folder)
        # The complete list of folders we scan for items and timelines.
        self.all_group_folders = [self.default_group_root_folder] + self.other_group_root_folders
        self.groups = []
        self.load()
        self.draw()

    def visible_timelines(self):
        for g in self.groups:
            for t in g.timelines:
                if not t.hidden:
                    yield t

    def set_default_deleted_items_path(self):
        # Set the folder location for deleted items, sort of like a recycle bin.
        self.default_deleted_items_path = os.path.join(self.app_folder, 'items', '_deleted_')
        bin.mkdir(self.default_deleted_items_path)

    def load(self):
        for group_folder in self.all_group_folders:
            g = Group(group_directory=group_folder, group_theme=self.theme, group_statusbox=self.statusbox,
                      group_keyboard=self.keyboard, group_canvas=self.canvas)
            self.groups.append(g)
        for t in g.timelines:
            self.timelines.append(t)

    def save(self):
        """ Save some details about each timeline and save groups dictionary so we can re-load. """
        debug('TaskManager.save')
        for group in self.groups:
            group.save()

    def get_new_timeline(self, group):
        timeline = None
        if group.timeline_count < 3:
            timeline = Timeline(key=bin.random_string(20), group=group, theme=self.theme, statusbox=self.statusbox,
                                keyboard=self.keyboard, timeline_type='daily', y=self.bottom, height=100,
                                time=datetime.datetime.now(), canvas=self.canvas, draw_labels=True)
            self.timelines.append(timeline)
            self.bottom = timeline.bottom
            self.save()
        else:
            self.statusbox.text = 'Only 3 timelines are allowed for each group.'
        return timeline


    def draw(self, x=None, y=None, width=None):

        debug('Taskmanager.draw')

        if x is None:
            x = self.x
        if width is None:
            width = self.canvas.winfo_reqwidth()
        if y is None:
            _y = 0
        else:
            _y = y

        self.statusbox.draw(x=x, y=_y, width=width)
        _y = self.statusbox.bottom

        for timeline in self.visible_timelines():
            timeline.draw(y=_y)
            _y = timeline.bottom

    def init(self):
        self.width = self.canvas.winfo_reqwidth()
        self.canvas.focus_set()

        self.canvas.tag_bind("timelines", "<ButtonPress-1>", self._timeline_mouse_down)
        self.canvas.tag_bind("timelines", "<B1-Motion>", self._timeline_mouse_drag)
        self.canvas.tag_bind("timelines", "<Motion>", self._timeline_mouse_motion)
        self.canvas.tag_bind("timelines", "<ButtonRelease-1>", self._timeline_mouse_up)
        self.canvas.tag_bind("timelines", "<Double-1>", self._timeline_mouse_doubleclick)
        self.canvas.bind_all("<MouseWheel>", self._timeline_mouse_wheel)

        self.canvas.tag_bind("BaseItem", "<ButtonPress-1>", self._item_mouse_down)
        self.canvas.tag_bind("BaseItem", "<B1-Motion>", self._item_mouse_drag)
        self.canvas.tag_bind("BaseItem", "<Motion>", self._item_mouse_over)
        self.canvas.tag_bind("BaseItem", "<ButtonRelease-1>", self._item_mouse_up)
        self.canvas.tag_bind("BaseItem", "<Double-1>", self._item_mouse_doubleclick)
        self.canvas.tag_bind("BaseItem", "<Button-3>", self._show_item_menu)

        self.drawers = None

        #self.load()

        #self.draw(0, 0, self.width)

        self.patch()

    def add_drawers(self):
        Drawers(root=self.root, canvas=self.canvas, theme=self.theme, keyboard=self.keyboard, height=25,
                x=0, y=self.bottom)

    def add_tag(self, object_id, tag):
        """
        Add a tag to a canvas object.
        """
        tags = self.canvas.gettags(object_id)
        if tag not in tags:
             debug('+TAG: {} OBJECT_ID: {}'.format(tag, object_id))
             self.canvas.addtag_withtag(tag, object_id)

    def _adjust_timeline_total_days(self, timeline, more_days=None, less_days=None):
        debug('TaskManager._adjust_timeline_total_days')

        if more_days:
            negative_or_positive = +1
        else:
            negative_or_positive = -1

        factor = timeline.days_displayed / 15

        timeline.days_displayed += factor * negative_or_positive
        timeline.draw()

    def _timeline_mouse_wheel(self, event):

        # TopLevel window (ItemForm) detects mousewheel and triggers event on root window. limiting widgetName to
        # canvas seems to fix the issue for now.
        if event.widget.widgetName != 'canvas':
            return

        #debug('TaskManager._timeline_mouse_wheel')

        object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y)

        # ToDo: Need to catch mouse up and down here.
        if self.keyboard.f3_key_down:
            if event.keycode == 120:
                #self.theme.get_next_background_color()
                timeline.group.background_color = self.theme.get_random_color()
                self.draw()
            return

        if object_id:
            if event.keycode == 120:
                index = item.COLORS.index(item.color)
                if index == 0:
                    index = len(item.COLORS) - 1
                else:
                    index -= 1
            else:
                index = item.COLORS.index(item.color)
                if index == len(item.COLORS) - 1:
                    index = 0
                else:
                    index += 1
            item.color = item.COLORS[index]
            self.draw_item(item)
            # self.statusbox.text=item.color
            # debug('color: {}'.format(item.color))

    def _build_menus(self):
        """
        Build one or more menu objects.
        """
        debug('TaskManager._build_menus')
        self.menu = tk.Menu(self.root, tearoff=0)
        #self.menu.add_command(label="Status", command=self._set_status_text_for_item)
        #self.menu.add_separator()
        #self.menu.add_command(label="Rename", command=self._open_item_rename_form)

    def callback(self, dict):
        debug('TaskManager.callback')
        cbkey = dict['cbkey']
        if cbkey == ItemForm.CLOSE_FORM:
            self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=None)
            self.draw()

    def _close(self):
        self.save()
        self.root.destroy()

    def _display_time_with_text(self, time, text=None):
        if time and text:
            self.statusbox.text = ('{0} {1}'.format(bin.to_char(time, '%a %b %d %I:%M %p'), text))
        elif time and not text:
            self.statusbox.text = ('{0}'.format(bin.to_char(time, '%a %b %d %I:%M %p')))
        else:
            self.statusbox.clear()

    #def _item_is_on_timeline(self, item, timeline):
    #    return item.datetime >= timeline.begin_time and item.datetime <= timeline.end_time

    def delete_selected_items(self):
        debug('TaskManager.delete_selected_items')
        self.items.delete_selected_items()
        self.unselect_items_that_are_selected(redraw_affected_items=False)
        self.draw()

    def hide_selected_items(self):
        debug('TaskManager.hide_selected_items')
        self.items.hide_selected_items()
        self.unselect_items_that_are_selected(redraw_affected_items=False)
        self.draw()

    def dump(self, file_name):
        f = open(file_name, mode='w')
        for item in self.items.all_items():
            if not item.deleted:
                f.write(item.title + '\n')
                f.write(bin.nvl(item.description, '') + '\n')
        f.close()

    def _get_closest_object_id_from_xy_with_tag(self, x, y, tag, start=0):
        object_id = self.canvas.find_closest(x, y, start=start)[0]
        #debug2('_get_closest_object_id_from_xy_with_tag: {}'.format(object_id))
        if tag in self.canvas.gettags(object_id):
            return object_id

    def _get_x_from_time(self, datetime_object, begin_time, total_days, width):
        r = bin.days_between_two_dates(datetime_object, begin_time) / total_days * width
        return r

    def _get_next_month(self, datetime_object):
        r = datetime_object.replace(day=28) + datetime.timedelta(days=4)
        #debug("get_next_month: r={0}".format(r))
        r = r.replace(day=1)
        #debug("get_next_month: r={0}".format(r))
        return r

    def _get_item_key_from_object_id(self, object_id):
        debug2('TaskManager._get_item_key_from_object_id')
        #return self._map_object_id_to_item_key[object_id]

    def _get_timeline_from_xy(self, x, y, off_screen_ok=False):
        #debug2('TaskManager._get_timeline_from_item: x={0} y={1}'.format(x, y))
        if off_screen_ok:
            for t in self.visible_timelines():
                if y > t.y and y < t.bottom:
                    #debug('_get_timeline_from_xy={}'.format(t))
                    return t
        else:
            for t in self.visible_timelines():
                if x > self.x and x < t.right and y > t.y and y < t.bottom:
                    #debug('_get_timeline_from_xy={}'.format(t))
                    return t

    def _is_item_being_dragged(self):
        if self.dragging.is_dragging_item():
            return True
        else:
            return False
        #return 'object_id' in self._dragging

    def _timelines_move(self, time, timeline):
        if not timeline.sync_time:
            timeline.move(time)
        else:
            for t in self.visible_timelines():
                if t.group == timeline.group and t.sync_time:
                    t.move(time)
        self._display_time_with_text(timeline.time)

    def _timelines_set_time(self, time, timeline):
        if True:
            for t in self.timelines:
                if t.group == timeline.group:
                    t.time = time
                    t.draw_details()
        else:
            timeline.time = time
            timeline.draw_details()

    def keypress(self, dict):
        debug2('TaskManager.keypress: {}'.format(dict))

        key = dict['key']

        timeline = self._get_timeline_from_xy(x=self.mouse[0], y=self.mouse[1])

        if timeline:
            move_days = timeline.types[timeline.type]['move_days']

        # These keys only apply when there are no selected items.
        if timeline and timeline.total_selected == 0:
            # These apply when the control key is down.
            if self.keyboard.control_key_down:
                # Arrow keys gets with control key control line and background colors for a single timeline.
                if key == 'Right':
                    debug('*** control-right ***')
                    timeline.colors.next_bgcolor()
                    self.draw()
                    debug('Setting text to {}'.format(timeline.colors.get_bgcolor_info()))
                    self.statusbox.text = timeline.colors.get_bgcolor_info()
                    return
                elif key == 'Left':
                    timeline.colors.last_bgcolor()
                    self.draw()
                    self.statusbox.text = timeline.colors.get_bgcolor_info()
                    return
                elif key == 'Up':
                    timeline.colors.next_lncolor()
                    self.draw()
                    self.statusbox.text = timeline.colors.get_lncolor_info()
                    return
                elif key == 'Down':
                    timeline.colors.last_lncolor()
                    self.draw()
                    self.statusbox.text = timeline.colors.get_lncolor_info()
                    return
                elif key == "h":
                    if timeline.group.visible_timeline_count > 1:
                        timeline.hidden = True
                        debug('hiding timeline {}'.format(timeline))
                        self.canvas.delete('all')
                        self.draw()
                    else:
                        self.statusbox.text = "This is the only visible timeline in the group."
                    return
                elif key == "u":
                    group = timeline.group
                    for t in group.timelines:
                        t.hidden = False
                    self.canvas.delete('all')
                    self.draw()
                    return
                elif key == "s":
                    timeline.sync_time = not timeline.sync_time
                    self.statusbox.text = 'SYNC_TIME={}'.format(timeline.sync_time)
                    return
                elif key == "c":
                    timeline.sync_colors = not timeline.sync_colors
                    self.statusbox.text = 'SYNC_COLORS={}'.format(timeline.sync_colors)

            elif self.keyboard.shift_key_down:
                # Arrow keys with shift key control line and background colors for timeline group.
                if key == 'Up':
                    self.colors.i = self.colors.colors_list.index(timeline.line_color)
                    timeline.group.line_color = self.colors.next_color()
                    for t in timeline.group.timelines:
                        t.line_color = timeline.group.line_color
                    self.statusbox.text = self.colors.get_color_info()
                    self.draw()
                    return
                elif key == 'Down':
                    self.colors.i = self.colors.colors_list.index(timeline.line_color)
                    timeline.group.line_color = self.colors.last_color()
                    for t in timeline.group.timelines:
                        t.line_color = timeline.group.line_color
                    self.statusbox.text = self.colors.get_color_info()
                    self.draw()
                    return

            else:
                if key == 'Right':
                    self._adjust_timeline_total_days(timeline, less_days=True)
                    return
                elif key == 'Left':
                    self._adjust_timeline_total_days(timeline, more_days=True)
                    return
                elif key == 'Up':
                    timeline.height -= 15
                    self.draw()
                    return
                elif key == 'Down':
                    timeline.height += 15
                    self.draw()
                    return


        # If left arrow...
        if dict['state'] > 1000 and dict['keycode'] == 37 and timeline:
            time = timeline.time + datetime.timedelta(days=move_days)
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('decrease_horizontal')
                else:
                    timeline._items_align('left')
            else:
                self._timelines_set_time(time, timeline)
        # If up arrow...
        elif dict['state'] > 1000 and dict['keycode'] == 38 and timeline:
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('decrease_vertical')
                else:
                    timeline._items_align('top')
        # If right arrow...
        elif dict['state'] > 1000 and dict['keycode'] == 39 and timeline:
            time = timeline.time - datetime.timedelta(days=move_days)
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('increase_horizontal')
                else:
                    timeline._items_align('right')
            else:
                self._timelines_set_time(time, timeline)
        # If down arrow...
        elif dict['state'] > 1000 and dict['keycode'] == 40 and timeline:
            if self.keyboard.shift_key_down:
                timeline._items_align('increase_vertical')
            else:
                timeline._items_align('bottom')
        elif dict['state'] > 100 and dict['keycode'] == 46:
            if self.keyboard.shift_key_down:
                self._shift_delete_purge_selected_items()
            else:
                self._keypress_delete()
        elif dict['state'] == 8 and dict['keycode'] == 27:
            self._keypress_escape()
        elif self.keyboard.f1_key_down:
            self._f1_change_item_label_display_mode()
        elif self.keyboard.f2_key_down:
            self._f2_switch_display_group()
        elif self.keyboard.f3_key_down:
            # ToDo: Introduce the concept of color schemes in the theme somehow, so you get some pallets, pick one and then
            # when mousewheeling colors something pops up and shows you where you are in the color scheme.
            self._keypress_f3()
        elif self.keyboard.f4_key_down:
            self._f4_switch_timeline_type()
        elif self.keyboard.f5_key_down:
            self._f5_add_timeline_to_group()
        elif self.keyboard.f6_key_down:
            self._f6_add_group()

    def _keypress_delete(self):
        debug('TaskManager._keypress_delete')
        # Todo: At the moment you can delete deleted items, delete should in fact purge here.
        self.delete_selected_items()

    def _keypress_escape(self):
        debug('TaskManager._keypress_escape')
        self.unselect_items_that_are_selected(redraw_affected_items=True)

    def _f1_change_item_label_display_mode(self):
        debug('TaskManager._f1_change_item_label_display_mode')
        x, y = self.mouse
        timeline = self._get_timeline_from_xy(x=x, y=y, off_screen_ok=False)
        if timeline:
            timeline.label_state.next_state()
            timeline.draw()
        else:
            debug('ERROR: timeline not found!')

    def _f2_switch_display_group(self):
        x, y = self.mouse
        timeline = self._get_timeline_from_xy(x=x, y=y, off_screen_ok=False)
        timeline.items.next_display_group()
        self.draw()

    def _keypress_f3(self):
        debug('Delete Timeline')
        timeline = self._get_timeline_from_mouse_position()
        if timeline:
            # We must delete all before the delete so we don't delete a statusbox update if it applies.
            self.canvas.delete('all')
            timeline.group.delete_timeline(timeline)
            self.draw()

    def _f4_switch_timeline_type(self):
        timeline = self._get_timeline_from_mouse_position()
        timeline.switch_type()

    def _f5_add_timeline_to_group(self):
        timeline = self._get_timeline_from_mouse_position()
        if timeline:
            timeline.group.copy_timeline(timeline)
            self.draw()

    def _f6_add_group(self):
        folder = Folder(folder_path=self.root_folder, items=Items(self.root_folder))
        g = Group(group_name='default', group_directory=self.root_folder, items=folder.items)
        self.groups.append(g)
        timeline = Timeline(group=g, theme=self.theme, statusbox=self.statusbox,
                            keyboard=self.keyboard, timeline_type='hourly', y=self.bottom, height=100,
                            time=datetime.datetime.now(), canvas=self.canvas, draw_labels=True)
        self.timelines.append(timeline)
        group = self.groups.get_new_group(group_name=bin.random_string(20),
                                          background_color=self.theme.get_random_color())
        self.draw()

    def _f5_add_timeline_group(self):
        form = modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text='Enter Timeline Group Name'
        )
        if form.text:
            self.add_group(group_id=form.text)

    def _shift_delete_purge_selected_items(self):
        debug('TaskManager._keypress_shift_delete')
        self._purge_selected_items(redraw=False)
        self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=None)

    def _get_item_from_object(self, object_id):
        key = self._get_item_key_from_object_id(object_id)
        item = self.items.get_by_key(key)
        return item

    def _get_item_from_xy(self, x, y):
        object_id = self._get_closest_object_id_from_xy_with_tag(x, y, 'item')
        return self._get_item_from_object(object_id)

    def _get_item_key_from_object_id(self, object_id):
        tags = self.canvas.gettags(object_id)
        for tag in tags:
            if tag.startswith('key='):
                return tag.split('=')[-1]

    def _get_xy(self, x, y, use_object_coords=False):
        item = None
        timeline = None
        time = None
        #taskbar_group=self.taskbar.get_group_from_xy(x=x, y=y)
        taskbar_group = None
        object_id = self._get_closest_object_id_from_xy_with_tag(x, y, 'BaseItem')
        timeline = self._get_timeline_from_xy(x, y)
        if timeline:
            time = timeline.get_time_from_x(x)
        if object_id:
            key = self._get_item_key_from_object_id(object_id)
            if timeline:
                item = timeline.items.get_by_key(key)
            if use_object_coords:
                x, y = self.canvas.coords(object_id)[0:2]
        debug2('_get_xy: {0} {1} {2} {3}'.format(object_id, item, timeline, time))
        return (object_id, item, timeline, time, taskbar_group)

    def select_item(self, item, timeline, object_id):
        # This could end up calling an unselect_all so make sure this line is before the select.
        timeline.items.select(item)
        self.add_tag(object_id=object_id, tag='TAG_SELECTED')

    def _item_mouse_down(self, event):
        debug('TaskManager._item_mouse_down')

        # Will not need to re-draw on mouse down since this will trigger a mouse up.

        object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y)

        if not item:
            return

        allow_drag = True

        timeline.items.selected_timeline = timeline

        if timeline.items.total_selected == 0:
            self.select_item(item, timeline, object_id)
        elif timeline.items.total_selected == 1 and not self.keyboard.control_key_down:
            if not item.selected:
                self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=timeline)
                self.select_item(item, timeline, object_id)
                allow_drag = False
            else:
                self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=timeline)
        elif timeline.items.total_selected >= 1 and self.keyboard.control_key_down:
            allow_drag = False
            if item.selected:
                timeline.items.unselect(item)
            else:
                self.select_item(item, timeline, object_id)
        elif timeline.items.total_selected > 1 and not self.keyboard.control_key_down and not item.selected:
            self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=timeline)
            self.select_item(item, timeline, object_id)

            # Shift-Delete should purge all selected items.
            # Space-bar should hide or unhide all selected items.
            # Space-bar should undelete all selected items.

        if allow_drag:
            self.select_item(item, timeline, object_id)
            # Get initial coords for all selected items in the event we need to abort the drag.
            self.dragging.item = item
            self.dragging.object_id = object_id
            self.dragging.coords = self.canvas.coords(object_id)
            self.dragging.x = self.dragging.x0 = event.x
            self.dragging.y = self.dragging.y0 = event.y
            self.dragging.timeline = timeline

    def _item_mouse_over(self, event):
        #debug2('TaskManager._item_mouse_over')

        self.mouse = (event.x, event.y)

        if not self._is_item_being_dragged():
            object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y, use_object_coords=True)
            if object_id:
                text = None
                if time and item:
                    if item.type in ('link', 'remark'):
                        text = item.title
                    elif item.has_tags():
                        text = '{0}@{1} <{2}>'.format(item.get_primary_tag(), item.title, item.status)
                    else:
                        text = '{0}@{1} <{2}>'.format('', item.title, item.status)
                    self._display_time_with_text(time, text)
                else:
                    debug('No coord time!')
            else:
                debug2('No object id!')

    def _item_mouse_drag(self, event):
        #debug('TaskManager._item_mouse_drag')

        self.mouse = (event.x, event.y)

        if self.dragging.is_dragging_item():
            debug('_item_mouse_drag')
            object_id = self.dragging.object_id
            coords = self.canvas.coords(object_id)
            timeline = self._get_timeline_from_xy(x=coords[0], y=coords[1])
            if timeline:
                self._display_time_with_text(timeline.get_time_from_x(coords[0]))
            delta_x = event.x - self.dragging.x
            delta_y = event.y - self.dragging.y
            self.dragging.x = event.x
            self.dragging.y = event.y
            self.canvas.move('TAG_SELECTED', delta_x, delta_y)
            if timeline and timeline.items.total_selected == 1:
                self.canvas.move('{}_LABEL_TAG'.format(object_id), delta_x, delta_y)
            else:
                self.canvas.move('LABEL_SELECTED', delta_x, delta_y)

    def _get_xy_from_object_id(self, object_id):
        return self.canvas.coords(object_id)[0:2]

    def _get_timeline_from_mouse_position(self):
        x, y = self.mouse
        timeline = self._get_timeline_from_xy(x, y)
        if not timeline:
            debug('*** Did not get timeline! ***')
        return timeline

    def _item_mouse_up(self, event):
        debug('TaskManager._item_mouse_up')

        self.mouse = (event.x, event.y)

        object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y, use_object_coords=True)

        delta_x = 0
        delta_y = 0

        if self.dragging.is_dragging_item():
            delta_x = event.x - self.dragging.x0
            delta_y = event.y - self.dragging.y0

        if delta_x != 0 or delta_y != 0:
            abort_drag = False
            mouse_up_over_timeline = self._get_timeline_from_xy(event.x, event.y)
            for object_id in self.canvas.find_withtag('TAG_SELECTED'):
                x, y = self.canvas.coords(object_id)[0:2]
                timeline = self._get_timeline_from_xy(x, y, off_screen_ok=True)
                if not timeline or timeline != mouse_up_over_timeline:
                    debug('*** Not a timeline, or items were dropped on more than one timeline, aborting drag.')
                    abort_drag = True
            if not abort_drag:
                # Loop through each item that has been selected and involved in the drag operation.
                for object_id in self.canvas.find_withtag('TAG_SELECTED'):
                    x, y = self._get_xy_from_object_id(object_id)
                    key = self._get_item_key_from_object_id(object_id)
                    if key:
                        item = timeline.items.get_by_key(key)
                        item.group_name = timeline.group_name
                        item.datetime = timeline.get_time_from_x(x)
                        item.y_as_pct_of_height = timeline._get_pct_of_height_from_y(y)
                        item.tags = []
                        item.save()
                self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=self.dragging.timeline)
            else:
                debug('*** ABORTING DRAG ***')
                self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=self.dragging.timeline)

        elif not self.keyboard.control_key_down:
            self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=timeline)
            self.select_item(item, timeline, object_id)

        self.dragging = None
        self.dragging = Dragging()
        self.statusbox.clear()
        self.draw()

    def _item_mouse_doubleclick(self, event):
        #debug('TaskManager._item_mouse_doubleclick')
        object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y)
        self.root.config(cursor='wait')
        self.root.update_idletasks()
        if item.type == 'task':
            self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=timeline)
            if self.keyboard.shift_key_down:
                bin.open_file_using_default_program(item.folder_with_escapes())
            else:
                f = ItemForm(root=self.root, theme=self.theme, item=item, cbfunc=(lambda dict: self.callback(dict)))
        elif item.type == 'remark':
            self._timeline_disable_window()
            if item.has_tags():
                text = '{0} [{1}]'.format(item.title.rstrip(), ','.join(item.tags))
            else:
                text = item.title
            f = modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text=text)
            self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=timeline)
            if f.text:
                item.text = f.text
                item.save()
                timeline.draw()
            self._timeline_enable_window()
            self.canvas.focus_force()
        elif item.type == 'link':
            if self.keyboard.shift_key_down:
                bin.open_file_using_default_program(item.title)
                self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=timeline)
            else:
                f = modalinputbox.ModalInputBox(
                    root=self.root,
                    canvas=self.canvas,
                    text=item.text)
                self.unselect_items_that_are_selected(redraw_affected_items=True, timeline=timeline)
                if f.text:
                    item.text = f.text
                    item.save()
                    self.draw_items()
        self.root.configure(cursor='')
        self.root.update_idletasks()

    def _open_item_rename_form(self):
        debug('_rename_item')
        object_id = self.temp['object_id']
        key = self._get_item_key_from_object_id(object_id)
        item = self.items.get_by_key(key)
        form = modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text=item.title)
        if form.text:
            item.title = form.text
            self.draw_item(key)
        self.canvas.focus_force()

    def _object_is_item(self, object_id):
        if 'BaseItem' in self.canvas.gettags(object_id):
            return True
        else:
            return False

    def patch(self):
        None

    def _purge_selected_items(self, redraw=False):
        debug('TaskManager._purge_selected_items')
        for item in self.items.all_selected_items():
            item.purged = True
            debug('purged item!')
            if redraw:
                self.draw_item(item, delete_first=True)

    def remove_item(self, key):
        # Not used
        debug('TaskManager.remove_item')
        item = self.items.get_by_key(key)
        item.deleted = True
        self.draw_item(item)

    #    def save(self):
    #        dict={}
    #        bin.save_database(name='TaskManager', dict=dict, folder_path=os.path.join(bin.application_root_path(), 'data'))
    #
    #    def load(self):
    #        """
    #        Restore any saved settings.
    #        """
    #        dict=bin.open_database(name='TaskManager', folder_path=os.path.join(bin.application_root_path(), 'data'))
    #        if dict:
    #            None
    #            #if 'drawers' in dict.keys():
    #            #    self.drawers=dict['drawers']
    #            #self.item_label_int=dict['item_label_int']

    def _set_status_text_for_item(self):
        debug('TaskManager._set_status_text_for_item')
        if self.temp['object_id']:
            object_id = self.temp['object_id']
            key = self._get_item_key_from_object_id(object_id)
            item = self.items.get_by_key(key)
            form = modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text='')
            if form.text:
                item.status = form.text
                self.draw_item(item)
            self.canvas.focus_force()

    def _show_item_menu(self, event):
        debug('TaskManager._show_item_menu')
        object_id = self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
        if self._object_is_item(object_id):
            self.temp['object_id'] = object_id
            x = self.canvas.winfo_rootx() + event.x
            y = self.canvas.winfo_rooty() + event.y
            self.menu.post(x + 15, y)

    def _timeline_mouse_down(self, event):
        debug('TaskManager._timeline_mouse_down')
        self.mouse = (event.x, event.y)

        # Determine which timeline was clicked on.
        t = self._get_timeline_from_xy(event.x, event.y)
        # Link status box to timelines status box.
        self.statusbox = t.statusbox

        t.items.selected_timeline = t

        if self.keyboard.shift_key_down:
            debug('Shift key is down.')
            # User wants to add a new item to the timeline.
            self.keyboard.shift_key_down = False
            self._timeline_mouse_click_add_item(event.x, event.y)
        elif t:
            # This may or may not be a drag operation, but initialize just in case.
            self.dragging.timeline = t
            self.dragging.time = t.time
            self.dragging.x = event.x
            self.dragging.y = event.y
            # Required in order to capture keypress events.
            self.canvas.focus_set()
        else:
            # In theory ending up here is impossible.
            self.dragging = None

    def _timeline_disable_window(self):
        self.theme.enabled = False
        self.draw()

    def _timeline_enable_window(self):
        self.theme.enabled = True
        self.draw()
        self.canvas.focus_force()

    def _timeline_mouse_click_add_item(self, x, y):
        """
        Present user with an input box and create a new item on the timeline.
        """

        #debug('_timeline_mouse_click_add_item')
        timeline = self._get_timeline_from_xy(x, y)

        if not timeline:
            return

        y_pct = timeline._get_pct_of_height_from_y(y)
        t = timeline.get_time_from_x(x)

        # ToDo: Can this just be a partially transparent rectangle?
        self._timeline_disable_window()

        form = modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text=''
        )

        if form.text:
            debug('form.text={}'.format(form.text))
            # ToDo: This section likely needs to go someplace else.
            # Strip leading and trailing blanks from test.
            text = form.text.strip()
            #If primary tag has been supplied the line will begin with @.
            if text[0:1] == '@':
                # Get the first word after the @.
                tag = text[1:].split(' ')[0]
                # Now remove the tag entirely from the text string.
                if len(text.split(' ', 1)) > 1:
                    text = text.split(' ', 1)[1]
                else:
                    text = tag
            else:
                tag = None

            # item_type = get_item_type_from_text(form.text)

            timeline.items.add_item(group_name=timeline.group.group_name, item_type='task', text=form.text, y_pct=y_pct,
                                    datetime=t, primary_tag=tag)

        self._timeline_enable_window()

    def _timeline_mouse_doubleclick(self, event):
        #debug('TaskManager._timeline_mouse_doubleclick')
        object_id, item, timeline, time, taskbar_group = self._get_xy(event.x, event.y)
        self._timelines_move(time, timeline)

    def _timeline_mouse_motion(self, event):
        self.mouse = (event.x, event.y)
        timeline = self._get_timeline_from_mouse_position()
        if timeline:
            self.statusbox = timeline.statusbox
            if self.keyboard.shift_key_down:
                # Display time under mouse pointer when shift key down but mouse pointer not own.
                self._display_time_with_text(timeline.get_time_from_x(event.x))
            else:
                self.statusbox.clear()

    def _timeline_mouse_drag(self, event):
        """
        Drag operation. B1-Motion is bound to this procedure.
        """
        #debug2('TaskManager._timeline_mouse_drag')

        self.mouse = (event.x, event.y)

        # Return if drag operation has not been initialized for the timeline.
        if not self.dragging.timeline:
            return

        t = self.dragging.timeline

        x = event.x - self.dragging.x
        y = event.y - self.dragging.y

        # Mouse is dragging a rectangle if this is the case.
        if not self.dragging.is_dragging_item() and not self.dragging.is_dragging_timeline() and \
                (self.dragging.is_dragging_selectbox() or ((y > 3 or y < -3) and (x > -50 and x < 50))):
            # This is a select using rectangle operation.
            self.canvas.delete('selectbox')
            self.dragging.selectbox_object_id = self.canvas.create_rectangle(self.dragging.x,
                                                                             self.dragging.y,
                                                                             event.x,
                                                                             event.y,
                                                                             outline=self.dragging.timeline.colors.lncolor,
                                                                             tags="selectbox")
        elif x == 0:
            # This is not a drag operation, yet.
            return
        elif x > 5 or not self.dragging.is_dragging_selectbox():
            self.dragging.dragging_timeline = True
            # This is a drag timeline operation.
            days = x / t.width * t.total_days * -1
            time = self.dragging.time + datetime.timedelta(days=days)
            self._timelines_move(time, t)


    def _timeline_mouse_up(self, event):
        #debug("TaskManager._timeline_mouse_up")
        if self.dragging.is_dragging_selectbox():
            x, y, x1, y1 = self.canvas.coords(self.dragging.selectbox_object_id)
            self.canvas.delete('selectbox')
            t = self._get_timeline_from_xy(event.x, event.y)
            # Only works if the start and stop of the drag are on the same timeline.
            if t.key == self.dragging.timeline.key:
                # Get a list of all of the objects enclosed by the rectangle.
                oids = self.canvas.find_enclosed(x, y, x1, y1)
                for oid in oids:
                    if 'BaseItem' in self.canvas.gettags(oid):
                        key = self._get_item_key_from_object_id(oid)
                        item = t.items.get_by_key(key)
                        # ToDo: This item selected business is just ugly.
                        self.select_item(item, t, oid)
            else:
                debug('*** t.name != dragging timeline name ***')
        elif self.dragging.timeline:
            x = event.x - self.dragging.x
            # if x==0 then the timeline was not moved, so this click on the timeline should unselect all times selected.
            if x == 0:
                # Items will stay selected if an actual timeline drag has taken place, but if not then all items will be unselected.
                self.unselect_items_that_are_selected(redraw_affected_items=False, timeline=self.dragging.timeline)
                # self._dragging['timeline'].unselect_all(draw=True)
        self.dragging = None
        self.dragging = Dragging()
        self.draw()

    def update_background_tasks(self):
        debug('TaskManager.update_background_tasks')
        for t in self.visible_timelines():
            t.draw_line_for_current_time()

    def unselect_items_that_are_selected(self, redraw_affected_items, timeline):
        debug('TaskManager.unselect_items_that_are_selected')

        # Remove selected tag from all items with tag.
        for object_id in self.canvas.find_withtag('TAG_SELECTED'):
            self.canvas.dtag(object_id, 'TAG_SELECTED')

        if timeline:
            timeline.unselect_items_that_are_selected(redraw_affected_items=redraw_affected_items)

            #if self.last_timeline_clicked:
            #self.last_timeline_clicked.unselect_all(draw=draw)
            #self.items.unselect_all(draw=draw)
