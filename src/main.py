#!python3

from multiprocessing import Process, Queue

from Overlay import iRacingOverlay
from iRacingManager import iRacingManager

import json
import os


if __name__ == '__main__':
    #load any existing settings currently stored in the settings.json file
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}

    try:
        # Create a queue for inter-process communication
        queue = Queue()

        # Initialize managers
        iRManager = iRacingManager(queue, settings)
        overlay = iRacingOverlay(queue, settings)

        # Setup the iRacingManager in a separate process
        iRManagerThread = Process(target=iRManager.run)

        # Start the separate processes
        print("Starting iRacingManager thread.")
        iRManagerThread.start()
        print("Starting iRacingOverlay.")
        overlay.run()

        iRManagerThread.join()
        print("Exiting main thread.")
    except KeyboardInterrupt:
        pass
