# OctoPrint-PrintJobHistory

[![Version](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=version&url=https://api.github.com/repos/OllisGit/OctoPrint-PrintJobHistory/releases&query=$[0].name)]()
[![Released](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=released&url=https://api.github.com/repos/OllisGit/OctoPrint-PrintJobHistory/releases&query=$[0].published_at)]()
![GitHub Releases (by Release)](https://img.shields.io/github/downloads/OllisGit/OctoPrint-PrintJobHistory/latest/total.svg)

The OctoPrint-Plugin stores all print-job informations of a print in a local database.
```
###########################################################################
Note:
Adding the plugin to the offical OctoPrint-Repository is requested.
So, at the moment you need to manuell install the plugin from the below URL
###########################################################################
```
#### Support my Efforts

This plugin, as well as my [other plugins](https://github.com/OllisGit/) were developed in my spare time.
If you like it, I would be thankful about a cup of coffee :)

[![More coffee, more code](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=6SW5R6ZUKLB5E&source=url)


## Included features

- [x] Print result (success, fail, cancel)
- [x] Start/End datetime -> duration
- [x] Username
- [x] Filename, filesize
- [x] Note (WYSIWYG-Editor)
- [x] Image (single Image)
- [x] Printed Layers/Height
- [x] Spoolname
- [x] Material
- [x] Used/Calculated length
- [x] Used weight
- [x] Filament cost

### UI features
- [x] List all printjobs
- [x] Edit single printjob
- [x] Capture/Upload Image
- [x] Filter history table (only print result)
- [x] Sort history table (printdate, filename)
- [x] Table column visibility
- [x] Capture image after print
- [x] Take Thumbnail from [UltimakerFormatPackage-Plugin](https://plugins.octoprint.org/plugins/UltimakerFormatPackage/)
- [x] Export all printjobs as CSV
- [x] Import printjobs from CSV
- [x] Better error-feedback (more then just the "happy-path")

### Not included
- No report diagramms

## Planning Release #2, ...
.. see:
- Poll: "What is the next big thing?" https://github.com/OllisGit/OctoPrint-PrintJobHistory/issues/6
- Planning Board: https://github.com/OllisGit/OctoPrint-PrintJobHistory/projects/1

## Screenshots
![plugin-tab](screenshots/plugin-tab.png "Plugin-Tab")
![editPrintJob-dialog](screenshots/editPrintJob-dialog.png "EditPrintJob-Dialog")
![plugin-settings](screenshots/plugin-settings.png "Plugin-Settings")
![missingplugins-dialog](screenshots/missingPlugins-dialog.png "MissingPlugins-Dialog")


## Setup

Install via the bundled [Plugin Manager](http://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/OllisGit/OctoPrint-PrintJobHistory/releases/latest/download/master.zip

## Roadmap

see [Planning-Board](https://github.com/OllisGit/OctoPrint-PrintJobHistory/projects/1)

## Versions

see [Release-Overview](https://github.com/OllisGit/OctoPrint-PrintJobHistory/releases/)


