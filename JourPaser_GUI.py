from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import threading
import sys
import paramiko
from paramiko import SSHClient

HOST_IP = "10.69.120.33"
USER_NAME = "root"
PASSWORD = "rootadmin"
NOKIA_ID='chrhong'

TARGET='/root/usr/journal/'

def journal_paser(progress_bar, source_file):
    try:
        print("thread start")

        local_file = source_file.get().replace('\\', '/').replace('\"', '')
        local_path = local_file[:local_file.rfind('/')+1]
        local_name = local_file[local_file.rfind('/')+1:]
        remote_name = local_name[:local_name.rfind('.')] + '.txt'
        remote_path = TARGET + NOKIA_ID + '/'
        remote_file = remote_path + remote_name

        print(local_file)
        print(local_path)
        print(local_name)
        print(remote_name)
        print(remote_path)
        print(remote_file)
        #SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=HOST_IP, port=22, username=USER_NAME, password=PASSWORD)
        print("SSH successfully")

        progress_bar.step(10)

        #SFTP connection
        tport = paramiko.Transport((HOST_IP, 22))
        tport.connect(username=USER_NAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(tport)
        print("SFTP successfully")

        progress_bar.step(10)

        files = sftp.listdir(TARGET)
        if NOKIA_ID not in files:
            stdin, stdout, stderr = ssh.exec_command("mkdir -p %s" %remote_path)
            print("Create new user: "+NOKIA_ID)
            print(stderr.readlines())

        progress_bar.step(10)

        stdin, stdout, stderr = ssh.exec_command("rm -f %s/*" %remote_path)
        print(stderr.readlines())

        progress_bar.step(10)

        sftp.put(local_file, remote_path + local_name)
        print('Upload file successfully')
        print('------')

        progress_bar.step(20)

        stdin, stdout, stderr = ssh.exec_command("journalctl -D " + remote_path + " > " + remote_file)
        print(stderr.readlines())

        progress_bar.step(20)

        sftp.get(remote_file, local_path + remote_name)
        print('Download file successfully')
        print('------')

        ssh.close()
        tport.close()

        progress_bar.step(20)

    except Exception:
        print("connect error")

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