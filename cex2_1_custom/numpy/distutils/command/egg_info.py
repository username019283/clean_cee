# uncompyle6 version 3.9.0
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.10.9 | packaged by Anaconda, Inc. | (main, Mar  8 2023, 10:42:25) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: numpy\distutils\command\egg_info.pyc
# Compiled at: 2013-04-07 07:04:04
from setuptools.command.egg_info import egg_info as _egg_info

class egg_info(_egg_info):

    def run(self):
        self.run_command('build_src')
        _egg_info.run(self)