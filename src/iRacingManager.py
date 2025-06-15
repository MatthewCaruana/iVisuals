import irsdk
import time
import json


# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1

class iRacingManager:

    def __init__(self, queue, settings):
        # initializing ir and state
        self.ir = irsdk.IRSDK()
        self.state = State()

        self.queue = queue
        self.tick = 0

    
    # here we check if we are connected to iracing
    # so we can retrieve some data
    def check_iracing(self):
        if self.state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.state.ir_connected = False
            # don't forget to reset your State variables
            self.state.last_car_setup_tick = -1
            # we are shutting down ir library (clearing all internal variables)
            self.ir.shutdown()
            print('irsdk disconnected')
        elif not self.state.ir_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            self.state.ir_connected = True
            print('irsdk connected')

    def updateSpeed(self):
        self.currentSpeed = int(self.ir['Speed'] * 3.6)

    def updateThrottle(self):
        self.currentThrottle = int(self.ir['Throttle'] * 100)

    def updateBrake(self):
        self.currentBrake = int(self.ir['Brake'] * 100)

    def updateClutch(self):
        self.currentClutch = int(100 - (self.ir['Clutch'] * 100))

    def updateGear(self):
        if self.ir['Gear'] == 0:
            self.currentGear = 'N'
        elif self.ir['Gear'] < 0:
            self.currentGear = 'R'
        else:
            self.currentGear = str(self.ir['Gear'])

    def updateStandings(self):
        if (self.ir['DriverInfo']):
            driverInfo = self.ir['DriverInfo']
        if (self.ir['SessionInfo']):
            sessionInfo = self.ir['SessionInfo']['Sessions'][0]
        if (sessionInfo['SessionType'] == 'Qualify' and self.ir['QualifyResultsInfo']):
            qualifyResultsInfo = self.ir['QualifyResultsInfo']

        self.standingsInfo = {}
        self.standingsInfo['Standings'] = []
        self.standingsInfo['SessionType'] = sessionInfo['SessionType']

        for i in range(len(sessionInfo['ResultsPositions'])):
            positionInfo = sessionInfo['ResultsPositions'][i]

            driverInCurrentPosition = _get_current_driver_info(driverInfo, positionInfo['CarIdx'])

            positionInfo['DriverName'] = driverInCurrentPosition['TeamName']
            positionInfo['CarNumber'] = driverInCurrentPosition['CarNumber']
            positionInfo['CarScreenName'] = driverInCurrentPosition['CarScreenName']
            positionInfo['IRating'] = driverInCurrentPosition['IRating']
            positionInfo['LicLevel'] = driverInCurrentPosition['LicLevel']
            positionInfo['LicSubLevel'] = driverInCurrentPosition['LicSubLevel']
            positionInfo['CurDriverIncidentCount'] = driverInCurrentPosition['CurDriverIncidentCount']

            self.standingsInfo['Standings'].append(positionInfo)

        


    def loop(self):
        self.ir.freeze_var_buffer_latest()

        self.updateSpeed()
        self.updateThrottle()
        self.updateBrake()
        self.updateClutch()
        self.updateGear()
        if(self.tick % 60 == 0):
            self.updateStandings()
        else:
            self.tick += 1
            self.standingsInfo = {}

    def constructMessage(self):
        message={
            'speed': self.currentSpeed,
            'throttle': self.currentThrottle,
            'brake': self.currentBrake,
            'clutch': self.currentClutch,
            'gear': self.currentGear,
            'standings': self.standingsInfo
            #'best_laps': self.ir['CarIdxBestLapTime']
        } 
            

        return str(message)

    
    def run(self):
        try:
            # infinite loop
            while True:
                # check if we are connected to iracing
                self.check_iracing()

                if self.state.ir_connected:
                    self.loop()

                    message = self.constructMessage()
                    self.queue.put(message)
                
                # maximum you can use is 1/60
                time.sleep(1/30)
        except KeyboardInterrupt: 
            self.ir.shutdown()
            print("Exiting iRacingManager.")
            pass

def _get_current_driver_info(driverInfo, carIdx):
    for driver in driverInfo['Drivers']:
        if driver['CarIdx'] == carIdx:
            return driver
    return None