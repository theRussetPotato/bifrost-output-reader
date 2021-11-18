"""
Drag and drop this file into your viewport to run the installer.
"""

import sys
import os
import shutil
import traceback
import time

import maya.cmds as cmds


tool_name = "bifrost_output_reader"


def onMayaDroppedPythonFile(*args):
    try:
        source_dir = os.path.dirname(__file__)
        source_path = os.path.normpath(os.path.join(source_dir, "scripts", tool_name))
        home_dir = os.getenv("HOME")
        install_path = None

        # Make sure this installer is relative to the main tool.
        if not os.path.exists(source_path):
            raise RuntimeError("Unable to find `scripts/{toolName}` relative to this installer file.".format(toolName=tool_name))

        # Suggest to install in user's preferences if it exists.
        if home_dir:
            install_path = os.path.normpath(os.path.join(home_dir, "maya", "scripts"))

            msg = (
                "The tool will be installed in a new folder here:\n"
                "{installPath}\n"
                "\n"
                "Is this ok?".format(
                    installPath=install_path))

            decision = cmds.confirmDialog(
                title="Installation path", message=msg, icon="warning",
                button=["OK", "Cancel", "No, let me pick another path!"],
                cancelButton="Cancel", dismissString="Cancel")

            if decision == "Cancel":
                return
            elif decision == "No, let me pick another path!":
                install_path = None

        # If no install path is supplied, open a file picker to choose a path.
        if install_path is None:
            results = cmds.fileDialog2(fileMode=3, okCaption="Install here", caption="Pick a folder to install to")
            if not results:
                return
            install_path = os.path.normpath(results[0])

        # Check if install path is in Python's path.
        python_paths = [os.path.normpath(path) for path in sys.path]
        if install_path not in python_paths:
            msg = (
                "Python isn't pointed to this path.\n"
                "\n"
                "This means Python won't be able to find the tool and run it.\n"
                "This can be set in your Maya.env or userSetup.py files.\n"
                "\n"
                "Do you want to continue anyways?")

            continue_anyways = cmds.confirmDialog(
                title="Warning!", message=msg, icon="warning",
                button=["OK", "Cancel"],
                cancelButton="Cancel", dismissString="Cancel")

            if continue_anyways == "Cancel":
                return

        # Remove directory if it already exists.
        tool_path = os.path.join(install_path, tool_name)
        if os.path.exists(tool_path):
            # Give a warning first!
            msg = ("This folder already exists:\n"
                   "{toolPath}\n"
                   "\n"
                   "Continue to overwrite it?".format(toolPath=tool_path))

            confirm_overwrite = cmds.confirmDialog(
                title="Overwrite?", message=msg, icon="warning",
                button=["OK", "Cancel"],
                cancelButton="Cancel", dismissString="Cancel")

            if confirm_overwrite == "Cancel":
                return

            shutil.rmtree(tool_path)

        # Windows may throw an 'access denied' exception doing a copytree right after a rmtree, so force a delay.
        time.sleep(1)
        shutil.copytree(source_path, tool_path)

        # Display success!
        msg = (
            "The tool has been successfully installed!\n"
            "If you want to remove it then simply delete this folder:\n"
            "{toolPath}\n\n"
            "Run the tool from the script editor by executing the following:\n\n"
            "from bifrost_output_reader import bifrost_output_reader\n"
            "bifrost_output_reader.launch()".format(toolPath=tool_path))

        cmds.confirmDialog(title="Success!", message=msg, button=["OK"])
    except Exception as e:
        print(traceback.format_exc())

        # Display error message if an exception was raised.
        msg = (
            "{err}\n"
            "\n"
            "If you need help or have questions please send an e-mail with subject "
            "'{toolName} installation' to jasonlabbe@gmail.com".format(
                err=e, toolName=tool_name))

        cmds.confirmDialog(title="Installation has failed!", message=msg, icon="critical", button=["OK"])
