from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
import enum

import os
from datetime import datetime

class FileType(enum.Enum):
    Local = 1
    Remote = 2

class FileObj():
    def __init__(self, filetype = FileType.Local):
        self.name = None
        self.dir = None
        self.size = 0
        self.sizestr = None
        self.timestamp = 0
        self.timestr = None
        self.type = filetype
        
    def setPath(self, filepath):
        # filepath should be relative to root
        self.name = os.path.basename(filepath)
        self.dir = filepath[:-1*len(self.name)]
        
    def setTime(self, timestamp):
        self.timestamp = timestamp
        self.timestr = datetime.fromtimestamp(timestamp).strftime(TIMESTAMP_FMT)
        
    def setSize(self, size):
        self.size = size
        self.sizestr = data_size(size)
        
    def getRemoteData(self, dwa):
        if self.type == FileType.Remote:
            if self.name is not None and self.dir is not None:
                fi = dwa.get_fileinfo(self.name, self.dir)
                lm = datetime.strptime(fi['lastModified'], TIMESTAMP_FMT)
                lm = datetime.timestamp(lm)
                self.setTime(lm)
                self.setSize(fi['size'])
            
        
    def __str__(self):
        return str(self.__dict__)

def build_local_file_map(cfg):
    local_map = {}
    files = cfg.ignore_spec.match_tree(cfg.dir)
    for f in files:
        fo = FileObj()
        fo.setPath(f)
        
        full_path = os.path.join(cfg.dir, f)
        finfo = os.stat(full_path)
        
        fo.setTime(finfo.st_mtime)
        fo.setSize(finfo.st_size)
        
        local_map[f] = fo
        
    return local_map
    
def build_remote_file_map(dwa, cfg, remote_directories):
    remote_files = {}
    def get_dir(path):
        items = dwa.get_directory(path)
        for i in items:
            if i['type'] == 'd':
                dir_path = path + '/' + i['name']
                cfg.ignore_spec.match_file(dir_path + '/')
                get_dir(dir_path)
            elif i['type'] == 'f':
                name = i['name']
                fpath = path + '/' + name
                success(fpath)
                if not cfg.ignore_spec.match_file(fpath):
                        continue
                fo = FileObj(FileType.Remote)
                fo.setPath(fpath)
                fo.getRemoteData(dwa)
                remote_files[fpath] = fo
    for d in remote_directories:
        if cfg.ignore_spec.match_file(d + '/'):
            get_dir(d)
            
    return remote_files
    