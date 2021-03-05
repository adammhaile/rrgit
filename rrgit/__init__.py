import argparse
import os
import yaml
from urllib.parse import urlparse
import ipaddress
import logging
from . commands import CommandMap
from . util import rrgit_error
from . log import error, warn, info
from . version import VERSION
import pathspec

logging.basicConfig(level=logging.INFO, format='%(message)s')

DEFAULT_IGNORE = [
    '/www/',
    '/gcodes/',
    '/scans/',
    '/menu/',
    '*.uf2',
    '*.bin',
]

class Config():
    def __init__(self, directory, no_warn = False):
        self.no_warn = no_warn
        self.dir = os.path.abspath(directory)
        self.config_path = os.path.join(self.dir, '.rrgit')
        self.ignore_path = os.path.join(self.dir, '.rrgitignore')
        if(not no_warn and not os.path.isfile(self.config_path)):
            raise rrgit_error(f'{self.dir} is not an rrgit directory!')
        self.cfg = {}
        self.valid = False
        self.hostname = None
        self.ignore = DEFAULT_IGNORE
        
        self.read()
        
        # pathspec is fliped, so apply flip to make it actually ignore
        flip_ignore = ['**', '!.rrgit', '!.rrgitignore']
        for i in range(len(self.ignore)):
            flip_ignore.append('!' + self.ignore[i])
        self.ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', flip_ignore)
        
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
            if not self.no_warn:
                error(str(e))
            self.valid = False
            return
            
        
        self.hostname = self.cfg.get('hostname', None)
        
        
        try:
            with open(self.ignore_path, 'r') as f:
                self.ignore = []
                for l in f.readlines:
                    l = l.rstrip()
                    if l:
                        self.ignore.append(l)
        except Exception as e:
            self.ignore = DEFAULT_IGNORE
        
        self.valid = True
        
    def write(self):
        self.cfg['hostname'] = self.hostname        
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.cfg, f, default_flow_style=False, indent=2)
            
        with open(self.ignore_path, 'w') as f:
            for i in self.ignore:
                f.write(i + '\n')
            
def parse_args():
    p = argparse.ArgumentParser(
        description='rrgit: RepRapFirmware/Duet config sync tool'
    )
    sp = p.add_subparsers(help='commands', dest='command')
    
    vp = sp.add_parser('version', help='Show rrgit version info')
    
    for cmd in CommandMap.values():
        cmd.add_parser(sp)
    
    return p, p.parse_args()
    
def main():
    try:
        parser, args = parse_args()
        if args.command == 'version':
            info(f'rrgit version {VERSION}')
            exit()
        elif args.command == 'clone':
            args.directory = os.path.abspath(args.directory)
            cwd = args.directory
            no_warn = True
        else:
            cwd = os.getcwd()
            no_warn = False
            
        if args.command is None:
            parser.print_help()
            exit()
            
        cfg = Config(cwd, no_warn)
    
        cmd = None
        if args.command in CommandMap:
            cmd = CommandMap[args.command](cfg, args)

        if cmd is not None:
            cmd.run()
            cmd.finalize()
        else:
            parser.print_help()
        
    except rrgit_error as e:
        error(e)
    except KeyboardInterrupt:
        error('\nInterrupt detected. Closing rrgit...')
        pass
