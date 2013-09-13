
from debug import *
from bin import *
import tkinter as tk

class ModalInputBox():
    def __init__(self, *args, **kwargs):
        debug('ModalInputBox: kwargs={}'.format(kwargs))

        self.root=kwargs['root']
        self.canvas=kwargs['canvas']

        if 'cbfunc' in kwargs.keys():
            self.cbfunc=kwargs['cbfunc']
        else:
            self.cbfunc=None

        if 'text' in kwargs.keys():
            self.text=kwargs['text']
        else:
            self.text=None

        if 'font' in kwargs.keys():
            self.font=kwargs['font']
        else:
            self.font=('Arial', 11)

        self.textbox=None
        self._open()

    def _reclaim_focus(self, event):
        debug('ModalInputBox.reclaim_focus')
        self.win.lift()

    def _open(self):
        debug('ModalInputBox.open')
        self.win=tk.Toplevel(self.root, padx=2, pady=2)
        self.win.bind('<Configure>', self._reclaim_focus )
        width=500
        height=30
        left=int((self.canvas.winfo_rootx()+0+(self.canvas.winfo_reqwidth()/2))-(width/2))
        top=int((self.canvas.winfo_rooty()+(0+self.canvas.winfo_reqheight())/2)-(height/2))
        self.win.geometry('{0}x{1}+{2}+{3}'.format(width, height, left, top))
        self.textbox1=tk.Entry(self.win, highlightthickness=1, takefocus=True, font=self.font, relief=tk.FLAT, bd=4,
                              insertwidth=1, insertofftime=500, insertontime=500)
        self.textbox1.pack(fill=tk.X, expand=False)
        self.textbox1.insert(0, self.text)
        self.win.bind("<Return>", self._save)
        self.win.bind("<Escape>", self._cancel)
        # Learned how to create a model window here, http://tkinter.unpythonic.net/wiki/ModalWindow.
        self.textbox1.focus_force()
        self.win.lift()
        self.win.transient(self.root)
        self.win.grab_set()
        # Nothing works without this line!
        self.win.update_idletasks()
        self.win.overrideredirect(1)
        self.root.wait_window(self.win)

    def _open_old(self):
        debug('ModalInputBox.open')
        self.win=tk.Toplevel(self.root, padx=2, pady=2)
        width=500
        height=30
        left=int((self.canvas.winfo_rootx()+0+(self.canvas.winfo_reqwidth()/2))-(width/2))
        top=int((self.canvas.winfo_rooty()+(0+self.canvas.winfo_reqheight())/2)-(height/2))
        self.win.geometry('{0}x{1}+{2}+{3}'.format(width, height, left, top))

#        self.frame1=tk.Frame(self.win, bd=1, relief=tk.FLAT)
#        self.frame1.pack(fill=tk.X, expand=False)
        self.textbox1=tk.Entry(self.win, highlightthickness=1, takefocus=True, font=self.font, relief=tk.FLAT, bd=4,
                              insertwidth=1, insertofftime=500, insertontime=500)
        self.textbox1.pack(fill=tk.X, expand=False)
        self.textbox1.insert(0, self.text)

#        self.frame2=tk.Frame(self.win, bd=1, relief=tk.FLAT)
#        self.frame2.pack(fill=tk.X, expand=False)
#
#        self.label=tk.Label(self.frame2, text='hello world!', anchor=tk.NW, highlightthickness=1, font=self.font,
#                            relief=tk.FLAT, bg='white', bd=4, fg='gray')
#        self.label.pack(fill=tk.BOTH, expand=False)

        #self.textbox.configure(state='readonly')

#        self.textbox2=tk.Entry(self.win, highlightthickness=1, takefocus=True, font=self.font, relief=tk.FLAT,
#                               bd=4, insertwidth=1, insertofftime=500, insertontime=500)
#        self.textbox2.pack(fill=tk.X, expand=False)
#        self.textbox2.insert(0, self.text)
#
#        self.textbox3=tk.Text(self.win, highlightthickness=1, height=300, takefocus=True, font=self.font,
#                              relief=tk.FLAT, bd=4, insertwidth=1, insertofftime=500, insertontime=500,
#                              readonlybackground='light gray')
#        self.textbox3.pack(fill=tk.BOTH, expand=False)
#        self.textbox3.insert(0, self.text)
#        self.textbox3.configure(state='readonly')

        self.win.bind("<Return>", self._save)
        self.win.bind("<Escape>", self._cancel)
        # Learned how to create a model window here, http://tkinter.unpythonic.net/wiki/ModalWindow.
        self.textbox1.focus_force()
        self.win.lift()
        self.win.transient(self.root)
        self.win.grab_set()
        # Nothing works without this line!
        self.win.update_idletasks()
        self.win.overrideredirect(1)
        self.root.wait_window(self.win)

    def _save(self, event):
        debug('ModalInputBox._save')
        self.text=self.textbox1.get()
        self.win.destroy()
        if self.cbfunc:
            self.cbfunc({'text': text})

    def _cancel(self, event):
        debug('ModalInputBox._cancel')
        self.win.destroy()