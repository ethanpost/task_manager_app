__author__ = 'Ethan_Post'

debug_list=None
buffered=False
debug_level=1

# ToDo: Implement sanelog here.

def _init():
    global debug_list
    debug_list=list(('',)*1000)

def critical(text):
    print(text)
    debug(text)

def debug3(text):
    global debug_list
    global debug_level
    if debug_level>=3:
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
    if debug_level>=2:
        if buffered:
            if not debug_list:
                _init()
            del debug_list[0]
            debug_list.append(str(text))
        else:
            print(text)

def debug(text):
    global debug_list
    global debug_level
    if debug_level>=1:
        if buffered:
            if not debug_list:
                _init()
            del debug_list[0]
            debug_list.append(str(text))
        else:
            print(text)

def dump():
    global debug_list
    if debug_list:
        for m in debug_list:
            if m:
                print(m)
        debug_list=list(('',)*1000)
  