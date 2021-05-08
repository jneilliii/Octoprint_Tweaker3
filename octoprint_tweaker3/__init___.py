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

class TweakerPlugin(octoprint.plugin.SimpleApiPlugin):

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

    def get_api_commands(self):
        return dict(
            tweak=["inputfile", "outputfile", "slice"],
            )

    def on_api_command(self, command, data):
        self._logger.info(command)
        if command == "tweak":
            if inputfile in data:
                arguments.inputfile = data["inputfile"]
            else:
                flask.abort(400)
            if outputfile in data:
                arguments.outputfile = data["outputfile"]
            else:
                arguments.outputfile = os.path.splitext(arguments.inputfile)[0] + "_tweaked.stl"
            try:
                FileHandler = FileHandler.FileHandler()
                objs = FileHandler.load_mesh(arguments.inputfile)
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
                    FileHandler.write_mesh(objs, info, arguments.outputfile, "asciistl") #arguments.outputfile should include the file path
                except FileNotFoundError:
                    raise FileNotFoundError("Output File '{}' not found.".format(arguments.outputfile))

            
                    
                    
            return flask.jsonify(file=os.path.split(arguments.outputfile))

    def on_api_get(self, request):
        return flask.jsonify(foo="bar")


_plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TweakerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.scripts": message_on_connect,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

