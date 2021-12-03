from os import system,name
from datetime import datetime
from colorama import Fore,Style
from __main__ import checker,lock
from random import choice
from tkinter import Tk,filedialog
from base64 import b64decode
from zlib import decompress
from tempfile import mkstemp
from time import sleep
from console.utils import set_title
from os import makedirs
from win32gui import GetWindowText, GetForegroundWindow

yellow = Fore.YELLOW
green = Fore.GREEN
reset = Fore.RESET
cyan = Fore.CYAN
red = Fore.RED
dark_yellow = Fore.YELLOW+Style.DIM
dark_cyan = Fore.CYAN+Style.DIM
bright = Style.BRIGHT

ICON = decompress(b64decode('eJxjYGAEQgEBBiDJwZDBy''sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
_, ICON_PATH = mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)

def reset_stats():
    checker.bad = 0
    checker.cpm = 0
    checker.good = 0
    checker.custom = 0
    checker.errors = 0
    checker.proxies.clear()
    checker.accounts.clear()
    checker.accounts_down.clear()
    checker.bad_proxies.clear()

def clear():
    """Clears the console"""
    system('cls' if name=='nt' else 'clear')

def ascii():
    """Prints the ascii logo"""
    print(cyan+r"            ______   ________   __       ________   ___   __     ________      ________    ________  ______      ")
    print(cyan+r"           /_____/\ /_______/\ /_/\     /_______/\ /__/\ /__/\  /_______/\    /_______/\  /_______/\/_____/\     ")
    print(cyan+r"           \:::__\/ \::: _  \ \\:\ \    \::: _  \ \\::\_\\  \ \ \__.::._\/    \::: _  \ \ \__.::._\/\:::_ \ \    ")
    print(cyan+r"            \:\ \  __\::(_)  \ \\:\ \    \::(_)  \ \\:. `-\  \ \   \::\ \      \::(_)  \ \   \::\ \  \:\ \ \ \   ")
    print(cyan+r"             \:\ \/_/\\:: __  \ \\:\ \____\:: __  \ \\:. _    \ \  _\::\ \__    \:: __  \ \  _\::\ \__\:\ \ \ \  ")
    print(cyan+r"              \:\_\ \ \\:.\ \  \ \\:\/___/\\:.\ \  \ \\. \`-\  \ \/__\::\__/\    \:.\ \  \ \/__\::\__/\\:\_\ \ \ ")
    print(cyan+r"               \_____\/ \__\/\__\/ \_____\/ \__\/\__\/ \__\/ \__\/\________\/     \__\/\__\/\________\/ \_____\/ ")

def get_time():
    """
    Gets the time and date in the format:
    Year-Month-Day Hour-Minute-Second
    """
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def save(name:str,type:str,time:str,content:str):
    """
    Saves the given account to a file
    save(
        name="NordVPN",
        type="good",
        time="2021-11-02 22-01-02",
        content="example@example.com:example123@"
    )
    """
    makedirs(f"Results/{time}",exist_ok=True)
    with lock:
        if type == "custom":
            with open(f"Results/{time}/{name}_custom.txt","a",errors="ignore") as file: file.write(content+"\n")
        elif type == "good":
            with open(f"Results/{time}/{name}_good.txt","a",errors="ignore") as file: file.write(content+"\n")
        else:
            with open(f"Results/{time}/{name}.txt","a",errors="ignore") as file: file.write(content+"\n")

def log(type:str,account:str,service:str=None):
    """
    Prints to the console
    log(
        type="good",
        account="example@gmail.com:example123@,
        service="NordVPN"
    )
    """
    with lock:
        if type == "custom":
            print(f"    [{yellow}Custom{reset}] {account} ~ {service}")
        if type == "good":
            print(f"    [{green}Good{reset}] {account} ~ {service}")
        if type == "bad":
            print(f"    [{red}Bad{reset}] {account} ~ {service}")
        else:
            print(f"    {cyan}{account}")

def set_proxy(proxy:str=False):
    """
    Returns a proxy to use in requests
    Set a proxy to get a dictionary response

    set_proxy(proxy="0.0.0.0")
    """
    if proxy:
        if ":" in proxy:
            spl = proxy.split(":")
            if len(spl) == 4:
                proxy = spl[2]+":"+spl[3]+"@"+spl[0]+":"+spl[1]

        if checker.proxy_type == "http": return {"http":f"http://{proxy}","https":f"https://{proxy}"}
        elif checker.proxy_type == "socks4": return {"http":f"socks4://{proxy}","https":f"socks4://{proxy}"}
        elif checker.proxy_type == "socks5": return {"http":f"socks5://{proxy}","https":f"socks5://{proxy}"}

    else:
        while 1:
            if len(checker.bad_proxies) == len(checker.proxies):
                checker.bad_proxies.clear()
            proxy = choice(checker.proxies)
            if proxy not in checker.bad_proxies:
                return proxy

def bad_proxy(proxy):
    if proxy not in checker.bad_proxies:
        checker.bad_proxies.append(proxy)

def get_file(title:str,type:str):
    """
    Gets a filepath
    Returns False if nothing was given
    get_file(title="Combo File",type="Combo File")
    """
    root = Tk()
    root.withdraw()
    try: root.iconbitmap(default=ICON_PATH)
    except: pass
    root.withdraw
    response = filedialog.askopenfilename(title=title,filetypes=((type, '.txt'),))
    return response if response not in ("",()) else False

def cui(modules:int):
    """Prints the cui"""

    while checker.checking:
        clear()
        ascii()
        print("\n\n")
        percent = round(((checker.good+checker.bad+checker.custom)/(len(checker.accounts)*modules))*100,2) if checker.good+checker.bad+checker.custom > 0 else 0.0
        print(f"""
    [{dark_cyan}Loaded Modules{reset}] {modules}

    [{green}Hits{reset}] {checker.good}
    [{yellow}Custom{reset}] {checker.custom}
    [{red}Bad{reset}] {checker.bad}

    [{dark_yellow}Errors{bright}{reset}] {checker.errors}
    [{dark_cyan}CPM{bright}{reset}] {checker.cpm}
    [{cyan}{bright}Progress{dark_cyan}{reset}] {checker.good+checker.bad+checker.custom}/{len(checker.accounts)*modules} = {percent}%
    
    [{cyan}S{reset}] Save Remaining Lines""")
        sleep(1)

def cui_2():
    """Prints the proxy checker cui"""
    while checker.checking:
        clear()
        ascii()
        print("\n\n")
        percent = round( ( (checker.good+checker.bad)/(len(checker.accounts)) )*100,2) if checker.good + checker.bad > 0 else 0.0
        print(f"""
    [{dark_cyan}Proxy Type{reset}] {checker.proxy_type.title()}

    [{green}Good{reset}] {checker.good}
    [{red}Bad{reset}] {checker.bad}

    [{dark_cyan}CPM{bright}{reset}] {checker.cpm}
    [{cyan}{bright}Progress{dark_cyan}{reset}] {checker.good+checker.bad}/{len(checker.accounts)} = {percent}%""")
        sleep(1)

def title(modules:int):
    """Sets the title while checking"""
    while checker.checking:
        try:
            checker.title = f"Calani AIO | Good: {checker.good}  ~  Custom: {checker.custom}  ~  Bad: {checker.bad}  ~  Errors: {checker.errors}  ~  CPM: {checker.cpm}  ~  Progress: {checker.good+checker.bad+checker.custom}/{len(checker.accounts)*modules} = {round(((checker.good+checker.bad+checker.custom)/(len(checker.accounts)*modules))*100,2)}%"
            set_title(checker.title)
            sleep(1)
        except:
            pass
def title_2():
    """Sets the title while checking for the proxy checker"""
    while checker.checking:
        try:
            checker.title = f"Calani AIO | Good: {checker.good} ~ Bad: {checker.bad} ~ CPM: {checker.cpm} ~ Progress: {checker.good+checker.bad}/{len(checker.accounts)} = { round( ( ( checker.good+checker.bad) / len(checker.accounts ) ) * 100 , 2 ) } %"
            set_title(checker.title)
            sleep(1)
        except:
            pass

def save_lines():
    if checker.checking:
        if "Calani AIO | Good: " in GetWindowText(GetForegroundWindow()):
            if not checker.saving:
                checker.saving = True
                with open(f"Results/{checker.time}/save_lines.txt","w") as file: file.write("\n".join(checker.accounts_down))
                checker.saving = False

def level_cpm():
    """This levels the cpm every 15 seconds"""
    while checker.checking:
        now = checker.cpm
        sleep(15)
        checker.cpm = (checker.cpm - now)*4