import os, getopt
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
totaldirs = totalfiles = 0
red = '\033[91m'
green = '\033[38;2;0;255;0m'
yellow = '\033[38;2;255;255;0m'
blue = '\033[94m'
clear = '\033[0m'

def signal_handler(sig, frame):
    print(f'{red}Process terminated by user{clear}')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def printOut(type = None, entry = ''):
    global dirs, files, totaldirs, totalfiles
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
    # Print total dirs and files
    os.system('clear')
    print(f'{yellow}Backing up files...')
    print(f'{blue}Total folders: {totaldirs} - Total files: {totalfiles}')
    print(f'{color}{text} "{entry}" ({dirs} dirs | {files} files)')

def ftp_directory_count(sftp, path):
    global totaldirs, totalfiles
    for entry in sftp.listdir(path):
        remotepath = path + "/" + entry
        mode = sftp.stat(remotepath).st_mode
        if S_ISDIR(mode):
            totaldirs += 1
            ftp_directory_count(sftp, remotepath)
        elif S_ISREG(mode):
            totalfiles += 1

def handler(sftp, remotedir, localdir, preserve=False):
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
            handler(sftp, remotepath, localpath, preserve)
        elif S_ISREG(mode):
            sftp.get(remotepath, localpath, preserve_mtime=preserve)
            printOut('file', entry)

print(f'{yellow}Connecting to {hostname}...')
try:
    with pysftp.Connection(host=hostname , port=2022, username=username, password=password, cnopts=cnopts) as sftp:
        print(f'{green}Connected to {hostname}')

        if len(sys.argv) > 1:
            if '--count' in sys.argv:
                print(f'{yellow}Counting files and folders. This may take a while...')
                ftp_directory_count(sftp, remote_path)

        handler(sftp, remote_path, local_path, preserve=False)
        print('[ ✓ ] Backup done !')
except Exception as e:
    print(f'{red}Failed to connect to {hostname}')
    print(f'{red}Error: {e} {clear}')