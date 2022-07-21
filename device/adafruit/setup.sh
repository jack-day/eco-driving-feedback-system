#!/bin/bash

# Install Adafruit RPi OLED Bonnet Dependencies
sudo apt-get add python3-pil
sudo pip3 install --upgrade setuptools  		   # These must be installed using pip
sudo pip3 install --upgrade adafruit-python-shell  # as they are required by raspi-blinka.py
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
sudo pip3 install adafruit-circuitpython-ssd1306

# I2C must also be enabled, see here: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
