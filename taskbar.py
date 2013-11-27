__author__ = 'Ethan Post'

# ToDo: Ability to open file dialog from file bar and file gets added to filebar.
# ToDo: Same as above but ability to add a folder.
# ToDo: Ability to set up filters using regex for file name patterns.
# ToDo: Hide a file until time X. Keep backups of files. Sync filebar to dropbox.
# ToDo: Add status updates to the group by clicking while holding down a key or double clicking.
# ToDo: Taskbar is not logging adds and deletes, need to add a logger or perhaps just log from tasks.

import tkinter as tk
import os
from bin import *
import time
from PIL import ImageTk, Image, ImageOps
from debug import *
from collections import OrderedDict
import keyboard

# If a task does has not been dropped on a timeline than it must currently live on the task bar.
# It must belong to a group on the task bar or it goes to the default group.
# Groups can be renamed.
# Group can be added and deleted.
# Groups can be dragged and dropped to change the order of the groups.
# Groups can not be deleted if there are still tasks in the group. They must be deleted or removed.
# When a task is dragged to the timeline it removed from the group but can easily be returned.
   # When it is deleted from the timeline user should ask if they want to delete the task or return to the group.
# Groups can have tags so tag filters apply to groups. Any task in a group inherits the groups tasks.
# You can change the color of the background on a group.
# You can assign an image to a group and it will be resized. User should be able to find a good aspect
   # ratio for the image so they look good.

class TaskBar():

    DELETE_TASK_FROM_TASKBAR=6001
    DRAGGING_TASK_FROM_TASKBAR=6002
    DROP_TASKBAR_ITEM=6003
    CANCEL_DRAG_AND_DROP=6004
    OPEN_TASK_FROM_TASKBAR=6005
    NEW_TASK_ADDED_TO_TASKBAR=6006
    
    def __init__(self, *args, **kwargs):

        debug('TaskBar: kwargs={}'.format(kwargs))

        if 'root' not in kwargs.keys():
            return
        else:
            self.root=kwargs['root']

        if 'canvas' not in kwargs.keys():
            return
        else:
            self.canvas=kwargs['canvas']

        if 'keyboard' not in kwargs.keys():
            self.keyboard=keyboard.Keyboard(canvas=self.canvas, cbfunc=(lambda dict: self.keypress(dict)))
        else:
            self.keyboard=kwargs['keyboard']

        if 'width' not in kwargs.keys():
            self.width=self.canvas.winfo_reqwidth()
        else:
            self.width=kwargs['width']

        # Height of the hourly timeline.
        if 'height' not in kwargs.keys():
            self.height=25
        else:
            self.height=kwargs['height']

        if 'statusbox' in kwargs.keys():
            self.statusbox=kwargs['statusbox']
        else:
            self.statusbox=None

        self.x=0
        self.y=0

        self._map_object_id_to_item_key={}

        self.temp={}

        if 'cbfunc' in kwargs.keys():
            self.cbfunc=kwargs['cbfunc']
        else:
            self.cbfunc=None

        d=open_database('taskbar')
        
        if 'groups' in d.keys():
            self.groups=d['groups']
        else:
            self.groups={}

        if 'items' in d.keys():
            self.items=d['items']
        else:
            self.items={}

        if 'groups_key_list' in d.keys():
            self.groups_key_list=d['groups_key_list']
        else:
            self.groups_key_list=[]
            self.add_new_group(key='default', name='Default')

        # ToDo: How is this offset working, not sure???
        self.offset=0

        if 'x' in kwargs.keys():
            self.x=kwargs['x']
        else:
            self.x=None

        if 'y' in kwargs.keys():
            self._y=kwargs['y']
        else:
            self._y=None

        if 'height' in kwargs.keys():
            self._height=kwargs['height']
        else:
            self._height=None

        if 'width' in kwargs.keys():
            self.width=kwargs['width']
        else:
            self.width=None

        if 'bordersize' in kwargs.keys():
            self.bordersize=kwargs['bordersize']
        else:
            self.bordersize=None

        self.bottom=None
        
        self._dragging={}
        
        self.total_width=None
        self.border=None

        self._draw_taskbar()
        
        self.draw_items()

        self.canvas.tag_bind("taskbar", "<ButtonPress-1>", self._group_mouse_click)
        self.canvas.tag_bind("taskbar", "<B1-Motion>", self._group_mouse_drag)
        self.canvas.tag_bind("taskbar", "<Motion>", self._group_mouse_motion)
        self.canvas.tag_bind("taskbar", "<ButtonRelease-1>", self._group_mouse_up)
        self.canvas.tag_bind("taskbar", "<Double-1>", self._group_mouse_doubleclick)
        self.canvas.tag_bind("taskbar_add_group", "<ButtonPress-1>", self._open_group_name_window)
        self.canvas.tag_bind("taskbar_delete_group", "<ButtonPress-1>", self._delete_group)

