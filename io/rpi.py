import RPi.GPIO as GPIO

from linearstage.gpio.base import GpioBase


class RPiGpio(GpioBase):
    _input_active_state = {}
    _DEBOUNCE_MS = 200
    """
    Implementation of the GpioBase interface on the raspberry pi.
    https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
    """
    @staticmethod
    def setup():
        # The GPIO.BOARD option specifies that you are referring to the pins by
        # the number of the pin/channel - i.e the numbers printed on the board
        # (e.g. P1) and in the middle of the diagrams below. The GPIO.BCM option
        # means that you are referring to the pins by the "Broadcom SOC channel"
        # number, these are the numbers after "GPIO" in the green rectangles
        # around the outside of the below diagrams.
        GPIO.setmode(GPIO.BCM)

    @staticmethod
    def initialise_output(pin: int):
        """
        Initialise the output on the given pin

        Args:
            pin (int): the pin to be initialised
        """
        try:
            _input_active_state.pop(pin)
        except KeyError:
            pass
        GPIO.setup(pin, GPIO.OUT)

    @staticmethod
    def initialise_input(pin: int, active_low: bool, event_callback=None):
        """
        Initialise the input on the given pin

        Args:
            pin (int): the index of the pin to be initialised
            active_low (bool): the active state of input - active_low = True
                implies that a signal of 1 implies False.
            event_callback (obj): a callable object to be invoked when the input
                transitions from false to true. Callback must take the signature
                callback(channel).
        """
        GPIO.setup(
            pin,
            GPIO.IN,
            GPIO.PUD_UP if active_low else GPIO.PUD_DOWN)
        RPiGpio._input_active_state[pin] = active_low
        if event_callback:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING if active_low else GPIO.RISING,
                callback=event_callback,
                bouncetime=RPiGpio._DEBOUNCE_MS)

    @staticmethod
    def set_high(pin: int):
        """
        Set the given output signal high

        Args:
            pin (int): the pin index
        """
        GPIO.output(pin, 1)

    @staticmethod
    def set_low(pin: int):
        """
        Set the given output signal low

        Args:
            pin (int): the pin index
        """
        GPIO.output(pin, 0)

    @staticmethod
    def input_triggered(pin: int):
        """
        Read the logical level of the given input

        Args:
            pin (int): the index of the pin

        Returns:
            bool: True if the input is triggered at this instant
        """
        try:
            active_low = RPiGpio._input_active_state[pin]
        except KeyError:
            raise error.GpioError("Pin %d has not been initialised as an input")
        signal = bool(GPIO.input(pin))
        logic_level = not signal if active_low else signal
        return logic_level

    @staticmethod
    def clean_up():
        """
        Clean up all channels configured during the running of the application
        """
        GPIO.cleanup()
