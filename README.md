# Bifrost Output Reader

Reads output attributes from a Bifrost graph and displays all of its data.

Click on the image below to watch a demo of it.

[![Tool demo](https://img.youtube.com/vi/ISaGk_V6dAg/0.jpg)](https://www.youtube.com/watch?v=ISaGk_V6dAg)

## Limitations

* Output port must have an active connection (can't create a port then unplug)
* This tool doesn't support the following types:
    * char2, char3, char4
    * Matrices that aren't 4x4 and non-floating point types
    * Enums
    * Amino objects
    * Locations
    * Custom types except bool2, bool3, bool4
    * Any 3D arrays

## Installation

Drag and drop the file installer.py onto a viewport to run it.

Follow the instructions to complete the installation.

The installer gives you a choice to install it into your maya preferences, or to pick a location.

You can also manually install it by simply copying the `bifrost_output_reader` directory to folder where your Python path is pointing to.

## Launching Tool

After installation you can immediately launch the tool by executing the following Python code in the Script Editor:

```
from bifrost_output_reader import bifrost_output_reader_tool
bifrost_output_reader_tool.launch()
```

## Dependencies

This script has no extra dependencies.

This tool is compatible with Python 2 and 3, so it will work with Maya 2018 and above.

## Reporting bugs & requesting features

You can send all bug reports and any feature requests to jasonlabbe@gmail.com.

For errors please include the following to ease debugging:

* Your operating system
* Your version of Maya
* If possible, open up the Script Editor and copy & paste the error message.
* Include any steps that will replicate the error.
