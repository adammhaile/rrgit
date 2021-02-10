from . command import Command
from .. util import rrgit_error
from .. log import error, warn, log

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
        
        if len(os.listdir(self.args.directory)) > 0:
            raise rrgit_error(f"fatal: destination path '{self.args.directory}' already exists and is not an empty directory.")
            
        self.connect()
        
    def run(self):
        def get_dir(path):
            dirpath = os.path.join(self.cfg.dir, path)
            os.makedirs(dirpath, exist_ok=True)
            items = self.dwa.get_directory(path)
            for i in items:
                if i['type'] == 'd':
                    log(i['name'])
                    get_dir(path + '/' + i['name'])
                elif i['type'] == 'f':
                    name = i['name']
                    log(f'{path}/{name}')
                    # print(f'{path}/{name}', end='\r')
                    data = None
                    try:
                        data = self.dwa.get_file(name, path, True)
                    except ValueError as e:
                        warn(f'Error: Could not retrieve {path}/{name}')
                    
                    if data is not None:
                        fi = self.dwa.get_fileinfo(name, path)
                        lastmod = fi['lastModified']
                        lm = datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S')
                        lm = datetime.timestamp(lm)
                        now = datetime.timestamp(datetime.now())
                        outpath = os.path.join(dirpath, name)
                        with open(outpath, 'wb') as of:
                            of.write(data)
                            
                        os.utime(outpath, (now, lm))
                            
        for d in self.directories:
            if d == 'www':
                continue
            # log(d)
            get_dir(d)
    
    def finalize(self):
        pass
        # self.cfg.write()
        