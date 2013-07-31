

import tkinter as tk
import re
from debug import *
import bin
import os
import keyboard
import statusbox
import modalinputbox
import filebar
import datetime
import theme

class ItemForm():
    def __init__(self, root, theme, item):
        self.form=tk.Toplevel(root)
        self.theme=theme
        self._status_doc='<Enter Status or #Milestone>'
        self.widget_width=75
        self.item=item
        self._draw()

    def _enable_title(self, event):
        self.title_box.configure(state=tk.NORMAL)
        self.title_box.focus_set()

    def _status_keypress(self, event):
        debug('ItemForm._item_form_update_status_history: {0} {1}'.format(event.state, event.keycode))
        if event.state==8 and event.keycode==13:
            # Enter Key
            if self.status_var.get() not in ('', self._status_doc):
                self.history_box.configure(state=tk.NORMAL)
                self.item.status=self.status_var.get()
                self.history_box.insert(1.0, self.item.status_history[0]+'\n')
                self.status_var.set('')
                self.history_box.configure(state=tk.DISABLED)
        elif event.state==8 and event.keycode==27:
            # Escape Key
            self.status_var.set(self._status_doc)
            self.history_box.configure(state=tk.DISABLED)

    def _update_title(self, event):
        if event.state==8 and event.keycode==13:
            self.item.title=self.title_var.get()
            self.title_box.configure(state=tk.DISABLED)

    def _update_tags(self, event):
        if event.state==8 and event.keycode==13:
            debug('update_tags')
            self.item.tags=self.tags_var.get().split(',')

    def _draw(self):

        item=self.item

        # Title
        title_frame=tk.Frame(self.form)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        self.title_var=tk.StringVar()
        self.title_box=tk.Entry(title_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT,
                                width=self.widget_width, disabledforeground='black', textvariable=self.title_var)
        self.title_box.pack(fill=tk.X)
        self.title_box.bind('<Double-1>', self._enable_title)
        self.title_box.bind('<Key>', self._update_title)
        self.title_var.set(self.item.title)
        self.form.title(item.title)
        self.title_box.configure(state=tk.DISABLED)

        line=tk.Frame(self.form, bd=2, relief=tk.RAISED, bg='dark gray', padx=10, pady=2)
        line.pack(fill=tk.X)

        # Status
        status_frame=tk.Frame(self.form)
        status_frame.pack(fill=tk.X, padx=2, pady=2)
        self.status_var=tk.StringVar()
        self.status_box=tk.Entry(status_frame, borderwidth=1, font=self.theme.font(size='>'), relief=tk.FLAT,
                                 width=self.widget_width, textvariable=self.status_var)
        self.status_box.pack(fill=tk.X)
        self.status_box.bind('<Key>', self._status_keypress)
        self.status_var.set(self._status_doc)
        self.status_box.focus_set()
        self.status_box.select_range(0, tk.END)

        # Status history.
        history_frame=tk.Frame(self.form)
        history_frame.pack(fill=tk.X, padx=2, pady=2)
        if len(self.item.status_history) <= 6:
            history_box_height=3
        else:
            history_box_height=6

        self.history_box=tk.Text(history_frame, height=history_box_height, borderwidth=1, font=self.theme.font(),
                                 relief=tk.FLAT, width=self.widget_width, fg='dark grey')
        self.history_box.pack(side=tk.LEFT, fill=tk.X)

        for text in item.status_history:
            self.history_box.insert(tk.END, text+'\n')

        history_bar=tk.Scrollbar(history_frame)
        history_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_box.configure(yscrollcommand=history_bar.set)
        history_bar.configure(command=self.history_box.yview)

        self.history_box.configure(state=tk.DISABLED)

        # Tags
        tags_frame=tk.Frame(self.form)
        tags_frame.pack(fill=tk.X, padx=2, pady=2)
        tags_label=tk.Label(tags_frame, text='Tags', font=self.theme.font(), anchor="w", width="10", relief=tk.FLAT, fg='black')
        tags_label.pack(fill=tk.X)
        self.tags_var=tk.StringVar()
        self.tags_box=tk.Entry(tags_frame, borderwidth=2, font=self.theme.font(size='>'), relief=tk.FLAT, width=self.widget_width,
                          textvariable=self.tags_var)
        self.tags_box.pack(fill=tk.X)
        self.tags_box.bind('<Key>', self._update_tags)
        self.tags_var.set(','.join(self.item.tags))

        canvas_frame=tk.Frame(self.form)
        canvas_frame.pack(fill=tk.X, padx=2, pady=2)
        canvas=tk.Canvas(canvas_frame, width=self.widget_width, height=60, bg='white')
        canvas.pack(fill=tk.X)

        f=filebar.FileBar(root=self.form, canvas=canvas, height=60)
        debug('folder={}'.format(item.folder))
        f.add_folder(directory=item.folder.replace('\\', '\\\\'))
        f.draw()

