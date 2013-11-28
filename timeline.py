
# ToDo: Add flashing attribute it items.

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

COLORS=['red', 'yellow']

XCOLORS=['red', 'orange', 'yellow', 'aquamarine2', 'lime green', 'lawn green', 'light sea green',
            'green yellow', 'light sky blue', 'white', 'SlateBlue1']

BACKGROUND_COLORS=['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
    'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
    'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
    'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
    'light slate gray', 'gray', 'light grey', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
    'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
    'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
    'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
    'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
    'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
    'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
    'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
    'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
    'indian red', 'saddle brown', 'sandy brown',
    'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
    'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
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
    'gray93', 'gray94', 'gray95', 'gray97', 'gray98', 'gray99']

def get_item_type_from_text(text):
    """
    Return the item type by parsing the input string.
    """
    if text[0:5] in ("http:", "https"):
        return 'link'

    if text.find('@') >= 0:
        tag=text.split('@')[0].strip()
        if ' ' not in tag:
            return 'task'

    return 'remark'

class ItemForm():

    CLOSE_FORM=23750
    
    def __init__(self, root, theme, item, cbfunc=None):
        self.form=tk.Toplevel(root)
        self.form.protocol("WM_DELETE_WINDOW", self._close_form)
        self.form.bind_class("Text","<Control-a>", self.select_all)
        self.form.bind_class("Entry","<Control-a>", self.select_all)
        self.keyboard=keyboard
        self.theme=theme
        self.cbfunc=cbfunc
        self._status_doc='<Enter Status or #Milestone>'
        self._description_doc='<Description/Notes>'
        self.widget_width=75
        self.item=item
        self.copy_of_item=copy.deepcopy(item)
        self.title_var=tk.StringVar()
        self._draw()

    def _update_status_history(self):
        self.history_box.configure(state=tk.NORMAL)
        self.history_box.delete(1.0, tk.END)
        for status in self.item.all_statuses():
            self.history_box.insert(tk.END, status)
        self.history_box.configure(state=tk.DISABLED)

    def _close_form(self):
        debug('ItemForm._close_form')
        self.item.title=self.title_var.get()
        self.item.description=self._get_description()
        self.item.tags=self.tags_var.get().split(',')
        self.item.save()
        if self.cbfunc:
            self.cbfunc({'cbkey': self.CLOSE_FORM})
        self.form.destroy()

    def _draw(self):

        item=self.item
        self.form.title(item.title)

        # Title
        title_frame=tk.Frame(self.form)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_label=tk.Label(title_frame, text='Title', font=self.theme.font(size='>'), anchor="w", relief=tk.FLAT,
                             fg='black')
        title_label.pack(fill=tk.X)
        self.title_box=tk.Entry(title_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT, width=self.widget_width,
                                textvariable=self.title_var)
        self.title_box.pack(fill=tk.X)
        self.title_box.bind('<Key>', self._keypress_title)
        self.title_box.bind('<FocusIn>', self.select_all)
        self.title_var.set(item.title)

        line=tk.Frame(self.form, bd=2, relief=tk.RAISED, padx=10, pady=2)
        line.pack(fill=tk.X)

        self._draw_description()

        # Status
        status_frame=tk.Frame(self.form)
        status_frame.pack(fill=tk.X, padx=2, pady=2)
        self.status_var=tk.StringVar()
        status_label=tk.Label(status_frame, text='Status', font=self.theme.font(size='>'), anchor="w", relief=tk.FLAT,
                             fg='black')
        status_label.pack(fill=tk.X)
        self.status_box=tk.Entry(status_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT,
                                 width=self.widget_width, textvariable=self.status_var)
        self.status_box.pack(fill=tk.X)
        self.status_box.bind('<Key>', self._keypress_status)
        self.status_box.bind('<FocusIn>', self._focus_in_status)
        self.status_var.set(self._status_doc)
        self.status_box.focus_set()
        self._focus_in_status()

        line=tk.Frame(status_frame, bd=2, relief=tk.RAISED, bg='dark gray', padx=10, pady=2)
        line.pack(fill=tk.X)

        # Status history.
        history_bar=tk.Scrollbar(status_frame)
        history_bar.pack(side=tk.RIGHT, fill=tk.Y)
        history_box_height=5
        self.history_box=tk.Text(status_frame, height=history_box_height, borderwidth=1, font=self.theme.font(size='>'),
                                 relief=tk.FLAT, width=self.widget_width, fg='dark grey')
        self.history_box.pack(side=tk.TOP, fill=tk.X)
        self.history_box.configure(yscrollcommand=history_bar.set)
        history_bar.configure(command=self.history_box.yview)
        self._update_status_history()

        # Tags
        debug('item.tags={}'.format(item.tags))
        tags_frame=tk.Frame(self.form)
        tags_frame.pack(fill=tk.X, padx=2, pady=2)
        tags_label=tk.Label(tags_frame, text='Tags', font=self.theme.font(size=">"), anchor="w", width="10", relief=tk.FLAT, fg='black')
        tags_label.pack(fill=tk.X)
        self.tags_var=tk.StringVar()
        self.tags_box=tk.Entry(tags_frame, borderwidth=2, font=self.theme.font(size='>'), relief=tk.FLAT, width=self.widget_width,
                          textvariable=self.tags_var)
        self.tags_box.pack(fill=tk.X)
        self.tags_box.bind('<Key>', self._keypress_tags)
        self.tags_box.bind('<FocusIn>', self._focus_in_tags)
        self.tags_var.set(','.join(item.tags))

        files_frame=tk.Frame(self.form)
        files_frame.pack(fill=tk.X, padx=2, pady=2)
        files_label=tk.Label(files_frame, text='Files', font=self.theme.font(size=">"), anchor="w", width="10", relief=tk.FLAT, fg='black')
        files_label.pack(fill=tk.X)

        canvas_frame=tk.Frame(self.form)
        canvas_frame.pack(fill=tk.X, padx=2, pady=2)
        canvas=tk.Canvas(canvas_frame, width=self.widget_width, height=60, bg='white')
        canvas.pack(fill=tk.X)

        self.filebar=filebar.FileBar(root=self.form, canvas=canvas, height=60)
        self.filebar.patterns_to_exclude=['_data_']
        self.filebar.add_folder(directory=bin.add_backslash_to_backslash(item.folder_with_escapes()))
        self.filebar.draw()


    def _draw_description(self):
        description_frame=tk.Frame(self.form)
        description_frame.pack(fill=tk.X, padx=2, pady=2)
        self.description_bar=tk.Scrollbar(description_frame)
        self.description_bar.pack(side=tk.RIGHT, fill=tk.Y)
        description_label=tk.Label(description_frame, text='More', font=self.theme.font(size='>'), anchor="w", relief=tk.FLAT,
                             fg='black')
        description_label.pack(fill=tk.X)
        description_box_height=6
        self.description_box=tk.Text(description_frame, height=description_box_height, borderwidth=1,
                                     font=self.theme.font(size='>'), relief=tk.FLAT, width=self.widget_width)
        self.description_box.pack(side=tk.TOP, fill=tk.X)
        self.description_box.configure(yscrollcommand=self.description_bar.set)
        self.description_bar.configure(command=self.description_box.yview)
        self._set_description_box_text(self.item.description)

        self.description_box.bind('<Tab>', self._focus_set_status_box)
        self.description_box.bind('<Shift-Tab>', self._focus_set_title_box)
        #self.description_box.bind('<FocusOut>', self._focus_out_description)
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
        if self._get_description() != self._description_doc or self._get_description()=='':
            self.item.description=self._get_description()
            self._description_doc=''
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
        debug('ItemForm._keypress_status: {0} {1}'.format(event.state, event.keycode))
        if event.state==8 and event.keycode==13:
            # Enter
            if self.status_var.get() not in ('', self._status_doc):
                self.item.status=self.status_var.get()
                self.status_var.set(self._status_doc)
                self._focus_in_status()
            self._update_status_history()
        elif event.state==8 and event.keycode==27:
            # Escape
            self.status_var.set(self._status_doc)
            self._focus_in_status()

    def _keypress_title(self, event):
        debug('ItemForm._keypress_title: state={0} keycode={1}'.format(event.state, event.keycode))
        if event.state==8 and event.keycode==27:
            # Escape
            self.title_var.set(self.copy_of_item.title)
            self._select_all_title()

        self.item.title=self.title_var.get()

    def _keypress_description(self, event):
        if event.state==8 and event.keycode==27:
            # Escape
            self._set_description_box_text(self.copy_of_item.description)
        if self._get_description().startswith(self._description_doc):
            self.item.description=None
        else:
            self.item.description=self._get_description()

    def _keypress_tags(self, event):
        if event.state==8 and event.keycode==27:
            # Escape
            self.tags_var.set(','.join(self.copy_of_item.tags))

    def _pack_description(self):
        self.description_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_box.pack(side=tk.TOP, fill=tk.X)

    def select_all(self, event):
        if event.widget.widgetName=='entry':
            event.widget.select_range(0, tk.END)
        else:
            event.widget.tag_add("sel","1.0","end")

    def _select_all_title(self):
        debug('ItemForm._select_all_title')
        self.title_box.select_range(0, tk.END)

    def _select_all_description(self, event=None):
        self.description_box.tag_add("sel","1.0","end")

    def _set_description_box_text(self, text=None):
        debug('ItemForm: _set_description_box_text')
        text=bin.nvl(text, self._description_doc)
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
        if event.state==8 and event.keycode==13:
            debug('update_tags')
            self.item.tags=self.tags_var.get().split(',')

