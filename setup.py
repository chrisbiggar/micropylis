'''
Created on Nov 5, 2015

@author: chris
'''
from distutils.core import setup
import py2exe
import shutil, os

try:
    os.remove("dist/avbin.dll")
except OSError:
    pass
shutil.copy("avbin.dll", "dist/avbin.dll")
shutil.rmtree("dist/cities")
shutil.copytree("cities", "dist/cities")
shutil.rmtree("dist/res")
shutil.copytree("res", "dist/res")
print "Done Copying Files"

setup(
    options={'py2exe': {"optimize": 2, 'bundle_files': 1}},
    windows=[{"script": "micro.py",
              "icon_resources": [(1, "res/micro.ico")],
              "dest_base": "Micropylis"}])
