from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

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
        status(f'Cloning from {self.cfg.hostname} ...')
        os.makedirs(self.cfg.dir, exist_ok=True)
                
        remote_files = build_remote_file_map(self.dwa, self.cfg, self.directories)
        paths = list(remote_files.keys())
        paths.sort()
        status('Downloading files...')
        for path in paths:
            fo = remote_files[path]
            fsize = color_string('(' + fo.sizestr + ')', 'yellow')
            info(f'{path} {fsize}')
            data = None
            try:
                data = fo.getFileData(self.dwa)
            except ValueError as e:
                warn(f'Error: Could not retrieve {path}')
            
            if data is not None:
                out_dir = os.path.join(self.cfg.dir, fo.dir)
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                outpath = os.path.join(self.cfg.dir, path)
                with open(outpath, 'wb') as of:
                    of.write(data)
                    
                now = datetime.timestamp(datetime.now())
                os.utime(outpath, (now, fo.timestamp))
    
    def finalize(self):
        self.cfg.write()
        