#        self.canvas.tag_bind("taskbar_item", "<ButtonPress-1>",   self._item_mouse_down)
#        self.canvas.tag_bind("taskbar_item", "<B1-Motion>",       self._item_mouse_drag)
#        self.canvas.tag_bind("taskbar_item", "<Motion>",          self._item_mouse_motion)
#        self.canvas.tag_bind("taskbar_item", "<ButtonRelease-1>", self._item_mouse_up)
#        self.canvas.tag_bind("taskbar_item", "<Double-1>",        self._item_mouse_doubleclick)
        
        self.toplevel=None

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y=y

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height=height

    def _update_bottom(self):
        self.bottom=self.y+self.height

    def keypress(self, dict):
        debug('TaskBar.keypress: {}'.format(dict))
        
    def add_statusbox_to_class(self, statusbox):
        debug2('TaskBar.add_statusbox_to_class')
        self.statusbox=statusbox
        
    def draw_items(self):
        debug2('TaskBar.draw_items')
        self.canvas.delete('taskbar_item')
        self.canvas.delete('taskbar_item_label')
        self._map_object_id_to_item_key={}
        self.bottom=self.y+self.height
        for key in self.items.keys():
            self.draw_item(key)

    def draw_item(self, key):
        debug2('TaskBar.draw_item: {}'.format(key))

        item=self.items[key]
        tags='taskbar_item {0} {1}'.format(item['key'], 'drags')
        group=self.groups[item['group_key']]
        x=int(group['x']+group['width']*item['x_as_pct_of_width'])
        y=int(group['y']+group['height']*item['y_as_pct_of_height'])
        
        object_id=self.canvas.create_rectangle(x, y, x+item['size'], y+item['size'], fill='white', outline='black', tags=tags, stipple=None, activefill='yellow')

        # Keep a reference so we can get a key using the object ID easily.
        self._map_object_id_to_item_key[object_id]=item['key']

    def update_task(self, key, save=True, **kwargs):
        debug('TaskBar.update_task')
        item=self.items[key]

        if 'group_key' in kwargs.keys():
            group=self.groups[kwargs['group_key']]
        else:
            group=self.groups[item['group_key']]

        for k in kwargs.keys():
            if k=='x':
                self.items[key]['x_as_pct_of_width']=abs(kwargs['x']-group['x'])/group['width']
            elif k=='y':
                self.items[key]['y_as_pct_of_height']=abs(kwargs['y']-group['y'])/group['height']
            elif k in item.keys():
                item[k]=kwargs[k]

        if save:
            self.save_taskbar()

    def add_item_to_taskbar_group (
        self,
        key,
        name,
        group_key=None,
        color=None,
        size=None,
        x_as_pct_of_width=None,
        y_as_pct_of_height=None,
        x=None,
        y=None):

        debug('TaskBar.add_item_to_taskbar')

        color=nvl(color, 'black')
        size=nvl(size, 10)

        group=self.groups[group_key]

        if x or y:
            x_as_pct_of_width=abs(x-group['x'])/group['width']
            y_as_pct_of_height=abs(y-group['y'])/group['height']
            
        self.items[key]={
            'key'                       : key,
            'name'                      : name,
            'group_key'                 : group_key,
            'color'                     : color,
            'size'                      : size,
            'x_as_pct_of_width'         : x_as_pct_of_width,
            'y_as_pct_of_height'        : y_as_pct_of_height
        }

        self.draw_item(key)
        self.save_taskbar()

    def get_group_from_xy(self, x, y):
        debug('TaskBar._get_group_from_xy: x={0} y={1}'.format(x, y))
        for g in self.groups.values():
            debug3('g: {}'.format(g))
            if x >= g['x'] and x <= g['right'] and y >= g['y'] and y <= g['bottom']:
                debug3('get_group_from_xy: {}'.format(g))
                return g

    def save_taskbar(self):
        d={}
        d['groups']=self.groups
        d['items']=self.items
        d['groups_key_list']=self.groups_key_list
        save_database('taskbar', d)
        
    def _open_group_name_window(self, event):
        debug('TaskBar.open_group_name_window')
        self.toplevel=tk.Toplevel(padx=1, pady=1)
        width=500
        height=30
        left=int((self.canvas.winfo_rootx()+self.x+(self.width/2))-(width/2))
        top=int((self.canvas.winfo_rooty()+(self.y+self.height)/2)-(height/2))
        self.toplevel.geometry('{0}x{1}+{2}+{3}'.format(width, height, left, top))
        self.toplevel.transient(self.root)
        self.toplevel.grab_set()
        # Nothing works without this line!
        self.toplevel.update_idletasks()
        self.toplevel.overrideredirect(1)
        self.name=tk.Entry(self.toplevel, highlightthickness=1, takefocus=True, font=('Arial', 8), text="", relief=tk.FLAT, bd=1, insertwidth=1, insertofftime=500, insertontime=500)
        self.name.pack(fill=tk.BOTH, expand=True)
        self.name.bind("<Return>", self._group_add_save)
        self.name.bind("<Escape>", self._group_add_cancel)
        # Learned how to create a model window here, http://tkinter.unpythonic.net/wiki/ModalWindow.
        self.name.focus_force()
        self.toplevel.lift()
        self.root.wait_window(self.toplevel)

    def _delete_group(self, event):
        debug('TaskBar._delete_group')
        group=self.get_group_from_xy(event.x, event.y)
        if not group:
            return

        for v in self.items.values():
            debug3('v: {}'.format(v))
            if v['group_key']==group['key']:
                debug3('_delete_group: {}'.format(v))
                v['group_key']='default'
                
        del self.groups[group['key']]
        self.groups_key_list.remove(group['key'])
        self._draw_groups()
        self.draw_items()
        self.save_taskbar()
        
    def add_new_group(self, key, name):
        debug('TaskBar.add_new_group')
        if key not in self.groups.keys():
            self.groups[key]={
                'key': key,
                'name': name,
                'x': None,
                'y': None,
                'right': None,
                'bottom': None,
                'width': None,
                'height': None
            }
        self.groups_key_list.append(key)
        self.save_taskbar()

    def _group_add_save(self, event):
        debug('TaskBar._group_add_save')
        new_key=random_string(20)
        self.add_new_group(key=new_key, name=self.name.get())
        self.toplevel.destroy()
        self.canvas.focus_force()
        self._draw_groups()

    def _group_add_cancel(self, event):
        self.toplevel.destroy()

    def _draw_taskbar(self):
        debug('TaskBar._draw_taskbar')
        
        if not self.x:
            self.x=self.canvas.winfo_x()
        if not self.y:
            self.y=self.canvas.winfo_y()
        if not self.width:
            self.width=self.canvas.winfo_reqwidth()
        if not self.height:
            self.height=self.canvas.winfo_reqheight()
        if not self.bordersize:
            self.bordersize=1

        group_count=len(self.groups)

        if self.width/group_count < 200:
            self.group_width=200
        else:
            self.group_width=int(self.width/group_count)
            self.group_width=200

        self.canvas.delete("taskbar")
        object_id=self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, fill='white', outline='black', tags="taskbar")
        self.canvas.tag_lower(object_id)
        self._draw_groups()
        self._update_bottom()

    def _draw_groups(self):
        debug3('TaskBar._draw_groups')
        self.canvas.delete("taskbar_group","taskbar_add_group", "taskbar_delete_group")
        x=self.x+self.offset
        y=self.y

        object_id=self.canvas.create_line(x, y, x, y+self.height, fill='black', tags="taskbar-group")

        for key in self.groups_key_list:
            group=self.groups[key]
            group['x']=x
            x+=self.group_width
            group['right']=x
            group['y']=y
            group['bottom']=y+self.height
            group['height']=self.height
            group['width']=self.group_width
            object_id=self.canvas.create_line(x, y, x, group['bottom'], fill='black', tags="taskbar_group")
            object_id=self.canvas.create_text(x+5-self.group_width,y+1, font=("Arial", 8), text=group['name'], anchor="nw", fill='black', tags="taskbar_group")
            if group['key'] != 'default':
                object_id=self.canvas.create_rectangle(group['right']-10, y, group['right'], group['y']+10, fill='light gray', tags='taskbar_add_group' )
                object_id=self.canvas.create_text(group['right']-8, y-2, font=("Arial", 8), text='x', anchor="nw", fill='black', tags="taskbar_delete_group")
        
        x0=x
        x+=int(self.group_width*.1)
        object_id=self.canvas.create_rectangle(x0, y, x, y+self.height, fill='light gray', tags="taskbar_add_group")
        object_id=self.canvas.create_text(x0+(int(self.group_width*.1/2)),y+int(self.height/2), font=("Arial", 16), text='+', anchor=tk.CENTER, fill='black', tags="taskbar_add_group")
        
        self.total_width=x

    def _group_mouse_click_add_item(self, x, y):
        # Need to save the x and y position. When the item is saved we will need to refer to this.
        self.temp={'x':x, 'y':y}
        self.toplevel=tk.Toplevel(padx=1, pady=1)
        width=500
        height=30
        left=int((self.canvas.winfo_rootx()+self.x+(self.width/2))-(width/2))
        top=int((self.canvas.winfo_rooty()+self.bottom/2)-(height/2))
        debug3('geo: {0}x{1}+{2}+{3}'.format(width, height, left, top))
        self.toplevel.geometry('{0}x{1}+{2}+{3}'.format(width, height, left, top))
        self.toplevel.transient(self.root)
        self.toplevel.grab_set()
        self.toplevel.update_idletasks()
        self.toplevel.overrideredirect(1)
        self.name=tk.Entry(self.toplevel, highlightthickness=1, takefocus=True, text="", relief=tk.FLAT, bd=1, insertwidth=1, insertofftime=500, insertontime=500)
        self.name.pack(fill=tk.BOTH, expand=True)
        self.name.bind("<Return>", self._group_mouse_click_add_item_save)
        self.name.bind("<Escape>", self._group_mouse_click_add_item_cancel)
        # Learned how to create a model window here, http://tkinter.unpythonic.net/wiki/ModalWindow.
        self.name.focus_force()
        self.toplevel.lift()
        self.root.wait_window(self.toplevel)

    def _group_mouse_click_add_item_save(self, event):
       debug('TaskBar._group_mouse_click_add_item_save')
       g=self.get_group_from_xy(self.temp['x'], self.temp['y'])
       if g:
           new_key=random_string(20)
           self.add_item_to_taskbar_group(
               key=new_key,
               name=self.name.get(),
               group_key=g['key'],
               x=self.temp['x'],
               y=self.temp['y']
           )
           self.toplevel.destroy()
           self.canvas.focus_force()
           self.save_taskbar()
           self.draw_item(key=new_key)
           if self.cbfunc:
               self.cbfunc({'cbkey': self.NEW_TASK_ADDED_TO_TASKBAR, 'item': self.items[new_key]})
       else:
           critical('_timeline_mouse_click_add_item_save: Did not identify the timeline!')

    def _group_mouse_click_add_item_cancel(self, event):
        self.toplevel.destroy()
        self.canvas.focus_force()

    def _group_mouse_click(self, event):
        debug('TaskBar._group_mouse_click')
        if not self.keyboard.shift_key_down:
            # Store the original position in case we need to abort the drag and drop.
            self._dragging['x']=self._dragging['x0']=event.x
            self._dragging['axis']='?'
            self.canvas.focus_set()
        else:
            # Determine which group was clicked on.
            g=self.get_group_from_xy(event.x, event.y)
            self.keyboard.shift_key_down=False
            self._group_mouse_click_add_item(event.x, event.y)

    def _group_mouse_drag(self, event):
        debug2("_group_mouse_drag")
        delta_x0 = event.x - self._dragging['x0']

        if not self._dragging['x']:
            return

        if self._dragging['axis']=='?':
            if abs(delta_x0) > 10:
                self._dragging['axis']='x'
            else:
                return

        delta_x = event.x - self._dragging["x"]
        self.offset=self.offset+delta_x
        if self.offset > 0:
            self.offset = 0
        self._dragging['x']=event.x

        if self._dragging['axis']=='x':
            # delta_x=self._get_valid_delta(delta_x)
            self._draw_groups()
            self.draw_items()

    def _group_mouse_motion(self, event):
        self.statustext(None)
    
    def _group_mouse_up(self, event):
        debug('TaskBar._group_mouse_up')
        # self.cbfunc({'#': self.TASKBAR_MOUSE_UP})

    def _group_mouse_doubleclick(self, event):
        debug("_group_mouse_doubleclick")

    def right_keypress(self):
        None

    def left_keypress(self):
        None

    def _get_closest_object_id_from_xy(self, x, y, start=0):
        object_id=self.canvas.find_closest(x, y, start=start)[0]
        return object_id

    def remove_item(self, key):
        debug('TaskBar.remove_item')
        del self.items[key]
        self.save_taskbar()
        self.draw_items()

    def delete_item(self, key):
        debug('TaskBar.delete_item')
        del self.items[key]
        self.save_taskbar()
        self.draw_items()
        if self.cbfunc:
            self.cbfunc({'cbkey': self.DELETE_TASK_FROM_TASKBAR, 'key': key})



    def _get_item_key_from_object_id(self, object_id):
        if object_id in self._map_object_id_to_item_key.keys():
            return self._map_object_id_to_item_key[object_id]
        else:
            return None

    def statustext(self, text):
        debug2('TaskBar.statustext: {}'.format(text))
        if self.statusbox:
            if text:
                self.statusbox.set_text(text)
            else:
                self.statusbox.clear()

    def _get_item_from_object_id(self, object_id):
        key=self._get_item_key_from_object_id(object_id)
        if key in self.items.keys():
            return self.items[key]
        else:
            return None
        
