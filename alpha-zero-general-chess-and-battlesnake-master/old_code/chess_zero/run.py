"""
Main entry point for running from command line.
"""

import os
import sys
import multiprocessing as mp

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

if __name__ == "__main__":
    mp.set_start_method('spawn')
    sys.setrecursionlimit(10000)
    # sys.setrecursionlimit() method is used to set the maximum depth of
    # the Python interpreter stack to the required limit. This limit prevents
    # any program from getting into infinite recursion, Otherwise infinite
    # recursion will lead to overflow of the C stack and crash the Python.
    from chess_zero import manager

    manager.start()