class TimelineLane():
    def __init__(self, name, theme, type, y, height, total_days, time, label_format, canvas, draw_labels=False):
        self.key=bin.random_string(20)
        self.name=name
        self._height=height
        self.theme=theme
        self.type=type
        self._y=y
        self._x=None
        self._width=None
        self.canvas=canvas
        self.total_days=total_days
        self.min_days=total_days/3
        self.max_days=total_days*4
        self._time=None
        self.label_format=label_format
        self._right=None
        self._bottom=None
        self.begin_time=None
        self.end_time=None
        self.first_label=None
        self.draw_labels=False
        self._database_path=os.path.join(bin.application_root_path(), 'data', 'timeline_{}.cfg'.format(self.name))
        self._update_bottom()
        self.object_id=None
        self.draw_labels=draw_labels
        self.time=time

    def save(self):
        d={'height':self.height,
           'total_days': self.total_days,
           'key': self.key}
        bin.save_database2(self._database_path, d)

    def load(self):
        d=bin.open_database2(self._database_path)
        if d:
            self.height=d['height']
            self.total_days=d['total_days']
            self.key=d['key']
            self.time=datetime.datetime.now()

    @property
    def bottom(self):
        return self._bottom

    @property
    def right(self):
        return self._right

    def draw(self, x=None, y=None, width=None):
        if x is not None:
            self.x=x

        if y is not None:
            self.y=y
            
        if width is not None:
            self.width=width

        self.canvas.delete('TIMELINE'+self.key)
        self.object_id=self.canvas.create_rectangle(self.x, self.y, self.right, self.bottom,
            fill=self.theme.background_color, outline=self.theme.line_color, tags='timelines TIMELINE'+self.key)
        self.canvas.tag_lower(self.object_id)
        self.draw_details()

    def _get_x_from_time(self, time):
        return bin.days_between_two_dates(time, self.begin_time)/self.total_days*self.width

    def _get_next_month(self, datetime_object):
        r=datetime_object.replace(day=28)+datetime.timedelta(days=4)
        r=r.replace(day=1)
        return r

    def draw_details(self):
        """
        Draw the lines and labels for the given timeline.
        """
        debug2('TimelineLane.draw_details')

        self.canvas.delete(self.key)

        font_size='<<'

        # Get the X position of the first label.

        x=self._get_x_from_time(self.first_label)

        label_time=self.first_label
        for i in range(1,100):
            l=bin.to_char(label_time, self.label_format)
            self.canvas.create_line(x, self.y, x, self.bottom, fill=self.theme.line_color, tags=self.key)
            self.canvas.create_text(x+3,self.bottom-8, font=self.theme.font(size=font_size), text=l, anchor='w', fill=self.theme.font_color, tags=self.key)
            if self.type=='hourly':
                label_time=label_time+datetime.timedelta(hours=1)
                if self.total_days <= 12/24:
                    for i in range(1,4):
                        minute_time=label_time+datetime.timedelta(days=i*15/1440)
                        x=self._get_x_from_time(minute_time)
                        self.canvas.create_line(x, self.y, x, self.bottom, fill='light gray', tags=self.key)
                        self.canvas.create_text(x+3,self.y+8, font=self.theme.font(size=font_size), text=str(i*15), anchor='w', fill='light gray', tags=self.key)
            elif self.type=='daily':
                if self.total_days <= 3:
                    for i in range(1,24):
                        hourly_time=label_time+datetime.timedelta(hours=i)
                        x=self._get_x_from_time(hourly_time)
                        self.canvas.create_line(x, self.y, x, self.bottom, fill='light gray', tags=self.key)
                        self.canvas.create_text(x+3,self.y+8, font=self.theme.font(size=font_size), text=str(i), anchor='w', fill='light gray', tags=self.key)
                label_time=label_time+datetime.timedelta(hours=24)
            elif self.type=='monthly':
                if self.total_days <= 60:
                    for i in range(1,bin.get_number_of_days_in_month_from_datetime(label_time)):
                        daily_time=label_time+datetime.timedelta(hours=i*24)
                        x=self._get_x_from_time(daily_time)
                        self.canvas.create_line(x, self.y, x, self.bottom, fill='light gray', tags=self.key)
                        self.canvas.create_text(x+3,self.y+8, font=self.theme.font(size=font_size), text=str(i+1), anchor='w', fill='light gray', tags=self.key)
                label_time=self._get_next_month(label_time)

            x=self._get_x_from_time(label_time)

            if label_time > self.begin_time+datetime.timedelta(days=self.total_days):
                break

        # Draw red line in middle of timeline.
        #if self.sync_timelines:
        x=self._get_x_from_time(self.time)
        self.canvas.create_line(x, self.y, x, self.y+self.height, fill='red', tags=self.key)

        # Draw blue line at current time.
        #tag="blue_line"
        #self.canvas.delete(tag)
        #x=self._get_x_from_time(datetime.datetime.now(), self.begin_time, self.total_days, self.width)
        #self.canvas.create_line(x, self.y, x, self.y+self.height, fill='blue', tags=tag)
        self._draw_current_time()

    def _draw_current_time(self):
        self.canvas.delete('blue_line')
        # Draw blue line at current time.
        x=self._get_x_from_time(datetime.datetime.now())
        self.canvas.create_line(x, self.y, x, self.y+self.height, fill='blue', tags='blue_line')

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y=y
        self._update_bottom()

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x=x
        self._update_right()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width=width
        self._update_right()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height=height
        self._update_bottom()

    def _update_bottom(self):
        self._bottom=self._y+self._height

    def _update_right(self):
        if self.width is not None and self.x is not None:
            self._right=self.x+self.width

    @property
    def time(self):
        return self._time

    @time.setter
    def time (self, time):
        self._time=time
        self.begin_time=self._time-datetime.timedelta(days=self.total_days/2)
        self.end_time=self.begin_time+datetime.timedelta(days=self.total_days)

        if self.type=='hourly':
            self.first_label=self.begin_time.replace(minute=0, second=0, microsecond=0)
        elif self.type=="daily":
            self.first_label=self.begin_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.type=="monthly":
            self.first_label=self.begin_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

