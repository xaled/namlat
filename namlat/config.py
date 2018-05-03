import os
import sys
VERSION = ""
if sys.argv[0] == '':
    SCRIPT_DIR = os.path.realpath(sys.argv[0])
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
LIB_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(LIB_DIR, "VERSION")) as fin:
    VERSION = fin.read()
JINJA2_TEMPLATE_DIR = os.path.join(LIB_DIR, "templates")
WEB_STATIC_DIR = os.path.join(LIB_DIR, "static/")
_is_root = os.geteuid() == 0  # TODO: windows
if _is_root:  # TODO: windows
    NAMLAT_HOME_DIR = '/var/lib/namlat'
else:
    NAMLAT_HOME_DIR = os.path.join(os.path.expanduser('~'), '.namlat')
DATA_DIR = os.path.join(NAMLAT_HOME_DIR, "data")
SLEEP = 60
