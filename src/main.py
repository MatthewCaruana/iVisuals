#!python3

from multiprocessing import Process, Queue

from Overlay import iRacingOverlay
from iRacingManager import iRacingManager

import json
import os


if __name__ == '__main__':
    try:
        # Create a queue for inter-process communication
        queue = Queue()

        # Initialize managers
        iRManager = iRacingManager(queue)
        overlay = iRacingOverlay(queue)

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
