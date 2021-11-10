import logging

LOG_FORMAT = "%(asctime)s|%(levelname)s|%(process)s-%(processName)s|%(thread)d-%(threadName)s|%(filename)s#%(" \
             "funcName)s->line:%(lineno)d|%(message)s "
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

log = logging.getLogger("logger")
