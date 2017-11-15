from psychopy import logging

MESSAGE = 31
logging.addLevel(MESSAGE, 'MESSAGE')
logging.msg = lambda msg: logging.log(msg, MESSAGE)
