'''
Created on Nov 5, 2015

@author: chris
'''
from distutils.core import setup
import py2exe


setup(
    options = {'py2exe': {"optimize": 2,
                          'bundle_files': 1}},
    windows = [{
            "script":"micro.py",
            "icon_resources": [(1, "res/icon32.ico")],
            "dest_base":"Micropylis"
            }])