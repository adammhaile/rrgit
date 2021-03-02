from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *
from .. import symbols

import contextlib

import os
import time
from datetime import datetime
# currently using polling observer because it works in all scenarios
# I know it's slow but nothing else will work with CIFS or WSL
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler


class Watch(Command, FileSystemEventHandler):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('watch', 
            help='Watch for local file changes and push to remote')
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
        self.observer = Observer()
        self.observer.schedule(self, self.cfg.dir, recursive=True)
        
        self.ignore_next = {}
        
    def create_lfo(self, path):
        path = path.replace('\\', '/')
        path = path.replace(self.cfg.dir + '/', '')
        if not self.cfg.ignore_spec.match_file(path):
            return None
        split = path.split('/')
        if len(split) == 0: 
            return None
        base = split[0]
        if base not in self.directories:
            return None  # skip invalid local dirs
            
        fo = FileObj()
        fo.setPath(path)
        
        if fo.path in self.ignore_next:
            del self.ignore_next[fo.path]
            return None
        
        full_path = os.path.join(self.cfg.dir, path)
        if os.path.isfile(full_path):
            finfo = os.stat(full_path)
            
            fo.setTime(finfo.st_mtime)
            fo.setSize(finfo.st_size)
        
        return fo
         
    def on_created(self, event):
        if(not os.path.isdir(event.src_path)):
            lfo = self.create_lfo(event.src_path)
            if lfo is not None:
                push = color_string('⇖', 'green')
                info(f'{symbols.push}: {lfo.path}')
                self.ignore_next[lfo.path] = lfo
                lfo.pushFile(self.dwa, self.cfg.dir)
    
    def on_deleted(self, event):
        if(not os.path.isdir(event.src_path)):
            lfo = self.create_lfo(event.src_path)
            if lfo is not None:
                lfo.type = FileType.Remote # convert to remote so we can delete
                delete = color_string('D', 'red')
                info(f'{symbols.delete}: {lfo.path}')
                lfo.delete(self.dwa)
        
    def on_modified(self, event):
        if(os.path.isfile(event.src_path)):
            lfo = self.create_lfo(event.src_path)
            if lfo is not None:
                mod = color_string('🖉', 'yellow')
                info(f'{symbols.modify} {lfo.path}')
                self.ignore_next[lfo.path] = lfo
                lfo.pushFile(self.dwa, self.cfg.dir)
        
    def on_moved(self, event):
        if(os.path.isfile(event.dest_path)):
            source_lfo = self.create_lfo(event.src_path)
            dest_lfo = self.create_lfo(event.dest_path)
            if source_lfo is not None and dest_lfo is not None:
                source_lfo.type = FileType.Remote # convert to remote so we can delete
                info(f'{source_lfo.path} {symbols.move} {dest_lfo.path}')
                source_lfo.delete(self.dwa)
                self.ignore_next[dest_lfo.path] = dest_lfo
                dest_lfo.pushFile(self.dwa, self.cfg.dir)
        
    def run(self):
        status('Starting file watcher...')
        self.observer.start()
        try:
            warn('Press enter to stop watching...\n')
            input('')
        except KeyboardInterrupt:
            pass
        self.observer.stop()
        self.observer.join()