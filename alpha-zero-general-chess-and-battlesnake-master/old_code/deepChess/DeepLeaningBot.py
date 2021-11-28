import argparse

from logging import getLogger, disable

from chess_zero.lib.logger import setup_logger
from chess_zero.config import Config
from chess_zero.manager import create_parser, setup, logger
from chess_zero.worker import sl
import os
import sys
import multiprocessing as mp

_PATH_ = os.path.dirname(os.path.dirname(__file__))


if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

mp.set_start_method('spawn')
sys.setrecursionlimit(10000)

parser = create_parser()
args = parser.parse_args()
config_type = args.type

if args.cmd == 'uci':
    disable(999999)  # plz don't interfere with uci

config = Config(config_type=config_type)
setup(config, args)

logger.info(f"config type: {config_type}")

sl.start(config)
