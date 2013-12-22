
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
from profilehooks import coverage, profile, timecall

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

class Drawers():
    def __init__(self):
        self.key=bin.random_string(20)
        self.name=name
        self._height=height
        self.theme=theme
        self.type=type
        self._y=y
        self._x=None
        self._database_path=os.path.join(bin.application_root_path(), 'data', 'drawers_{}.cfg'.format(self.name))

    def load(self):
        d=bin.open_database2(self._database_path)
        if d:
            self.height=d['height']
            self.key=d['key']
        
class Timeline():
    label_display_formats=['none', 'title', 'tag@title', 'status']
    object_type='timeline'
    def __init__(self, name, theme, items, statusbox, type, y, height, time, canvas, draw_labels=False, group=0):

        self._pages=4
        self._type=None
        self.label_format=None
        self._time=None
        self.min_days_displayed=None
        self.max_days_displayed=None
        self._total_days_displayed=None
        self.total_days=None

        self.key=bin.random_string(20)
        self.name=name
        self.height=height
        self.canvas=canvas
        self.theme=theme
        self.items=items
        self.group=group
        self.statusbox=statusbox
        self.type=type
        self.y=y
        # X always 0 for now.
        self.x=0
        self.width=canvas.winfo_reqwidth()*self._pages
        self.left=self.x-(self.width/2)
        self.right=self.x+(self.width/2)
        self.top=self.y
        self.middle=canvas.winfo_reqwidth()/2
        self.bottom=self.y+height
        self._right=None
        self._bottom=None
        self.begin_time=None
        self.end_time=None
        self.first_label=None
        self._database_path=os.path.join(bin.application_root_path(), 'data', 'timeline_{}.cfg'.format(self.name))
        self.object_id=None
        self.draw_labels=draw_labels
        self.time=time
        self.label_display_format_index=0
        self._highlight_selected=False

    def _on_configure(self):
        debug('Timeline: _on_configure')
        self.width=self.canvas.winfo_reqwidth()*self._pages
        self.left=self.x-(self.width/2)
        self.right=self.x+(self.width/2)
        self.top=self.y
        self.middle=self.canvas.winfo_reqwidth()/2
        self.bottom=self.y+self.height
        #debug('reqwidth={}'.format(self.canvas.winfo_reqwidth()))

    @property
    def total_selected(self):
        return self.items.total_selected

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type=type
        if type=='hourly':
            self.label_format='%I%p'
            self._total_days_displayed=.5
            self.min_days_displayed=.1
            self.max_days_displayed=1
        elif type=='daily':
            self.label_format='%d%a'
            self._total_days_displayed=5
            self.min_days_displayed=2
            self.max_days_displayed=15
        elif type=='monthly':
            self.label_format='%B %y'
            self._total_days_displayed=90
            self.min_days_displayed=60
            self.max_days_displayed=180
        debug('type={0} label_format={1}'.format(type, self.label_format))
        self.total_days=self._total_days_displayed*self._pages

    @property
    def highlight_selected(self):
        return self._highlight_selected

    @highlight_selected.setter
    def highlight_selected(self, tf):
        if tf != self._highlight_selected:
            debug('highlight_selected={0} for timeline {1}'.format(tf, self.name))
            self._highlight_selected=tf
            self.unselect_all(draw=False)
            
    def _get_pct_of_height_from_y(self, y):
       debug2('Timeline._get_pct_of_height_from_y')
       y_as_pct_of_height=abs(y-self.y)/self.height
       return y_as_pct_of_height

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

            debug2('distance_between_items={}'.format(distance_between_items))
            # Get the y position of the first item as our starting point.
            y=top_of_first_item
            for item in items_sorted_from_top_down:
                rollback=(y+item[1].size > self.bottom)
                pct_of_height=self._get_pct_of_height_from_y(y)
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

    def switch_label_display_format(self):
        debug('Timeline.switch_label_display_format')
        self.label_display_format_index+=1
        if self.label_display_format_index > len(self.label_display_formats)-1:
            self.label_display_format_index=0

    @property
    def total_days_displayed(self):
        return self._total_days_displayed

    @total_days_displayed.setter
    def total_days_displayed(self, total_days_displayed):
        if total_days_displayed > self.min_days_displayed and total_days_displayed < self.max_days_displayed:
            self.total_days=total_days_displayed*self._pages
            self._total_days_displayed=total_days_displayed
            self._on_time_change()


    def unselect_all(self, draw=True):
        debug('Timeline.unselect_all')
        # Set selected attribute to false for all items.
        for item in self.items.all_items():
            if item.selected:
                item.selected=None
                if draw:
                    self.draw_item(item)
        self.items.total_selected=0

    def draw_items(self):
        debug2('Timeline.draw_items')
        for item in self.items.all_items():
            self.draw_item(item)

    # ToDo: Change display_label to include_label
    def draw_item(self, item, x=None, y=None, tag=None):
        debug('Timeline.draw_item: x={0} y={1}'.format(x, y))

        if x is not None:
            item.x=x
        else:
            item.x=self._get_x_from_time(item.datetime)

        if y is not None:
            item.y=y
        else:
            item.y=self.y+(self.height*item.y_as_pct_of_height)



        unique_id='{0}_{1}'.format(self.name, item.key)
        key='key={}'.format(item.key)
        tags='{0} {1} {2} {3} {4}'.format(key, 'BaseItem', item.key, unique_id, self.key)

        debug('x={0} y={1}'.format(item.x, item.y))

        self.canvas.delete(unique_id)

        if item.selected and self.highlight_selected:
            border_width=2
            outline_color='black'
            dash=(1,2)
            tags=tags + ' selected'
        else:
            border_width=1
            outline_color='black'
            dash=None

        object_id=self.canvas.create_rectangle(item.x, item.y, item.x+item.size, item.y+item.size, fill=item.color,
           outline=outline_color, tags=tags, stipple=None, width=border_width, dash=dash)

        debug('drawing, object_id={}'.format(object_id))
        
        if self.draw_labels:
            debug2('Drawing label')
            display_format=self.label_display_formats[self.label_display_format_index]
            if display_format=='none':
                label=None
            elif display_format=='title':
                label=item.title
            elif display_format=='tag@title':
                if len(item.tags) > 0:
                    label='{0}@{1}'.format(item.tags[0], item.title)
                else:
                    label=item.title
            elif display_format=='status':
                if item.status is not None:
                    label=item.status
                else:
                    label=item.title
            x,y,right,bottom=self.canvas.coords(object_id)
            self.canvas.create_text(right+5, y-2, text=label, font=self.theme.font(size='<<'), fill="black",
                tags=tags, anchor="nw", justify="left")

        return object_id

    def save(self):
        d={'height':self.height,
           'total_days': self.total_days,
           'key': self.key}
        bin.save_database2(self._database_path, d)

    def load(self):
        d=bin.open_database2(self._database_path)
        if d:
            #self.height=d['height']
            #self.total_days=d['total_days']
            self.key=d['key']
            self.time=datetime.datetime.now()

    def redraw(self):
        self._on_configure()
        self.draw()
        
    def draw(self, y=None):

        if y is not None:
            self.top=y
            self.y=y

        self._on_configure()
        self.canvas.delete(self.key)
        self.object_id=self.canvas.create_rectangle(self.left, self.top, self.right, self.bottom,
            fill=self.theme.background_color, outline=self.theme.line_color, tags=(self.key, 'timelines'))
        self.canvas.tag_lower(self.object_id)
        self.draw_details(delete=False)
        debug('Timeline.draw: x={0} top={1} right={2} bottom={3} middle={4}'.format(self.x, self.top, self.right, self.bottom, self.middle))

    def _get_x_from_time(self, time):
        r=self.left+(bin.days_between_two_dates(time, self.begin_time)/self.total_days*self.width)
        debug2('_get_x_from_time: time={0} begin_time={1} total_days={2} width={3} r={4}'.format(time, self.begin_time, self.total_days, self.width, r))
        return r
        
    def _get_time_from_x(self, x):
        x_as_days_from_begin_time=self.total_days*((abs(self.left)+x)/self.width)
        # ToDo: I don't understand why the +1 is needed here! WHY???? And only works when total days not .5!
        r=self.begin_time+datetime.timedelta(days=x_as_days_from_begin_time)
        debug('_get_time_from_x: x={0} total_days={1} width={2} begin_time={3} r={4} x_as_days_from_begin_time={5}'.format(x, self.total_days, self.width, self.begin_time, r, x_as_days_from_begin_time))
        return r

    def move2(self, days):
        time_to_move_to=self.time+datetime.timedelta(days=days)
        x_to=self._get_x_from_time(time_to_move_to)
        x_from=self._get_x_from_time(self.time)
        x=x_from-x_to
        #x_to_move_to=self._get_x_from_time(time)
        #x_now=self._get_x_from_time(self.time)
        #x=x_now-x_to_move_to
        debug('Timeline.move: x={}'.format(x))
        self.canvas.move('moves', x, 0)
        self.time=time_to_move_to

    def move(self, time):
        coords=self.canvas.coords(self.object_id)
        x_to_move_to=self._get_x_from_time(time)
        x_now=self._get_x_from_time(self.time)
        x=x_now-x_to_move_to
        debug('Timeline.move: x={}'.format(x))
        self.canvas.move(self.key, x, 0)
        self.time=time
        
    def _get_next_month(self, datetime_object):
        r=datetime_object.replace(day=28)+datetime.timedelta(days=4)
        r=r.replace(day=1)
        return r

    def draw_details(self, delete=True):
        """
        Draw the lines and labels for the given timeline.
        """
        debug2('Timeline.draw_details')

        if delete:
            self.canvas.delete(self.key)

        self.canvas.delete('red'+self.key)
        
        font_size='<<'

        # Get the X position of the first label.

        x=self._get_x_from_time(self.first_label)
        debug('first_label={}'.format(x))

        label_time=self.first_label
        span=999
        for i in range(1,500):
            l=bin.to_char(label_time, self.label_format)
            self.canvas.create_line(x, self.top, x, self.bottom, fill=self.theme.line_color, tags=(self.key))
            self.canvas.create_text(x+3,self.bottom-8, font=self.theme.font(size=font_size), text=l, anchor='w', fill=self.theme.font_color, tags=(self.key))

            if i==2:
                span=x-first_x

            first_x=x

            if self.type=='hourly':
                label_time=label_time+datetime.timedelta(hours=1)
                #if self.total_days_displayed <= .5:
                if span > 100:
                    for i in range(1,4):
                        minute_time=label_time+datetime.timedelta(days=i*15/1440)
                        x=self._get_x_from_time(minute_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill='light gray', tags=(self.key))
                        self.canvas.create_text(x+3,self.top+8, font=self.theme.font(size=font_size), text=str(i*15), anchor='w', fill='light gray', tags=(self.key))
            elif self.type=='daily':
                if span > 400:
                    for i in range(1,24):
                        hourly_time=label_time+datetime.timedelta(hours=i)
                        x=self._get_x_from_time(hourly_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill='light gray', tags=(self.key))
                        self.canvas.create_text(x+3,self.top+8, font=self.theme.font(size=font_size), text=str(i), anchor='w', fill='light gray', tags=(self.key))
                label_time=label_time+datetime.timedelta(hours=24)
            elif self.type=='monthly':
                if span > 500:
                    for i in range(1,bin.get_number_of_days_in_month_from_datetime(label_time)):
                        daily_time=label_time+datetime.timedelta(hours=i*24)
                        x=self._get_x_from_time(daily_time)
                        self.canvas.create_line(x, self.top, x, self.bottom, fill='light gray', tags=(self.key))
                        self.canvas.create_text(x+3,self.top+8, font=self.theme.font(size=font_size), text=str(i+1), anchor='w', fill='light gray', tags=(self.key))
                label_time=self._get_next_month(label_time)

            x=self._get_x_from_time(label_time)

            #if label_time > self.begin_time+datetime.timedelta(days=self.total_days):
                #break
            if label_time > self.end_time:
                break

        # Draw red line in middle of timeline.
        x=self._get_x_from_time(self.time)
        self.canvas.create_line(self.middle, self.top, self.middle, self.bottom, fill='red', tags=('red'+self.key))

        # Draw blue line at current time.
        #tag="blue_line"
        #self.canvas.delete(tag)
        #x=self._get_x_from_time(datetime.datetime.now(), self.begin_time, self.total_days, self.width)
        #self.canvas.create_line(x, self.y, x, self.y+self.height, fill='blue', tags=tag)
        self._draw_current_time()

        self.draw_items()

    def _draw_current_time(self):
        self.canvas.delete('blue'+self.key)
        # Draw blue line at current time.
        x=self._get_x_from_time(datetime.datetime.now())
        self.canvas.create_line(x, self.top, x, self.bottom, fill='blue', tags=(self.key, 'blue'+self.key))

    @property
    def time(self):
        return self._time

    @time.setter
    def time (self, time):
        self._time=time
        self._on_time_change()

    def _on_time_change(self):
        debug('_on_time_change: type={}'.format(self.type))
        #self.begin_time=self._time-datetime.timedelta(days=self.total_days/2+(self.total_days/self._pages/2))
        self.begin_time=self.time-datetime.timedelta(days=(self.total_days/2)+(self.total_days_displayed/2))
        self.end_time=self.begin_time+datetime.timedelta(days=self.total_days)

        if self.type=='hourly':
            self.first_label=self.begin_time.replace(minute=0, second=0, microsecond=0)
            debug('first_label={}'.format(self.first_label))
        elif self.type=="daily":
            self.first_label=self.begin_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.type=="monthly":
            self.first_label=self.begin_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

