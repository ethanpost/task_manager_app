
import tkinter as tk
from debug import debug as debug, critical as error
# from debug import dump as dump_debug
import timeline
import theme
import datetime

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_title('task_manager_app')

        self.version=0

        self.canvas=tk.Canvas(self, background="white", bd=0, height=600, width=950, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=False)
        
        self.theme=theme.Theme()
        self.theme.font_name="Courier"

        self.timeline=timeline.Timeline(root=self, canvas=self.canvas, theme=self.theme)

        self.timeline.add(name='hourly', type='hourly', y=0, height=100, total_days=8/24, time=datetime.datetime.now(),
            label_format='%I%p', draw_labels=True)

        self.timeline.add(name='daily', type='daily', y=100, height=85, total_days=7, time=datetime.datetime.now(),
            label_format='%d%a', draw_labels=False)

        self.timeline.add(name='monthly', type='monthly', y=185, height=75, total_days=180, time=datetime.datetime.now(),
            label_format='%B %y', draw_labels=False)

        self.geometry('950x285+100+100')
        
        # self.timeline.dump(file_name='C:\\temp\\dump.txt')

        self.bind('<Configure>', self.configure_event)

        self.timeline.init()

    def cbfunc(self, dict):
        debug('cbfunc: {}'.format(dict))

    def configure_event(self, event):
        self.timeline.width=event.width
        self.canvas.configure(height=event.height)
        self.timeline.draw()
        self.timeline.draw_items()

    def update_background_tasks(self):
        debug('App.update_background_tasks')
        self.timeline.update_background_tasks()
        self.after(10000, self.update_background_tasks)

if __name__ == "__main__":
    app = App()
    #app.after(10000, app.update_background_tasks)
    app.mainloop()