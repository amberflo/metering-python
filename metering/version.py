import sys


VERSION = "3.0.0"

USER_AGENT = "Amberflo.io SDK {}; Python {}".format(
    VERSION, " ".join(sys.version.split())  # clean-up white spaces
)
