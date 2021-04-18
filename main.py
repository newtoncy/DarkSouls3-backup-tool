# -*- coding: utf-8 -*-

# @File    : main.py
# @Date    : 2021-04-18
# @Author  : 王超逸
# @Brief   : 存档备份热键

from pathlib import Path
from shutil import copytree, rmtree
from textwrap import dedent

from pynput import keyboard
from functools import partial
from threading import RLock, Thread
import os

mutex_lock = RLock()

DarkSoulsIII = "DarkSoulsIII"


def get_save_dir() -> Path:
    return Path.home() / "AppData" / "Roaming" / DarkSoulsIII


def get_backup_dir() -> Path:
    return get_save_dir().parent / f"{DarkSoulsIII}_bak"


def bak_save(rename_to: str):
    with mutex_lock:
        if not get_save_dir().exists():
            print("找不到存档文件")
            return
        if (get_backup_dir() / rename_to).exists():
            print(f"备份{rename_to}被覆盖")
            rmtree(get_backup_dir() / rename_to)
        copytree(get_save_dir(), get_backup_dir() / rename_to)
        print(f"游戏存档备份到{rename_to}")


def recover_dir(name: str):
    with mutex_lock:
        bak_origin_save()
        if get_save_dir().exists():
            rmtree(get_save_dir())
        copytree(get_backup_dir() / name, get_save_dir())
        print(f"恢复{name}")


def remove_dir(name: str):
    if not (get_backup_dir() / name).exists():
        print(f"备份{name}不存在")
        return
    rmtree(get_backup_dir() / name)
    print(f"删除备份:{name}")


def bak_origin_save():
    bak_save(DarkSoulsIII + "_bak")


def get_bak_name(key):
    return f"HotKey_{key}"


def help():
    print(dedent(
        """
        下文 name 表示存档名，index 表示存档序号, <>包裹的表示必填项，/分隔的表示他们具有同样的含义，任选其一即可    
        
        备份 bak/backup/save <name>
        
        列出备份 list/ls
            将给出 (index) name
            
        恢复备份 rcv/rec/recover/re
            rcv <index> 
            rcv -n/--name <name> 
            rcv -i/--index <index>
        
        删除备份 del/rm
            del <index> 
            del -n/--name <name> 
            del -i/--index <index>
            
        帮助 help
        """
    ).strip())


def get_name_from_cmd(args):
    global listed, backup_lookup
    assert args
    index = None
    name = None
    if len(args) == 1:
        try:
            index = int(args[0])
        except ValueError as e:
            raise ValueError(args[0]+"不是整数")
    elif len(args) == 2 and args[0] in {"--index", "-i"}:
        index = int(args[1])
    elif len(args) == 2 and args[0] in {"--name", "-n"}:
        name = args[1]
    else:
        raise ValueError(help())

    if index is not None:
        if listed:
            if 0 <= index < len(backup_lookup):
                return backup_lookup[index]
            else:
                raise ValueError("该存档序号不存在")
        else:
            raise ValueError("使用存档序号需要先使用list命令")

    assert name
    if not (get_backup_dir() / name).exists():
        raise ValueError("存档名不存在")


listed = False
backup_lookup = []


def main():
    print("不死人快乐sl，F5~F8 拷贝存档，F9~F12 恢复存档，输入help了解更多功能\n")
    bk_key_list = ["F5", "F6", "F7", "F8"]
    recover_key_map = {
        "F9": "F5",
        "F10": "F6",
        "F11": "F7",
        "F12": "F8"
    }
    hot_key = {}
    for i in bk_key_list:
        hot_key[f"<{i}>"] = partial(bak_save, get_bak_name(i))

    for k, v in recover_key_map.items():
        hot_key[f"<{k}>"] = partial(recover_dir, get_bak_name(v))

    def listen_hot_key():
        with keyboard.GlobalHotKeys(hot_key) as h:
            h.join()

    hot_key_thread = Thread(target=listen_hot_key)
    hot_key_thread.start()

    # 接下来，提供几个命令
    global backup_lookup, listed
    while True:
        try:
            input_ = input()
            if not input_:
                continue
            command, *args = tuple(input_.split())
            if command == "help":
                help()
            elif command in {"bak", "backup", "save"}:
                bak_save(args[-1])
            elif command in {"rcv", "rec", "recover", "re"}:
                recover_dir(get_name_from_cmd(args))
            elif command in {"list", "ls"}:
                listed = True
                backup_lookup.clear()
                for i, name in enumerate(os.listdir(get_backup_dir())):
                    print(f"({i}) {name}")
                    backup_lookup.append(name)
            elif command in {"del", "rm"}:
                remove_dir(get_name_from_cmd(args))
            else:
                help()
        except ValueError as e:
            print(e)
        except Exception as e:
            help()


if __name__ == '__main__':
    main()
