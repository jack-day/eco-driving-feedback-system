"""
Gear Shift Indicator (GSI)

Calculates the most economical upshift point based on OBD data and displays
shifting lights on the Raspberry Pis display.
"""
import math
from os import path
from PIL import ImageFont
from utils import kmhToMps


# Gear Shift Indicator
# -------------------------------------------------------------------------
class GSI:
    RMC_COEFF = 1.08
    """Rotating mass correction coefficient"""
    ROLL_RES_COEFF = 0.01
    """Coefficient of rolling resistance"""
    GRAVITY = 9.81
    AIR_DENSITY = 1.202
    PSGR_WEIGHT = 75
    """Passenger weight (kg)"""
    ADD_RPM_COEFF = 400
    """Permitted additional engine speed coefficient"""

    def __init__(self, settings, journey):
        """Gear Shift Indicator"""
        self.settings = settings
        self.journey = journey
        self.half = 4
        """Number of indication dots in each side of the GSI"""
        self.total = self.half * 2
        """Total number of indication dots"""
        self.dotDispCnt = 0
        """Number of dots being displayed on one side of the GSI"""
        self.dotBounds = []
        """Boundary coordinates for each dot to be used in drawing"""
        self.minRPMDiff = 500
        """The minimum RPM diff between the current and optimal upshift RPM for
        the first indication dot to be displayed"""
        self.dotRPMDiff = self.minRPMDiff / (
            self.half - 1  # (half - 1) because all dots of a half would be
        )                  # indicating an upshift and thus an rpm diff of <=0
        """RPM diff increment for each indication dot"""
        self.throttleActive = False
        """Whether the throttle is being pressed"""

        self.initDotBounds()
        self.initUpshiftNotice()

    @property
    def isIndicating(self):
        if self.throttleActive:
            return self.dotDispCnt == self.half

    def initDotBounds(self):
        """Initialise boundary coordinates for each indication dot"""
        x0 = 4
        y0 = 29
        diam = 6
        gap = 3

        for _ in range(self.total):
            self.dotBounds.append([(x0, y0), (x0 + diam, y0 + diam)])
            x0 += diam + gap

    def initUpshiftNotice(self):
        """Initialise upshift notice message"""
        gap = 6
        rightmostDot = self.dotBounds[-1]
        rectX0 = 4
        rectY0 = rightmostDot[1][1] + gap
        rectX1 = rightmostDot[1][0]
        rectY1 = 64 - gap
        textX = rectX0 + round((rectX1 - rectX0) / 2)
        textY = rectY0 + round((rectY1 - rectY0) / 2)
        fontFile = path.join(path.dirname(path.dirname(__file__)),
            'assets/fonts/Roboto/Roboto-Regular.ttf')

        self.upshiftNotice = {
            'rectangle': [(rectX0, rectY0), (rectX1, rectY1)],
            'text': (textX, textY),
            'font': ImageFont.truetype(fontFile)
        }

    # Helpers
    # -------------------------------------------------------------------------
    def getCurrentGear(self, rpm, speed):
        """Returns the current gear position"""
        if speed < 1:  # Driving in reverse will still produce positive speed
            return 1

        gearRatio = rpm / speed
        currGear = 0
        currGearDiff = math.inf

        # Find closest gear ratio and select as current gear
        for gearIndex in range(self.settings['vehicleSpecs']['gearCount'] + 1):
            gear = self.settings['vehicleSpecs']['gears'][gearIndex]
            gearDiff = abs(gearRatio - gear)

            if gearDiff < currGearDiff:
                currGear = gearIndex
                currGearDiff = gearDiff

        return currGear

    def getVehicleMass(self):
        """Calculates vehicle mass, accounting for journey variables"""
        personsWeight = self.PSGR_WEIGHT * (self.journey['passengers'] + 1)

        mass = (self.settings['vehicleSpecs']['curbWeight'] + personsWeight +
            self.journey['cargo'])

        if self.journey['roofAtt']:
            mass += self.journey['roofAtt']['weight']

        return mass

    # Tractive effort calculations
    # -------------------------------------------------------------------------
    def calcDrag(self, frontalArea, dragCoeff, speed):
        """Calculates aerodynamic drag"""
        return (0.5 * self.AIR_DENSITY * dragCoeff * frontalArea *
            math.pow(speed, 2))

    def calcTracEff(self, obdData, prevOBDData, grade):
        """Calculates tractive effort"""
        mass = self.getVehicleMass()
        vel = kmhToMps(obdData['speed'])

        timeDiff = obdData['time'] - prevOBDData['time']
        if timeDiff == 0:
            acceleration = 0
        else:
            acceleration = (vel - kmhToMps(prevOBDData['speed'])) / timeDiff
            acceleration = 0 if acceleration < 0 else acceleration

        rollRes = self.ROLL_RES_COEFF * mass * self.GRAVITY * math.cos(grade)
        drag = self.calcDrag(
            self.settings['vehicleSpecs']['frontalArea'],
            self.settings['vehicleSpecs']['dragCoeff'],
            vel
        )

        if self.journey['roofAtt']:
            drag += self.calcDrag(
                self.journey['roofAtt']['frontalArea'],
                self.journey['roofAtt']['dragCoeff'],
                vel
            )

        gradeRes = mass * self.GRAVITY * math.sin(grade)

        return self.RMC_COEFF * mass * acceleration + rollRes + drag + gradeRes

    # Updating status
    # -------------------------------------------------------------------------
    def calcUpshiftRPM(self, obdData, prevOBDData):
        """Calculates the optimal upshift RPM"""
        altDiff = obdData['alt'] - prevOBDData['alt']
        avgSpeed = kmhToMps((obdData['speed'] + prevOBDData['speed']) / 2)
        distance = avgSpeed * (obdData['time'] - prevOBDData['time'])
        gradient = math.atan(altDiff / distance)
        gradientDeg = math.degrees(gradient)

        if gradientDeg <= 3:
            return 2000
        elif gradientDeg > 3:
            tracEff = self.calcTracEff(obdData, prevOBDData, gradient)
            tracEffFlat = self.calcTracEff(obdData, prevOBDData, 0)
            permittedAddRPM = self.ADD_RPM_COEFF * (tracEff / tracEffFlat - 1)

            if permittedAddRPM > 2000:
                permittedAddRPM = 2000

            return 2000 + permittedAddRPM

    def update(self, obdData, prevOBDData):
        """Update the GSI's status"""
        self.throttleActive = obdData['throttle'] >= 1
        gear = self.getCurrentGear(obdData['rpm'], obdData['speed'])

        if (
            obdData['speed'] < 1 or
            gear == 0 or
            gear == self.settings['vehicleSpecs']['gearCount']
        ):
            self.dotDispCnt = 0
            return

        upshiftRPM = self.calcUpshiftRPM(obdData, prevOBDData)
        rpmDiff = upshiftRPM - obdData['rpm']

        # No Dots
        if rpmDiff > self.minRPMDiff:
            self.dotDispCnt = 0
            return

        # All Dots
        if rpmDiff <= 0:
            self.dotDispCnt = self.half
            return

        # 1 Dot to (self.half - 1) dots
        for i in range(1, self.half):
            dotMaxDiff = round(self.minRPMDiff - (self.dotRPMDiff * (i - 1)))
            dotMinDiff = round(dotMaxDiff - self.dotRPMDiff)

            if dotMaxDiff >= rpmDiff and rpmDiff > dotMinDiff:
                self.dotDispCnt = i
                return

    # Draw
    # -------------------------------------------------------------------------
    def draw(self, imgDraw):
        """Draws the GSI on the display using the given img drawing object"""
        for i in range(self.half):
            if (i + 1) <= self.dotDispCnt:
                imgDraw.ellipse(self.dotBounds[i], fill=1)

        for i in range(self.total - 1, self.half - 1, -1):
            if i >= (self.total - self.dotDispCnt):
                imgDraw.ellipse(self.dotBounds[i], fill=1)

        if self.dotDispCnt == self.half:
            imgDraw.rectangle(self.upshiftNotice['rectangle'], fill=1)
            imgDraw.text(self.upshiftNotice['text'], 'Shift Up',
                fill=0, anchor='mm', font=self.upshiftNotice['font'])
