import sys
import time
import logging
import autotest


counter = 0
timesRun = 0

autotest = autotest.AutoTest()

_logger = logging.getLogger("IoT Tester")
_logger.info("[Tester] Main started.")

_initialTime = time.time()

try:
    ret = autotest.executeTests(sys.argv) #sys.argv[1:], quickStop=STOP_AT_FIRST_TEST_ERROR
except Exception as ex:
    print("[Tester] Exception ocurred: ", ex)
    raise ex # Write a full description of error in terminal
    
_totalElapsedTime = int(time.time() - _initialTime) #Stopping stopwatch
hours, remainder = divmod(_totalElapsedTime, 3600)
minutes, seconds = divmod(remainder, 60)
_logger.info("[TestEngine] Main finished, total time: {}h:{}m:{}s. Return value (how many tests failed): '{}'.".format(hours, minutes, seconds, ret)) 

sys.exit(ret)
