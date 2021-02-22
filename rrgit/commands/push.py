from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

import os
from datetime import datetime
import glob

class Push(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('push', 
            help='Push changes to RRF/Duet device')
        p.add_argument('--force', '-f', action='store_true', default=False)
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        report = build_status_report(self.dwa, self.cfg, self.directories)
        
        lo = report['local_only']
        
        rn = list(report['remote_newer'].keys())
        rn.sort()
        ln = list(report['local_newer'].keys())
        ln.sort()
        ds = list(report['diff_size'].keys())
        ds.sort()
        
        if not self.args.force and (len(rn) > 0 or len(ds) > 0) :
            if len(rn) > 0:
                error('The following files have newer remote changes.')
                for path in rn:
                    info(f'- {path}')
            if len(ds) > 0:
                error('The following files differ only in size.')
                for path in ds:
                    info(f'- {path}')
            error('Use -f to force overwritting remote copies.')
            return
            
        if len(lo) > 0 or len(rn) > 0 or len(ln) > 0 or len(ds) > 0:
            status('Pushing files to remote...')
            for path in lo:
                status(f'- {path}')
                report['local_files'][path].pushFile(self.dwa, self.cfg.dir)
                
            for path in rn:
                fo = report['local_files'][path]
                status(f'- {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["local_newer"].items():
                status(f'- {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["diff_size"].items():
                status(f'- {path}')
                lfo = fo[1]
                lfo.pushFile(self.dwa, self.cfg.dir)
        else:
            success('No changes detected')
        