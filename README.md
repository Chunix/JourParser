# This is a easy journal log parser tool

The project try to make journal log parsing on windows easily. The basic logic is to transfer the journal log to a remote linux server to convert and pull the result back. So the tool requires **a remote/local linux env which you have access rights**.

#### Package
`pyinstaller.exe -i JourParser.ico -F JourParser.py`

#### Protable Installation
1. Download latest [JourParser.zip](https://github.com/chrhong/JourParser/releases/tag/v1.0).
2. Config the `configure.json` before your first using
    * `host_ip`: your remote linux server ip
    * `user_pwd` and `user_name`: your remote linux server ip's username and password
    * `remote_path`: give a your journal folder on your remote linux server. eg: mine is `/root/usr/journal/chrhong/`
    * `context_menu`: must be `"disable"` before your first using
3. Run `JourParser.exe` as administrator first time.
4. Then you can find a `"JourParser"` item in your contextmenu, click it and you can get a result in the same folder.

![](demo.png)

5. Enjoy it.

#### **Note and Warnings !**
1. `remote_path` should be paticularly created and only used to put journal file. Because the tool will clean up the folder every time.
Suggestion is to create your own folder here: `/root/usr/journal/**yourUniqueName**/`

2. `context_menu` once `enable`, mean you already add the `JourParser` to your contextmenu, if you move the `JourParser.exe` to another place, you need to run `"Usage Step2 and Step3"` as above again.
