from . log import *

class rrgit_error(Exception):
    pass

TIMESTAMP_FMT = '%Y-%m-%dT%H:%M:%S'

# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def data_size(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            if unit == '':
                return f'{num} {unit}{suffix}'
            else:
                return f'{num:.1f} {unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f} Yi{suffix}'
    
def yes_or_no(question):
    msg = question+' [y|n]: '
    msg = color_string(msg, 'yellow')
    reply = str(input(msg)).lower().strip()
    if len(reply) and reply[0] == 'y':
        return True
    else:
        return False