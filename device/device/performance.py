"""
Eco Driving Performance

Calculates and diplays the drivers eco driving performance.

.. image:: ../img/accumulated_feedback_flowchart.png
"""
from functools import lru_cache
from datetime import datetime, timezone
import api
import db
from utils import kmhToMps


# Mean
# -------------------------------------------------------------------------
class Mean:
    """Mean that can be updated by new values"""

    def __init__(self, value=None, count=0):
        self.value = value
        self.count = count

    def increment(self, newVal):
        """Adds a new value to the mean, recalculating it incrementally"""
        if self.value is not None:
            self.value += (newVal - self.value) / float(self.count + 1)
        else:
            self.value = newVal

        self.count += 1

    def combine(self, mean):
        """Combines the current mean with another mean"""
        if mean.value is None or self.count + mean.count == 0:
            return

        if self.value is None:
            self.value = mean.value
            self.count = mean.count
            return

        n1x1 = self.value * self.count
        n2x2 = mean.value * mean.count
        self.value = (n1x1 + n2x2) / (self.count + mean.count)
        self.count += mean.count

    def __str__(self):
        return f'(Mean: {self.value}, Count: {self.count})'


# Journey
# -------------------------------------------------------------------------
class JourneyPerformance:
    """Driving data performance factors for a journey"""

    ACC_MIN_SPD_DIFF = 1
    """Minimum speed difference in kmh for differences in speed between
    driving data to be classified as acceleration or deceleration"""

    IDLE_MIN_WAIT = 5
    """Minimum number of seconds at zero speed until the time period is
    classified as idling"""

    def __init__(self, journeyID):
        self.journeyID = journeyID
        self.drivingDataCount = 0
        """Number of driving data entries"""
        self.startTime = 0
        """Journey start timestamp"""
        self.endTime = 0
        """Journey end timestamp"""
        self.travelTime = 0
        """Total journey travel time in seconds"""
        self.idleTime = 0
        """Total seconds of idles longer than 5 seconds"""
        self.distance = 0
        """Journey distance in kilometers"""

        self.drivAccSmoothness = Mean()
        self.startAccSmoothness = Mean()
        self.decSmoothness = Mean()
        self.gsiAdh = Mean()
        self.spdLimAdh = Mean()
        self.motorwaySpd = Mean()
        self.idleDur = Mean()
        self.calcPerformance()

    # Updating values
    # --------------------------------------------------------------------
    def updAccSmoothness(self, initialDrivingData, finalDrivingData):
        """Updates the driving and starting acceleration smoothness means"""
        speedDiff = finalDrivingData['speed'] - initialDrivingData['speed']

        if speedDiff < self.ACC_MIN_SPD_DIFF:
            return

        timeDelta = finalDrivingData['time'] - initialDrivingData['time']
        acceleration = kmhToMps(speedDiff) / timeDelta.total_seconds()

        if initialDrivingData['speed'] < 1:
            self.startAccSmoothness.increment(acceleration)
        else:
            self.drivAccSmoothness.increment(acceleration)

    def updDecSmoothness(self, initialDrivingData, finalDrivingData):
        """Updates the deceleration smoothness mean"""
        speedDiff = finalDrivingData['speed'] - initialDrivingData['speed']

        if speedDiff > -self.ACC_MIN_SPD_DIFF:
            return

        timeDelta = finalDrivingData['time'] - initialDrivingData['time']
        deceleration = kmhToMps(speedDiff) / timeDelta.total_seconds()
        self.decSmoothness.increment(deceleration)

    def updGSIAdh(self, speed, gsiIsIndicating):
        """Updates the GSI adherence mean"""
        if gsiIsIndicating is None:
            return

        if speed >= 1:
            if gsiIsIndicating:
                self.gsiAdh.increment(0)
            else:
                self.gsiAdh.increment(100)

    def updSpdLimAdh(self, speed, speedLimit):
        """Updates the speed limit adherence mean"""
        if speedLimit is None or speed < 1:
            return

        if speed <= speedLimit:
            self.spdLimAdh.increment(100)
        else:
            self.spdLimAdh.increment(0)

    def updMotorwaySpd(self, speed, speedLimit):
        """Updates the motorway speed mean"""
        if speedLimit == 113:
            self.motorwaySpd.increment(speed)

    def updIdle(self, idleStart, idleStop):
        """Updates the idle duration mean and total idle time"""
        idleTime = (idleStop - idleStart).total_seconds()
        if idleTime >= self.IDLE_MIN_WAIT:
            self.idleTime += idleTime
            self.idleDur.increment(idleTime)

    def updDistance(self, initialDrivingData, finalDrivingData):
        """Updates the journey distance"""
        speedDiff = finalDrivingData['speed'] - initialDrivingData['speed']
        timeDelta = finalDrivingData['time'] - initialDrivingData['time']
        timeDiff = timeDelta.total_seconds()

        if timeDiff > 0:
            acceleration = kmhToMps(speedDiff) / timeDiff
            accDistance = 0.5 * acceleration * (timeDiff ** 2)
            distance = kmhToMps(initialDrivingData['speed']) * timeDiff
            self.distance += (distance + accDistance) / 1000

    # Calculate Performance
    # --------------------------------------------------------------------
    def calcPerformance(self):
        """Calculates performance statistics from journey driving data"""
        drivingData = db.getJourneyDrivingData(self.journeyID)
        if len(drivingData) == 0:
            return

        self.drivingDataCount = 0
        self.startTime = drivingData[0]['time']
        self.endTime = drivingData[-1]['time']
        self.travelTime = (self.endTime - self.startTime).total_seconds()
        if self.travelTime == 0:
            return

        prevData = None
        idleStart = None

        for data in drivingData:
            if prevData:
                self.updDistance(prevData, data)
                self.updAccSmoothness(prevData, data)
                self.updDecSmoothness(prevData, data)

                if idleStart:
                    if data['engineOn'] is False:
                        self.updIdle(idleStart, data['time'])
                        idleStart = None
                    elif data['speed'] >= 1:
                        self.updIdle(idleStart, prevData['time'])
                        idleStart = None

            self.updGSIAdh(data['speed'], data['gsiIndicating'])
            self.updSpdLimAdh(data['speed'], data['spdLim'])
            self.updMotorwaySpd(data['speed'], data['spdLim'])

            if idleStart is None and data['speed'] < 1 and data['engineOn']:
                idleStart = data['time']

            prevData = data
            self.drivingDataCount += 1

        # Check for idling at end of journey
        if idleStart:
            self.updIdle(idleStart, prevData['time'])

    # API
    # --------------------------------------------------------------------
    def updateAPI(self):
        """Update API journey performance stats"""
        if self.drivingDataCount < 2:  
            return  # Prevent uploading stats with insufficient driving data

        apiID = db.getJourneyApiID(self.journeyID)
        data = {
            'start': self.startTime.isoformat(),
            'end': self.endTime.isoformat(),
            'distance': self.distance,
            'idleSecs': round(self.idleTime),
        }

        if self.gsiAdh.value is not None:
            data['gsiAdh'] = self.gsiAdh.value

        if apiID:
            api.updateJourney(apiID, data)
        else:
            apiID = api.createJourney(data)
            db.updateJourneyApiID(self.journeyID, apiID)


