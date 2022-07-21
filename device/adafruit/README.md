# Adafruit

This directory contains the required setup files to install and configure the
[Adafruit 128x64 OLED Bonnet for Raspberry Pi](https://www.adafruit.com/product/3531).

More information on the required setup steps and dependencies can be found [here](https://learn.adafruit.com/adafruit-128x64-oled-bonnet-for-raspberry-pi/usage).

`setup.sh` is a bash script that will perform all the needed setup steps. This 
has been separated from the device's main application setup as the installation
will fail when not installed on an RPi, thus for CI and testing, this setup 
should not be performed.