class BaseItem():

    COLORS=['white', 'grey', 'black', 'green', 'blue', 'yellow', 'red']

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

    display_groups=['default', 'hidden', 'deleted']

    def __init__(self, folder):

        self.items={}
        self.label_display_format_index=0
        self.display_group_index=0

        deleted=re.compile('.*_deleted_.*')
        # Find all items. Each item has a _data_ directory.
        for data_dir in bin.find(root=folder, type='d', name='_data_'):
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

    def delete_selected_items(self):
        debug('Items.delete_selected_items')
        for item in self.all_selected_items:
            item.deleted=True

    def hide_selected_items(self):
        debug('Items.hide_selected_items')
        for item in self.all_selected_items:
            item.hidden=True

    def clear_items_from_screen(self):
        self.canvas.delete('BaseItem')
        
    def switch_display_group(self):
        debug('Items.switch_display_group')
        self.display_group_index+=1
        if self.display_group_index > len(self.display_groups)-1:
            self.display_group_index=0
            
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

    def delete_by_key(self, key, save=True):
        """
        Delete an item.
        """
        self.items[key].deleted=True
        del self.items[key]

    def save(self):
        for item in self.all_items():
            item.save()

#    def draw(self, item, x=None, y=None, tag=None, draw_label=False, highlight_selected=False):
#        """
#        Draw a single item on the canvas at a single point.
#        """
#        draw=False
#        if self.get_display_group()=='default' and not item.hidden and not item.deleted:
#            draw=True
#        elif self.get_display_group()=='hidden' and item.hidden and not item.deleted:
#            draw=True
#        elif self.get_display_group()=='deleted' and item.deleted:
#            draw=True
#
#        if draw:
#            object_id=item._draw(canvas=self.canvas, theme=self.theme, x=x, y=y, tag=tag, draw_label=draw_label,
#                highlight_selected=highlight_selected)
#            self.object_id_map[object_id]=item.key

    def select(self, item):
        """
        Mark an item as selected.
        """
        if not item.selected:
            item.selected=True
            self._total_selected+=1
            debug('*** total_selected={}'.format(self._total_selected))

    def unselect(self, item):
        """
        Mark an item as unselected.
        """
        if item.selected:
            item.selected=False
            self._total_selected-=1
            debug('*** total_selected={}'.format(self._total_selected))

    def get_display_group(self):
        return self.display_groups[self.display_group_index]
        

