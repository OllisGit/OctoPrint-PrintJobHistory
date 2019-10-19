# OctoPrint-PrintJobHistory

# WORK IN PROGRESS!!!! Not released, yet!!

[![Version](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=version&url=https://api.github.com/repos/OllisGit/OctoPrint-PrintJobHistory/releases&query=$[0].name)]()
[![Released](https://img.shields.io/badge/dynamic/json.svg?color=brightgreen&label=released&url=https://api.github.com/repos/OllisGit/OctoPrint-PrintJobHistory/releases&query=$[0].published_at)]()
![GitHub Releases (by Release)](https://img.shields.io/github/downloads/OllisGit/OctoPrint-PrintJobHistory/latest/total.svg)

The OctoPrint Plugin stores all print-job informations of a print in a database

#### Support my Efforts

This plugin, as well as my [other plugins](https://github.com/OllisGit/) were developed in my spare time.
If you like it, I would be thankful about a cup of coffee :) 

[![More coffee, more code](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=2BJP2XFEKNG9J&source=url)


## Planning Release #1
 
should include the following features:

### Basic attributes to be captures:
- [x] Print result (success, fail, cancel)
- [x] Start/End datetime -> duration
- [x] Username
- [x] Filename, filesize
- [x] Note
- [x] Image
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
- [x] Export all printjobs as CSV
- [ ] Filter history table
- [ ] Sort history table
- [ ] Capture image after print
- [ ] Link to timelaps

### Not included
- No report diagramms
- No adjustment settings (e.g ???)
- No fancy looking UI


## Planning Release #2, ... 
....to be done.... see Planning Board: https://github.com/OllisGit/OctoPrint-PrintJobHistory/projects/1

## Screenshots
![plugin-settings](screenshots/plugin-settings.png "Plugin-Settings")
![plugin-tab](screenshots/plugin-tab.png "Plugin-Tab")
![editPrintJob-dialog](screenshots/editPrintJob-dialog.png "EditPrintJob-Dialog")
![missingplugins-dialog](screenshots/missingPlugins-dialog.png "MissingPlugins-Dialog")


## Setup

Install via the bundled [Plugin Manager](http://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/OllisGit/OctoPrint-PrintJobHistory/releases/latest/download/master.zip

## Roadmap

see [Planning-Board](https://github.com/OllisGit/OctoPrint-PrintJobHistory/projects/1)

## Versions

see [Release-Overview](https://github.com/OllisGit/OctoPrint-PrintJobHistory/releases/)


