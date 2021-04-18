# -*- coding: utf-8 -*-

# @File    : hook-pynput.py
# @Date    : 2021-04-18
# @Author  : 王超逸
# @Brief   : 
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules("pynput.keyboard")
hiddenimports += collect_submodules("pynput.mouse")

