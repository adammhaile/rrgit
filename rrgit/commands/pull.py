from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

import os
from datetime import datetime
import glob

class Pull(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('pull', 
            help='Pull changes from RRF/Duet device')
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.local_map = {}
        self.connect()
        
    def run(self):
        build_status_report(self.dwa, self.cfg, self.directories)
        return
        remote_files = build_remote_file_map(self.dwa, self.cfg, self.directories)
        local_files = build_local_file_map(self.cfg)
        
        paths = list(remote_files.keys())
        paths.sort()
        for path in paths:
            warn(f'{path} -> {remote_files[path]}')
            
        # local_map = build_local_file_map(self.cfg)
        # for k, v in local_map.items():
        #     warn(f'{k} -> {v}')
            
        # def get_dir(path):
        #     dirpath = os.path.join(self.cfg.dir, path)
        #     os.makedirs(dirpath, exist_ok=True)
        #     items = self.dwa.get_directory(path)
        #     for i in items:
        #         if i['type'] == 'd':
        #             logging.info(i['name'])
        #             get_dir(path + '/' + i['name'])
        #         elif i['type'] == 'f':
        #             name = i['name']
        #             info(f'{path}/{name}')
        #             data = None
        #             try:
        #                 fi = self.dwa.get_fileinfo(name, path)
        #                 fsize = fi['size']
        #                 lastmod = fi['lastModified']
        #                 lm = datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S')
        #                 print(lm)
        #                 print(f'Size: {fsize} bytes, Last Mod: {lastmod}')
        #             except ValueError as e:
        #                 raise e
        #                 error(f'Error: Could not retrieve info for {path}/{name}')
                            
        # for d in self.directories:
        #     if d == 'www':
        #         continue
        #     info(d)
        #     get_dir(d)
    
    def finalize(self):
        pass
        # self.cfg.write()
        