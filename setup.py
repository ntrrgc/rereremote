import os
from cx_Freeze import setup, Executable

buildOptions = {
    "packages": [],
    "excludes": [],
    "include_files": [
        ('rereremote/static', ''),
    ],
}

base = lambda name: name if os.name == 'nt' else None
suffix = '.exe' if os.name == 'nt' else ''

executables = [
    Executable('rereremote/main.py', base=base('Console'),
               targetName='rereremote' + suffix, icon='icon.ico'),
    Executable('rereremote/gui/main.py', base=base('Win32GUI'),
               targetName='rereremote_gui' + suffix, icon='icon.ico'),
]

setup(name='rereremote',
      version='0.1',
      description='Control presentations with your phone',
      options={
          "build_exe": buildOptions,
      },
      executables=executables)
