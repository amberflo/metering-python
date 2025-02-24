import sys


# This line is parsed by setup.py to get the version
VERSION = "3.3.1"

USER_AGENT = "Amberflo.io SDK {}; Python {}".format(
    VERSION, " ".join(sys.version.split())  # clean-up white spaces
)
