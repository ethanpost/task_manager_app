__author__ = 'Ethan_Post'

import os
import re
import sys
import shutil
import string
import random
import shelve
import copy
from debug import *
import datetime
import subprocess
from PIL import ImageTk, Image, ImageOps
from calendar import monthrange

def sort_lists_in_list(data, column_number=0):
    """
    Take a list of lists and sort the outer list using one of the columns in the inner lists.

    Should also work with tuples.

    http://stackoverflow.com/questions/3121979/how-to-sort-list-tuple-of-lists-tuples
    """
    r = sorted(data, key=lambda func : func[column_number])
    return r
    
def get_number_of_days_in_month_from_datetime(datetime):
    return monthrange(datetime.year, datetime.month)[1]
    
def touch (file_path):
    if not os.path.isfile(file_path):
        open(file_path, 'w').close()
    
def remove_duplicates_from_list(seq):
    # http://www.peterbe.com/plog/uniqifiers-benchmark
    # Order preserving
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]
   
def find(root, type=None, name='.*'):
    """
    Works like unix find command (this is a generator).

    root is the root directory to start the search from.
    type 'd' for directory or 'f' for file, None will match the pattern against the full path to anything found.
    name Is a regular expression to match to.
    """
    #debug('root={0} type={1} name={2}'.format(root, type, name))
    pattern=re.compile(name)
    for root_dir, dirs, files in os.walk(root):
        # debug('zzz: {}'.format(files))
        if type=='f' or type is None:
            for file in files:
                if re.match(pattern, file):
                    yield os.path.join(root_dir, file)

        if type=='d' or type is None:
            basename=os.path.basename(root_dir)
            if re.match(pattern, basename):
                yield root_dir

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

def add_backslash_to_backslash(string):
    r=string.replace('\\', '\\\\')
    debug('bin.add_backslash_to_backslash: {0} {1}'.format(string, r))
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

def write(file_name, text):
    t=[]
    if type(text) != list:
        t.append(text)
    else:
        t=text
    f=open(file_name, 'a')
    for l in t:
        f.write(l+'\n')
    f.close()

class reverse_logger():
    def __init__(self, file_path):
        self._filepath=file_path
        self._f=None
        self._buffer=[]
        if not os.path.exists(self._filepath):
            # Just create the missing file.
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

def get_valid_path_name_from_string(string):
    debug('bin.get_valid_folder_name_from_string: string={}'.format(string))
    string=re.sub(r"[\/\\\:\*\?\"\<\>\|\.]", "", string)
    # Replace spaces with underscores.
    return string.strip().replace(' ', '_')

def to_char (t=datetime.datetime.now(), f='%H:%M'):
    """Return a string from a date using the format specified."""
    #f='%c'
    #f='%a %b %d %I:%M %p'
    return datetime.datetime.strftime(t, f)

def date_to_string (date=datetime.datetime.now(), format='YYYY_MM_DD_HH24_MI_SS'):
    """
    Return a string from a date using the format specified.
    """
    format=re.sub('YYYY', '%Y', format)
    format=re.sub('MM', '%m', format)
    format=re.sub('MON', '%b', format)
    format=re.sub('MONTH', '%B', format)
    format=re.sub('DD', '%d', format)
    format=re.sub('HH24', '%H', format)
    format=re.sub('MI', '%M', format)
    format=re.sub('SS', '%S', format)
    return datetime.datetime.strftime(date, format)

def mv (source_path, target_path):
    debug('mv: {0} {1}'.format(source_path, target_path))
    shutil.move(source_path, target_path)
    
def mkdir(directory):
    if not os.path.exists(directory):
        debug('mkdir: {}'.format(directory))
        os.makedirs(directory)

def rmdir(directory):
    shutil.rmtree(directory)

def application_root_path():
    return os.path.dirname(os.path.realpath(__file__))

def application_root_folder():
    return os.path.dirname(os.path.realpath(__file__))

def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def open_database(
    name,
    folder_path=application_root_folder(),
    file_name='app.db'):
    debug('open_database: {0} {1} {2}'.format(name, folder_path, file_name))
    file_path=os.path.join(folder_path, file_name)
    debug('file_path={}'.format(file_path))
    d=shelve.open(file_path, writeback=True)
    if name in d.keys():
        r=d[name]
    else:
        r={}
    d.close()
    debug('open_database: r={}'.format(r))
    return r

def save_database(
    name,
    dict,
    folder_path=application_root_folder(),
    file_name='app.db'):
    debug('save_database: {}'.format(dict))
    file_path=os.path.join(folder_path, file_name)
    d=shelve.open(file_path, writeback=True)
    d[name]=dict
    d.close()

def open_database2(file_path):
    #debug('bin.open_database2: {0}'.format(file_path))
    d=shelve.open(file_path, writeback=True)
    #debug('bin.open_database2: {0}'.format(d))
    return d['0']

def save_database2(file_path, object):
    #debug('save_database2: {0} {1}'.format(file_path, object))
    d=shelve.open(file_path, writeback=True)
    #debug('save_database2: {}'.format(d))
    d['0']=object
    d.close()