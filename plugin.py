# TP-Link Tapo Plugin
#
# Author: 593304
#
"""
<plugin key="TapoPlugin" name="TP-Link Tapo Plugin" author="593304" version="0.2" externallink="">
    <description>
        <h2>TP-Link Tapo Plugin</h2><br/>
        <p>The plugin will connect to a Tapo device with the given IP address, username(e-mail address) and password.</p>
        <p>Before using this plugin, you have to install the<a href="https://pypi.org/project/PyP100/" style="margin-left: 5px">PyP100 module</a></p>
        <br />
        <br />
    </description>
    <params>
        <param field="Mode1" label="Username" width="250px" required="true"/>
        <param field="Password" label="Password" width="250px" required="true" password="true"/>
        <param field="Address" label="IP address" width="250px" required="true"/>
        <param field="Mode2" label="Debug" width="50px">
            <options>
                <option label="on" value="on"/>
                <option label="Off" value="off" default="off"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
from PyP100 import PyP100
import json


# Simple heartbeat with a 10 secs interval
class Heartbeat():
    def __init__(self):
        self.callback = None
        self.interval = 1

    def setHeartbeat(self, callback):
        Domoticz.Heartbeat(self.interval)
        Domoticz.Log("Heartbeat interval is " + str(self.interval) + ".")
        self.callback = callback
            
    def beatHeartbeat(self):
        self.callback()


class TapoPlugin:
    def __init__(self):
        self.unit = None
        self.p100 = None
        self.lastState = None
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        
        # Setting up debug mode
        if (Parameters["Mode2"] != "off"):
            Domoticz.Debugging(1)
            Domoticz.Debug("Debug mode enabled")

        # Setting up heartbeat
        self.heartbeat = Heartbeat()
        self.heartbeat.setHeartbeat(self.update)

        # Creating PyP100 object
        ip = Parameters["Address"]
        email = Parameters["Mode1"]
        password = Parameters["Password"]
        self.p100 = PyP100.P100(ip, email, password)
        Domoticz.Debug("Tapo object created with IP: " + ip)

        # Getting last state to get device type
        self.update(False)

        # Creating device
        self.unit = 1
        if self.unit not in Devices:
            typeName = "Selector Switch"
            switchType = 0
            # ToDo: Need a real Tapo bulb to create the dimmer/color switch device for Domoticz
            #if "bulb" in self.lastState["type"].lower():
            #    typeName = ...
            #    switchType = ...
            
            Domoticz.Device(
                Name = self.lastState["type"],
                Unit = self.unit,
                TypeName = typeName, 
                Switchtype = switchType,
                Image = 9,
                Options = {}).Create()

        self.update()

        DumpConfigToLog()

        return

    def onStop(self):
        Domoticz.Log("onStop called")
        return

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called; connection: %s, status: %s, description: %s" % (str(Connection), str(Status), str(Description)))
        return

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called; connection: %s, data: %s" % (str(Connection), str(Data)))
        return

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Unit != self.unit:
            Domoticz.Error("Unknown device with unit: " + str(Unit))
            return

        commandValue = 1 if Command == "On" else 0
        if self.lastState["device_on"] == commandValue:
            Domoticz.Log("Command and last state is the same, nothing to do")
            return
        
        self.p100.handshake()
        self.p100.login()
        if Command == "On":
            self.p100.turnOn()
        else:
            self.p100.turnOff()
        self.update()

        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)
        return

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        return

    def onHeartbeat(self):
        self.heartbeat.beatHeartbeat()
        return

    def update(self, updateDomoticz = True):
        self.p100.handshake()
        self.p100.login()
        lastState = json.loads(self.p100.getDeviceInfo())
        if lastState["error_code"] != 0:
            self.lastState = None
            Domoticz.Error("Cannot get last state from devicem error code: " + str(lastState["error_code"]))
        else:
            self.lastState = lastState["result"]
            Domoticz.Debug(json.dumps(self.lastState))

        # Update device
        if self.unit not in Devices or not updateDomoticz:
            return
        # ToDo: Need a real Tapo bulb to properly update Domoticz device with not just the power state
        powerState = self.lastState["device_on"]
        powerStateValue = 1 if powerState else 0
        powerStateStr = "On" if powerState else "Off"
        if (Devices[self.unit].nValue != powerStateValue) or (Devices[self.unit].sValue != powerStateStr):
            Domoticz.Debug("Updating %s (%d, %s)" % (Devices[self.unit].Name, powerStateValue, powerStateStr))
            Devices[self.unit].Update(nValue = powerStateValue, sValue = powerStateStr)

        return

global _plugin
_plugin = TapoPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
