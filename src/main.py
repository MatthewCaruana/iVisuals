#!python3

from multiprocessing import Process, Queue

from Overlay import iRacingOverlay
from iRacingManager import iRacingManager


if __name__ == '__main__':
    queue = Queue()

    iRManager = iRacingManager(queue)
    overlay = iRacingOverlay(queue)

    iRManagerThread = Process(target=iRManager.run)

    iRManagerThread.start()
    overlay.run()

    iRManagerThread.join()

    print("Exiting main thread.")
