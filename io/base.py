import abc


class GpioBase(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def setup():
        return

    @staticmethod
    @abc.abstractmethod
    def initialise_output(pin: int):
        return

    @staticmethod
    @abc.abstractmethod
    def initialise_input(pin: int, normally_high: bool, event_callback):
        return

    @staticmethod
    @abc.abstractmethod
    def set_high(pin: int):
        return

    @staticmethod
    @abc.abstractmethod
    def set_low(pin: int):
        return

    @staticmethod
    @abc.abstractmethod
    def input_triggered(pin: int):
        return

    @staticmethod
    @abc.abstractmethod
    def clean_up():
        return
