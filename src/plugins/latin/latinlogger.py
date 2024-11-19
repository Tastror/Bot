import sys
import logging

latinlogger = logging.getLogger("latin")
latinlogger.setLevel(logging.DEBUG)
latinlogger.propagate = False

hfh_formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
)
hfh = logging.handlers.RotatingFileHandler(
    '../latin.log', mode="a", maxBytes=1024 * 1024 * 8, backupCount=1
)
hfh.setFormatter(hfh_formatter)
latinlogger.addHandler(hfh)

hsh_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(module)s | %(message)s"
)
hsh = logging.StreamHandler(sys.stdout)
hsh.setFormatter(hsh_formatter)
latinlogger.addHandler(hsh)

