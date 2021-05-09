# coding=utf-8
from __future__ import absolute_import

# Reworking Christoph Schranz's Tweaker application into an Octoprint plugin.

import octoprint.plugin
import os
import time
import requests
import flask

from .MeshTweaker import Tweak
from . import FileHandler

class TweakerPlugin():

    # ~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            autoprint=dict(
                displayName="Tweaker-3",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="AutoprintLabs",
                repo="Octoprint_Tweaker3",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/AutoprintLabs/Octoprint_Tweaker3/archive/{target_version}.zip"
            )
        )

def tweak_on_upload(path, file_object, links=None, printer_profile=None, allow_overwrite=True, *args, **kwargs):
    

    name, type = os.path.splitext(file_object.filename)
    if not ((type="stl") or (type="3mf")):
        return file_object


    FileHandler = FileHandler.FileHandler()
    try:
        objs = FileHandler.load_mesh(path)
        if objs is None:
            sys.exit()
    except(KeyboardInterrupt, SystemExit):
        raise SystemExit("Error, loading mesh from file failed!")
    c = 0
    info = dict()
    for part, content in objs.items():
        mesh = content["mesh"]
        info[part] = dict()
        try:
            cstime = time()
            x = Tweak(mesh, verbose=False)
            info[part]["matrix"] = x.matrix
        except (KeyboardInterrupt, SystemExit):
            raise SystemExit("\nError, tweaking process failed!")
    if not args.result:
        try:
            FileHandler.write_mesh(objs, info, path, "asciistl") #arguments.outputfile should include the file path
            self._logger.info("Wrote tweaked file to {}".format(path))
        except FileNotFoundError:
            raise FileNotFoundError("Output File '{}' not found.".format(path))
    

    return octoprint.filemanager.util.DiskFileWrapper(file_object.filename, path))

_plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TweakerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.filemanager.preprocessor": tweak_on_upload,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }



