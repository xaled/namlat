import os
import sys

if sys.argv[0] == '':
    SCRIPT_DIR = os.path.realpath(sys.argv[0])
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
JINJA2_TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "templates")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
SLEEP = 20
