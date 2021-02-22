from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

import os
from datetime import datetime
import glob

class Status(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('status', 
            help='Fetch status and show remote vs local')
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        report = build_status_report(self.dwa, self.cfg, self.directories)
        
        ro = report['remote_only']
        lo = report['local_only']
        shared = report['shared']
        
        rn = list(report["remote_newer"].keys())
        rn.sort()
        ln = list(report["local_newer"].keys())
        ln.sort()
        ds = list(report["diff_size"].keys())
        ds.sort()
        
        nl()
        
        diff = False
        if len(ro) > 0:
            diff = True
            header = color_string('remote only:\t', 'red')
            for path in ro:
                info(f'{header}{path}')
            nl()
                
        if len(lo) > 0:
            diff = True
            header = color_string('local only:\t', 'red')
            for path in lo:
                info(f'{header}{path}')
            nl()
                
        if len(rn) > 0:
            diff = True
            header = color_string('remote newer:\t', 'red')
            for path in rn:
                info(f'{header}{path}')
            nl()
                
        if len(ln) > 0:
            diff = True
            header = color_string('local newer:\t', 'red')
            for path in ln:
                info(f'{header}{path}')
            nl()
                
        if len(ds) > 0:
            diff = True
            header = color_string('diff size:\t', 'red')
            for path in ds:
                info(f'{header}{path}')
            nl()
                
        if not diff:
            success('Remote and Local are identical')
        
    def finalize(self):
        pass
        