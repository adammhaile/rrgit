import argparse
import os
import yaml
from duetwebapi import DuetWebAPI as DWA
from urllib.parse import urlparse
import ipaddress
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')

class rrgit_error(Exception):
    pass

class Config():
    def __init__(self, directory):
        self.dir = os.path.abspath(directory)
        self.config_path = os.path.join(self.dir, '.rrgit')
        self.cfg = {}
        
        self.valid = False
        
        self.hostname = None
        
        self.read()
        
    def set_hostname(self, hostname):
        try:
            ip = ipaddress.ip_address(hostname)
            self.hostname = hostname
        except ValueError:
            uri = urlparse(hostname)
            if uri.netloc:
                self.hostname = uri.netloc
            else:
                self.hostname = hostname

    def read(self):
        try:
            with open(self.config_path, 'r') as f:
                self.cfg = yaml.safe_load(f)
                if self.cfg is None:
                    self.cfg = {}
                    self.valid = False
                    return
        except Exception as e:
            logging.debug(str(e))
            self.valid = False
            return
            
        
        self.hostname = self.cfg.get('hostname', None)
        
        self.valid = True
        
    def write(self):
        self.cfg['hostname'] = self.hostname
        
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.cfg, f, default_flow_style=False, indent=2)
            
class Command():
    @staticmethod
    def add_parser(sp):
        pass
        
    def __init__(self, cfg, args):
        self.cfg = cfg
        self.args = args
        self.dwa = None
        self.directories = []
        
        if not self.cfg.valid:
            raise rrgit_error('Error: Invalid config')
        
    def run(self):
        pass
    
    def finalize(self):
        pass
        
    def connect(self):
        if not self.cfg.valid:
            raise rrgit_error('This is not a valid rrgit directory!')
        
        try:
            host_path = f'http://{self.cfg.hostname}'
            self.dwa = DWA(host_path)
            dirs = self.dwa.get_model('directories')
            for d in dirs:
                self.directories.append(dirs[d][3:-1])
            self.directories = list(set(self.directories)) # remove dupes
            logging.info(f'Connected to {self.cfg.hostname}')
        except ValueError as e:
            raise rrgit_error('')
        
class Clone(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('clone', 
            help='Clone RRF/Duet config to local directory')
        p.add_argument('hostname', action='store', 
            help='RRF/Duet hostname or IP')
        p.add_argument('directory', action='store', 
            help='Directory to clone into', 
            nargs='?', 
            default=os.getcwd())
        
    def __init__(self, cfg, args):
        if cfg.hostname is not None:
            raise rrgit_error(f'{cfg.dir} is already an rrgit directory!')
        
        cfg.set_hostname(args.hostname)
        cfg.valid = True
        
        super().__init__(cfg, args)

        self.connect()
        
    def run(self):
        def get_dir(path):
            dirpath = os.path.join(self.cfg.dir, path)
            os.makedirs(dirpath, exist_ok=True)
            items = self.dwa.get_directory(path)
            for i in items:
                if i['type'] == 'd':
                    logging.info(i['name'])
                    get_dir(path + '/' + i['name'])
                elif i['type'] == 'f':
                    name = i['name']
                    logging.info(f'{path}/{name}')
                    data = None
                    try:
                        data = self.dwa.get_file(name, path, True)
                    except ValueError as e:
                        logging.error(f'Error: Could not retrieve {path}/{name}')
                    
                    if data is not None:
                        fi = self.dwa.get_fileinfo(name, path)
                        lastmod = fi['lastModified']
                        lm = datetime.datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S')
                        lm = datetime.datetime.timestamp(lm)
                        now = datetime.datetime.timestamp(datetime.datetime.now())
                        outpath = os.path.join(dirpath, name)
                        with open(outpath, 'wb') as of:
                            of.write(data)
                            
                        os.utime(outpath, (now, lm))
                            
        for d in self.directories:
            if d == 'www':
                continue
            logging.info(d)
            get_dir(d)
    
    def finalize(self):
        self.cfg.write()
        
class Pull(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('pull', 
            help='Pull changes from RRF/Duet device')
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        def get_dir(path):
            dirpath = os.path.join(self.cfg.dir, path)
            os.makedirs(dirpath, exist_ok=True)
            items = self.dwa.get_directory(path)
            for i in items:
                if i['type'] == 'd':
                    logging.info(i['name'])
                    get_dir(path + '/' + i['name'])
                elif i['type'] == 'f':
                    name = i['name']
                    logging.info(f'{path}/{name}')
                    data = None
                    try:
                        fi = self.dwa.get_fileinfo(name, path)
                        fsize = fi['size']
                        lastmod = fi['lastModified']
                        lm = datetime.datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S')
                        print(lm)
                        print(f'Size: {fsize} bytes, Last Mod: {lastmod}')
                    except ValueError as e:
                        raise e
                        logging.error(f'Error: Could not retrieve info for {path}/{name}')
                            
        for d in self.directories:
            if d == 'www':
                continue
            logging.info(d)
            get_dir(d)
    
    def finalize(self):
        self.cfg.write()
        
commands = {
    'clone': Clone,
    'pull': Pull
}

def parse_args():
    p = argparse.ArgumentParser(
        description='rrgit: RepRapFirmware/Duet config sync tool'
    )
    sp = p.add_subparsers(help='commands', dest='command')
    
    for cmd in commands.values():
        cmd.add_parser(sp)
    
    return p.parse_args()
    
def main():
    args = parse_args()
    print(args)
    
    cwd = os.getcwd()
    cfg = Config(cwd)
    
    try:
        cmd = None
        if args.command in commands:
            cmd = commands[args.command](cfg, args)

        if cmd is not None:
            cmd.run()
            cmd.finalize()
        
    except rrgit_error as e:
        print(e)
