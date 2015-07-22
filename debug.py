__author__ = 'Ethan_Post'

debug_list = None
buffered = False
debug_level = 1
line_number = 0

# ToDo: Implement sanelog here.

def _init():
    global debug_list
    debug_list = list(('',) * 1000)


def critical(text):
    print(text)
    debug(text)


def debug3(text):
    global debug_list
    global debug_level
    if debug_level >= 3:
        if buffered:
            if not debug_list:
                _init()
            del debug_list[0]
            debug_list.append(str(text))
        else:
            print(text)


def debug2(text):
    global debug_list
    global debug_level
    if debug_level >= 2:
        if buffered:
            if not debug_list:
                _init()
            del debug_list[0]
            debug_list.append(str(text))
        else:
            print(text)


def debug(text):
    if text[:3] != '***':
        return
    global debug_list
    global debug_level
    global line_number
    if debug_level >= 1:
        if buffered:
            if not debug_list:
                _init()
            del debug_list[0]
            debug_list.append(str(text))
        else:
            line_number += 1
            print('{}: {}'.format(line_number, text))


def dump():
    global debug_list
    if debug_list:
        for m in debug_list:
            if m:
                print(m)
        debug_list = list(('',) * 1000)
  