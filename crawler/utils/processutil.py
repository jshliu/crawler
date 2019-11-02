import os
import signal
import sys


def multiprocess_worker(workers=[]):
    '''
    workers = [(worker, args, kwargs), (worker, args, kwargs)]
    '''
    pids = {}
    for worker, args, kwargs in workers:
        pids.update(_create_child(worker, args, kwargs))
    return pids


def _create_child(worker, args, kwargs):
    pid = os.fork()
    if not pid:
        worker(*args, **kwargs)
        sys.exit()
    return {pid: (worker, args, kwargs)}



if __name__ == "__main__":
    pass