class Item():
    def __init__(self):
        debug('Item!')
        self.key=None
        self._text=None
        self.title=None
        self.x=None
        self.y=None
        self.image_path=None
        self.state=None
        self.size=None
        self.shape='rectangle'
        self.type=None
        self.datetime=None
        self.y_as_pct_of_height=None
        self.tags=[]
        self._status=None
        self.status_history=[]
        self.folder=None
        self.object_id=None

    @property
    def text (self):
        return self._text

    @text.setter
    def text (self, text):
        self._text=text
        self._parse_input_text(text)

    @property
    def status (self):
        return self._status

    @status.setter
    def status(self, text):
        # Status history is stored in a list, with most recent status first, we also add a timestamp.
        self.status_history.insert(0, bin.to_char(datetime.datetime.now(), '%a %b %d %I:%M %p') + ' ' + text)
        self._status=text

    def add_tags(self, tags=None):
        """
        Append a single tag or extend the tag list with multiple tags if you pass in a list of tags.
        """
        if type(tags)==list:
            self.tags.extend(tags)
        else:
            self.tags.append(tags)

    def _parse_input_text(self, text):
            """
            Take the input text and parse out tags, title and current status.

            Title <status> [tag, tag]
            tag@Title <status> [tag,tag]

            """
            debug('Item._parse_input_text: {}'.format(text))

            # Values before the first '@' are tags and should be in a comma separated list
            # Some tags are special, like colors, only the first color will apply.

            self.tags=[]
            if text.find('@') > 0:
                at_tag=False
                tag=text.split('@')[0].strip()
                if ' ' not in tag:
                    at_tag=True
                    self.add_tags(tag)
                    text=text.split('@')[1]
                    
            debug('! tags={0} text={1}'.format(self.tags, text))

            # Status is in last set of angle brackets if it exist.
            if text.rfind('<') > 0:
                b=text.rfind('<')
                e=text.rfind('>')
                if b < e:
                    self.status=text[b+1:e]
                    text=text[0:b]+text[e+1:]

            debug('! status={0} text={1}'.format(self.status, text))

            # Everything in last set of brackets are tags.
            if text.rfind('['):
                b=text.rfind('[')
                e=text.rfind(']')
                if b < e:
                    are_tags=True
                    tags=text[b+1:e].split(',')
                    tags=[tag.strip() for tag in tags]
                    for tag in tags:
                        if ' ' in tag:
                            # Tags with blanks are not valid. These are probably not tags.
                            are_tags=False
                    if are_tags:
                        self.add_tags(tags)
                        text=text[0:b]+text[e+1:]

            debug('! tags={0} text={1}'.format(self.tags, text))

            self.title=text

    def _get_folder_path(self):
        new_path=os.path.join(bin.application_root_folder(), 'timeline', bin.get_valid_folder_name_from_string(self.title))
        return new_path

class NewItem(Item):
    def __init__(self, text, x, y, dt):
        super().__init__()
        # ToDo: Need to blow right up here if text is not set and x and y need to be > 0.
        debug('NewItem! {}'.format(dt))

        self.key=bin.random_string(20)
        self.x=x
        self.y=y
        # None marks a new item when drawing.
        self.state=None
        self.status='Created'
        self.datetime=dt
        
        # This action will end up setting the title, tags and status.
        self.text=text

        # At a minimum title must be set, if not we just assign text to it, but this should already be done.
        if not self.title:
            self.title=text

        self.folder=self._get_folder_path()

        bin.mkdir(self.folder)

class Items():
    def __init__(self, *args, **kwargs):
        # Returns a dictionary of all items
        self.items=bin.open_database('TIMELINE_ITEMS')

    def all_items(self):
        return self.items.values()

    def get_by_key(self, key):
        return self.items[key]

    def delete_by_key(self, key, save=True):
        """
        Delete an item.
        """
        del self.items[key]
        if save:
            self.save()
        
    def save(self):
        debug('Items.save')
        bin.save_database('TIMELINE_ITEMS', self.items)

