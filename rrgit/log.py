from colorama import init, Fore, Back, Style

init()

def log(msg):
    print(msg)

def error(msg):
    print(f'{Fore.RED}{msg}{Style.RESET_ALL}')
    
def warn(msg):
    print(f'{Fore.YELLOW}{msg}{Style.RESET_ALL}')
    
def green(msg):
    print(f'{Fore.GREEN}{msg}{Style.RESET_ALL}')