class TaskManager():

    def __init__(self, root, canvas, theme, **kwargs):
        self.root=root
        self.canvas=canvas
        self.theme=theme
        #self.group='default'
        self.timelines=[]
        self.statusbox=None
        # All drawable objects must have a draw method and bottom property.
        # Drawable objects are timelines and statusboxes (so far).
        self._drawable_objects=[]
        self.drawers=[]
        self.bottom=0
        self.groups={}
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

        self._build_menus()

        # Reference to application root_path.
        self.app_folder=bin.application_root_path()

        # Where deleted item are stored.
        self.default_deleted_items_path=os.path.join(self.app_folder, 'items', '_deleted_')
        bin.mkdir(self.default_deleted_items_path)

    def set_group(self, name, items, sync=True):
        self.group={'name': name, 'items': items, 'sync': sync}
        
    def add_timeline (self, name, type, items, y, height, statusbox=None, draw_labels=None, group=0):
    
        time=datetime.datetime.now()
        timeline=Timeline(name=name, theme=self.theme, items=items, statusbox=statusbox, type=type, y=y, height=height,
            time=time, canvas=self.canvas, draw_labels=draw_labels, group=group)
        timeline.load()
        self.timelines.append(timeline)
        self._drawable_objects.append(timeline)
        self.bottom=timeline.bottom
        if group not in self.groups.keys():
            self.groups[group]={'sync':True}
       
    def draw(self, x=None, y=None, width=None):
        if x is None:
            x=self.x
        if width is None:
            width=self.canvas.winfo_reqwidth()
        if y is None:
            _y=0
        else:
            _y=y
        # All drawable objects must have a draw method and bottom property.
        for object in self._drawable_objects:
            if object.object_type=='timeline':
                object.draw(y=_y)
            else:
                object.draw(x=x, y=_y, width=width)
            _y=object.bottom
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

        self.drawers=None
        
        #self.load()

        #self.draw(0, 0, self.width)

        self.patch()

    def add_statusbox(self, statusbox):
        self._drawable_objects.append(statusbox)

    def add_drawers(self):
        Drawers(root=self.root, canvas=self.canvas, theme=self.theme, keyboard=self.keyboard, height=25,
            x=0, y=self.bottom)
        
    def add_tag(self, object_id, tag):
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

        factor=timeline.total_days_displayed/15

        timeline.total_days_displayed+=factor*negative_or_positive
        timeline.draw()

    def _timeline_mouse_wheel(self, event):

        # TopLevel window (ItemForm) detects mousewheel and triggers event on root window. limiting widgetName to
        # canvas seems to fix the issue for now.
        if event.widget.widgetName != 'canvas':
            return
        
        debug('Timeline._timeline_mouse_wheel')

        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)

        if self.keyboard.f3_key_down:
            self.theme.get_next_background_color()
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
                    #self.taskbar.y=self.bottom
                    #self.taskbar._draw_taskbar()
                    #self.statusbox.y=self.taskbar.bottom
                    #self.draw_items()
                elif event.keycode==-120:
                    timeline.height-=15
                    self.draw()
                    #self.taskbar.y=self.bottom
                    #self.taskbar._draw_taskbar()
                    #self.statusbox.y=self.taskbar.bottom
                    #self.draw_items()
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

    def _item_is_on_timeline(self, item, timeline):
        return item.datetime >= timeline.begin_time and item.datetime <= timeline.end_time

    def delete_selected_items(self):
        debug("Timeline.delete_selected_items")
        self.items.delete_selected_items()
        self.unselect_all_items(draw=False)
        self.draw_items()

    def hide_selected_items(self):
        debug("Timeline.hide_selected_items")
        self.items.hide_selected_items()
        self.unselect_all_items(draw=False)
        self.draw_items()

    def dump(self, file_name):
        f=open(file_name, mode='w')
        for item in self.items.all_items():
            if not item.deleted:
                f.write(item.title+'\n')
                f.write(bin.nvl(item.description, '')+'\n')
        f.close()

    def _get_closest_object_id_from_xy_with_tag(self, x, y, tag, start=0):
        object_id=self.canvas.find_closest(x, y, start=start)[0]
        #debug2('_get_closest_object_id_from_xy_with_tag: {}'.format(object_id))
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

    def  _get_timeline_from_xy(self, x, y, off_screen_ok=False):
        #debug2('Timeline._get_timeline_from_item: x={0} y={1}'.format(x, y))
        if off_screen_ok:
            for t in self.timelines:
                if y > t.y and y < t.bottom:
                    return t
        else:
            for t in self.timelines:
                if x > self.x and x < t.right and y > t.y and y < t.bottom:
                    return t

    def _is_item_being_dragged (self):
        return 'object_id' in self._dragging

    def _timelines_move(self, time, timeline):
        if self.groups[timeline.group]['sync']==True:
            timeline.move(time)
            for t in self.timelines:
                if t.group==timeline.group:
                    #t.move(time)
                    t.time=time
        else:
            t.move(time)

    def _timelines_set_time(self, time, timeline):
        #if self.groups[timeline.group]['sync']==True:
        if True:
            for t in self.timelines:
                if t.group==timeline.group:
                    t.time=time
                    t.draw_details()
        else:
            timeline.time=time
            timeline.draw_details()

    def keypress(self, dict):
        debug2('Timeline.keypress: {}'.format(dict))

        timeline=self._get_timeline_from_xy(x=self.mouse[0], y=self.mouse[1])

        if timeline:
            move_days={'s': 15/1440, 'daily': 8/24, 'monthly': 4}[timeline.name]

        # If left arrow...
        if dict['state']>1000 and dict['keycode']==37 and timeline:
            time=timeline.time+datetime.timedelta(days=move_days)
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('decrease_horizontal')
                else:
                    timeline._items_align('left')
            else:
                self._timelines_set_time(time, timeline)
        # If up arrow...
        elif dict['state']>1000 and dict['keycode']==38 and timeline:
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('decrease_vertical')
                else:
                    timeline._items_align('top')
        # If right arrow...
        elif dict['state']>1000 and dict['keycode']==39 and timeline:
            time=timeline.time-datetime.timedelta(days=move_days)
            if timeline.items.total_selected > 1:
                if self.keyboard.shift_key_down:
                    timeline._items_align('increase_horizontal')
                else:
                    timeline._items_align('right')
            else:
                self._timelines_set_time(time, timeline)
        # If down arrow...
        elif dict['state']>1000 and dict['keycode']==40 and timeline:
            if self.keyboard.shift_key_down:
                timeline._items_align('increase_vertical')
            else:
                timeline._items_align('bottom')
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
            self.groups[timeline.group]['sync']=not self.groups[timeline.group]['sync']

    def _keypress_delete(self):
        debug('Timeline._keypress_delete')
        # Todo: At the moment you can delete deleted items, delete should in fact purge here.
        self.delete_selected_items(redraw=True)
        
    def _keypress_escape(self):
        debug('Timeline._keypress_escape')
        self.unselect_all_items(draw=True)

    def _keypress_f1(self):
        debug('Timeline._keypress_f1')
        x,y=self.mouse
        timeline=self._get_timeline_from_xy(x=x, y=y, off_screen_ok=False)
        if timeline:
            timeline.switch_label_display_format()
            timeline.draw_items()
        #self.statusbox.text='Display Mode {}'.format(self.item_label_int)
        
    def _keypress_f2(self):
        self.items.switch_display_group()
        self.items.clear_items_from_screen()
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

    def _get_item_key_from_object_id(self, object_id):
        tags=self.canvas.gettags(object_id)
        for tag in tags:
            if tag.startswith('key='):
                return tag.split('=')[-1]
            
    def _get_xy(self, x, y, use_object_coords=False):
        item=None
        timeline=None
        time=None
        #taskbar_group=self.taskbar.get_group_from_xy(x=x, y=y)
        taskbar_group=None
        object_id=self._get_closest_object_id_from_xy_with_tag(x, y, 'BaseItem')
        timeline=self._get_timeline_from_xy(x, y)
        if timeline:
            time=timeline._get_time_from_x(x)
        if object_id:
            key=self._get_item_key_from_object_id(object_id)
            if timeline:
                item=timeline.items.get_by_key(key)
            if use_object_coords:
                x,y=self.canvas.coords(object_id)[0:2]
        debug2('_get_xy: {0} {1} {2} {3}'.format(object_id, item, timeline, time))
        return (object_id, item, timeline, time, taskbar_group)


    def select_timeline(self, timeline):
        #debug('TaskManager.select_timeline: _drawable_objects={}'.format(self._drawable_objects))
        for object in self._drawable_objects:
            if object.object_type=='timeline':
                #debug('TaskManager.select_timeline: name={}'.format(object.name))
                if object.name==timeline.name:
                    if not object.highlight_selected:
                        self.unselect_all_items(draw=False, timeline=object)
                        object.highlight_selected=True
                else:
                    object.highlight_selected=False

    def select_item(self, item, timeline, object_id):
        # This could end up calling an unselect_all so make sure this line is before the select.
        self.select_timeline(timeline)
        timeline.items.select(item)
        debug('select_item: object_id={}'.format(object_id))
        self.add_tag(object_id, 'selected')

    def _item_mouse_down(self, event):
        debug('Timeline._item_mouse_down')

        # Will not need to re-draw on mouse down since this is always triggered by mouse up.

        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)
        allow_drag=not self.keyboard.control_key_down

        if not item:
            debug('*** Did not click an item. ***')
            return

        self.select_timeline(timeline)

        if timeline.items.total_selected==0:
            self.select_item(item, timeline, object_id)
        elif timeline.items.total_selected==1 and not self.keyboard.control_key_down:
            debug('****')
            if not item.selected:
                self.unselect_all_items(draw=False, timeline=timeline)
                self.select_item(item, timeline, object_id)
                allow_drag=False
            else:
                self.unselect_all_items(draw=False, timeline=timeline)
                
        elif timeline.items.total_selected>=1 and self.keyboard.control_key_down:
            if item.selected:
                timeline.items.unselect(item)
                self.canvas.dtag(object_id, 'selected')
            else:
                self.select_item(item, timeline, object_id)
        elif timeline.items.total_selected > 1 and not self.keyboard.control_key_down and not item.selected:
                self.unselect_all_items(draw=True, timeline=timeline)
                self.select_item(item, timeline, object_id)

        #if timeline.items.total_selected==0:
        #    self.last_timeline_clicked=None

            # Shift-Delete should purge all selected items.
            # Space-bar should hide or unhide all selected items.
            # Space-bar should undelete all selected items.
            
        if allow_drag:
            self.select_item(item, timeline, object_id)
            # Get initial coords for all selected items in the event we need to abort the drag.
            self._dragging['all_coords']={}
            self._dragging['item']=item
            self._dragging['object_id']=object_id
            self.canvas.tag_raise(object_id)
            self._dragging['coords']=self.canvas.coords(object_id)
            self._dragging['x']=self._dragging['x0']=event.x
            self._dragging['y']=self._dragging['y0']=event.y
            self._dragging['timeline']=timeline
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
            self._display_time_with_text(self._dragging['timeline']._get_time_from_x(coords[0]))
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

       # if not item:
            #debug('*** Item not found. ***')
            #return

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
                    # Objects were dropped in such a way that they ended up on two or more timelines.
                    abort_drag=True
            if not abort_drag:
                for object_id in self.canvas.find_withtag('selected'):
                    x,y=self.canvas.coords(object_id)[0:2]
                    key=self._get_item_key_from_object_id(object_id)
                    item=timeline.items.get_by_key(key)
                    item.datetime=timeline._get_time_from_x(x)
                    debug('item.datetime: {}'.format(item.datetime))
                    item.y_as_pct_of_height=(y-timeline.y)/timeline.height
                    item.save()
                self.unselect_all_items(draw=False, timeline=self._dragging['timeline'])
            else:
                debug('*** aborting drag event ***')
                self._item_mouse_drag_abort(event.x, event.y)
                self.unselect_all_items(draw=False, timeline=self._dragging['timeline'])
                
        elif not self.keyboard.control_key_down:
            self.unselect_all_items(draw=False, timeline=timeline)
            self.select_item(item, timeline, object_id)

        self._dragging={}
        self.statusbox.clear()
        #timeline.draw_items()
        self.draw()
    
    def _item_mouse_doubleclick(self, event):
        debug('Timeline._item_mouse_doubleclick')
        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)
        self.root.config(cursor='wait')
        self.root.update_idletasks()
        if item.type=='task':
            self.unselect_all_items(draw=True, timeline=timeline)
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
            self.unselect_all_items(draw=True, timeline=timeline)
            if f.text:
                item.text=f.text
                item.save()
                self.draw_items()
            self._timeline_enable_window()
            self.canvas.focus_force()
        elif item.type=='link':
            if self.keyboard.shift_key_down:
                bin.open_file_using_default_program(item.title)
                self.unselect_all_items(draw=True, timeline=timeline)
            else:
                f=modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text=item.text)
                self.unselect_all_items(draw=True, timeline=timeline)
                if f.text:
                    item.text=f.text
                    item.save()
                    self.draw_items()
        self.root.configure(cursor='')
        self.root.update_idletasks()

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
        if 'BaseItem' in self.canvas.gettags(object_id):
            return True
        else:
            return False

    def patch(self):
        None

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
        bin.save_database(name='TaskManager', dict=dict, folder_path=os.path.join(bin.application_root_path(), 'data'))

    def load(self):
        """
        Restore any saved settings.
        """
        dict=bin.open_database(name='TaskManager', folder_path=os.path.join(bin.application_root_path(), 'data'))
        if dict:
            None
            #if 'drawers' in dict.keys():
            #    self.drawers=dict['drawers']
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
        self.statusbox=t.statusbox

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

    def _timeline_enable_window(self):
        self.theme.enabled=True
        self.draw()
        self.canvas.focus_force()

    def _timeline_mouse_click_add_item(self, x, y):
        """
        Present user with an input box and create a new item on the timeline.
        """
        timeline=self._get_timeline_from_xy(x, y)

        if not timeline:
            return

        y_pct=timeline._get_pct_of_height_from_y(y)
        t=timeline._get_time_from_x(x)

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
            timeline.items.items[new_item.key]=new_item
            new_item.save()

        self._timeline_enable_window()

    def _timeline_mouse_doubleclick(self, event):
        debug('Timeline._timeline_mouse_doubleclick')
        object_id,item,timeline,time,taskbar_group=self._get_xy(event.x, event.y)
        self.groups[timeline.group]['sync']=True
        self._timelines_move(time, timeline)
        #self._timelines_set_time(time, timeline)
    
    def _timeline_mouse_motion(self, event):
        self.mouse=(event.x, event.y)
        timeline=self._get_timeline_from_xy(x=event.x, y=event.y, off_screen_ok=False)
        if timeline:
            self.statusbox=timeline.statusbox
            if self.keyboard.shift_key_down:
                # Display time under mouse pointer when shift key down but mouse pointer not own.
                self._display_time_with_text(timeline._get_time_from_x(event.x))
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
                days=x/t.width*t.total_days*-1
                time=self._dragging['time']+datetime.timedelta(days=days)
                self._timelines_move(time, t)
                #t.move(self._dragging['time']+datetime.timedelta(days=days))
                #t.time=self._dragging['time']+datetime.timedelta(days=days)
                self._display_time_with_text(t.time)
                
                #self._timelines_set_time(t.time, t)

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
                    if 'BaseItem' in self.canvas.gettags(oid):
                        key=self._get_item_key_from_object_id(oid)
                        item=t.items.get_by_key(key)
                        # ToDo: This item selected business is just ugly.
                        self.select_item(item, t, oid)
            else:
                debug('*** t.name != dragging timeline name ***')
        elif "timeline" in self._dragging.keys():
            x=event.x-self._dragging['x']
            # if x==0 then the timeline was not moved, so this click on the timeline should unselect all times selected.
            if x==0:
                # Items will stay selected if an actual timeline drag has taken place, but if not then all items will be unselected.
                self.unselect_all_items(draw=False, timeline=self._dragging['timeline'])
                # self._dragging['timeline'].unselect_all(draw=True)
        self._dragging={}
        self.draw()

    def update_background_tasks(self):
        debug('Timeline.update_background_tasks')
        for t in self.timelines:
            t._draw_current_time()

    def unselect_all_items(self, draw=True, timeline=None):
        debug('Timeline.unselect_all_items')

        # Remove selected tag from all items.
        for object_id in self.canvas.gettags('selected'):
            self.canvas.dtag(object_id, 'selected')

        if timeline:
            timeline.unselect_all(draw=draw)

        #if self.last_timeline_clicked:
            #self.last_timeline_clicked.unselect_all(draw=draw)
        #self.items.unselect_all(draw=draw)
