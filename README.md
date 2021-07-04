# Domoticz-Tapo
TP-Link Tapo Plugin for Domoticz. This version only supports the creation of on/off switches. Tested with the Tapo P100 smart plug device.

## Prerequisites
### PyP100 library
This module is using [Toby Johnson's PyP100 library](https://pypi.org/project/PyP100/). Install this module by running this command: `pip3 install PyP100`.  
You will also need the IP address of your Tapo device(s).

## Installation
Connect to your Domoticz server via SSH and go to Domoticz's plugins directory. Clone this repository into the plugins directory:  
`git clone https://github.com/593304/Domoticz-Tapo.git`  
Then restart Domoticz service to add the Tapo plugin to the hardware list in Domoticz.
```
sudo /etc/init.d/domoticz.sh stop
sudo /etc/init.d/domoticz.sh start
```
OR  
```
sudo service domoticz.sh stop
sudo service domoticz.sh start
```

## Configuration
If Domoticz started, then go to the Hardware page on your Domoticz website and add a new one. You should find the TP-Link Tapo Plugin in the Type list. Select it and set the following values:
   - Username (the email address of your Tapo account)
   - Password (the password for your Tapo account)
   - IP address (the local IP address of your Tapo device)
   - Debug (you cn turn on or off debug messages)
