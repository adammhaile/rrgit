from colorama import init, Fore, Back, Style

init()

def info(msg):
    print(msg)

def error(msg):
    print(f'{Fore.RED}{msg}{Fore.RESET}')
    
def warn(msg):
    print(f'{Fore.YELLOW}{msg}{Fore.RESET}')
    
def success(msg):
    print(f'{Fore.GREEN}{msg}{Fore.RESET}')
    
print_red = error
print_green = success
print_yellow = warn

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