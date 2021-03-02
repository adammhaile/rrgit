from . command import Command
from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
from . file_ops import *

import os
from datetime import datetime
import time
# from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("EVENT")
        print(event.event_type)
        print(event.src_path)
        print()

# if __name__ == "__main__":
#     path = sys.argv[1] if len(sys.argv) > 1 else '.'

#     event_handler = EventHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=True)
#     observer.start()
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()

class Watch(Command):
    @staticmethod
    def add_parser(sp):
        p = sp.add_parser('watch', 
            help='Watch for local file changes and push to remote')
        
    def __init__(self, cfg, args):
        super().__init__(cfg, args)
        self.connect()
        
        self.event_handler = EventHandler()
        self.observer = Observer()
        print(self.cfg.dir)
        self.observer.schedule(self.event_handler, self.cfg.dir, recursive=True)
        
    def run(self):
        status('Starting file watcher...')
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()