import sys
import logging

pylogger = logging.getLogger("pylogger")
pylogger.setLevel(logging.DEBUG)
pylogger.propagate = False

hfh_formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
)
hfh = logging.handlers.RotatingFileHandler(
    '../pylogger.log', mode="a", maxBytes=1024 * 1024 * 8, backupCount=1
)
hfh.setFormatter(hfh_formatter)
pylogger.addHandler(hfh)

hsh_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(module)s | %(message)s"
)
hsh = logging.StreamHandler(sys.stdout)
hsh.setFormatter(hsh_formatter)
pylogger.addHandler(hsh)