#    def _item_mouse_down(self, event):
#        debug('TaskBar._item_mouse_down')
#        object_id=self._get_closest_object_id_from_xy(event.x, event.y)
#
#        if not object_id:
#            return
#
#        if self.keyboard.escape_key_down:
#            self.delete_item(self._get_item_key_from_object_id(object_id))
#
#        if 'drags' in self.canvas.gettags(object_id):
#            self._dragging['object_id']=object_id
#
#            self.canvas.tag_raise(object_id)
#            # Store the original position in case we need to abort the drag and drop.
#            self._dragging['x']=self._dragging['x0']=event.x
#            self._dragging['y']=self._dragging['y0']=event.y
#
#    def _item_mouse_motion(self, event):
#        debug('_item_mouse_motion')
#        if 'object_id' not in self._dragging:
#            object_id=self._get_closest_object_id_from_xy(event.x, event.y)
#            if object_id:
#                key=self._get_item_key_from_object_id(object_id)
#                if key:
#                    text=self.items[key]['name']
#                    self.statustext(text)
#
#    def _item_mouse_drag(self, event):
#        debug('_item_mouse_drag')
#        if 'object_id' in self._dragging:
#            object_id=self._dragging['object_id']
#            coords=self.canvas.coords(object_id)
#            item=self._get_item_from_object_id(object_id)
#            self.cbfunc({'cbkey':self.DRAGGING_TASK_FROM_TASKBAR, 'x':coords[0], 'y':coords[1], 'name':item['name']})
#            delta_x = event.x - self._dragging["x"]
#            delta_y = event.y - self._dragging["y"]
#            self._dragging["x"] = event.x
#            self._dragging["y"] = event.y
#            self.canvas.move(object_id, delta_x, delta_y)
#
#    def _item_mouse_drag_abort(self, x, y):
#        debug('_item_mouse_drag_abort')
#        delta_x = self._dragging["x0"] - x
#        delta_y = self._dragging["y0"] - y
#        self.canvas.move(self._dragging['object_id'], delta_x, delta_y)
#
#    def _item_mouse_up(self, event):
#        debug('TaskBar._item_mouse_up')
#
#        if 'object_id' not in self._dragging:
#            return
#        else:
#            object_id=self._dragging['object_id']
#
#        delta_x = event.x - self._dragging["x0"]
#        delta_y = event.y - self._dragging["y0"]
#
#        if delta_x != 0 or delta_y != 0:
#            x0,y0,right,bottom=self.canvas.coords(object_id)
#            item=self._get_item_from_object_id(object_id)
#            group=self.get_group_from_xy(x0, y0)
#            if group:
#
#                self.canvas.delete(item['key'])
#                self.update_task(key=item['key'], save=True, group_key=group['key'], x=x0, y=y0)
#
#                del self._map_object_id_to_item_key[object_id]
#                self.draw_item(item['key'])
#
#                if self.cbfunc:
#                    self.cbfunc({'cbkey': self.DROP_TASKBAR_ITEM, 'item': item})
#            else:
#                self._item_mouse_drag_abort(event.x, event.y)
#                if self.cbfunc:
#                     # Add the x and y drop locations.
#                    self.cbfunc({'cbkey': self.CANCEL_DRAG_AND_DROP, 'item': item, 'x':x0, 'y':y0})
#
#        self._dragging={}
#        self.statustext(None)
#
#    def _item_mouse_doubleclick(self, event):
#        debug('_item_mouse_doubleclick')
#        object_id=self._get_closest_object_id_from_xy(event.x, event.y)
#        if self.cbfunc:
#            self.cbfunc({'cbkey': self.OPEN_TASK_FROM_TASKBAR, 'key': self._get_item_key_from_object_id(object_id)})