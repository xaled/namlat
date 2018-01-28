import os, sys
from os.path import join

if sys.argv[0] == '':
    SCRIPT_DIR = os.path.realpath(sys.argv[0])
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
DATA_DIR = join(SCRIPT_DIR, "data")
SLEEP = 20
