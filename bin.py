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


# LISTS
# -------------------------------------------------------------------------------------------------
def sort_lists_in_list(data, column_number=0):
    """
    Take a list of lists and sort the outer list using one of the columns in the inner lists.

    Should also work with tuples.

    http://stackoverflow.com/questions/3121979/how-to-sort-list-tuple-of-lists-tuples
    """
    r = sorted(data, key=lambda func: func[column_number])
    return r


def get_list_of_deltas_from_list(data, order='a-b'):
    deltas = []
    l = len(data)
    if l > 1:
        for i in range(1, l):
            if order == 'a-b':
                deltas.append(data[i - 1] - data[i])
            else:
                deltas.append(data[i] - data[i - 1])
    return deltas


def get_number_of_days_in_month_from_datetime(datetime):
    return monthrange(datetime.year, datetime.month)[1]


def touch(file_path):
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
    # debug('root={0} type={1} name={2}'.format(root, type, name))
    pattern = re.compile(name)
    for root_dir, dirs, files in os.walk(root):
        # debug('zzz: {}'.format(files))
        if type == 'f' or type is None:
            for file in files:
                if re.match(pattern, file):
                    yield os.path.join(root_dir, file)

        if type == 'd' or type is None:
            basename = os.path.basename(root_dir)
            if re.match(pattern, basename):
                yield root_dir


def seconds_between_two_dates(t1, t2):
    """
    Return the number of seconds between two dates.
    """
    r = (t1 - t2)
    r = r.days * 86400 + r.seconds
    debug2('bin.seconds_between_two_dates: r={}'.format(r))
    return r


def minutes_between_two_dates(t1, t2):
    """
    Return the number of minutes between two dates.
    """
    r = seconds_between_two_dates(t1, t2) / 60
    debug2('bin.minutes_between_two_dates: r={}'.format(r))
    return r


def days_between_two_dates(t1, t2):
    """
    Return the number of days between two dates.
    """
    r = minutes_between_two_dates(t1, t2) / 60 / 24
    debug2('bin.days_between_two_dates: r={}'.format(r))
    return r


def add_backslash_to_backslash(string):
    r = string.replace('\\', '\\\\')
    debug2('bin.add_backslash_to_backslash: {0} {1}'.format(string, r))
    return r


# ToDo: Add caching here and need a way to check modified time on file in event cache is invalidated.
def get_photoimage_thumbnail(file_path, size=40, border_color='black', border_size=1):
    """
    Takes a file, turns it into a thumbnail, and returns a photoimage object.
    """
    thumbnail = Image.open(file_path).convert("RGB")
    thumbnail = ImageOps.expand(thumbnail, border=border_size, fill=border_color)
    thumbnail.thumbnail((size, size), Image.ANTIALIAS)
    thumbnail = ImageTk.PhotoImage(thumbnail)
    return thumbnail


def nvl(var, value_if_none, value_if_not_none=None):
    if var is None:
        return value_if_none
    elif value_if_not_none is not None:
        return value_if_not_none
    else:
        return var


def write(file_name, text):
    t = []
    if type(text) != list:
        t.append(text)
    else:
        t = text
    f = open(file_name, 'a')
    for l in t:
        f.write(l + '\n')
    f.close()


class reverse_logger():
    def __init__(self, file_path):
        self._filepath = file_path
        self._f = None
        self._buffer = []
        if not os.path.exists(self._filepath):
            # Just create the missing file.
            open(self._filepath, 'w').close()

    def write(self, text):
        if not self._f:
            self._f = open('{}~'.format(self._filepath), 'w')
        self._buffer.append(text)

    def close(self):
        self._f.writelines(self._buffer)
        self._buffer = []
        for l in open(self._filepath, 'r'):
            self._f.write(l)
        self._f.close()
        self._f = None
        os.remove(self._filepath)
        os.rename('{}~'.format(self._filepath), self._filepath)


def open_file_using_default_program(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))


def sublime(file):
    program_path = "C:\\Program Files\\Sublime Text 2\\sublime_text.exe"
    debug2('file={0} program_path={1}'.format(file, program_path))
    # process = subprocess.Popen([program_path, file], stdout=subprocess.PIPE)
    os.startfile(file)


def run_program(program_path=None, file_path=None):
    process = subprocess.Popen([program_path, file_path], shell=True)


def get_valid_path_name_from_string(string):
    if string is None:
        string = 'zzz'
    debug2('bin.get_valid_folder_name_from_string: string={}'.format(string))
    string = re.sub(r"[\/\\\:\*\?\"\<\>\|\.]", "", string)
    # Replace spaces with underscores.
    return string.strip().replace(' ', '_')


