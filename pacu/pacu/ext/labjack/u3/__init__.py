import time

try:
    import u3
except ImportError:
    U3 = None
else:
    U3 = u3.U3

# TODO: needs to have reset_counter to be able to
#       split between periods in frame counting manner
class U3Resource(object):
    timer0 = u3.Timer0()
    timer1 = u3.Timer1()
    counter = u3.Counter0()
    _reset_offset = 0
    def __init__(self, instance, horigin, lorigin, high, low):
        self.instance = instance
        self.horigin = horigin
        self.lorigin = lorigin
        self.high = high
        self.low = low
    def get_monotonic(self):
        high, low = self.instance.getFeedback(self.timer1, self.timer0)
        b_high = '{:b}00000000000000000000000000000000'.format(high - self.high)
        b_low = '{:032b}'.format(low - self.low)
        tick = int(b_high, 2) + int(b_low, 2)
        return tick * 2.5e-07
        # tick = '{:b}{:032b}'.format(high-self.high, low-self.low)
        # return int(tick, 2) * 2.5e-07
    def get_time(self):
        return self.get_monotonic() - self._reset_offset
    def get_origin(self):
        high, low = self.instance.getFeedback(self.timer1, self.timer0)
        b_high = '{:b}00000000000000000000000000000000'.format(high - self.high)
        b_low = '{:032b}'.format(low - self.low)
        tick = int(b_high, 2) + int(b_low, 2)
        return tick * 2.5e-07
        # high, low = self.instance.getFeedback(self.timer1, self.timer0)
        # tick = '{:b}{:032b}'.format(high-self.horigin, low-self.lorigin)
        # return int(tick, 2) * 2.5e-07
    def get_counter(self):
        return self.instance.getFeedback(self.counter)[0]
    def reset_counter(self):
        raise NotImplementedError
    def reset_timer(self):
        self._reset_offset = self.get_monotonic()

class U3Proxy(object):
    t0config = u3.Timer0Config(TimerMode=10)
    t1config = u3.Timer1Config(TimerMode=11)
    timer0 = u3.Timer0()
    timer1 = u3.Timer1()
    horigin = None
    lorigin = None
    def __init__(self):
        self.instance = U3(debug=False, autoOpen=False)
    def __enter__(self):
        self.instance.open()
        self.instance.configIO(
            TimerCounterPinOffset=4, NumberOfTimersEnabled=2,
            EnableCounter0=True, EnableCounter1=0, FIOAnalog=0)
        _, _, low, high = self.instance.getFeedback(
            self.t0config, self.t1config, self.timer0, self.timer1)
        self.horigin = self.horigin or high
        self.lorigin = self.lorigin or low
        return U3Resource(self.instance, self.horigin, self.lorigin, high, low)
    def __exit__(self, type, value, tb):
        self.instance.close()

def test():
    with U3Proxy() as u3:
        print 'monotonic', u3.get_monotonic()
        print 'origin', u3.get_origin()
        print 'time', u3.get_time()
        import time
        time.sleep(0.5)
        print '0.5 passed'
        u3.reset_timer()
        print 'timer reset'
        print 'monotonic', u3.get_monotonic()
        print 'origin', u3.get_origin()
        print 'time', u3.get_time()

class U3Trigger(object):
    def __init__(self):
        self.instance = U3(debug=False, autoOpen=False)
    def __enter__(self):
        self.instance.open()
        self.instance.configIO(
            TimerCounterPinOffset=4, NumberOfTimersEnabled=0,
            EnableCounter0=0, EnableCounter1=0, FIOAnalog=0)
        return self
    def __exit__(self, type, value, tb):
        self.instance.close()
    def fire(self, pin=0):
        self.instance.setFIOState(pin, 1)
        self.instance.setFIOState(pin, 0)
