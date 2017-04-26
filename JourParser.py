import sys
import os
import paramiko
from paramiko import SSHClient
import json
import winreg

CONFIG_FILE = "configure.json"

def hang_up_to_watch_errors():
    print("Stop to see what error occurs!!!")
    print("You can Exit with 'Ctrl + C'...")
    while(1):
        pass

    sys.exit()

def journal_paser(source_file, config_dict):
    step_keyword = "Read Configuration"
    ret_bool = True

    try:
        print("journal paser start!")

        user_name = config_dict["user_name"]
        user_pwd = config_dict["user_pwd"]
        host_ip = config_dict["host_ip"]
        remote_path = config_dict["remote_path"]

        local_file = source_file.replace('\\', '/').replace('\"', '')
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

        step_keyword = "SFTP connection"
        tport = paramiko.Transport((host_ip, 22))
        tport.connect(username=user_name, password=user_pwd)
        sftp = paramiko.SFTPClient.from_transport(tport)
        print("SFTP successfully")

        step_keyword = "remove old file"
        stdin, stdout, stderr = ssh.exec_command("rm -f %s/*" %remote_path)
        print(stderr.readlines())

        step_keyword = "upload file"
        sftp.put(local_file, remote_path + local_name)
        print('Upload file successfully')
        print('------')

        step_keyword = "paser journal"
        stdin, stdout, stderr = ssh.exec_command("journalctl -D " + remote_path + " > " + remote_file)
        print(stderr.readlines())

        step_keyword = "download file"
        sftp.get(remote_file, local_path + remote_name)
        print('Download file successfully')
        print('------')

        ssh.close()
        tport.close()

        ret_bool = True

    except Exception:
        print(step_keyword + " error!")
        ret_bool = False

    return ret_bool

def regist_contextmenu(workpath):
    workpath = workpath.replace('/', '\\')
    print('---')
    print(workpath)

    target_icon = workpath + "\\JourParser.exe"
    target_cmd = workpath + "\\JourParser.exe '%1'"

    try:
        subkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,"*\\shell")
        try:
            targetkey = winreg.OpenKey(subkey,"JourParser")
            winreg.DeleteKey(targetkey,"command")
        except OSError:
            print("Key missing, create one.")
        finally:
            targetkey = winreg.CreateKey(subkey,"JourParser")
            winreg.SetValueEx(targetkey, "Icon", 0,  winreg.REG_SZ, target_icon)
            winreg.SetValue(targetkey, "command",  winreg.REG_SZ, target_cmd)
            winreg.CloseKey(subkey)

    except OSError:
        print("Contextmenu register failed!")
        hang_up_to_watch_errors()
        return False
    else:
        return True

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
        json_str = json.dumps(dict_str, indent=2)

        file_desc = open(config_path, "w")
        file_desc.write(json_str)
        file_desc.close()

        #exit directly
        sys.exit(0)

    return dict_str

def main():

    if len(sys.argv) != 2:
        print("argv error!")
        #debug file
        source_file = "D:/userdata/chrhong/Desktop/system.journal"
    else:
        source_file = sys.argv[1].strip("\'\"")

    config_dict = config_load()

    if source_file and config_dict and journal_paser(source_file, config_dict):
        return

    hang_up_to_watch_errors()

if __name__ == "__main__":
    main()