class BaseItem():

    COLORS=['white', 'grey', 'black', 'green', 'blue', 'yellow', 'red']
    DISPLAY_FORMAT='none'

    def __init__(self, app_folder, text, x=None, datetime=None, y=None, y_pct=None):
        # Root folder for other files and folders.
        self._app_folder=app_folder
        # Unique 20 character key generated automatically.
        self.key=bin.random_string(20)
        # Title of item, does not need to be unique.
        self.title=None
        # Used to store x/y position within the app at various points.
        self.x=x
        self._y=y
        # Used to position the item on the hourly, daily and monthly timeline.
        self._y_as_pct_of_height=y_pct
        self._backup={}
        # Path to image to display instead of a shape.
        self.image_path=None
        # Size of image or shape.
        self.size=8
        self.type=None
        self.datetime=datetime
        self.color='blue'
        self._selected=False
        self.folder=None
        self.description=None
        self._text=text
        self._tags=[]
        # There is a getter/setter for this property. When an item is deleted it is moved to a _deleted_ folder.
        # Will add a purge process which removes deleted items. Also needs to be some sort of automatic purge
        # which takes place.
        self._deleted=False
        self._purged=False
        self.hidden=False
        # Stores entire status history including a datetime stamp.
        self._status=[]
        # Stores only the text of the last status.
        self.status_text_only=None
        self.label_int=0
        #self.display_format='none'
        self._parse_text(text)

        # At a minimum title must be set, if not we just assign text to it, but this should already be done.
        if not self.title:
            self.title=text

        self.folder_name='{0}_{1}'.format(bin.date_to_string(), bin.get_valid_path_name_from_string(self.title))

        bin.mkdir(self.folder_with_escapes())

    # ToDo: Change display_label to include_label
    def _draw(self, canvas, theme, x=None, y=None, tag=None, draw_label=False, highlight_selected=False):
        debug('BaseItem._draw: draw_label={}'.format(draw_label))
        if x is not None:
            self.x=x
        if y is not None:
            self.y=y

        tags='{0} {1} {2}'.format('BaseItem', self.key, tag)
        
        canvas.delete(tag)

        if self.selected and highlight_selected:
            border_width=2
            outline_color='black'
            dash=(1,2)
            tags='{0} {1}'.format(tags, 'selected',)
        else:
            border_width=1
            outline_color='black'
            dash=None

        object_id=canvas.create_rectangle(self.x, self.y, self.x+self.size, self.y+self.size, fill=self.color,
           outline=outline_color, tags=tags, stipple=None, width=border_width, dash=dash)

        if draw_label:
            debug('Drawing label')
            x,y,right,bottom=canvas.coords(object_id)
            canvas.create_text(right+5, y-2, text=self.get_label(),
                font=theme.font(size='<<'), fill="black", tags=tag, anchor="nw", justify="left")

        return object_id

    @property
    def y_as_pct_of_height(self):
        return self._y_as_pct_of_height

    @y_as_pct_of_height.setter
    def y_as_pct_of_height(self, pct):
        self._backup['y_as_pct_of_height']=self._y_as_pct_of_height
        self._y_as_pct_of_height=pct

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._backup['y']=self._y
        self._y=y

    def restore(self):
        if 'y_as_pct_of_height' in self._backup.keys():
            self._y_as_pct_of_height=self._backup['y_as_pct_of_height']
        if 'y' in self._backup.keys():
            self._y=self._backup['y']

    def get_label(self):
        debug('get_label: {}'.format(self.DISPLAY_FORMAT))
        if self.DISPLAY_FORMAT=='none':
            return None
        elif self.DISPLAY_FORMAT=='title':
            return self.title
        elif self.DISPLAY_FORMAT=='tag@title':
            if len(self.tags) > 0:
                return '{0}@{1}'.format(self.tags[0], self.title)
            else:
                return self.title
        elif self.DISPLAY_FORMAT=='status':
            if self.status is not None:
                return self.status
            else:
                return self.title
      
    def patch(self):
        """
        Some housekeeping when we initially load the item from the .dat file.
        """
        self._selected=False
        if not hasattr(self, '_y_as_pct_of_height'):
            self._y_as_pct_of_height=None
        if not hasattr(self, '_backup'):
            self._backup={}
        if not hasattr(self, '_y'):
            self._y=self.y
        #if self.y is None:
            #self.y=10

    def folder_with_escapes(self):
        return bin.add_backslash_to_backslash(os.path.join(self._app_folder, 'items', self.folder_name))
        
    @property
    def text (self):
        return self._text
        
    @text.setter
    def text (self, text):
        self._text=text
        self._parse_text(text)

    @property
    def tags (self):
        return self._tags

    @tags.setter
    def tags (self, tags_list):
        tags_list=bin.remove_duplicates_from_list(tags_list)
        tags_list=[x.lower() for x in tags_list]
        self._tags=tags_list

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
        if tf==True:
            self._selected=True
        else:
            self._selected=False

    @property
    def status (self):
        return self.status_text_only

    @status.setter
    def status(self, text):
        # Status history is stored in a list, with most recent status first, we also add a timestamp.
        self._status.insert(0, bin.to_char(datetime.datetime.now(), '%a %b %d %I:%M %p') + ' ' + text + '\n')
        self.status_text_only=text
        # If label display is using status, we need to force it to update.
        # Todo: This is ugly.
        self.label_int=self.label_int

    def all_statuses(self):
        for status in self._status:
                yield status

    @property
    def purged (self):
        return self._purged

    @purged.setter
    def purged (self, purged_true_false):
        if purged_true_false==True:
            self._purged=True
            # Save must occur before the move or it recreates the original directory defined by folder_path.
            #self.save()
            #debug('BaseItem: *** Moving {} to _deleted_'.format(self.folder_path))
            #bin.mv(self.folder_path, os.path.join(self.folder_path, '..', '_deleted_'))
        else:
            # Todo: This can never happen
            self._purged=False

    @property
    def deleted (self):
        return self._deleted

    @deleted.setter
    def deleted (self, deleted_true_false):
        if deleted_true_false==True:
            self._deleted=True
            # Save must occur before the move or it recreates the original directory defined by folder_path.
            #self.save()
            #debug('BaseItem: *** Moving {} to _deleted_'.format(self.folder_path))
            #bin.mv(self.folder_path, os.path.join(self.folder_path, '..', '_deleted_'))
        else:
            # Todo: Need to add un-delete feature.
            self._deleted=False

    def move(self, app_folder):
        None

    def save(self):
        debug('BaseItem.save')
        data_folder=os.path.join(self.folder_with_escapes(), '_data_')
        bin.mkdir(data_folder)
        bin.save_database2(os.path.join(data_folder, self.key), object=self)

#    def load(self, dict):
#        for key in dict.keys():
#            setattr(self, key, dict[key])

    def _parse_text(self, text):
        None

