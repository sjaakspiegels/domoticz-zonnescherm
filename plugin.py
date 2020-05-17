# Domoticz Zonnescherm
# Works with domoticz and MQTT
# Author: Sjaak Spiegels
#
"""
<plugin key="Zonnescherm" name="Zonnescherm" version="1.0.0" author="Sjaak" wikilink="" externallink="">
    <params>
        <param field="Address" label="MQTT Server" width="200px" required="true" default=""/>
        <param field="Port" label="MQTT Port" width="150px" required="true" default="1883"/>
        <param field="Username" label="MQTT Username" width="150px" required="true" default=""/>
        <param field="Password" label="MQTT Password" width="150px" required="true" default="" password="true"/>
        <param field="Mode1" label="MQTT State Topic" width="150px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal" />
            </options>
      </param>
  </params>
  </plugin>
"""

import Domoticz
import http.client
import base64
import json
import paho.mqtt.client as mqtt

class BasePlugin:
 
    mqttClient = None
    mqttserveraddress = "localhost"
    mqttserverport = 1883
    mqttusername = ""
    mqttpassword = ""
    mqttstatetopic = ""

    def __init__(self):
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)        
            Domoticz.Log("Debugging ON")

        if (len(Devices) == 0):
            Options = {"LevelActions": "||","LevelNames": "|Omhoog|Stop|Omlaag","LevelOffHidden": "true","SelectorStyle": "0"}
            Domoticz.Device(Name="Zonnescherm", Unit=1, TypeName="Selector Switch", Switchtype=18, Options=Options).Create()
            Domoticz.Log("Devices created.")

        self.mqttserveraddress = Parameters["Address"].strip()
        self.mqttserverport = Parameters["Port"].strip()
        self.mqttusername = Parameters["Username"].strip()
        self.mqttpassword = Parameters["Password"].strip()
        self.mqttstatetopic = Parameters["Mode1"].strip()


        self.mqttClient = mqtt.Client()
        self.mqttClient.on_connect = onMQTTConnect
        self.mqttClient.on_subscribe = onMQTTSubscribe
        self.mqttClient.on_message = onMQTTmessage
        self.mqttClient.username_pw_set(username=self.mqttusername, password=self.mqttpassword)
        self.mqttClient.connect(self.mqttserveraddress, int(self.mqttserverport), 60)        
        self.mqttClient.loop_start()

    def onStop(self):
        Domoticz.Debug("onStop called")
        self.mqttClient.unsubscribe(self.mqttstatetopic)
        self.mqttClient.disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMQTTConnect(self, client, userdata, flags, rc):
        Domoticz.Debug("onMQTTConnect called")
        Domoticz.Debug("Connected to " + self.mqttserveraddress + " with result code {}".format(rc))
        self.mqttClient.subscribe("shellies/" + self.mqttstatetopic + "/roller/0",1)

    def onMQTTSubscribe(self, client, userdata, mid, granted_qos):
        Domoticz.Debug("onMQTTSubscribe called")

    def onMQTTmessage(self, client, userdata, message):
        Domoticz.Debug("message topic=" + message.topic)
        payload = str(message.payload.decode("utf-8"))
        Domoticz.Debug("message received " + payload)

        if payload == "open":
            Domoticz.Debug("Scherm omhoog")
            UpdateDevice(Unit=99, nValue = 10, sValue= "10")
        elif payload == "stop":
            Domoticz.Debug("Scherm stop")
            UpdateDevice(Unit=99, nValue = 20, sValue= "20")
        elif payload == "close":
            Domoticz.Debug("Scherm omlaag")
            UpdateDevice(Unit=99, nValue = 30, sValue= "30")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Level == 10:
            Domoticz.Log("Scherm omhoog")
            self.mqttClient.publish("shellies/" + self.mqttstatetopic + "/roller/0/cmd", payload = "open", qos=1)
        elif Level == 20:
            Domoticz.Log("Scherm stop")
            self.mqttClient.publish("shellies/" + self.mqttstatetopic + "/roller/0/cmd", payload = "stop", qos=1)
        elif Level == 30:
            Domoticz.Log("Scherm omlaag")
            self.mqttClient.publish("shellies/" + self.mqttstatetopic + "/roller/0/cmd", payload = "close", qos=1)


    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onDeviceModified(self, Unit):
        Domoticz.Debug("onDeviceModified called for Unit " + str(Unit))

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

global _plugin
_plugin = BasePlugin()

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

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

def onMQTTConnect(client, userdata, flags, rc):
    global _plugin
    _plugin.onMQTTConnect(client, userdata, flags, rc)

def onMQTTSubscribe(client, userdata, mid, granted_qos):
    global _plugin
    _plugin.onMQTTSubscribe(client, userdata, mid, granted_qos)

def onMQTTmessage(client, userdata, message):
    global _plugin
    _plugin.onMQTTmessage(client, userdata, message)

def UpdateDevice(Unit, nValue, sValue):
# Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return