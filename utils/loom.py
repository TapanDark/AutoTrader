import threading
import logging
from collections import defaultdict
import Queue


class Loom(object):
    """
        A utility to manage threads
    """
    _queuedTasks = defaultdict(lambda: tuple([Queue.Queue(), threading.Event()]))
    _dropTasks = defaultdict(lambda: tuple([Queue.Queue(maxsize=1), threading.Event()]))

    @classmethod
    def _needle(cls, taskTuple):
        queue, runningEvent = taskTuple
        try:
            while True:
                func, args, kwargs = queue.get(block=False)
                func(*args, **kwargs)
                queue.task_done()
        except Queue.Empty:
            logging.debug("Finished batch of tasks. Exiting.")
            runningEvent.clear()

    @classmethod
    def _startLoom(cls, taskTuple):
        thread = threading.Thread(target=cls._needle, args=[taskTuple])
        thread.start()

    @classmethod
    def queueTask(cls, func, *args, **kwargs):
        funcId = id(func)
        try:
            cls._queuedTasks[funcId][0].put((func, args, kwargs))
        except Queue.Full:
            logging.error("Memory Overflow!!" % func.__name__)
            return False
        logging.debug("Queued task %s" % func.__name__)
        if not cls._queuedTasks[funcId][1].is_set():
            cls._queuedTasks[funcId][1].set()
            cls._startLoom(cls._queuedTasks[funcId])  # start processor
        return True

    @classmethod
    def pushTask(cls, func, *args, **kwargs):
        funcId = id(func)
        if cls._dropTasks[funcId][1].is_set():
            logging.debug("Last call to %s has not exited. Skipping update" % func.__name__)
            return True
        else:
            cls._dropTasks[funcId][0].put((func, args, kwargs))
            cls._dropTasks[funcId][1].set()
            cls._startLoom(cls._dropTasks[funcId])  # start processor
        return True

    @classmethod
    def waitForLoom(cls):
        logging.info("Waiting for loom to finish weaving all threads.")
        for task in cls._queuedTasks:
            queue, runningEvent = cls._queuedTasks[task]
            queue.join()
        for task in cls._dropTasks:
            queue, runningEvent = cls._queuedTasks[task]
            queue.join()


if __name__ == "__main__":
    import time
    from utils.tradeLogger import TradeLogger

    TradeLogger.basicConfig()


    def runner(sleepTime, count):
        for i in xrange(0, count):
            print("PIKACHU %s" % i)
            time.sleep(sleepTime)


    def runner2(sleepTime, count):
        for i in xrange(0, count):
            print("TASK2 %s" % i)
            time.sleep(sleepTime)


    Loom.pushTask(runner, 1, 10)
    Loom.pushTask(runner, 1, 10)
    Loom.pushTask(runner2, 1, 10)
    Loom.pushTask(runner, 1, 10)
    Loom.pushTask(runner2, 1, 10)
    Loom.pushTask(runner2, 1, 10)

    Loom.queueTask(runner, 1, 10)
    Loom.queueTask(runner2, 1, 10)
    Loom.queueTask(runner2, 1, 10)
    Loom.queueTask(runner, 1, 10)
    Loom.queueTask(runner, 1, 10)
    Loom.queueTask(runner2, 1, 10)
    Loom.waitForLoom()
