from . command import Command
from .. util import *
from .. log import *
from . file_ops import *
from .. import symbols

import os
from datetime import datetime
import glob
import tempfile

class Diff(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('diff', 
            help='Display complete file diff between local and remote')
        p.add_argument('file_patterns', action='store',
            help='File pathspec to pull', nargs='*',
            default=None)
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
    def run(self):
        report = build_status_report(self.dwa, self.cfg, self.directories)
        
        # pull_files = {}
        # if self.args.force or len(self.args.file_patterns) > 0:
        #     pull_files = report['remote_files']
        #     if len(self.args.file_patterns) > 0:
        #         pull_files = filter_by_patterns(pull_files, self.args.file_patterns)
        
        # lo = report['local_only']
        # ro = report['remote_only']
        
        diff_files = {}
        for t in ['remote_newer', 'local_newer', 'diff_size']:
            for path, fo in report[t].items():
                if path not in diff_files:
                    diff_files[path] = (report['remote_files'][path], report['local_files'][path])
        
        diff_files = filter_by_patterns(diff_files, self.args.file_patterns)
        
        if diff_files:
            with tempfile.TemporaryDirectory() as tmpdir:
                status('Pulling remote files to be compared...')
                for path, fos in diff_files.items():
                    rfo, lfo = fos
                    info(f'{symbols.pull} {path}')
                    rfo.pullFile(self.dwa, tmpdir)
                nl()
                for path, fos in diff_files.items():
                    diff = gen_file_diff(path, os.path.join(tmpdir, path), os.path.join(self.cfg.dir, path))
                    info(diff)
        else:
            success('Remote and Local are identical')
