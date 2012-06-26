#!/usr/bin/env python
#
#from distutils.core import setup
import distutils
from DistUtilsExtra.command import *
import os

def setup(**attrs):
    '''Install quickly unity lens template files'''
    v = attrs.setdefault('data_files', [])
    for (path, dirs, files) in os.walk('.'):
        print(path)
        if not path in ('./private_lib', './images'):
            continue
        if 'tests' in path:
            continue
        for f in files:
            f = os.path.join(path, f)
            v.append((os.path.join('share', 'unity-lens-radios', os.path.dirname(f[2:])), [f]))
    distutils.core.setup(**attrs)

setup(name="unity-lens-radios",
      version="0.1",
      author="Didier Roche",
      author_email="didrocks@ubuntu.com",
      url="http://launchpad.net/unity-lens-radios",
      license="GNU General Public License (GPL3)",
      data_files=[
    ('share/unity-lens-radios', ['unity-lens-radios']),
    ('share/dbus-1/services', ['unity-lens-radios.service']),
    ], cmdclass={"build":  build_extra.build_extra,
                 "build_i18n": build_i18n.build_i18n,})
