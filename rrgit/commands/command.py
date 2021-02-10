from .. log import *
from .. util import rrgit_error
from duetwebapi import DuetWebAPI as DWA

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
            success(f'Connected to {self.cfg.hostname}')
        except ValueError as e:
            raise rrgit_error('')