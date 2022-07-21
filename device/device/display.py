"""
Display Interaction

Provides interaction with the Raspberry Pis display HAT.
"""
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw
import adafruit_ssd1306
from threading import Thread
from pathlib import Path
import api


def loadImg(filename):
    """ Loads an image stored in /assets/img/ returning the image object"""
    filepath = Path(
        Path(__file__).resolve().parent.parent,
        'assets/img/',
        filename
    )
    img = Image.open(filepath).convert('1')
    img.load()
    return img


class Display:
    def __init__(self, gsi, accFdbck):
        """Device display"""
        i2c = busio.I2C(board.SCL, board.SDA)
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        self.on = True
        self.activeUI = 'eco-driving'
        self.gsi = gsi
        self.accumulatedFeedback = accFdbck

        self.initButtons()
        self.initDisplay()
        self.loadImgs()

        thread = Thread(target=self.draw)
        thread.start()

    def initButtons(self):
        """
        Input pin/buttons setup

        Adapted from code found here:
        https://learn.adafruit.com/adafruit-128x64-oled-bonnet-for-raspberry-pi/usage#library-usage-3024370-20
        """

        buttonA = DigitalInOut(board.D5)
        buttonA.direction = Direction.INPUT
        buttonA.pull = Pull.UP

        buttonB = DigitalInOut(board.D6)
        buttonB.direction = Direction.INPUT
        buttonB.pull = Pull.UP

        self.buttons = {
            "A": buttonA,
            "B": buttonB
        }

    def initDisplay(self):
        """
        Display Initialisation

        Adapted from code found here:
        https://learn.adafruit.com/adafruit-128x64-oled-bonnet-for-raspberry-pi/usage#library-usage-3024370-20
        """

        # Clear display.
        self.display.fill(0)
        self.display.show()

        # Create blank image for drawing
        self.width = self.display.width
        self.height = self.display.height
        # Mode '1' for 1-bit color
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image
        self.imgDraw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image
        self.imgDraw.rectangle((0, 0, self.width, self.height),
            outline=0, fill=0)

    def loadImgs(self):
        """Pre-loads images so they are not loaded during drawing"""
        self.imgs = {
            'wifiOff': loadImg('wifi_off.bmp'),
            'plant0to20': loadImg('plant/0_to_20.bmp'),
            'plant20to40': loadImg('plant/20_to_40.bmp'),
            'plant40to60': loadImg('plant/40_to_60.bmp'),
            'plant60to80': loadImg('plant/60_to_80.bmp'),
            'plant80to100': loadImg('plant/80_to_100.bmp'),
        }

    # Drawing
    # -------------------------------------------------------------------------
    def clear(self):
        """Clears the entire display"""
        self.display.fill(0)
        self.display.show()

    def stop(self):
        self.on = False

    def draw(self):
        """Draw loop for the entire display"""
        while self.on:
            # Clear previously drawn objects
            self.imgDraw.rectangle((0, 0, self.width, self.height),
                outline=0, fill=0)

            if self.activeUI == 'eco-driving':
                self.gsi.draw(self.imgDraw)
                self.accumulatedFeedback.draw(self)

                if not api.lastRequestSuccessful:
                    self.imgDraw.bitmap((4, 4), self.imgs['wifiOff'], fill=1)

            self.display.image(self.image)
            self.display.show()

        self.clear()
