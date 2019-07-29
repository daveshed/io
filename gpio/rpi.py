from stage import gpio
from gpio import error


class OutputChannel(gpio.OutputInterface):
    """
    Concrete implementation of the OutputInterface abstraction
    """
    def __init__(self, pin: int, gpio):
        """
        Initialise the given pin as an output on the gpio instance supplied

        Args:
            pin (int): the physical pin to initialise
            gpio (RPi.GPIO): the raspberry pi gpio driver instance
        """
        self._gpio = gpio
        self._pin = pin
        self._state = None
        self._gpio.setup(pin, gpio.OUT)
        self.set_low()

    @property
    def pin(self):
        """
        The physical pin that this output refers to

        Returns:
            int: the index of the pin this output applies to
        """
        return self._pin

    @property
    def state(self):
        """
        The signal at the output

        Retruns:
            bool: True if the output is high
        """
        return self._state

    def set_high(self):
        """
        Set the output high
        """
        self._gpio.output(self._pin, 1)
        self._state = True

    def set_low(self):
        """
        Set the output low
        """
        self._gpio.output(self._pin, 0)
        self._state = False


class InputChannel(gpio.InputInterface):
    """
    Concrete implementation of the InputInterface abstraction
    """
    _DEBOUNCE_MS = 200

    class CallbackManager:

        def __init__(self):
            self.callbacks = []

        def __call__(self, *args, **kwargs):
            for callback in self.callbacks:
                callback(args, kwargs)

    def __init__(self, pin: int, active_low: bool, gpio):
        """
        Initialise the given pin as an input on the gpio instance supplied

        Args:
            pin (int): the physical pin to use
            active_low (bool): True if the input is active_low ie. a low input
                is interpreted as logical True value
            gpio (obj): the gpio driver instance
        """
        self._callback_manager = InputChannel.CallbackManager()
        self._pin = pin
        self._active_low = active_low
        self._gpio = gpio
        self._gpio.setup(
            pin, gpio.IN, gpio.PUD_UP if active_low else gpio.PUD_DOWN)
        self._gpio.add_event_detect(
            pin,
            gpio.FALLING if active_low else gpio.RISING,
            callback=self._callback_manager,
            bouncetime=InputChannel._DEBOUNCE_MS)

    @property
    def state(self):
        """
        The current logical state of the input

        Returns:
            bool: True if the input is recieving a logical high value at the
                present moment
        """
        signal = bool(self._gpio.input(self._pin))
        logic_level = not signal if self._active_low else signal
        return logic_level

    def register_callback(self, callback):
        """
        Register a callback to be called when the input is activated
        """
        self._callback_manager.callbacks.append(callback)

    def deregister_callback(self, callback):
        """
        Deregister a callback that has already been registered
        """
        try:
            self._callback_manager.callbacks.remove(callback)
        except ValueError:
            raise error.GpioError(
                "Cannot deregister %r. Not registered" % callback)