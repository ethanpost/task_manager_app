
import tkinter as tk
from datetime import *
from debug import debug as debug, critical as error
# from debug import dump as dump_debug
import timeline

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.wm_title('task_manager_app')
        self.version=0

        timeline_height=(100,85,70)
        statusbox_height=25
        canvas_height=sum(timeline_height)+statusbox_height

        self.geometry('950x{}+100+100'.format(canvas_height))

        self.canvas=tk.Canvas(self, background="white", bd=0, height=canvas_height, width=950, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=False)

        self.timeline=timeline.Timeline(
            root=self,
            canvas=self.canvas,
            default_item_type='task',
            height=timeline_height
        )

        self.timeline.dump(file_name='C:\\temp\\dump.txt')

        self.bind('<Configure>', self.configure_event)

    def cbfunc(self, dict):
        debug('cbfunc: {}'.format(dict))

    def configure_event(self, event):
        self.timeline.width=event.width
        self.canvas.configure(height=event.height)
        self.timeline._timelines_draw()
        self.timeline.draw_items()

    def update_background_tasks(self):
        debug('App.update_background_tasks')
        self.timeline.update_background_tasks()
        self.after(10000, self.update_background_tasks)

if __name__ == "__main__":
    app = App()
    #app.after(10000, app.update_background_tasks)
    app.mainloop()