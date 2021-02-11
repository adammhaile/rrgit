from . command import Command, TIMESTAMP_FMT
from .. util import rrgit_error, data_size
from .. log import *

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
        
    def build_local_file_map(self):
        def on_error(e):
            raise(e)
            
        self.local_map = {}
        files = self.cfg.ignore_spec.match_tree(self.cfg.dir, on_error=on_error)
        for f in files:
            full_path = os.path.join(self.cfg.dir, f)
            finfo = os.stat(full_path)
            self.local_map[f] = (finfo.st_size, finfo.st_mtime, datetime.fromtimestamp(finfo.st_mtime).strftime(TIMESTAMP_FMT))

        for k, v in self.local_map.items():
            warn(f'{k} -> {v}')
        
        
    def run(self):
        self.build_local_file_map()
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
        