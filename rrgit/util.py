class rrgit_error(Exception):
    pass

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