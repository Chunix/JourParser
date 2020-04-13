import os
import sys
import json
import threading

import winreg
import paramiko
from paramiko import SSHClient
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

CONFIG_FILE = "configure.json"

def hang_up_to_watch_errors():
    print("Stop to see what error occurs!!!")
    print("You can Exit with 'Ctrl + C'...")
    while(1):
        pass

    sys.exit()

def config_load():
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        root_path = os.path.dirname(sys.executable)
    elif __file__:
        root_path = os.path.dirname(__file__)

    config_path = root_path + "/" + CONFIG_FILE

    try:
        file_desc = open(config_path, "r")
        dict_str = json.load(file_desc)
        file_desc.close()
    except IOError:
        dict_str = {}
        print("File open failed! --> " + config_path)
        return dict_str

    if dict_str['context_menu'] == "disable" and regist_contextmenu(root_path):
        dict_str['context_menu'] = "enable"

        if dict_str['remote_path'][-1] != '/':
            dict_str['remote_path'] = dict_str['remote_path'] + '/'
            print("[Info] Add '/' at the end of your target path:")
            print(dict_str['remote_path'])

        json_str = json.dumps(dict_str, indent=2)

        file_desc = open(config_path, "w")
        file_desc.write(json_str)
        file_desc.close()

        #exit directly
        sys.exit(0)

    return dict_str

def journal_paser(source_file, progress_bar=None):
    step_keyword = "Read Configuration"
    ret_bool = True
    print(source_file)
    try:
        print("Journal parser start!")

        step_keyword = "Configuration load!"
        config_dict = config_load()

        user_name = config_dict["user_name"]
        user_pwd = config_dict["user_pwd"]
        host_ip = config_dict["host_ip"]
        remote_path = config_dict["remote_path"]

        local_file = source_file.replace('\\', '/').replace('\"', '')
        local_path = local_file[:local_file.rfind('/')+1]
        local_name = local_file[local_file.rfind('/')+1:]
        remote_name = local_name[:local_name.rfind('.')] + '.txt'
        remote_file = remote_path + remote_name

        print("===========================")
        print("Local file, path and name:")
        print(local_file)
        print(local_path)
        print(local_name)
        print("===========================")
        print("Remote file, path and name:")
        print(remote_file)
        print(remote_path)
        print(remote_name)
        print("===========================")

        step_keyword = "SSH connection"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, 22, user_name, user_pwd)
        print("SSH successfully")

        if progress_bar:
            progress_bar.step(10)

        step_keyword = "SFTP connection"
        tport = paramiko.Transport((host_ip, 22))
        tport.connect(username=user_name, password=user_pwd)
        sftp = paramiko.SFTPClient.from_transport(tport)
        print("SFTP successfully")

        if progress_bar:
            progress_bar.step(10)

        step_keyword = "remove old file"
        stdin, stdout, stderr = ssh.exec_command("rm -f %s/*" %remote_path)
        print(stderr.readlines())

        if progress_bar:
            progress_bar.step(10)

        step_keyword = "upload file"
        sftp.put(local_file, remote_path + local_name)
        print('Upload file successfully')
        print('------')

        if progress_bar:
            progress_bar.step(10)

        step_keyword = "paser journal"
        stdin, stdout, stderr = ssh.exec_command("journalctl -D " + remote_path + " > " + remote_file)
        print(stderr.readlines())

        if progress_bar:
            progress_bar.step(10)

        step_keyword = "download file"
        sftp.get(remote_file, local_path + remote_name)
        print('Download file successfully')
        print('------')

        if progress_bar:
            progress_bar.step(20)

        ssh.close()
        tport.close()

        if progress_bar:
            progress_bar.step(30)

        ret_bool = True

    except Exception:
        print("[Error] " + step_keyword)
        ret_bool = False

    print("Journal parser end!")
    return ret_bool

def regist_contextmenu(workpath):
    workpath = workpath.replace('/', '\\')
    print('---')
    print(workpath)

    target_icon = workpath + "\\JourParser.exe"
    target_cmd = workpath + "\\JourParser.exe \"%1\""

    try:
        #Not check if it is already exist, since we can overwrite it
        subkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,"*\\shell")
        targetkey = winreg.CreateKey(subkey,"JourParser")
        winreg.SetValueEx(targetkey, "Icon", 0,  winreg.REG_SZ, target_icon)
        winreg.SetValue(targetkey, "command",  winreg.REG_SZ, target_cmd)
        winreg.CloseKey(subkey)
    except OSError:
        print("[Error] Contextmenu register failed!")
        hang_up_to_watch_errors()
        return False
    else:
        return True

# xWindows
def start_journal_thread(progress_bar, source_file):
    threading.Thread(target=journal_paser, args={source_file.get(), progress_bar}).start()
    return

def browse(source_file):
    file_path = askopenfilename()
    source_file.delete(0, END)
    source_file.insert(index=0, string=file_path)
    print("browse button is clicked, file path:" + file_path)

def xWindows():
    root = Tk()
    root.title("Journal Paser 1.0")
    root.geometry('400x100')
    root.resizable(False, False)
    file_location = StringVar()

    source_file = Entry(root, text = 'Source file:', textvariable=file_location, borderwidth=3, width = 50)
    source_file.place(x=10, y=20, anchor=NW)

    button_browse = Button(root, fg="green", text='Browse', width=8, command=lambda: browse(source_file))
    button_browse.place(x=320, y=17, anchor=NW)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=101)
    progress_bar.place(x=10, y=60,anchor=NW)
    progress_bar.step(0)

    button_browse = Button(root, fg="green", text="Let's go", width=8, command=lambda: start_journal_thread(progress_bar,source_file))
    button_browse.place(x=320, y=57, anchor=NW)

    root.mainloop()

def main():
    config_dict = config_load()
    if not config_dict:
        hang_up_to_watch_errors()
        return

    if len(sys.argv) < 2:
        print("[Info] no argv! Please right click the target journal file to choose JourParser!")
        hang_up_to_watch_errors()
        """
        Note:
        gui mode is not convinient, disabled!
        there is also issues while using this mode:
        1. outputs is not printed in window while problem detected.
        2. sometimes journal_paser stop at configure load, which may related with
           sourcefile configuration.
        """
        # xWindows()
    else:
        source_file = ' '.join(sys.argv[1:]).strip("\'\"")

        if not source_file:
            print("[Error] Null path")
            hang_up_to_watch_errors()
            return

        if not journal_paser(source_file):
            hang_up_to_watch_errors()
            return

if __name__ == "__main__":
    main()