# Accumulated Feedback
# -------------------------------------------------------------------------
class AccumulatedFeedback:
    """Accumulated feedback calculated from the drivers eco-driving performance
    over the last 30 days"""

    def __init__(self, currentJourney={'id': 0}):
        self.journeys = []
        self.drivingDataCount = 0
        self.ecoDrivingScore = None
        self.plantImg = None

        self.drivAccSmoothness = Mean()
        self.startAccSmoothness = Mean()
        self.decSmoothness = Mean()
        self.gsiAdh = Mean()
        self.spdLimAdh = Mean()
        self.motorwaySpd = Mean()
        self.idleDur = Mean()
        self.jrnyIdlePct = Mean()
        self.jrnyDist = Mean()

        self.drivAccSmoothnessScore = None
        self.startAccSmoothnessScore = None
        self.decSmoothnessScore = None
        self.gsiAdhScore = None
        self.spdLimAdhScore = None
        self.motorwaySpdScore = None
        self.idleDurScore = None
        self.jrnyIdlePctScore = None
        self.jrnyDistScore = None

        # Calculate means per journey so memory isn't filled by all
        # of the time-series driving data from the past 30 days
        for journeyID in db.getJourneyIDsWithinLastNdays(30):
            journeyPerf = JourneyPerformance(journeyID)
            self.addJourney(journeyPerf)
            if journeyPerf.journeyID == currentJourney['id']:
                journeyPerf.updateAPI()

        self.updFactorScores()
        self.updEcoDrivingScore()
        self.updateAPI()

    def addJourney(self, journey):
        """Adds a journey to the accumulated feedback and updates the means"""
        self.journeys.append(journey)
        self.drivingDataCount += journey.drivingDataCount

        self.drivAccSmoothness.combine(journey.drivAccSmoothness)
        self.startAccSmoothness.combine(journey.startAccSmoothness)
        self.decSmoothness.combine(journey.decSmoothness)
        self.gsiAdh.combine(journey.gsiAdh)
        self.spdLimAdh.combine(journey.spdLimAdh)
        self.motorwaySpd.combine(journey.motorwaySpd)
        self.idleDur.combine(journey.idleDur)

        if journey.travelTime > 0:
            jrnyIdlePct = (journey.idleTime / journey.travelTime) * 100
            self.jrnyIdlePct.increment(jrnyIdlePct)
            self.jrnyDist.increment(journey.distance)

    # Factor Scores
    # --------------------------------------------------------------------
    @staticmethod
    @lru_cache(maxsize=8)  # 8 to cache all means that use linear scores
    def calcLinearScore(value, min, max, reverseScore=False):
        """
        Calculates a score from 0 to 100 with a linear distrubtion between a
        min and a max.

        Setting reverseScore to 'True' will for example switch 75/100 to 25/100
        """
        if value is None:
            return None

        score = ((value - min) / (max - min)) * 100

        if reverseScore is True:
            score = 100 - score

        if score < 0:
            return 0
        elif score > 100:
            return 100
        else:
            return round(score)

    def calcMotorwaySpdScore(self):
        """Calculates the score for the mean motorway speed"""
        # Score distribution: 75 mph = 0 | 70 mph = 75 | 60 mph = 100
        if self.motorwaySpd.value is None:
            return

        mph = self.motorwaySpd.value / 1.60934

        if mph == 70:
            return 75
        elif mph > 70:
            score = ((mph - 70) / (75 - 70)) * 75
            score = 75 - score  # Reverse score
        else:
            score = ((mph - 60) / (70 - 60)) * 25
            # Reverse Score and add 75 to get range of 75-100 instead of 0-25
            score = (25 - score) + 75

        if score < 0:
            return 0
        elif score > 100:
            return 100
        else:
            return round(score)

    def updFactorScores(self):
        """Updates the scores for all eco-driving factors"""
        for factorName, bounds in {
            'drivAccSmoothness': {
                'min': 0.2, 'max': 1.4705, 'reverseScore': True,
            },
            'startAccSmoothness': {
                'min': 0.2, 'max': 2.598, 'reverseScore': True,
            },
            'decSmoothness': {
                'min': -6.72, 'max': -0.2,
            },
            'gsiAdh': {
                'min': 0, 'max': 100,
            },
            'spdLimAdh': {
                'min': 0, 'max': 100,
            },
            'idleDur': {
                'min': 5, 'max': 60, 'reverseScore': True,
            },
            'jrnyIdlePct': {
                'min': 0, 'max': 100, 'reverseScore': True,
            },
            'jrnyDist': {
                'min': 2, 'max': 5,
            }
        }.items():
            value = getattr(self, factorName).value
            if value is not None:
                setattr(self, factorName + 'Score', self.calcLinearScore(
                    value,
                    bounds['min'], bounds['max'],
                    bounds.get('reverseScore', False)
                ))

        self.motorwaySpdScore = self.calcMotorwaySpdScore()

    # Overall eco-driving score
    # --------------------------------------------------------------------
    def updEcoDrivingScore(self):
        """Updates the overall eco-driving score"""
        weightedSum = 0
        totalWeights = 0

        for (score, weight) in [
            (self.drivAccSmoothnessScore, 4),
            (self.decSmoothnessScore, 4),
            (self.gsiAdhScore, 3),
            (self.spdLimAdhScore, 3),
            (self.motorwaySpdScore, 3),
            (self.idleDurScore, 2),
            (self.jrnyIdlePctScore, 2),
            (self.jrnyDistScore, 1),
            (self.startAccSmoothnessScore, 1)
        ]:
            if score is not None:
                weightedSum += score * weight
                totalWeights += weight

        if totalWeights > 0:
            self.ecoDrivingScore = round(weightedSum / totalWeights)
        else:
            self.ecoDrivingScore = 100

    # Draw to display
    # --------------------------------------------------------------------
    def draw(self, display):
        """Draws a plant at different levels of growth as an interpretive
        schematic to represent the drivers eco-driving score"""
        if 0 <= self.ecoDrivingScore <= 20:
            img = display.imgs['plant0to20']
        elif 20 < self.ecoDrivingScore <= 40:
            img = display.imgs['plant20to40']
        elif 40 < self.ecoDrivingScore <= 60:
            img = display.imgs['plant40to60']
        elif 60 < self.ecoDrivingScore <= 80:
            img = display.imgs['plant60to80']
        elif 80 < self.ecoDrivingScore <= 100:
            img = display.imgs['plant80to100']

        display.imgDraw.bitmap((82, 4), img, fill=1)

    # API
    # --------------------------------------------------------------------
    def updateAPI(self):
        """Update API with calculated scores"""
        if self.drivingDataCount < 2:
            return  # Prevent uploading scores with insufficient driving data

        scores = {
            'calculatedAt': datetime.now(timezone.utc).isoformat(),
            'ecoDriving': self.ecoDrivingScore
        }

        for name, score in {
            'drivAccSmoothness': self.drivAccSmoothnessScore,
            'startAccSmoothness': self.startAccSmoothnessScore,
            'decSmoothness': self.decSmoothnessScore,
            'gsiAdh': self.gsiAdhScore,
            'speedLimitAdh': self.spdLimAdhScore,
            'motorwaySpeed': self.motorwaySpdScore,
            'idleDuration': self.idleDurScore,
            'journeyIdlePct': self.jrnyIdlePctScore,
            'journeyDistance': self.jrnyDistScore
        }.items():
            if score is not None:
                scores[name] = score

        api.addScores(scores)
