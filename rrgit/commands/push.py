from . command import Command
from .. util import *
from .. log import *
from . file_ops import *
from .. import symbols

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
        
        lo = report['local_only']
        ro = report['remote_only']
        
        push_files = {}
        if self.args.force or len(self.args.file_patterns) > 0:
            push_files = report['local_files']
            if len(self.args.file_patterns) > 0:
                push_files = filter_by_patterns(push_files, self.args.file_patterns)
        
        rn = list(report['remote_newer'].keys())
        rn.sort()
        ln = list(report['local_newer'].keys())
        ln.sort()
        ds = list(report['diff_size'].keys())
        ds.sort()
            
        if push_files:
            status('Pushing changes to remote...')
            paths = list(push_files.keys())
            paths.sort()
            for path in paths:
                fo = push_files[path]
                info(f'{symbols.push} {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            ro_filtered = {}
            for path in ro:
                ro_filtered[path] = report['remote_files'][path]
                
            ro_filtered = filter_by_patterns(ro_filtered, self.args.file_patterns)
                    
            if len(ro_filtered.keys()) > 0:
                if not self.args.yes:
                    error('The following files are remote only and will be deleted.')
                    for path, fo in ro_filtered.items():
                        info(f'- {path}')
                    if not yes_or_no('Delete remote files?'):
                        return
                for path, fo in ro_filtered.items():
                    info(f'{symbols.delete} {path}')
                    fo.delete(self.dwa)
        elif len(lo) > 0 or len(ro) or len(rn) > 0 or len(ln) > 0 or len(ds) > 0:
            if not self.args.yes and (len(rn) > 0 or len(ro) > 0 or len(ds) > 0) :
                if len(rn) > 0:
                    error('The following files have newer remote changes.')
                    for path in rn:
                        info(f'- {path}')
                if len(ro) > 0:
                    error('The following files are remote only and will be deleted.')
                    for path in ro:
                        info(f'- {path}')
                if len(ds) > 0:
                    error('The following files differ only in size.')
                    for path in ds:
                        info(f'- {path}')
                if not yes_or_no('Overwrite remote with local?'):
                    return
            status('Pushing changes to remote...')
            for path in lo:
                info(f'{symbols.push} {path}')
                report['local_files'][path].pushFile(self.dwa, self.cfg.dir)
                
            for path in rn:
                fo = report['local_files'][path]
                info(f'{symbols.push} {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["local_newer"].items():
                info(f'{symbols.push} {path}')
                fo.pushFile(self.dwa, self.cfg.dir)
                
            for path, fo in report["diff_size"].items():
                info(f'{symbols.push} {path}')
                lfo = fo[1]
                lfo.pushFile(self.dwa, self.cfg.dir)
                
            for path in ro:
                info(f'{symbols.delete} {path}')
                report['remote_files'][path].delete(self.dwa, self.cfg.dir)
        else:
            success('No changes detected')
        