class Timeline():

    # Callback identifiers.
    DRAG_AND_DROP=7000
    CANCEL_DRAG_AND_DROP=7001
    ADD_ITEM_TO_TIMELINE=7002
    OPEN_TASK_FROM_TIMELINE=7003
    DELETE_ITEM_FROM_TIMELINE=7004
      
    def __init__(self, *args, **kwargs):

        debug('Timeline: kwargs={}'.format(kwargs))

        self.root=kwargs['root']
        self.canvas=kwargs['canvas']
        self.theme=theme.Theme()

        self.item_label_display_int=0

        if 'keyboard' in kwargs.keys():
            self.keyboard=kwargs['keyboard']
        else:
            self.keyboard=keyboard.Keyboard(canvas=self.canvas, cbfunc=(lambda dict: self.keypress(dict)))

        if 'width' in kwargs.keys():
            self.width=kwargs['width']
        else:
            self.width=self.canvas.winfo_reqwidth()
            
        if 'height' in kwargs.keys():
            self.height=kwargs['height']
        else:
            self.height=(100,90,80)
        
        if 'statusbox' in kwargs.keys():
            self.statusbox=kwargs['statusbox']
        else:
            self.statusbox=statusbox.StatusBox(
            root=self.root,
            canvas=self.canvas,
            x=2,
            y=2,
            height=16,
            width=self.width)

        if 'default_item_type' in kwargs.keys():
           self.default_item_type=kwargs['default_item_type']
        else:
           self.default_item_type=None

        if 'default_item_shape' in kwargs.keys():
           self.default_item_type=kwargs['default_item_shape']
        else:
           self.default_item_shape='rectangle'

        self.x=0
        self.y=0

        # Stores information during drag and drop operations.
        self._dragging={}

        self.thumbnails={}
        
        self.timeline_time=None
        
        # Use object_id to return the key which was used to add the item (add_item).
        self._map_object_id_to_item_key={}

        if 'cbfunc' in kwargs.keys():
            self.cbfunc=kwargs['cbfunc']
        else:
            self.cbfunc=None

        self.canvas.focus_set()

        self.canvas.tag_bind("timelines", "<ButtonPress-1>",   self._timeline_mouse_click)
        self.canvas.tag_bind("timelines", "<B1-Motion>",       self._timeline_mouse_drag)
        self.canvas.tag_bind("timelines", "<Motion>",          self._timeline_mouse_motion)
        self.canvas.tag_bind("timelines", "<ButtonRelease-1>", self._timeline_mouse_up)
        self.canvas.tag_bind("timelines", "<Double-1>",        self._timeline_mouse_doubleclick)

        self.canvas.tag_bind("item", "<ButtonPress-1>",   self._item_mouse_down)
        self.canvas.tag_bind("item", "<B1-Motion>",       self._item_mouse_drag)
        self.canvas.tag_bind("item", "<Motion>",          self._item_mouse_over)
        self.canvas.tag_bind("item", "<ButtonRelease-1>", self._item_mouse_up)
        self.canvas.tag_bind("item", "<Double-1>",        self._item_mouse_doubleclick)
        self.canvas.tag_bind("item", "<Button-3>",        self._show_item_menu)

        self.hourly={
            'name': 'hourly',
            'y': self.y,
            'height': self.height[0],
            'total_days': .66
        }
        self.hourly['begin_time']=datetime.datetime.now()-datetime.timedelta(days=self.hourly['total_days']/2)
        self.hourly['label_format']='%I%p'

        self.daily={
            'name': 'daily',
            'y': self.hourly['y']+self.hourly['height'],
            'height': self.height[1],
            'total_days': 14
        }
        self.daily['begin_time']=datetime.datetime.now()-datetime.timedelta(days=self.daily['total_days']/2)
        self.daily['label_format']='%d%a'

        self.monthly={
            'name': 'monthly',
            'y': self.daily['y']+self.daily['height'],
            'height': self.height[2],
            'total_days': 120
        }
        self.monthly['begin_time']=datetime.datetime.now()-datetime.timedelta(days=self.monthly['total_days']/2)
        self.monthly['label_format']='%B %y'

        self.timelines=(self.hourly, self.daily, self.monthly)

        self._timelines_draw()

        # This is a dict of all of the items in the database, indexed by key.
        self.items=Items()

        self.patch()

        self.draw_items()

        # Just a temporary dict which we can use for this and that.
        self.temp={}

        self._build_menus()

    def _build_menus(self):
        """
        Build one or more menu objects.
        """
        debug('Timeline._build_menus')
        self.menu=tk.Menu(self.root, tearoff=0)
        #self.menu.add_command(label="Status", command=self._set_status_text_for_item)
        #self.menu.add_separator()
        #self.menu.add_command(label="Rename", command=self._open_item_rename_form)

    def delete_item_by_key(self, key):
        debug('Timeline.delete_item_by_key')
        self.items.delete_by_key(key, save=True)
        self.draw_items()
        if self.cbfunc:
            self.cbfunc({'cbkey': self.DELETE_ITEM_FROM_TIMELINE, 'key': key})

    def _display_time_with_text(self, time, text=None):
        debug2('Timeline._display_time_with_text')
        if time and text:
            self.statusbox.text=('{0} {1}'.format(bin.to_char(time, '%a %b %d %I:%M %p'), text))
        elif time and not text:
            self.statusbox.text=('{0}'.format(bin.to_char(time, '%a %b %d %I:%M %p')))
        else:
            self.statusbox.clear()

    def draw_items(self):
        debug('Timeline.draw_items')
        self.canvas.delete('all_items_and_labels')
        self._map_object_id_to_item_key={}
        # ToDo: Probably needs to be changed to an iterator.
        for item in self.items.all_items():
            self.draw_item(item, delete_first=False)

    def draw_item(self, item, delete_first=True):
        debug('Timeline.draw_item')

        # If this is a new item.
        if not item.state:
            item.y_as_pct_of_height=self._get_y_as_pct_of_height_from_xy(item.x, item.y)
            if not item.size:
                item.size=int(self.height[0]/10)
            item.state='open'
            self.save()

        if delete_first:
            self.canvas.delete(item.key)

        item_tags='all_items_and_labels item drags ' + item.key
        label_tags='all_items_and_labels ' + item.key
            
        for timeline in self.timelines:
            if item.datetime >= timeline['begin_time'] and item.datetime <= timeline['end_time']:

                size=item.size*{'hourly': 1, 'daily': .8, 'monthly': .8*.8}[timeline['name']]

                x=bin.days_between_two_dates(item.datetime, timeline['begin_time'])/timeline['total_days']*self.width
                y=timeline['y']+(timeline['height']*item.y_as_pct_of_height)
                if item.shape=='rectangle':
                    item.object_id=self.canvas.create_rectangle(x, y, x+size, y+size, fill='green', outline='black', tags=item_tags, stipple=None, activefill='black')
                elif item.image_path:
                    thumb_key='{0}_{1}'.format(item.key, timeline['name'])
                    # ToDo: Iterator here?
                    if thumb_key not in self.thumbnails.keys():
                        thumbnail=bin.get_photoimage_thumbnail(item.file_path, border_color='black', border_size=1, size=size)
                        self.thumbnails[thumb_key]=thumbnail
                    item.object_id=self.canvas.create_image(x, y, anchor=tk.NW, image=self.thumbnails[thumb_key], state=tk.NORMAL, tags=item_tags)
                        
                # Keep a reference so we can get a key using the object ID easily.
                self._map_object_id_to_item_key[item.object_id]=item.key

                # Draw labels for hourly timeline.
                # ToDo: This is going to break for images.
                if timeline['name']=="hourly":
                    
                    if   self.item_label_display_int==0:
                        display_text=''
                    elif self.item_label_display_int==1:
                        display_text=item.title
                    elif self.item_label_display_int==2:
                        display_text='{0}@{1}'.format(item.tags[0], item.title)
                    elif self.item_label_display_int==3:
                        display_text='{}'.format(item.status)
                    elif self.item_label_display_int==4:
                        display_text='{0}@{1}'.format(item.tags[0], item.status)
                    elif self.item_label_display_int==5:
                        display_text='{0}@{1} <{2}>'.format(item.tags[0], item.title, item.status)

                    x,y,right,bottom=self.canvas.coords(item.object_id)
                    object_id=self.canvas.create_text(right+5, y-2, text=display_text, font=self.theme.font(size='<<'), fill="black", tags=label_tags, anchor="nw", justify="left")

    def _get_closest_object_id_from_xy_with_tag(self, x, y, tag, start=0):
        object_id=self.canvas.find_closest(x, y, start=start)[0]
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
        debug('Timeline._get_item_key_from_object_id')
        return self._map_object_id_to_item_key[object_id]

    def _get_time_from_xy(self, x, y):
        debug('Timeline._get_time_from_item')
        timeline=self._get_timeline_from_xy(x, y)
        if timeline:
            return timeline['begin_time']+datetime.timedelta(days=x/self.width*timeline['total_days'])
        else:
            return None

    def _get_timeline_from_xy(self, x, y):
        debug('Timeline._get_timeline_from_item: x={0} y={1}'.format(x, y))
        for t in self.timelines:
            if x > self.x and x < t['right'] and y > t['y'] and y < t['bottom']:
                return t

    def _get_y_as_pct_of_height_from_xy(self, x, y):
        timeline=self._get_timeline_from_xy(x, y)
        y_as_pct_of_height=abs(y-timeline['y'])/timeline['height']
        return y_as_pct_of_height

    def _is_item_being_dragged (self):
        return 'object_id' in self._dragging
    
    def keypress(self, dict):
        debug('Timeline.keypress: {}'.format(dict))
        # F1 key press
        if dict['state']==8 and dict['keycode']==112:
            self.item_label_display_int+=1
            if self.item_label_display_int > 4:
                self.item_label_display_int=0
            # ToDo: To speed performance up here I cold just draw the hourly items.
            self.draw_items()
        
    def _item_mouse_down(self, event):
        debug2('_item_mouse_down: x={0} y={1}'.format(event.x, event.y))
        # event.x and event.y are the based on the item of the cursor. not the object being clicked.
        object_id=self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
        if self.keyboard.escape_key_down:
            self.delete_item_by_key(self._get_item_key_from_object_id(object_id))

        if 'drags' in self.canvas.gettags(object_id):
            key=self._get_item_key_from_object_id(object_id)
            self._dragging['item']=self.items.get_by_key(key)
            self._dragging['object_id']=object_id
            self.canvas.tag_raise(object_id)
            # Store the original position in case we need to abort the drag and drop.
            self._dragging['coords']=self.canvas.coords(object_id)
            self._dragging['x']=self._dragging['x0']=event.x
            self._dragging['y']=self._dragging['y0']=event.y

    def _item_mouse_over(self, event):
        debug2('Timeline._item_mouse_over')
        if not self._is_item_being_dragged():
            object_id=self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
            if object_id:
                coords=self.canvas.coords(object_id)
                time=self._get_time_from_xy(coords[0], coords[1])
                timeline=self._get_timeline_from_xy(event.x, event.y)
                key=self._get_item_key_from_object_id(object_id)
                item=self.items.get_by_key(key)
                text=None
                if time and key:

                    if self.item_label_display_int==0:
                        text=''
                    elif self.item_label_display_int==1:
                        text=item.title
                    elif self.item_label_display_int==2:
                        text='{0}@{1}'.format(item.tags[0], item.title)
                    elif self.item_label_display_int==3:
                        '[{}]'.format(item.status)
                    elif self.item_label_display_int==4:
                        text='{0}@{1}'.format(item.tags[0], item.status)

                    self._display_time_with_text(time, text)
                else:
                    debug('No coord time!')
            else:
                debug('No object id!')

    def _item_mouse_drag(self, event):
        debug2('_item_mouse_drag')
        if 'object_id' in self._dragging:
            object_id=self._dragging['object_id']
            coords=self.canvas.coords(object_id)
            self._display_time_with_text(self._get_time_from_xy(coords[0], coords[1]))
            delta_x = event.x - self._dragging["x"]
            delta_y = event.y - self._dragging["y"]
            self._dragging["x"] = event.x
            self._dragging["y"] = event.y
            self.canvas.move(object_id, delta_x, delta_y)

    def _item_mouse_drag_abort(self, x, y):
        debug2('_item_mouse_drag_abort')
        x,y,right,bottom=self._dragging['coords']
        self.canvas.coords(self._dragging['object_id'], x, y, right, bottom)

    def _item_mouse_up(self, event):
        debug2('_item_mouse_up')

        if 'object_id' not in self._dragging:
            return
        else:
            object_id=self._dragging['object_id']

        delta_x = event.x - self._dragging["x0"]
        delta_y = event.y - self._dragging["y0"]

        if delta_x != 0 or delta_y != 0:
            x,y=self.canvas.coords(object_id)[0:2]
            item=self._dragging['item']
            timeline=self._get_timeline_from_xy(x,y)
            if timeline:
                item.datetime=self._get_time_from_xy(x,y)
                item.x=x
                item.y_as_pct_of_height=(y-timeline['y'])/timeline['height']
                del self._map_object_id_to_item_key[object_id]
                self.canvas.delete(item.key)
                self.draw_item(item)
                # Make sure we save changes to timeline database.
                self.save()
                if self.cbfunc and item.type != 'image':
                    self.cbfunc({'cbkey': self.DRAG_AND_DROP, 'item': item})
            else:
                self._item_mouse_drag_abort(event.x, event.y)
                if self.cbfunc:
                     # Add the x and y drop locations.
                    self.cbfunc({'cbkey': self.CANCEL_DRAG_AND_DROP, 'item': item, 'x':x, 'y':y})

        self._dragging={}
        self.statusbox.clear()

    def _item_mouse_doubleclick(self, event):
        debug2('Timeline._item_mouse_doubleclick')
        object_id=self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
        key=self._get_item_key_from_object_id(object_id)
        item=self.items.get_by_key(key)
        f=ItemForm(root=self.root, theme=self.theme, item=item)
        #self.open_form_for_item(key)
        #self.canvas.focus_force()

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

    def remove_item(self, key):
        debug('Timeline.remove_item')
        self.items.delete(key=key, save=True)
        self.draw_items()

    def save(self):
        self.items.save()
        
    def _save_timeline_begin_times(self):
        self.hourly['dragging_begin_time']=self.hourly['begin_time']
        self.daily['dragging_begin_time']=self.daily['begin_time']
        self.monthly['dragging_begin_time']=self.monthly['begin_time']

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

    def _set_first_label_time(self):
        """
        Calculates the time of the first label for each timeline using the current begin_time.
        """
        self.hourly['first_label']=self.hourly['begin_time'].replace(minute=0, second=0, microsecond=0)
        self.daily['first_label']=self.daily['begin_time'].replace(hour=0, minute=0, second=0, microsecond=0)
        self.monthly['first_label']=self.monthly['begin_time'].replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _show_item_menu(self, event):
        debug('Timeline._show_item_menu')
        object_id=self._get_closest_object_id_from_xy_with_tag(event.x, event.y, 'item')
        if self._object_is_item(object_id):
            self.temp['object_id']=object_id
            x=self.canvas.winfo_rootx()+event.x
            y=self.canvas.winfo_rooty()+event.y
            self.menu.post(x+15, y)

    def _timeline_mouse_click(self, event):
        debug('Timeline._timeline_mouse_click')
        # Determine which timeline was clicked on.
        t=self._get_timeline_from_xy(event.x, event.y)

        if self.keyboard.shift_key_down:
            self.keyboard.shift_key_down=False
            self._timeline_mouse_click_add_item(event.x, event.y)
        else:
            self._save_timeline_begin_times()

            if t:
                self._dragging['timeline']=t
                # Required in order to capture keypress events.
                self.canvas.focus_set()
                debug('timeline={}'.format(t))
            else:
                self._dragging={}
                critical('ERROR: Could not locate a timeline on mouse down click!')
            # Need a reference to the original mouse down item.
            self._dragging['x']=event.x

    def _timeline_mouse_click_add_item(self, x, y):
        timeline=self._get_timeline_from_xy(x, y)
        if timeline:
            self.theme.enabled=False
            self._timelines_draw()
            self.draw_items()
            form=modalinputbox.ModalInputBox(
                root=self.root,
                canvas=self.canvas,
                text=''
            )
            if form.text:
                new_item=NewItem(text=form.text, x=x, y=y, dt=self._get_time_from_xy(x, y))
                key=new_item.key
                self.items.items[key]=new_item
                # Do not save here, save will occur on the draw since this is a new item.
                self.draw_item(new_item)
                if self.cbfunc:
                    self.cbfunc({'cbkey': self.ADD_ITEM_TO_TIMELINE, 'item': self.items[key]})
            self.theme.enabled=True
            self._timelines_draw()
            self.draw_items()
            self.canvas.focus_force()

    def _timeline_mouse_doubleclick(self, event):
        debug2('_timeline_mouse_doubleclick')
        t=self._get_time_from_xy(event.x, event.y)
        for timeline in self.timelines:
            timeline['begin_time']=t-datetime.timedelta(days=timeline['total_days']/2)
            self._timelines_draw_details()

    def _timeline_mouse_motion(self, event):
        if self.keyboard.shift_key_down:
            self._display_time_with_text(self._get_time_from_xy(event.x, event.y))
        else:
            self.statusbox.clear()

    def _timeline_mouse_drag(self, event):
        debug2("_timeline_mouse_drag")

        if "timeline" not in self._dragging.keys():
            critical('timeline not in _dragging.keys!')
            return

        t=self._dragging['timeline']

        if t:
            x=event.x-self._dragging['x']
            if x==0:
                return

            days=x/self.width*t['total_days']*-1

            self.monthly['begin_time']=self.monthly['dragging_begin_time']+datetime.timedelta(days=days)
            self.daily['begin_time']=self.monthly['begin_time']+datetime.timedelta(days=self.monthly['total_days']/2)-datetime.timedelta(days=self.daily['total_days']/2)
            self.hourly['begin_time']=self.monthly['begin_time']+datetime.timedelta(days=self.monthly['total_days']/2)-datetime.timedelta(days=self.hourly['total_days']/2)

            self.timeline_time=self.monthly['begin_time']+datetime.timedelta(days=self.monthly['total_days']/2)
            self._display_time_with_text(self.timeline_time)

            self._timelines_draw_details()
            self.draw_items()
        else:
            critical('ERROR: timeline not found while dragging!')

    def _timeline_mouse_up(self, event):
        debug2("timeline_mouse_up")
        self.draw_items()
        self._dragging_timeline={}
        self.statusbox.clear()

    def _timelines_draw(self):
        debug2('_timelines_draw')
        self.canvas.delete("timelines")
        for t in self.timelines:
            t['right']=self.x+self.width
            t['bottom']=t['y']+t['height']
            t['center_x']=self.x+(self.width/2)
            t['center_y']=t['y']+(t['height']/2)
            object_id=self.canvas.create_rectangle(self.x, t['y'], t['right'], t['bottom'], fill=self.theme.background_color, outline=self.theme.line_color, tags="timelines")
            self.canvas.tag_lower(object_id)
        self._timelines_draw_details()

    def _timelines_draw_details(self):
        debug2('Timeline._timelines_draw_details')
        self.canvas.delete("timeline_detail")
        # Recalculate the time of first label for each timeline using current begin_time.
        self._set_first_label_time()
        for t in self.timelines:
            font_size={'hourly':'<<', 'daily': '<<', 'monthly': '<<'}[t['name']]
            t['end_time']=t['begin_time']+datetime.timedelta(days=t['total_days'])
            x=self._get_x_from_time(t['first_label'], t['begin_time'], t['total_days'], self.width)
            label_time=t['first_label']
            for i in range(1,100):
                l=bin.to_char(label_time, t['label_format'])
                self.canvas.create_line(x, t['y'], x, t['bottom'], fill=self.theme.line_color, tags="timeline_detail")
                self.canvas.create_text(x+3,t['bottom']-8, font=self.theme.font(size=font_size), text=l, anchor="w", fill=self.theme.font_color, tags="timeline_detail")
                if t['name']=='hourly':
                    label_time=label_time+datetime.timedelta(hours=1)
                elif t['name']=='daily':
                    label_time=label_time+datetime.timedelta(hours=24)
                elif t['name']=='monthly':
                    label_time=self._get_next_month(label_time)
                x=self._get_x_from_time(label_time, t['begin_time'], t['total_days'], self.width)
                if label_time > t['begin_time']+datetime.timedelta(days=t['total_days']):
                    break

            # Draw red line in middle of timeline.
            x=self._get_x_from_time(t['begin_time']+datetime.timedelta(days=t['total_days']/2), t['begin_time'], t['total_days'], self.width)
            self.canvas.create_line(x, t['y'], x, t['y']+t['height'], fill='red', tags="timeline_detail")

            # Draw blue line at current time.
            x=self._get_x_from_time(datetime.datetime.now(), t['begin_time'], t['total_days'], self.width)
            self.canvas.create_line(x, t['y'], x, t['y']+t['height'], fill='blue', tags="timeline_detail")
