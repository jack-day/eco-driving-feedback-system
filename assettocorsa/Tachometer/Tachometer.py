import sys
import ac
import acsys

rpmLabel = 0

def acMain(ac_version):
   global rpmLabel
   appWindow = ac.newApp("Tachometer")
   ac.setSize(appWindow, 200, 100)

   rpmLabel = ac.addLabel(appWindow, "RPM: 0")
   ac.setFontSize(rpmLabel, 24)
   ac.setPosition(rpmLabel, 50, 50)

   return "Tachometer"

def acUpdate(deltaT):
   global rpmLabel
   rpm = round(ac.getCarState(0, acsys.CS.RPM))
   if rpmLabel > 0:
      ac.setText(rpmLabel, "RPM: {}".format(rpm))

def acShutdown():
	pass