class Link(BaseItem):

    COLORS=['light sky blue']

    def __init__(self, app_folder, text, x=None, datetime=None, y=None, y_pct=None):
        super().__init__(app_folder, text, x, datetime, y, y_pct)
        self.color='light sky blue'
        self.type='link'
        #self._parse_text(self.text)

    def _parse_text(self, text):
        """
        Links are created in this fashion.

        http://google.com <Google> [tag,tag]
        """

        debug('Link._parse_text: text={}'.format(text))
        # Grab http link
        if text.find('http') > 0:
            link=text.split(' ')[0].strip()
            text=text.split(' ', 1)[1]
            self.title=link

        # Alternative text is in last set of angle brackets if it exist.
        if text.rfind('<') > 0:
            b=text.rfind('<')
            e=text.rfind('>')
            if b < e:
                self.title=text[b+1:e]
                text=text[0:b]+text[e+1:]

        # Everything in last set of brackets are tags.
        are_tags=[]
        if text.rfind('['):
            b=text.rfind('[')
            e=text.rfind(']')
            if b < e:
                are_tags=text[b+1:e].split(',')
                are_tags=[t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags=[]

        self.tags=are_tags

class Remark(BaseItem):

    COLORS=['yellow']

    def __init__(self, app_folder, text, x=None, datetime=None, y=None, y_pct=None):
        super().__init__(app_folder, text, x, datetime, y, y_pct)
        self.color='yellow'
        self.type='remark'
        #self._text=text
        #self._parse_text(self._text)

    def _parse_text(self, text):
        """
        Remarks are created in this fashion.
        
        >Remark [tag,tag]
        """
        debug('Remark._parse_text: {}'.format(text))
        if self._text.rfind('>')==0:
            self._text=self._text.split('>')[1]

        are_tags=[]
        if self._text.rfind('['):
            b=self._text.rfind('[')
            e=self._text.rfind(']')
            if b < e:
                are_tags=self._text[b+1:e].split(',')
                are_tags=[t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags=[]
                
        self.tags=are_tags
        if len(are_tags) > 0:
            self.title=self._text[0:b]+self._text[e+1:]
        else:
            self.title=self._text

class Task(BaseItem):

    COLORS=['green', 'blue', 'red']

    def __init__(self, app_folder, text, x=None, datetime=None, y=None, y_pct=None):
        super().__init__(app_folder, text, x, datetime, y, y_pct)
        self.type='task'
        #self._parse_text(text)
        self.color='green'
            
    @property
    def text (self):
        return self._text

    @text.setter
    def text (self, text):
        self._text=text
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

        at_tag=None
        if text.find('@') > 0:
            tag=text.split('@')[0].strip()
            if ' ' not in tag:
                at_tag=tag
                text=text.split('@')[1]

        debug('! tags={0} text={1}'.format(self.tags, text))

        # Status is in last set of angle brackets if it exist.
        if text.rfind('<') > 0:
            b=text.rfind('<')
            e=text.rfind('>')
            if b < e:
                self._status=text[b+1:e]
                text=text[0:b]+text[e+1:]

        # Everything in last set of brackets are tags.
        are_tags=[]
        if text.rfind('['):
            b=text.rfind('[')
            e=text.rfind(']')
            if b < e:
                are_tags=text[b+1:e].split(',')
                are_tags=[t.strip() for t in are_tags]
                for t in are_tags:
                    if ' ' in t:
                        # Tags with blanks are not valid. These are probably not tags.
                        are_tags=[]
                if len(are_tags) > 0:
                    text=text[0:b]+text[e+1:]

        if at_tag:
            are_tags.append(at_tag)
        self.tags=are_tags

        debug('! tags={0} text={1}'.format(self.tags, text))

        self.title=text

class Items():

    label_display_formats=['none', 'title', 'tag@title', 'status']

    def __init__(self, root_dir, canvas, theme):

        self.items={}
        self.canvas=canvas
        self.theme=theme

        self.object_id_map={}

        self.label_display_format_index=0

        deleted=re.compile('.*_deleted_.*')
        # Find all items. Each item has a _data_ directory.
        for data_dir in bin.find(root=root_dir, type='d', name='_data_'):
            # Ignore anything with _deleted_ in the path.
            if not re.match(deleted, data_dir):
                # The item is stored in the .dat file.
                for file in bin.find(root=data_dir, type='f', name='.*\.dat'):
                    key=os.path.basename(file).replace('.dat', '')
                    d=bin.open_database2(file.replace('.dat', ''))
                    self.items[key]=d
                    d.patch()

        # if the item is not shared and not the same version, patch it and save
        # if the item is shared and the version does not match mark it as read only
        # items should have a save all and each item should also have a save

        # should add a load for above with a directory name, then we can add
        # directories to the timeline and use the same items class.

        self._total_selected=0

        self.patch()

    def switch_label_display_format(self):
        debug('Items.switch_label_display_format')
        self.label_display_format_index+=1
        if self.label_display_format_index > len(self.label_display_formats)-1:
            self.label_display_format_index=0
        for item in self.items.values():
            item.DISPLAY_FORMAT=self.label_display_formats[self.label_display_format_index]
            
    def patch(self):
        for item in self.all_items():
            None

    @property
    def total_selected(self):
        return self._total_selected

    @total_selected.setter
    def total_selected(self, total_selected):
        self._total_selected=total_selected

    def all_items(self):
        return self.items.values()

    def all_selected_items(self):
        for item in self.all_items():
            if item.selected:
                yield item

    def get_by_key(self, key):
        return self.items[key]

    def get_by_object_id(self, object_id):
        if object_id in self.object_id_map.keys():
            return self.items[self.object_id_map[object_id]]

    def delete_by_key(self, key, save=True):
        """
        Delete an item.
        """
        self.items[key].deleted=True
        del self.items[key]

    def save(self):
        for item in self.all_items():
            item.save()

    def draw(self, item, x=None, y=None, tag=None, draw_label=False, highlight_selected=False):
        """
        Draw a single item on the canvas at a single point.
        """
        object_id=item._draw(canvas=self.canvas, theme=self.theme, x=x, y=y, tag=tag, draw_label=draw_label,
            highlight_selected=highlight_selected)
        self.object_id_map[object_id]=item.key

    def select(self, item):
        """
        Mark an item as selected.
        """
        item.selected=True
        self._total_selected+=1

    def unselect(self, item):
        """
        Mark an item as unselected.
        """
        item.selected=False
        self._total_selected-=1
        
    def get_item_from_object_id(self, object_id):
        key=self.object_id_map[object_id]
        if key:
            return self.items[key]

    def unselect_all(self, draw=True):
         # Set selected attribute to false for all items.
        for item in self.all_items():
            if item.selected:
                item.selected=None
                if draw:
                    self.draw(item)
               
        self.total_selected=0

class Timeline():

    def __init__(self, root, canvas, theme, **kwargs):
        self.root=root
        self.canvas=canvas
        self.theme=theme
        self.timelines=[]
        self.bottom=0
        self.sync_timelines=True
        # Just a temporary dict which we can use for this and that.
        self.temp={}
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.keyboard=keyboard.Keyboard(canvas=self.canvas, cbfunc=(lambda dict: self.keypress(dict)))
        self.x=0
        self.y=0
        # Stores information during drag and drop operations.
        self._dragging={}
        self.mouse=(0, 0)
        self._f2_display_mode=0
        self.display_items=True
        self.display_hidden_items=False
        self.display_deleted_items=False
        
        # Reference to application root_path.
        self.app_folder=bin.application_root_path()

        # Where item objects are stored.
        self.app_folder_for_items=os.path.join(self.app_folder, 'items')
        bin.mkdir(self.app_folder_for_items)

        # Where deleted item are stored.
        self.default_deleted_items_path=os.path.join(self.app_folder, 'items', '_deleted_')
        bin.mkdir(self.default_deleted_items_path)

        # This is a dict of all of the items in the database, indexed by key.
        self.items=Items(root_dir=self.app_folder_for_items, canvas=self.canvas, theme=self.theme)

        self.last_timeline_clicked=None

    def add (self, name, type, y, height, total_days, time, label_format, draw_labels):
        timeline=TimelineLane(name=name, theme=self.theme, type=type, y=y, height=height,
            total_days=total_days, time=time, label_format=label_format, canvas=self.canvas, draw_labels=draw_labels)
        timeline.load()
        self.timelines.append(timeline)
        self.bottom=timeline.bottom
        self.thumbnails={}
        self._build_menus()
        self._vertical_distance_between_items=None
        self._horizontal_distance_between_items=None

    def draw(self, x=None, y=None, width=None):
        if x is None:
            x=self.x
        if width is None:
            width=self.width
        if y is None:
            _y=0
        else:
            _y=y
        for timeline in self.timelines:
            timeline.draw(x=x, y=_y, width=width)
            _y=timeline.bottom
        self.bottom=_y
        
    def init(self):
        self.width=self.canvas.winfo_reqwidth()
        self.canvas.focus_set()

        self.canvas.tag_bind("timelines", "<ButtonPress-1>",   self._timeline_mouse_down)
        self.canvas.tag_bind("timelines", "<B1-Motion>",       self._timeline_mouse_drag)
        self.canvas.tag_bind("timelines", "<Motion>",          self._timeline_mouse_motion)
        self.canvas.tag_bind("timelines", "<ButtonRelease-1>", self._timeline_mouse_up)
        self.canvas.tag_bind("timelines", "<Double-1>",        self._timeline_mouse_doubleclick)
        self.canvas.bind_all("<MouseWheel>", self._timeline_mouse_wheel)

        self.canvas.tag_bind("BaseItem", "<ButtonPress-1>",   self._item_mouse_down)
        self.canvas.tag_bind("BaseItem", "<B1-Motion>",       self._item_mouse_drag)
        self.canvas.tag_bind("BaseItem", "<Motion>",          self._item_mouse_over)
        self.canvas.tag_bind("BaseItem", "<ButtonRelease-1>", self._item_mouse_up)
        self.canvas.tag_bind("BaseItem", "<Double-1>",        self._item_mouse_doubleclick)
        self.canvas.tag_bind("BaseItem", "<Button-3>",        self._show_item_menu)

        self.load()

        self.draw(0, 0, self.width)

        self.taskbar=taskbar.TaskBar(
            root=self.root,
            canvas=self.canvas,
            keyboard=self.keyboard,
            height=25,
            x=0,
            y=self.bottom
        )

        self.statusbox=statusbox.StatusBox(
            root=self.root,
            canvas=self.canvas,
            theme=self.theme,
            font_size='<',
            x=4,
            y=self.taskbar.bottom,
            height=16,
            width=self.width)
        
        self.draw_items()

        self.patch()

    def add_tag_to_object(self, object_id, tag):
        """
        Add a tag to a canvas object.
        """
        tags=self.canvas.gettags(object_id)
        if tag not in tags:
            self.canvas.addtag_withtag(tag, object_id)

    def _adjust_timeline_total_days(self, timeline, more_days=None, less_days=None):
        debug('Timeline._adjust_timeline_total_days')
        
        if more_days:
            negative_or_positive=+1
        else:
            negative_or_positive=-1

        factor=timeline.total_days/15

        debug('total_days={0} min_days={1} max_days={2}'.format(timeline.total_days, timeline.min_days, timeline.max_days))
        if (more_days and timeline.total_days < timeline.max_days) or \
           (less_days and timeline.total_days > timeline.min_days):
            timeline.total_days+=factor*negative_or_positive
            timeline.draw_details()
            self.draw_items()

    def get_next_background_color(self):
        debug('Timeline.get_next_background_color')
        for color in BACKGROUND_COLORS:
            debug('color: {}'.format(color))
            yield color

    def _timeline_mouse_wheel(self, event):

        # TopLevel window (ItemForm) detects mousewheel and triggers event on root window. limiting widgetName to
        # canvas seems to fix the issue for now.
        if event.widget.widgetName != 'canvas':
            return
        
        debug('Timeline._timeline_mouse_wheel')

        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)

        if self.keyboard.f3_key_down:
            self.theme.background_color=self.get_next_background_color()
            self.draw()
            return

        if object_id:
            if event.keycode==120:
                index=item.COLORS.index(item.color)
                if index==0:
                    index=len(item.COLORS)-1
                else:
                    index-=1
            else:
                index=item.COLORS.index(item.color)
                if index==len(item.COLORS)-1:
                    index=0
                else:
                    index+=1
            item.color=item.COLORS[index]
            self.draw_item(item)
            # self.statusbox.text=item.color
            # debug('color: {}'.format(item.color))
        elif timeline:
            self.statusbox.clear()
            if self.keyboard.shift_key_down:
                if event.keycode==120:
                    timeline.height+=15
                    self.draw()
                    self.taskbar.y=self.bottom
                    self.taskbar._draw_taskbar()
                    self.statusbox.y=self.taskbar.bottom
                    self.draw_items()
                elif event.keycode==-120:
                    timeline.height-=15
                    self.draw()
                    self.taskbar.y=self.bottom
                    self.taskbar._draw_taskbar()
                    self.statusbox.y=self.taskbar.bottom
                    self.draw_items()
            else:
                if event.keycode==120:
                    self._adjust_timeline_total_days(timeline, more_days=True)
                elif event.keycode==-120:
                    self._adjust_timeline_total_days(timeline, less_days=True)

    def _build_menus(self):
        """
        Build one or more menu objects.
        """
        debug('Timeline._build_menus')
        self.menu=tk.Menu(self.root, tearoff=0)
        #self.menu.add_command(label="Status", command=self._set_status_text_for_item)
        #self.menu.add_separator()
        #self.menu.add_command(label="Rename", command=self._open_item_rename_form)

    def callback(self, dict):
        debug('Timeline.callback')
        cbkey=dict['cbkey']
        if cbkey==ItemForm.CLOSE_FORM:
            self.unselect_all_items(draw=True)
            self.draw_items()
            
    def _close(self):
        self.save()
        self.items.save()
        for t in self.timelines:
            t.save()
            
        self.root.destroy()

    def _display_time_with_text(self, time, text=None):
        debug2('Timeline._display_time_with_text')
        if time and text:
            self.statusbox.text=('{0} {1}'.format(bin.to_char(time, '%a %b %d %I:%M %p'), text))
        elif time and not text:
            self.statusbox.text=('{0}'.format(bin.to_char(time, '%a %b %d %I:%M %p')))
        else:
            self.statusbox.clear()

    def draw_items(self):
        debug2('Timeline.draw_items')
        for timeline in self.timelines:
            highlight_selected=False
            if self.last_timeline_clicked is not None:
                highlight_selected=self.last_timeline_clicked.name==timeline.name
            for item in self.items.all_items():
                x=self._get_x_from_time(item.datetime, timeline.begin_time, timeline.total_days, timeline.width)
                y=timeline.y+(item.y_as_pct_of_height*timeline.height)
                self.items.draw(item, x=x, y=y, tag='{0}_{1}'.format(timeline.name, item.key),
                    draw_label=timeline.draw_labels, highlight_selected=highlight_selected)
                
    def _item_is_on_timeline(self, item, timeline):
        return item.datetime >= timeline.begin_time and item.datetime <= timeline.end_time

    def _delete_selected_items(self, redraw=False):
        debug("Timeline_delete_selected_items")
        for item in self.items.all_selected_items():
            item.deleted=True
            if redraw:
                self.draw_item(item, delete_first=True)
        self.unselect_all_items(draw=True)
            
    def dump(self, file_name):
        f=open(file_name, mode='w')
        for item in self.items.all_items():
            if not item.deleted:
                f.write(item.title+'\n')
                f.write(bin.nvl(item.description, '')+'\n')
        f.close()

    def _get_closest_object_id_from_xy_with_tag(self, x, y, tag, start=0):
        object_id=self.canvas.find_closest(x, y, start=start)[0]
        debug2('_get_closest_object_id_from_xy_with_tag: {}'.format(object_id))
        if tag in self.canvas.gettags(object_id):
            return object_id

    def _get_x_from_time(self, datetime_object, begin_time, total_days, width):
        r=bin.days_between_two_dates(datetime_object, begin_time)/total_days*width
        return r

    def _get_next_month(self, datetime_object):
        r=datetime_object.replace(day=28)+datetime.timedelta(days=4)
        #debug("get_next_month: r={0}".format(r))
        r=r.replace(day=1)
        #debug("get_next_month: r={0}".format(r))
        return r

    def _get_item_key_from_object_id(self, object_id):
        debug2('Timeline._get_item_key_from_object_id')
        #return self._map_object_id_to_item_key[object_id]

    def _get_time_from_xy(self, x, y):
        debug2('Timeline._get_time_from_item')
        timeline=self._get_timeline_from_xy(x, y, off_screen_ok=True)
        if timeline:
            return timeline.begin_time+datetime.timedelta(days=x/self.width*timeline.total_days)
        else:
            return None

    def  _get_timeline_from_xy(self, x, y, off_screen_ok=False):
        debug2('Timeline._get_timeline_from_item: x={0} y={1}'.format(x, y))
        if off_screen_ok:
            for t in self.timelines:
                if y > t.y and y < t.bottom:
                    return t
        else:
            for t in self.timelines:
                if x > self.x and x < t.right and y > t.y and y < t.bottom:
                    return t

    def _get_y_as_pct_of_height_from_xy(self, x, y):
        debug2('Timeline._get_y_as_pct_of_height_from_xy: x={0} y={1}'.format(x, y))
        timeline=self._get_timeline_from_xy(x, y)
        if timeline:
            y_as_pct_of_height=abs(y-timeline.y)/timeline.height
        else:
            debug('ERROR!')
            y_as_pct_of_height=None
        debug('y_as_pct_of_height={}'.format(y_as_pct_of_height))
        return y_as_pct_of_height

    def _hide_selected_items(self):
        debug('Timeline._hide_selected_items')
        for item in self.items.all_selected_items():
            item.hidden=True
            item.selected=False
            self.draw_item(item, delete_first=True)
        self.unselect_all_items(draw=True)

    def _is_item_being_dragged (self):
        return 'object_id' in self._dragging

    def _timelines_set_time(self, time):
        if self.sync_timelines:
            for t in self.timelines:
                t.time=time

    def keypress(self, dict):
        debug('Timeline.keypress: {}'.format(dict))

        timeline=self._get_timeline_from_xy(x=self.mouse[0], y=self.mouse[1])

        if timeline:
            move_days={'hourly': 15/1440, 'daily': 8/24, 'monthly': 4}[timeline.name]

        # If left arrow...
        if dict['state']>1000 and dict['keycode']==37 and timeline:
            time=timeline.time+datetime.timedelta(days=move_days)
            if self.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    self._items_align('decrease_horizontal')
                else:
                    self._items_align('left')
            elif self.sync_timelines:
                self._timelines_set_time(time)
                self.draw()
                self.draw_items()
            else:
                timeline.time=time
                self.draw()
                self.draw_items()
        # If up arrow...
        elif dict['state']>1000 and dict['keycode']==38 and timeline:
            if self.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    self._items_align('decrease_vertical')
                else:
                    self._items_align('top')
        # If right arrow...
        elif dict['state']>1000 and dict['keycode']==39 and timeline:
            time=timeline.time+datetime.timedelta(days=move_days)
            if self.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    self._items_align('increase_horizontal')
                else:
                    self._items_align('right')
            elif self.sync_timelines:
                self._timelines_set_time(time)
                self.draw()
                self.draw_items()
            else:
                timeline.time=time
                self.draw()
                self.draw_items()
        # If down arrow...
        elif dict['state']>1000 and dict['keycode']==40 and timeline:
            if self.keyboard.shift_key_down:
                self._items_align('increase_vertical')
            else:
                self._items_align('bottom')
        elif dict['state']>100 and dict['keycode']==46:
            if self.keyboard.shift_key_down:
               self._keypress_shift_delete()
            else:
                self._keypress_delete()
        elif dict['state']==8 and dict['keycode']==27:
            self._keypress_escape()
        elif dict['state']==8 and dict['keycode']==112:
            self._keypress_f1()
        elif dict['state']==8 and dict['keycode']==113:
            self._keypress_f2()
        elif dict['state']==8 and dict['keycode']==114:
            self._keypress_f3()
        elif dict['state']==8 and dict['keycode']==76:
            # l Key
            self.sync_timelines=not self.sync_timelines

    def _keypress_delete(self):
        debug('Timeline._keypress_delete')
        # Todo: At the moment you can delete deleted items, delete should in fact purge here.
        self._delete_selected_items(redraw=True)
        
    def _keypress_escape(self):
        debug('Timeline._keypress_escape')
        self.unselect_all_items(draw=True)

    def _keypress_f1(self):
        debug('Timeline._keypress_f1')
        self.items.switch_label_display_format()
        self.draw_items()
        #self.statusbox.text='Display Mode {}'.format(self.item_label_int)
        
    def _keypress_f2(self):

        self._f2_display_mode+=1

        if self._f2_display_mode > 2:
            self._f2_display_mode=0

        if self._f2_display_mode==0:
            self.display_items=True
            self.display_hidden_items=False
            self.display_deleted_items=False
            text='Display: Default'
        elif self._f2_display_mode==1:
            self.display_items=False
            self.display_hidden_items=True
            self.display_deleted_items=False
            text='Display: Hidden Items'
        elif self._f2_display_mode==2:
            self.display_items=False
            self.display_hidden_items=False
            self.display_deleted_items=True
            text='Display: Deleted Items'

        self.statusbox.text=text
        self.draw_items()

    def _keypress_f3(self):
        None

    def _keypress_shift_delete(self):
        debug('Timeline._keypress_shift_delete')
        self._purge_selected_items(redraw=False)
        self.unselect_all_items(draw=True)


    def _get_item_from_object(self, object_id):
        key=self._get_item_key_from_object_id(object_id)
        item=self.items.get_by_key(key)
        return item
    
    def _get_item_from_xy(self, x, y):
        object_id=self._get_closest_object_id_from_xy_with_tag(x, y, 'item')
        return self._get_item_from_object(object_id)

    def _get_xy(self, x, y, use_object_coords=False):
        item=None
        timeline=None
        time=None
        taskbar_group=self.taskbar.get_group_from_xy(x=x, y=y)
        object_id=self._get_closest_object_id_from_xy_with_tag(x, y, 'BaseItem')
        if object_id:
            item=self.items.get_by_object_id(object_id)
            if use_object_coords:
                x,y=self.canvas.coords(object_id)[0:2]
        timeline=self._get_timeline_from_xy(x, y)
        time=self._get_time_from_xy(x, y)
        debug2('_get_xy: {0} {1} {2} {3}'.format(object_id, item, timeline, time))
        return (object_id, item, timeline, time, taskbar_group)


    def _items_align(self, direction):
        debug('Timeline._items_align: direction={}'.format(direction))
        times=[]
        all_selected_items=[]

        for item in self.items.all_selected_items():
            all_selected_items.append([item.y, item, item.x])
            times.append(item.datetime)

        number_of_items=len(all_selected_items)

        if direction in ('right', 'left'):
            if direction=='right':
                time=max(times)   
            elif direction=='left':
                time=min(times)
            for item in self.items.all_selected_items():
                item.datetime=time
        elif direction=='top':
            sorted_items=bin.sort_lists_in_list(all_selected_items, 0)
            for item in self.items.all_selected_items():
                item.y=sorted_items[0][1].y
                item.y_as_pct_of_height=sorted_items[0][1].y_as_pct_of_height
        elif direction=='bottom':
            sorted_items=bin.sort_lists_in_list(all_selected_items, 0)
            for item in self.items.all_selected_items():
                item.y=sorted_items[-1][1].y
                item.y_as_pct_of_height=sorted_items[-1][1].y_as_pct_of_height
        elif direction in ('increase_vertical', 'decrease_vertical') and number_of_items > 1:

            rollback=False
            items_modified=[]
            distance_between_items=[]

            items_sorted_from_top_down=bin.sort_lists_in_list(all_selected_items, 0)
            top_of_first_item=int(items_sorted_from_top_down[0][0])


            for i in range(1, number_of_items):
                distance_between_items.append(items_sorted_from_top_down[i][0]-items_sorted_from_top_down[i-1][0])

            distance_between_items=min(distance_between_items)

            if distance_between_items > 10:
                 multiplier={'increase_vertical': 1.2, 'decrease_vertical': .8}[direction]
            else:
                 multiplier={'increase_vertical': 2, 'decrease_vertical': .2}[direction]
                
            distance_between_items=int(distance_between_items*multiplier)

            # Vertical distance can't be less than 0.
            if distance_between_items <= 0:
                distance_between_items={'increase_vertical': 5, 'decrease_vertical': 0}[direction]

            debug('distance_between_items={}'.format(distance_between_items))
            # Get the y position of the first item as our starting point.
            y=top_of_first_item
            for item in items_sorted_from_top_down:
                rollback=(y+item[1].size > self.last_timeline_clicked.bottom)
                pct_of_height=self._get_y_as_pct_of_height_from_xy(item[1].x, y)
                rollback=pct_of_height is None or rollback
                if rollback:
                    break
                item[1].y=y
                item[1].y_as_pct_of_height=pct_of_height
                items_modified.append(item[1])
                y+=distance_between_items

            if rollback:
                debug('rollback!')
                for item in items_modified:
                    item.restore()

        elif direction in ('increase_horizontal', 'decrease_horizontal'):

            items_sorted_from_left_to_right=bin.sort_lists_in_list(all_selected_items, 2)
            minutes_between_items=[]

            for i in range(1, number_of_items):
                minutes_between_items.append(bin.minutes_between_two_dates(items_sorted_from_left_to_right[i][1].datetime, items_sorted_from_left_to_right[i-1][1].datetime))

            minutes_between_items=int(min(minutes_between_items))

            if minutes_between_items > 10:
                 multiplier={'increase_horizontal': 1.2, 'decrease_horizontal': .8}[direction]
            else:
                 multiplier={'increase_horizontal': 2, 'decrease_horizontal': .2}[direction]

            minutes_between_items=int(minutes_between_items*multiplier)

            # Horizontal distance can't be less than 0.
            if minutes_between_items <= 0:
                minutes_between_items={'increase_horizontal': 5, 'decrease_horizontal': 0}[direction]

            debug('minutes_between_items={}'.format(minutes_between_items))
            t=items_sorted_from_left_to_right[0][1].datetime
            for item in items_sorted_from_left_to_right:
                item[1].datetime=t
                t=t+datetime.timedelta(minutes=minutes_between_items)
                
        self.draw_items()

    def select_item(self, item, timeline, object_id):
        self.items.select(item)
        self.add_tag_to_object(object_id, 'selected')
        self.last_timeline_clicked=timeline

    def _item_mouse_down(self, event):
        debug('Timeline._item_mouse_down')

        # Will not need to re-draw on mouse down since this is always triggered by mouse up.

        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)

        if not item:
            debug('*** Did not click an item. ***')
            return

        if self.items.total_selected > 0 and self.last_timeline_clicked.name!=timeline.name:
            self.unselect_all_items(draw=False)

        if self.items.total_selected==0:
            self.select_item(item, timeline, object_id)
        elif self.items.total_selected==1 and not self.keyboard.control_key_down:
            if item.selected:
                self.unselect_all_items(draw=False)
            else:
                self.unselect_all_items(draw=True)
                self.select_item(item, timeline, object_id)
        elif self.items.total_selected>=1 and self.keyboard.control_key_down:
            if item.selected:
                self.items.unselect(item)
                self.canvas.dtag(object_id, 'selected')
            else:
                self.select_item(item, timeline, object_id)
        elif self.items.total_selected > 1 and not self.keyboard.control_key_down and not item.selected:
                self.unselect_all_items(draw=True)
                self.select_item(item, timeline, object_id)

        if self.items.total_selected==0:
            self.last_timeline_clicked=None

            # Shift-Delete should purge all selected items.
            # Space-bar should hide or unhide all selected items.
            # Space-bar should undelete all selected items.
            
        if not self.keyboard.control_key_down:
            self.select_item(item, timeline, object_id)
            # Get initial coords for all selected items in the event we need to abort the drag.
            self._dragging['all_coords']={}
            self._dragging['item']=item
            self._dragging['object_id']=object_id
            self.canvas.tag_raise(object_id)
            self._dragging['coords']=self.canvas.coords(object_id)
            self._dragging['x']=self._dragging['x0']=event.x
            self._dragging['y']=self._dragging['y0']=event.y
             # Store the original position of all selected items in case we need to abort the drag and drop.
            for object_id in self.canvas.gettags('selected'):
                self._dragging['all_coords']['object_id']=self.canvas.coords(object_id)

    def _item_mouse_over(self, event):
        debug2('Timeline._item_mouse_over')
        
        self.mouse=(event.x, event.y)

        if not self._is_item_being_dragged():
            object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y, use_object_coords=True)
            if object_id:
                text=None
                if time and item:
                    if item.type in ('link', 'remark'):
                        text=item.title
                    elif item.has_tags():
                        text='{0}@{1} <{2}>'.format(item.get_primary_tag(), item.title, item.status)
                    else:
                        text='{0}@{1} <{2}>'.format('', item.title, item.status)
                    self._display_time_with_text(time, text)
                else:
                    debug('No coord time!')
            else:
                debug2('No object id!')

    def _item_mouse_drag(self, event):
        debug('Timeline._item_mouse_drag')

        self.mouse=(event.x, event.y)

        if 'object_id' in self._dragging:
            debug('Dragging')
            object_id=self._dragging['object_id']
            coords=self.canvas.coords(object_id)
            self._display_time_with_text(self._get_time_from_xy(coords[0], coords[1]))
            delta_x = event.x - self._dragging["x"]
            delta_y = event.y - self._dragging["y"]
            self._dragging["x"] = event.x
            self._dragging["y"] = event.y
            self.canvas.move('selected', delta_x, delta_y)

    def _item_mouse_drag_abort(self, x, y):
        debug('Timeline._item_mouse_drag_abort')
        for k, v in self._dragging['all_coords'].items():
             debug('v={}'.format(v))
             x,y,right,bottom=v
             self.canvas.coords(k, x, y, right, bottom)

    def _item_mouse_up(self, event):
        debug('Timeline._item_mouse_up')

        self.mouse=(event.x, event.y)

        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y, use_object_coords=True)

        if not item:
            debug('*** Item not found. ***')
            return

        delta_x=0
        delta_y=0

        if 'object_id' in self._dragging:
            delta_x = event.x - self._dragging["x0"]
            delta_y = event.y - self._dragging["y0"]

        if delta_x!=0 or delta_y!=0:
            abort_drag=False
            first_timeline=None
            for object_id in self.canvas.find_withtag('selected'):
                x,y=self.canvas.coords(object_id)[0:2]
                timeline=self._get_timeline_from_xy(x,y, off_screen_ok=True)
                if not timeline:
                    abort_drag=True
                elif first_timeline is None:
                    first_timeline=timeline.name
                elif first_timeline != timeline.name:
                    abort_drag=True
            if not abort_drag:
                for object_id in self.canvas.find_withtag('selected'):
                    x,y=self.canvas.coords(object_id)[0:2]
                    item=self.items.get_by_object_id(object_id)
                    item.selected=False
                    timeline=self._get_timeline_from_xy(x,y, off_screen_ok=True)
                    item.datetime=self._get_time_from_xy(x,y)
                    item.y_as_pct_of_height=(y-timeline.y)/timeline.height
                    item.save()
                self.draw_items()
                self.unselect_all_items(draw=False)
            else:
                self._item_mouse_drag_abort(event.x, event.y)
        elif not self.keyboard.control_key_down:
            self.unselect_all_items(draw=False)
            self.select_item(item, timeline, object_id)

        self._dragging={}
        self.statusbox.clear()
        self.draw_items()
    
    def _item_mouse_doubleclick(self, event):
        debug('Timeline._item_mouse_doubleclick')
        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)
        self.root.config(cursor='wait')
        self.root.update_idletasks()
        if item.type=='task':
            self.unselect_all_items(draw=True)
            if self.keyboard.shift_key_down:
                bin.open_file_using_default_program(item.folder_with_escapes())
            else:
                f=ItemForm(root=self.root, theme=self.theme, item=item, cbfunc=(lambda dict: self.callback(dict)))
        elif item.type=='remark':
            self._timeline_disable_window()
            if item.has_tags():
                text='{0} [{1}]'.format(item.title.rstrip(), ','.join(item.tags))
            else:
                text=item.title
            f=modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text=text)
            self.unselect_all_items(draw=True)
            if f.text:
                item.text=f.text
                item.save()
                self.draw_items()
            self._timeline_enable_window()
            self.canvas.focus_force()
        elif item.type=='link':
            if self.keyboard.shift_key_down:
                bin.open_file_using_default_program(item.title)
                self.unselect_all_items(draw=True)
            else:
                f=modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text=item.text)
                self.unselect_all_items(draw=True)
                if f.text:
                    item.text=f.text
                    item.save()
                    self.draw_items()
        self.root.configure(cursor='')
        self.root.update_idletasks()

    def test(self, event):
        debug('Timeline.test')

    def _open_item_rename_form(self):
        debug('_rename_item')
        object_id=self.temp['object_id']
        key=self._get_item_key_from_object_id(object_id)
        item=self.items.get_by_key(key)
        form=modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text=item.title)
        if form.text:
            item.title=form.text
            self.draw_item(key)
        self.canvas.focus_force()

    def _object_is_item(self, object_id):
        if 'item' in self.canvas.gettags(object_id):
            return True
        else:
            return False

    def patch(self):
        None
