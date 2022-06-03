import os
import pysftp
from stat import S_ISDIR, S_ISREG

hostname = ''
username = ''
password = ''
start_directory = '/'
backup_dir = './test'

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

def get_r_portable(sftp, remotedir, localdir, preserve_mtime=False):
    for entry in sftp.listdir(remotedir):
        remotepath = remotedir + "/" + entry
        localpath = os.path.join(localdir, entry)
        mode = sftp.stat(remotepath).st_mode
        if S_ISDIR(mode):
            try:
                os.mkdir(localpath)
            except OSError as error:     
                print(error)
                pass
            get_r_portable(sftp, remotepath, localpath, preserve_mtime)
        elif S_ISREG(mode):
            sftp.get(remotepath, localpath, preserve_mtime=preserve_mtime)

  
sftp = pysftp.Connection(host=hostname , port=2022, username=username, password=password, cnopts=cnopts)

directory_structure = sftp.listdir_attr()

remote_path="/"
local_path="./test"

get_r_portable(sftp, remote_path, local_path, preserve_mtime=False)