from colorama import init, Fore, Back, Style

init()

text_colors = {
    'black': Fore.BLACK,
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
}

def color_string(txt, color):
    c = text_colors.get(color, Fore.WHITE)
    return f'{c}{txt}{Fore.RESET}'
    
def cprint(msg, color):
    print(color_string(msg, color))
    
def nl():
    print()
def info(msg):
    print(msg)

def error(msg):
    print(color_string(msg, 'red'))
    
def warn(msg):
    print(color_string(msg, 'yellow'))
    
def success(msg):
    print(color_string(msg, 'green'))
    
def status(msg):
    print(color_string(msg, 'cyan')) 
