from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename

import threading
import sys
import paramiko
from paramiko import SSHClient
import json

CONFIG_FILE = "configure.json"

def config_load():
    try:
        root_path = sys.path[0]

        file_desc = open(root_path + "/" + CONFIG_FILE, "r")
        dict_str = json.load(file_desc)
        file_desc.close()
    except Exception:
        dict_str = {}
        print("File open failed!")

    return dict_str

def journal_paser(progress_bar, source_file):
    step_keyword = "journal_paser entry"

    try:
        print("thread start")

        step_keyword = "Configuration load!"
        config_dict = config_load()
        user_name = config_dict["user_name"]
        user_pwd = config_dict["user_pwd"]
        host_ip = config_dict["host_ip"]
        remote_path = config_dict["remote_path"]

        local_file = source_file.get().replace('\\', '/').replace('\"', '')
        local_path = local_file[:local_file.rfind('/')+1]
        local_name = local_file[local_file.rfind('/')+1:]
        remote_name = local_name[:local_name.rfind('.')] + '.txt'
        remote_file = remote_path + remote_name

        print(local_file)
        print(local_path)
        print(local_name)
        print(remote_name)
        print(remote_path)
        print(remote_file)

        step_keyword = "SSH connection"
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, 22, user_name, user_pwd)
        print("SSH successfully")

        progress_bar.step(10)

        step_keyword = "SFTP connection"
        tport = paramiko.Transport((host_ip, 22))
        tport.connect(username=user_name, password=user_pwd)
        sftp = paramiko.SFTPClient.from_transport(tport)
        print("SFTP successfully")

        progress_bar.step(10)

        step_keyword = "remove old file"
        stdin, stdout, stderr = ssh.exec_command("rm -f %s/*" %remote_path)
        print(stderr.readlines())

        progress_bar.step(10)

        step_keyword = "upload file"
        sftp.put(local_file, remote_path + local_name)
        print('Upload file successfully')
        print('------')

        progress_bar.step(20)

        step_keyword = "paser journal"
        stdin, stdout, stderr = ssh.exec_command("journalctl -D " + remote_path + " > " + remote_file)
        print(stderr.readlines())

        progress_bar.step(20)

        step_keyword = "download file"
        sftp.get(remote_file, local_path + remote_name)
        print('Download file successfully')
        print('------')

        ssh.close()
        tport.close()

        progress_bar.step(30)

    except Exception:
        print(step_keyword + " error!")

def start_journal_thread(progress_bar, source_file):
    threading.Thread(target=journal_paser, args={progress_bar, source_file}).start()
    return

def browse(source_file):
    file_path = askopenfilename()
    source_file.insert(index=0, string=file_path)
    print("browse button is clicked, file path:" + file_path)

def main():

    root = Tk()
    root.title("Journal Paser 1.0")
    root.geometry('400x100')  
    root.resizable(True, True)
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

if __name__ == "__main__":
    main()