def to_char(t=datetime.datetime.now(), f='%H:%M'):
    """Return a string from a date using the format specified."""
    # f='%c'
    # f='%a %b %d %I:%M %p'
    return datetime.datetime.strftime(t, f)


def date_to_string(date=datetime.datetime.now(), format='YYYY_MM_DD_HH24_MI_SS'):
    """
    Return a string from a date using the format specified.
    """
    format = re.sub('YYYY', '%Y', format)
    format = re.sub('MM', '%m', format)
    format = re.sub('MON', '%b', format)
    format = re.sub('MONTH', '%B', format)
    format = re.sub('DD', '%d', format)
    format = re.sub('HH24', '%H', format)
    format = re.sub('MI', '%M', format)
    format = re.sub('SS', '%S', format)
    return datetime.datetime.strftime(date, format)


def mv(source_path, target_path):
    debug('mv: {0} {1}'.format(source_path, target_path))
    shutil.move(source_path, target_path)


def mkdir(directory):
    if not os.path.exists(directory):
        debug2('mkdir: {}'.format(directory))
        os.makedirs(directory)


def rmdir(directory):
    shutil.rmtree(directory)


def application_root_path():
    return os.path.dirname(os.path.realpath(__file__))

def application_root_folder():
    return os.path.dirname(os.path.realpath(__file__))

def application_root_dir():
    return os.path.dirname(os.path.realpath(__file__))

def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))


def random_integer(start, end):
    return random.randint(start, end)


def open_database(
        name,
        folder_path=application_root_folder(),
        file_name='app.db'):
    debug2('open_database: {0} {1} {2}'.format(name, folder_path, file_name))
    file_path = os.path.join(folder_path, file_name)
    debug2('file_path={}'.format(file_path))
    d = shelve.open(file_path, writeback=True)
    if name in d.keys():
        r = d[name]
    else:
        r = {}
    d.close()
    debug2('open_database: r={}'.format(r))
    return r


def if_database(file_path):
    if os.path.isfile('{}.dat'.format(file_path)):
        return True
    else:
        return False


def save_database(
        name,
        dict,
        folder_path=application_root_folder(),
        file_name='app.db'):
    debug2('save_database: {}'.format(dict))
    file_path = os.path.join(folder_path, file_name)
    d = shelve.open(file_path, writeback=True)
    d[name] = dict
    d.close()


def open_database2(file_path):
    """
    Returns a saved object using file_path.
    """
    d = shelve.open(file_path, writeback=True)
    if d:
        return d['0']
    else:
        return None


def save_database2(file_path, object):
    """
    Saves an object to file_path.
    """
    # debug('object: {}'.format(object))
    d = shelve.open(file_path, writeback=True)
    d['0'] = object
    d.close()


def open_list(list_name, directory=None):
    """
    Returns a list object using file_path.
    """
    if not directory:
        file_name = os.path.join(application_root_folder(), list_name)
    else:
        file_name = os.path.join(directory, list_name)
    d = shelve.open(file_name, writeback=True)
    if d:
        return d[list_name]
    else:
        return []


def save_list(list_name, list_object, directory=None):
    """
    Saves an list object to file_path.
    """
    if not directory:
        file_name = os.path.join(application_root_folder(), list_name)
    else:
        file_name = os.path.join(directory, list_name)
    d = shelve.open(file_name, writeback=True)
    d[list_name] = list_object
    d.close()


def open_dict(dict_name, directory=None):
    """
    Returns a dict object using file_path.
    """
    r = None
    if not directory:
        file_name = os.path.join(application_root_folder(), dict_name)
    else:
        file_name = os.path.join(directory, dict_name)
    d = shelve.open(file_name, writeback=True)
    if d:
        r = d[dict_name]
        d.close()
        return r
    else:
        d.close()
        return {}


def save_dict(dict_name, dict_object, directory=None):
    """
    Saves an dict object to file_path.
    """
    debug('Saving dict {} to {}'.format(dict_object, directory))
    if not directory:
        file_name = os.path.join(application_root_folder(), dict_name)
    else:
        file_name = os.path.join(directory, dict_name)
    d = shelve.open(file_name, writeback=True)
    d[dict_name] = dict_object
    d.close()


def canvas_get_closest_object_id_withtag(*, canvas, x, y, tag):
    object_id = canvas.find_closest(x, y, start=None)[0]
    if tag in canvas.gettags(object_id):
        return object_id
    else:
        return None