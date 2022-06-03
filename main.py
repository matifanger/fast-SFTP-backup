import os
import pysftp
from stat import S_ISDIR, S_ISREG
from configparser import ConfigParser
import signal
import sys

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

config = ConfigParser()
config.read("config.ini")

hostname = config["ftp"]["hostname"]
username = config["ftp"]["username"]
password = config["ftp"]["password"]
local_path = config["folders"]["local"]
remote_path = config["folders"]["host"]

dirs = files = 0
red = '\033[91m'
green = '\033[38;2;0;255;0m'
yellow = '\033[38;2;255;255;0m'
clear = '\033[0m'

def signal_handler(sig, frame):
    print(f'{red}Process terminated by user{clear}')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def printOut(type = None, entry = ''):
    global dirs, files
    if type == 'dir':
        dirs += 1
        text = '[ + ] New folder'
        color = green
    elif type == 'file':
        files += 1
        text = '[ + ] New file'
        color = green
    elif type == 'dir-exists':
        text = '[ - ] Folder exists'
        color = yellow
    print(f'{color}{text} "{entry}" ({dirs} dirs | {files} files)')

def get_r_portable(sftp, remotedir, localdir, preserve_mtime=False):
    for entry in sftp.listdir(remotedir):
        remotepath = remotedir + "/" + entry
        localpath = os.path.join(localdir, entry)
        mode = sftp.stat(remotepath).st_mode
        if S_ISDIR(mode):
            try:
                os.mkdir(localpath)
                printOut('dir', entry)
            except OSError:     
                printOut('dir-exists', entry)
                pass
            get_r_portable(sftp, remotepath, localpath, preserve_mtime)
        elif S_ISREG(mode):
            sftp.get(remotepath, localpath, preserve_mtime=preserve_mtime)
            printOut('file', entry)

print(f'{yellow}Connecting to {hostname}...')
try:
    with pysftp.Connection(host=hostname , port=2022, username=username, password=password, cnopts=cnopts) as sftp:
        print(f'{green}Connected to {hostname}')
        get_r_portable(sftp, remote_path, local_path, preserve_mtime=False)
        print('[ ✓ ] Backup done !')
except Exception as e:
    print(f'{red}Failed to connect to {hostname}')
    print(f'{red}Error: {e} {clear}')