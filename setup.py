'''
Created on Nov 5, 2015

@author: chris
'''
import shutil, os, zipfile
from distutils.core import setup
import py2exe

try:
    import zlib
    mode = zipfile.ZIP_DEFLATED
except ImportError:
    mode = zipfile.ZIP_STORED


def zipResources(resDest):
    zip = zipfile.ZipFile(resDest, "w", mode)

    # do misc resources
    zip.write("avbin.dll")

    # do res directory
    for dirpath,dirs,files in os.walk('res'):
        for f in files:
            fileName, ext = os.path.splitext(f)
            if ext == ".db":
                continue
            fn = os.path.join(dirpath, f)
            zip.write(fn)

    zip.close()

zipResources("dist/res.zip")
shutil.rmtree("dist/cities")
shutil.copytree("cities", "dist/cities")
print "Done Copying Resources"

setup(
    options={'py2exe': {"optimize": 2, 'bundle_files': 1}},
    windows=[{"script": "micro.py",
              "icon_resources": [(1, "build/exe/micro.ico")],
              "dest_base": "Micropylis"}])
