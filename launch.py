import multiprocessing

import sys
sys.path.append("..")
import port

from sensor import ft
from sensor import sideCam

if __name__ == "__main__":
    pool = multiprocessing.Pool(processes = 8)
    #start ft process
    pool.apply_async(ft.mainLoop, (port.LOG,))
    pool.apply_async(sideCam.mainLoop, (port.LOG,))
    pool.close()
    pool.join()