#        for item in self.items.all_items():
#            item.delete=False
#            item.purged=False
#            item.hidden=False

    def _purge_selected_items(self, redraw=False):
        debug('Timeline._purge_selected_items')
        for item in self.items.all_selected_items():
            item.purged=True
            debug('purged item!')
            if redraw:
                self.draw_item(item, delete_first=True)

    def remove_item(self, key):
        # Not used
        debug('Timeline.remove_item')
        item=self.items.get_by_key(key)
        item.deleted=True
        self.draw_item(item)

    def save(self):
        dict={}
        bin.save_database(name='timeline', dict=dict, folder_path=os.path.join(bin.application_root_path(), 'data'))

    def load(self):
        """
        Restore any saved settings.
        """
        dict=bin.open_database(name='timeline', folder_path=os.path.join(bin.application_root_path(), 'data'))
        if dict:
            None
            #self.item_label_int=dict['item_label_int']

    def _set_status_text_for_item(self):
        debug('Timeline._set_status_text_for_item')
        if self.temp['object_id']:
            object_id=self.temp['object_id']
            key=self._get_item_key_from_object_id(object_id)
            item=self.items.get_by_key(key)
            form=modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text='')
            if form.text:
                item.status=form.text
                self.draw_item(item)
            self.canvas.focus_force()

    def _show_item_menu(self, event):
        debug('Timeline._show_item_menu')
        object_id=self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
        if self._object_is_item(object_id):
            self.temp['object_id']=object_id
            x=self.canvas.winfo_rootx()+event.x
            y=self.canvas.winfo_rooty()+event.y
            self.menu.post(x+15, y)

    def _timeline_mouse_down(self, event):
        debug('Timeline._timeline_mouse_down')
        self.mouse=(event.x, event.y)

        # Determine which timeline was clicked on.
        t=self._get_timeline_from_xy(event.x, event.y)

        if self.keyboard.shift_key_down:
            # User wants to add a new item to the timeline.
            self.keyboard.shift_key_down=False
            self._timeline_mouse_click_add_item(event.x, event.y)
        elif t:
            # This may or may not be a drag operation, but initialize just in case.
            self._dragging['timeline']=t
            self._dragging['time']=t.time
            # Need a reference to the original mouse down item.
            self._dragging['x']=event.x
            self._dragging['y']=event.y
            # Required in order to capture keypress events.
            self.canvas.focus_set()
        else:
            # In theory ending up here is impossible.
            self._dragging={}

    def _timeline_disable_window(self):
        self.theme.enabled=False
        self.draw()
        self.draw_items()

    def _timeline_enable_window(self):
        self.theme.enabled=True
        self.draw()
        self.draw_items()
        self.canvas.focus_force()

    def _timeline_mouse_click_add_item(self, x, y):
        """
        Present user with an input box and create a new item on the timeline.
        """
        timeline=self._get_timeline_from_xy(x, y)

        if not timeline:
            return

        y_pct=self._get_y_as_pct_of_height_from_xy(x, y)
        t=self._get_time_from_xy(x, y)

        self._timeline_disable_window()

        form=modalinputbox.ModalInputBox(
            root=self.root,
            canvas=self.canvas,
            text=''
        )

        if form.text:
            item_type=get_item_type_from_text(form.text)
            if item_type=='link':
                new_item=Link(app_folder=self.app_folder, text=form.text, y_pct=y_pct, datetime=t)
            elif item_type=='remark':
                new_item=Remark(app_folder=self.app_folder, text=form.text, y_pct=y_pct, datetime=t)
            elif item_type=='task':
                new_item=Task(app_folder=self.app_folder, text=form.text, y_pct=y_pct, datetime=t)
            self.items.items[new_item.key]=new_item
            new_item.save()

        self._timeline_enable_window()

    def _timeline_mouse_doubleclick(self, event):
        debug2('Timeline._timeline_mouse_doubleclick')
        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)
        if self.sync_timelines:
            for t in self.timelines:
                t.time=time
                t.draw_details()
        else:
            timeline.time=time
            timeline.draw_details()

        self.draw_items()

    def _timeline_mouse_motion(self, event):
        self.mouse=(event.x, event.y)
        if self.keyboard.shift_key_down:
            # Display time under mouse pointer when shift key down but mouse pointer not own.
            self._display_time_with_text(self._get_time_from_xy(event.x, event.y))
        else:
            self.statusbox.clear()

    def _timeline_mouse_drag(self, event):
        """
        Drag operation. B1-Motion is bound to this procedure.
        """
        debug2("Timeline._timeline_mouse_drag: {0} {1}".format(event.x, event.y))

        self.mouse=(event.x, event.y)

        # Return if drag operation has not been initialized.
        if "timeline" not in self._dragging.keys():
            return

        t=self._dragging['timeline']

        if t:
            x=event.x-self._dragging['x']
            y=event.y-self._dragging['y']
            if 'dragging' not in self._dragging.keys() and \
               ('selectbox_object_id' in self._dragging.keys() or ((y > 3 or y < -3) and (x > -50 and x < 50))):
                # This is a select using rectangle operation.
                self.canvas.delete('selectbox')
                self._dragging['selectbox_object_id']=self.canvas.create_rectangle(self._dragging['x'], self._dragging['y'], event.x, event.y, outline=self.theme.line_color, tags="selectbox")
            elif x==0:
                # This is not a drag operation, yet.
                return
            elif x > 5 or 'selectbox_object_id' not in self._dragging.keys():
                self._dragging['dragging']=True
                # This is a drag timeline operation.
                days=x/self.width*t.total_days*-1
                t.time=self._dragging['time']+datetime.timedelta(days=days)
                self._display_time_with_text(t.time)
                if self.sync_timelines:
                    for timeline in self.timelines:
                       timeline.time=t.time
                       timeline.draw_details()
                else:
                    timeline.draw_details()

                self.draw_items()

    def _timeline_mouse_up(self, event):
        debug("Timeline._timeline_mouse_up")
        if 'selectbox_object_id' in self._dragging.keys():
            x,y,x1,y1=self.canvas.coords(self._dragging['selectbox_object_id'])
            self.canvas.delete('selectbox')
            t=self._get_timeline_from_xy(event.x, event.y)
            # Only works if the start and stop of the drag are on the same timeline.
            if t.name == self._dragging['timeline'].name:
                # Get a list of all of the objects enclosed by the rectangle.
                oids=self.canvas.find_enclosed(x, y, x1, y1)
                for oid in oids:
                    debug('tags: {}'.format(self.canvas.gettags(oid)))
                    if 'BaseItem' in self.canvas.gettags(oid):
                        item=self.items.get_item_from_object_id(oid)
                        # ToDo: This item selected business is just ugly.
                        self.select_item(item, t, oid)
                self.draw_items()
            else:
                debug('*** t.name != dragging timeline name ***')
        elif "timeline" in self._dragging.keys():
            x=event.x-self._dragging['x']
            if x==0:
                # Items will stay selected if an actual timeline drag has taken place, but if not then all items will be unselected.
                self.unselect_all_items(draw=True)
        self._dragging={}

    def update_background_tasks(self):
        debug('Timeline.update_background_tasks')
        for t in self.timelines:
            t._draw_current_time()

    def unselect_all_items(self, draw=True):
        debug('Timeline.unselect_all_items')

        # Remove selected tag from all items.
        for object_id in self.canvas.gettags('selected'):
            self.canvas.dtag(object_id, 'selected')

        self.items.unselect_all(draw=draw)

        self._vertical_distance_between_items=None