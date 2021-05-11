# coding=utf-8
from __future__ import absolute_import

# Reworking Christoph Schranz's Tweaker application into an Octoprint plugin.

import octoprint.plugin
import os
import time
import sys
import logging

from .MeshTweaker import Tweak
from .FileHandler import FileHandler


class tweaker3(octoprint.plugin.SlicerPlugin):
    slicer_properties = dict(
            type="tweaker",
            name="Tweaker Autorotate",
            same_device=True,
            progress_report=False,
            source_file_types=["tweakstl"],
            destination_extensions=[".stt"]
        )
    # ~~ Softwareupdate hook
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.tweaker3")
        self._logger.info("Tweaker") # This shows up in OP boot  
    def initialize(self):
        self._logger.info("Tweaker initialized")# This shows up in OP boot 
    def is_slicer_configured(self):
        return True

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
    ##~~ Slicer plugin API
    def get_slicer_properties(self):
        return self.slicer_properties

    def get_slicer_default_profile(self):
        return octoprint.slicing.SlicingProfile(
            slicer="tweaker",
             name="default",
             data={},
             display_name="Default",
             default=True)

    def do_slice(self, model_path, printer_profile, machinecode_path=None, profile_path=None, position=None,
                 on_progress=None, on_progress_args=None, on_progress_kwargs=None):
        
        self._logger.warn("Tweaking file") # neiher this log nor any others in the function show up.
        #return True,dict(analysis=dict())
        if not machinecode_path:
            machinecode_path = model_path

        myFileHandler = FileHandler()
        objs = myFileHandler.load_mesh(model_path)
        if objs is None:
            self._logger.info("No Mesh found in {}".format(model_path))
            return False, "No mesh found"
        info = dict()
        for part, content in objs.items():
            mesh = content["mesh"]
            info[part] = dict()
            x = Tweak(mesh, verbose=False)
            info[part]["matrix"] = x.matrix
        self._logger.info("Object Tweaked")
        try:
            FileHandler.write_mesh(objs, info, machinecode_path,
                                    "tweakstl")  # arguments.outputfile should include the file path
            self._logger.info("Wrote tweaked file to {}".format(machinecode_path))
            return True,dict(analysis={})
        except FileNotFoundError:
            self._logger.info("Output File '{}' not found.".format(machinecode_path))
            return False, "Output File '{}' not found.".format(machinecode_path)

    def cancel_slicing(self, machinecode_path):
        self._logger.info("cancelled slicing")

    def get_slicer_profile(self, path):
        return self.get_slicer_default_profile(self)

    def get_slicer_profiles(self, path):
        return dict([("default" ,self.get_slicer_default_profile())])

    def get_extension_tree(*args, **kwargs):
        return dict(
            machinecode=dict(
                tweaker3=["tweakstl"]
            )
        )
    

__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    global __plugin_hooks__
    __plugin_implementation__ = tweaker3()

    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.filemanager.extension_tree": __plugin_implementation__.get_extension_tree
    }
