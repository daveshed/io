from linearstage.gpio.base import GpioBase


class MockGpio(GpioBase):
    """
    https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
    """
    triggered = False

    @staticmethod
    def initialise_output(pin: int):
        pass

    @staticmethod
    def initialise_input(
            pin: int,
            active_low: bool,
            event_callback=None):
        pass

    @staticmethod
    def set_high(pin: int):
        pass

    @staticmethod
    def set_low(pin: int):
        pass

    @staticmethod
    def input_triggered(pin):
        return __class__.triggered

    @staticmethod
    def clean_up():
        pass
