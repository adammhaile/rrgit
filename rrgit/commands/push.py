from . command import Command
from .. util import *
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
        p.add_argument('--force', '-f', action='store_true', default=False, 
            help='push all, regardless of remote file status')
        p.add_argument('--yes', '-y', action='store_true', default=False, 
            help='suppress overwrite confirmation')
        p.add_argument('file_patterns', action='store',
            help='File pathspec to pull', nargs='*',
            default=None)
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        report = build_status_report(self.dwa, self.cfg, self.directories)
        
        push_files = {}
        if self.args.force or len(self.args.file_patterns) > 0:
            push_files = report['local_files']
            if len(self.args.file_patterns) > 0:
                push_files = filter_by_patterns(push_files, self.args.file_patterns)
        
        lo = report['local_only']
        
        rn = list(report['remote_newer'].keys())
        rn.sort()
        ln = list(report['local_newer'].keys())
        ln.sort()
        ds = list(report['diff_size'].keys())
        ds.sort()
            
        if push_files:
            status('Pushing files to remote...')
            paths = list(push_files.keys())
            paths.sort()
            for path in paths:
                fo = push_files[path]
                info(f'- {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
        elif len(lo) > 0 or len(rn) > 0 or len(ln) > 0 or len(ds) > 0:
            if not self.args.yes and (len(rn) > 0 or len(ds) > 0) :
                if len(rn) > 0:
                    error('The following files have newer remote changes.')
                    for path in rn:
                        info(f'- {path}')
                if len(ds) > 0:
                    error('The following files differ only in size.')
                    for path in ds:
                        info(f'- {path}')
                if not yes_or_no('Overwrite remote with local?'):
                    return
            status('Pushing files to remote...')
            for path in lo:
                info(f'- {path}')
                report['local_files'][path].pushFile(self.dwa, self.cfg.dir)
                
            for path in rn:
                fo = report['local_files'][path]
                info(f'- {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["local_newer"].items():
                info(f'- {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["diff_size"].items():
                info(f'- {path}')
                lfo = fo[1]
                lfo.pushFile(self.dwa, self.cfg.dir)
        else:
            success('No changes detected')
        