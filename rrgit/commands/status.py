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
        status(f'Remote Only: {report["remote_only"]}')
        status(f'Local Only: {report["local_only"]}')
        status(f'Shared: {report["shared"]}')
        status(f'Remote Newer: {list(report["remote_newer"].keys())}')
        status(f'Local Newer: {list(report["local_newer"].keys())}')
        status(f'Diff Size: {list(report["diff_size"].keys())}')
        
    def finalize(self):
        pass
        