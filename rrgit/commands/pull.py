import logging
from . command import Command
from .. util import rrgit_error

import os
from datetime import datetime

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
                        lm = datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S')
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
        