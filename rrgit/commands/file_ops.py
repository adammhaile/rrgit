from .. util import rrgit_error, data_size, TIMESTAMP_FMT
from .. log import *
import enum
import copy

import pathspec

import os
from datetime import datetime

import difflib

class FileType(enum.Enum):
    Local = 1
    Remote = 2

class FileObj():
    def __init__(self, filetype = FileType.Local):
        self.name = None
        self.dir = None
        self.path = None
        self.size = 0
        self.sizestr = None
        self.timestamp = 0
        self.timestr = None
        self.type = filetype
        
    def setPath(self, filepath):
        # filepath should be relative to root
        self.name = os.path.basename(filepath)
        self.dir = filepath[:-1*len(self.name)]
        self.path = filepath
        
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
                
    def getFileData(self, dwa):
        return dwa.get_file(self.name, self.dir, True)
        
    def delete(self, dwa, local_dir = None):
        if self.type == FileType.Remote:
            dwa.delete_file(self.name, self.dir)
        elif local_dir is not None and self.type == FileType.Local:
            path = os.path.join(local_dir, self.dir, self.name)
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            base_dir = os.path.join(local_dir, self.dir)
            if os.listdir(base_dir):
                try:
                    os.rmdir(base_dir)
                except OSError:
                    pass
            
    def pullFile(self, dwa, local_dir):
        if self.type == FileType.Remote:
            data = self.getFileData(dwa)
            if data is not None:
                out_dir = os.path.join(local_dir, self.dir)
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                outpath = os.path.join(local_dir, self.dir, self.name)
                with open(outpath, 'wb') as of:
                    of.write(data)
                    
                now = datetime.timestamp(datetime.now())
                os.utime(outpath, (now, self.timestamp))
                
    def pushFile(self, dwa, local_dir):
        if self.type == FileType.Local:
            local_path = os.path.join(local_dir, self.path)
            try:
                with open(local_path, 'rb') as f:
                    data = f.read()
            except:
                error(f'Error: Failed to read ./{self.path}')
            
            try:
                res = dwa.upload_file(data, self.name, self.dir)
            except ValueError:
                error(f'Error: API failure pushing ./{self.path}')
            
            # now fetch remote's timestamp and write it to local
            # only way to ensure they match
            rfo = copy.deepcopy(self)
            rfo.type = FileType.Remote
            rfo.getRemoteData(dwa)
            
            now = datetime.timestamp(datetime.now())
            os.utime(local_path, (now, rfo.timestamp))
                
            
                    
    def __str__(self):
        return str(self.__dict__)

def build_local_file_map(cfg, remote_directories):
    status('Building local file listing...')
    local_map = {}
    files = cfg.ignore_spec.match_tree(cfg.dir)
    for f in files:
        f = f.replace('\\', '/')
        split = f.split('/')
        if len(split) == 0: 
            continue
        base = split[0]
        if base not in remote_directories:
            continue  # skip invalid local dirs
        fo = FileObj()
        fo.setPath(f)
        
        full_path = os.path.join(cfg.dir, f)
        finfo = os.stat(full_path)
        
        fo.setTime(finfo.st_mtime)
        fo.setSize(finfo.st_size)
        
        local_map[f] = fo
        
    return local_map
    
def build_remote_file_map(dwa, cfg, remote_directories):
    status('Fetching remote file listing...')
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
            
    
def build_status_report(dwa, cfg, remote_directories):
    remote_files = build_remote_file_map(dwa, cfg, remote_directories)
    local_files = build_local_file_map(cfg, remote_directories)
    
    remote_paths = set(remote_files.keys())
    local_paths = set(local_files.keys())
    
    ro = list(remote_paths - local_paths)
    ro.sort()
    
    lo = list(local_paths - remote_paths)
    lo.sort()
    
    shared = list(remote_paths & local_paths)
    shared.sort()
    
    result = {
        'remote_only' : ro,
        'remote_files': remote_files,
        'local_only' : lo,
        'local_files': local_files,
        'shared' : shared,
        'remote_newer' : {},
        'local_newer' : {},
        'diff_size' : {},
    }
    
    for path in result['shared']:
        fo_remote = remote_files[path]
        fo_local = local_files[path]
        if fo_remote.timestamp > fo_local.timestamp:
            result['remote_newer'][path] = fo_remote
        elif fo_local.timestamp > fo_remote.timestamp:
            result['local_newer'][path] = fo_local
        elif fo_remote.size != fo_local.size:
            result['diff_size'][path] = (fo_remote, fo_local)

    return result
    
def gen_pathspec(patterns):
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
def filter_by_patterns(file_map, patterns):
    spec = gen_pathspec(patterns)
    result = {}
    for path, fo in file_map.items():
        if spec.match_file(path):
            result[path] = fo
    return result
    
def gen_file_diff(path, fremote, flocal):
    with open(fremote, 'r') as f:
        remote_lines = f.readlines()
    with open(flocal, 'r') as f:
        local_lines = f.readlines()
        
    delta = difflib.unified_diff(remote_lines, local_lines, f'<remote>/{path}', f'<local>/{path}')
    result = ''
    for l in delta:
        if l.startswith('+'):
            result += color_string(l, 'green')
        elif l.startswith('-'):
            result += color_string(l, 'red')
        elif l.startswith('^'):
            result += color_string(l, 'blue')
        else:
            result += l
    return result