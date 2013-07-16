__author__ = 'Ethan_Post'

import os
import sys
import shutil
import string
import random
import shelve
import copy
from debug import *
from datetime import *
import subprocess
from PIL import ImageTk, Image, ImageOps

def seconds_between_two_dates (t1, t2):
    """
    Return the number of seconds between two dates.
    """
    r=(t1-t2)
    r=r.days*86400+r.seconds
    debug3('bin.seconds_between_two_dates: r={}'.format(r))
    return r

def minutes_between_two_dates (t1, t2):
    """
    Return the number of minutes between two dates.
    """
    r=seconds_between_two_dates(t1, t2)/60
    debug3('bin.minutes_between_two_dates: r={}'.format(r))
    return r

def days_between_two_dates (t1, t2):
    """
    Return the number of days between two dates.
    """
    r=minutes_between_two_dates (t1, t2)/60/24
    debug3('bin.days_between_two_dates: r={}'.format(r))
    return r

# ToDo: Add caching here and need a way to check modified time on file in event cache is invalidated.
def get_photoimage_thumbnail(file_path, size=40, border_color='black', border_size=1):
    """
    Takes a file, turns it into a thumbnail, and returns a photoimage object.
    """
    thumbnail=Image.open(file_path).convert("RGB")
    thumbnail=ImageOps.expand(thumbnail,border=border_size,fill=border_color)
    thumbnail.thumbnail((size, size), Image.ANTIALIAS)
    thumbnail=ImageTk.PhotoImage(thumbnail)
    return thumbnail

def nvl(var, value_if_none):
    if var is None:
        return value_if_none
    else:
        return var
    
class reverse_logger():
    def __init__(self, *args, **kwargs):
        self._filepath=kwargs['filepath']
        self._f=None
        self._buffer=[]
        if not os.path.exists(
            self._filepath):
            open(self._filepath, 'w').close()

    def write(self, text):
        if not self._f:
            self._f=open('{}~'.format(self._filepath), 'w')
        self._buffer.append(text)

    def close(self):
        self._f.writelines(self._buffer)
        self._buffer=[]
        for l in open(self._filepath, 'r'):
            self._f.write(l)
        self._f.close()
        self._f=None
        os.remove(self._filepath)
        os.rename('{}~'.format(self._filepath), self._filepath)

def open_file_using_default_program(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

def sublime (file):
    program_path="C:\\Program Files\\Sublime Text 2\\sublime_text.exe"
    debug('file={0} program_path={1}'.format(file, program_path))
    #process = subprocess.Popen([program_path, file], stdout=subprocess.PIPE)
    os.startfile(file)

def run_program (program_path=None, file_path=None):
    process = subprocess.Popen([program_path, file_path], shell=True)

def to_char (t=datetime.now(), f='%H:%M'):
    """Return a string from a date using the format specified."""
    #f='%c'
    #f='%a %b %d %I:%M %p'
    return datetime.strftime(t, f)

def mkdir(directory):
    if not os.path.exists(directory):
        debug('mkdir: {}'.format(directory))
        os.makedirs(directory)

def rmdir(directory):
    shutil.rmtree(directory)

def application_root_folder():
    return os.path.dirname(os.path.realpath(__file__))

def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def open_database(name):
    debug('open_database: {}'.format(name))
    file_path=os.path.join(application_root_folder(), 'app.db')
    d=shelve.open(file_path, writeback=True)
    if name in d.keys():
        r=d[name]
    else:
        r={}
    d.close()
    debug('open_database: r={}'.format(r))
    return r

def save_database(name, dict):
    debug('save_database: {}'.format(dict))
    #c={}
    #for key, value in dict.items():
        #debug('key={}'.format(key))
        #c[key]=value
    file_path=os.path.join(application_root_folder(), 'app.db')
    d=shelve.open(file_path, writeback=True)
    #d[name]=c
    d[name]=dict
    d.close()