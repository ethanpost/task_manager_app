import tkinter as tk
from debug import debug as debug, critical as error
# from debug import dump as dump_debug
import taskmanager
import theme
import datetime
import os
import bin
import cProfile
import shutil


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.version = 0
        # Initial geometry of our window (width, height, xoffset, yoffset)
        self.geometry('950x360+100+100')
        self.set_window_title('Task Manager')

        # Create a theme object which will be used to handle colors and fonts.
        self.theme = theme.Theme()
        self.theme.font_name = "Courier"
        self.theme.background_color = 'white'

        self.canvas = tk.Canvas(self, background=self.theme.background_color, bd=0, height=600, width=950,
                                highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=False)

        # folder = os.path.join(bin.application_root_folder(), 'items')
        #bin.mkdir(folder)
        # Create an items object.
        #self.items = taskmanager.Items(folder=folder)

        # Create a task manager.
        #self.tm = taskmanager.TaskManager(root=self, canvas=self.canvas, items=self.items, theme=self.theme)
        self.tm = taskmanager.TaskManager(root=self, canvas=self.canvas, theme=self.theme)



        #        folder=os.path.join(bin.application_root_folder(), 'items2')
        #        bin.mkdir(folder)
        #        self.items2=taskmanager.Items(folder=folder)

        #self.sb=statusbox.StatusBox(root=self, canvas=self.canvas, theme=self.theme)
        #self.sb2=statusbox.StatusBox(root=self, canvas=self.canvas, theme=self.theme)
        #self.tm.add_statusbox(self.sb)
        #self.tm.add_timeline(name='hourly', type='hourly', y=0, height=100, statusbox=self.sb, draw_labels=True, group=0)
        #self.tm.add_timeline(name='daily', type='daily', y=101, height=85, statusbox=self.sb, draw_labels=False, group=0)
        #self.tm.add_timeline(name='monthly', type='monthly', y=101+85+1, height=75, statusbox=self.sb, draw_labels=False, group=0)
        #self.tm.add_timeline(name='monthly2', type='monthly2', y=101+85+1+75+1, height=100, statusbox=self.sb, draw_labels=True, group=1)

        #self.tm.add_statusbox(self.sb2)
        self.tm.draw(x=0, y=0)

        # self.timeline.dump(file_name='C:\\temp\\dump.txt')

        self.bind('<Configure>', self.configure_event)

        self.tm.init()

    def set_window_title(self, title):
        self.wm_title(title)

    def cbfunc(self, dict):
        debug('cbfunc: {}'.format(dict))

    def configure_event(self, event):
        self.canvas.configure(height=event.height, width=event.width)
        debug('configure_event: h={0} w={1}'.format(event.height, event.width))
        self.tm.draw()

    def update_background_tasks(self):
        debug('App.update_background_tasks')
        self.tm.update_background_tasks()
        self.after(10000, self.update_background_tasks)


def RunApp():
    app = App()
    app.after(10000, app.update_background_tasks)
    app.mainloop()


def RunAppReset():
    shutil.rmtree(os.path.join(bin.application_root_folder(), 'taskrx'))
    for f in bin.find(root=bin.application_root_path(), type='f', name='taskrx*'):
        debug('Found {}'.format(f))
        os.remove(f)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    # cProfile.run('RunApp()', filename='C:\\task_manager_app\\foo.dat')
    #RunAppReset()
    RunApp()

    #app = App()
    #app.after(10000, app.update_background_tasks)
    #app.mainloop()