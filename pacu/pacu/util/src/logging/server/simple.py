from .. import identity

identity.log.formatter = 'simple_color_formatter'

from .__main__ import s, loop

if __name__ == '__main__':
    try:
        while True:
            print
            loop(s)
            print
    except BaseException as e: # including keyboard interrupt
        pass
