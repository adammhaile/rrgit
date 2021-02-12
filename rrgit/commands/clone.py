from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *

import os
from datetime import datetime

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
        
        if os.path.exists(self.args.directory) and len(os.listdir(self.args.directory)) > 0:
            raise rrgit_error(f"fatal: destination path '{self.args.directory}' already exists and is not an empty directory.")
            
        self.connect()
        
    def run(self):
        def get_dir(path, indent):
            dirpath = os.path.join(self.cfg.dir, path)
            os.makedirs(dirpath, exist_ok=True)
            items = self.dwa.get_directory(path)
            num_items = len(items)
            for n in range(num_items):
                i = items[n]
                if n == (num_items - 1):
                    tree_char = '└─'
                    new_indent = indent + '  '
                else:
                    tree_char = '├─'
                    new_indent = indent + '│ '
                
                if i['type'] == 'd':
                    dir_path = path + '/' + i['name']
                    match_path = dir_path + '/'
                    if self.cfg.ignore_spec.match_file(match_path):
                        info(f"{indent}{tree_char}┐{i['name']}")
                        get_dir(dir_path, new_indent)
                elif i['type'] == 'f':
                    name = i['name']
                    if not self.cfg.ignore_spec.match_file(path + '/' + name):
                        continue
                    fi = self.dwa.get_fileinfo(name, path)
                    fsize = color_string('(' + data_size(fi['size']) + ')', 'cyan')
                    info(f'{indent}{tree_char} {name} {fsize}')
                    data = None
                    try:
                        data = self.dwa.get_file(name, path, True)
                    except ValueError as e:
                        warn(f'Error: Could not retrieve {path}/{name}')
                    
                    if data is not None:
                        lastmod = fi['lastModified']
                        lm = datetime.strptime(lastmod, TIMESTAMP_FMT)
                        lm = datetime.timestamp(lm)
                        now = datetime.timestamp(datetime.now())
                        outpath = os.path.join(dirpath, name)
                        with open(outpath, 'wb') as of:
                            of.write(data)
                            
                        os.utime(outpath, (now, lm))
        
        info(f'Cloning from {self.cfg.hostname} ...')
        os.makedirs(self.cfg.dir, exist_ok=True)
        for d in self.directories:
            if self.cfg.ignore_spec.match_file(d + '/'):
                info(f'{d}')
                get_dir(d, '  ')
    
    def finalize(self):
        self.cfg.write()
        